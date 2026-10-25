"""
Gemini Client module supporting Google Gemini Multimodal Vision and Text APIs.
Provides seamless fallback to Demonstration Mode when no API key is provided,
and dual SDK / REST implementation for maximum reliability.
"""

import os
import json
import base64
import io
import requests
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image

# Available models
DEFAULT_MODEL = "gemini-2.5-flash"
MODEL_OPTIONS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]


def resolve_api_key(user_input_key: Optional[str] = None) -> Optional[str]:
    """
    Resolves the Gemini API key from user input, environment variables, or Streamlit secrets.
    """
    if user_input_key and user_input_key.strip():
        return user_input_key.strip()
    
    # Check OS environment
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    
    # Try streamlit secrets safely
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            secret_key = st.secrets["GEMINI_API_KEY"]
            if secret_key and str(secret_key).strip():
                return str(secret_key).strip()
    except Exception:
        pass
    
    return None


def extract_json_payload(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts and parses JSON object from an LLM response string,
    handling markdown fences (```json ... ```) and leading/trailing chatter.
    """
    if not response_text:
        return None
    
    cleaned = response_text.strip()
    
    # Check for markdown code fences
    if "```json" in cleaned:
        parts = cleaned.split("```json")
        if len(parts) > 1:
            candidate = parts[1].split("```")[0].strip()
            try:
                return json.loads(candidate)
            except Exception:
                pass
    elif "```" in cleaned:
        parts = cleaned.split("```")
        if len(parts) > 1:
            candidate = parts[1].strip()
            try:
                return json.loads(candidate)
            except Exception:
                pass
    
    # Try finding the first '{' and last '}'
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        slice_candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(slice_candidate)
        except Exception:
            pass

    # Direct parse attempt
    try:
        return json.loads(cleaned)
    except Exception:
        return None


def image_to_base64_jpeg(pil_img: Image.Image) -> str:
    """Converts a PIL Image to a base64 encoded JPEG string."""
    buffered = io.BytesIO()
    # Convert RGBA to RGB if necessary
    if pil_img.mode in ("RGBA", "P"):
        pil_img = pil_img.convert("RGB")
    pil_img.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


class GeminiMultimodalClient:
    """
    Multimodal client managing calls to Google Gemini models with automatic
    demonstration mode fallback and zero-crash exception handling.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_MODEL):
        self.api_key = resolve_api_key(api_key)
        self.model_name = model_name
        self.is_demo_mode = self.api_key is None or len(self.api_key.strip()) < 5

    def analyze_image_with_prompt(
        self,
        image: Image.Image,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Sends an image + prompt to Gemini.
        Returns: (success: bool, raw_text: str, parsed_json: Optional[Dict])
        """
        if self.is_demo_mode:
            return False, "Demonstration Mode Active (No API Key provided)", None

        # Method 1: Try official google-genai SDK if available
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction
            
            # Format image as bytes
            buffered = io.BytesIO()
            rgb_img = image.convert("RGB") if image.mode in ("RGBA", "P") else image
            rgb_img.save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()

            part_image = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            response = client.models.generate_content(
                model=self.model_name,
                contents=[part_image, prompt],
                config=config
            )
            raw_text = response.text or ""
            parsed = extract_json_payload(raw_text)
            return True, raw_text, parsed

        except Exception as e_sdk:
            # Fallback to direct REST API call (resilient against SDK environment disparities)
            try:
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                b64_img = image_to_base64_jpeg(image)

                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": b64_img
                                    }
                                },
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
                if system_instruction:
                    payload["system_instruction"] = {
                        "parts": [{"text": system_instruction}]
                    }

                headers = {"Content-Type": "application/json"}
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=45)
                
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                        parsed = extract_json_payload(text)
                        return True, text, parsed
                    return False, f"API returned empty candidate response: {resp.text}", None
                else:
                    return False, f"Gemini API Error (HTTP {resp.status_code}): {resp.text}", None

            except Exception as e_rest:
                return False, f"Vision API Call Failed: SDK error ({str(e_sdk)}) | REST error ({str(e_rest)})", None

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str
    ) -> Tuple[bool, str]:
        """
        Multi-turn text generation for Site Assistant chatbot.
        messages format: [{"role": "user"|"assistant", "content": "..."}]
        """
        if self.is_demo_mode:
            return False, "Demonstration Mode Active (No API Key provided)"

        # REST implementation for multi-turn chat
        try:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            payload = {
                "contents": contents,
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                }
            }

            headers = {"Content-Type": "application/json"}
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=35)
            
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    text = "".join(p.get("text", "") for p in parts)
                    return True, text
                return False, "Received empty response from assistant."
            else:
                return False, f"Chat API Error (HTTP {resp.status_code}): {resp.text}"

        except Exception as e:
            return False, f"Assistant communication error: {str(e)}"
