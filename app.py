"""
Multimodal Construction Intelligence Platform (Skill Wallet Capstone Project 1)
Production-Ready Streamlit Application for Construction Site AI Analytics.

Author: Senior Full-Stack AI Engineer
Features:
1. Sidebar: Secure Gemini API Key & Architecture Overview (with Demo Mode fallback)
2. Tab 1: Site Safety & PPE Audit (Epic 2) - OSHA & IS 456 Vision Compliance
3. Tab 2: Crack Diagnostics & Structural Integrity (Epic 2) - Defect & Repair Engine
4. Tab 3: Planning & Real Estate Valuation (Epic 3) - CapEx, BOQ, INR Valuation & 3D Render
5. Tab 4: Daily Site Assistant & Weather-Aware Advisory (Epic 5) - Alerts & Multi-turn Chat
"""

import os
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modular components
from modules.ui_components import inject_custom_css, render_hero_header, status_pill
from modules.gemini_client import GeminiMultimodalClient, MODEL_OPTIONS, DEFAULT_MODEL, resolve_api_key
from modules.safety_audit import render_safety_audit_tab
from modules.crack_diagnostics import render_crack_diagnostics_tab
from modules.planning_valuation import render_planning_valuation_tab
from modules.site_assistant import render_site_assistant_tab


def render_sidebar():
    """Renders the comprehensive sidebar with API Key management and Architecture Overview."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <span style="font-size: 3rem;">🏗️</span>
            <h2 style="margin: 0; color: #f8fafc; font-size: 1.35rem;">Construction Intelligence</h2>
            <span style="font-size: 0.75rem; color: #f59e0b; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                Skill Wallet Capstone 1
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # 1. API Key Input
        st.markdown("### 🔑 API Configuration")
        st.caption("Enter your Google Gemini API Key. If left blank, the platform automatically runs in **Demonstration Mode** with rich simulated AI telemetry.")
        
        # Check pre-configured environment key
        preconfigured_key = resolve_api_key(None)
        
        user_key = st.text_input(
            "Google Gemini API Key:",
            type="password",
            placeholder="AIzaSy...",
            value=preconfigured_key if preconfigured_key else "",
            help="Securely input your Google Gemini API Key. Can also be set via GEMINI_API_KEY environment variable or st.secrets."
        )

        selected_model = st.selectbox(
            "Select Gemini Model:",
            MODEL_OPTIONS,
            index=0,
            help="Choose between ultra-fast Gemini 2.5 Flash or comprehensive Gemini 2.5 Pro."
        )

        # Initialize client
        client = GeminiMultimodalClient(api_key=user_key, model_name=selected_model)

        # Connection status badge
        if client.is_demo_mode:
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 8px; padding: 8px 12px; margin: 10px 0;">
                <div style="color: #fbbf24; font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                    <span>🟠</span> Demonstration Mode Active
                </div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 4px;">
                    Full UI interactive telemetry & pre-loaded scenarios ready for testing without API key.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 8px 12px; margin: 10px 0;">
                <div style="color: #34d399; font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                    <span>🟢</span> Live Gemini AI Connected
                </div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 4px;">
                    Model: <code>{selected_model}</code> active for live vision and chat inference.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # 2. System Architecture Overview
        st.markdown("### 🏛️ Platform Architecture")
        with st.expander("System Technology Stack", expanded=False):
            st.markdown("""
            - **Frontend & App Framework**: Streamlit (Python 3.10+)
            - **Multimodal AI**: Google Gemini 2.5 Flash / Pro (Vision & Text)
            - **Computer Vision Pipeline**: High-res PIL Image ingestion & spatial defect detection
            - **3D Render Synthesis**: Pollinations AI Flux architectural generator
            - **Analytical Engine**: Plotly Interactive S-Curves & Gauges
            - **Persistence**: Session State (Zero external DB dependency)
            """)

        with st.expander("Regulatory & Engineering Codes", expanded=False):
            st.markdown("""
            - **OSHA 29 CFR 1926**:
              - `1926.100`: Head Protection (Hard Hats)
              - `1926.201`: High-Vis Safety Signaling
              - `1926.501`: Duty to Have Fall Protection
              - `1926.1431`: Crane Wind & Safety Limits
            - **Bureau of Indian Standards (BIS)**:
              - `IS 456:2000`: Plain & Reinforced Concrete
              - `IS 2925`: Industrial Safety Helmets
              - `IS 3521`: Full Body Safety Harnesses
              - `IS 7861`: Extreme Weather Concreting
              - `IS 13920`: Ductile Detailing for Seismic Forces
            - **ACI Standards**:
              - `ACI 224.1R`: Concrete Crack Diagnostics
              - `ACI 305R / 306R`: Hot & Cold Weather Curing
            """)

        # Reset button
        st.divider()
        if st.button("🔄 Reset Inspection Session", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        st.caption("Multimodal Construction Intelligence Platform v1.0.0 • Cloud Ready")

    return client


def main():
    # Inject professional CSS theme
    inject_custom_css()

    # Render Sidebar and retrieve configured client
    client = render_sidebar()

    # Render Top Branding Header
    render_hero_header()

    # Main Tab Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "🦺 1. Site Safety & PPE Audit (Epic 2)",
        "🧱 2. Crack Diagnostics & Integrity (Epic 2)",
        "🏗️ 3. Planning & Real Estate Valuation (Epic 3)",
        "🌤️ 4. Daily Site Assistant & Weather Advisory (Epic 5)"
    ])

    with tab1:
        render_safety_audit_tab(client)

    with tab2:
        render_crack_diagnostics_tab(client)

    with tab3:
        render_planning_valuation_tab()

    with tab4:
        render_site_assistant_tab(client)


if __name__ == "__main__":
    main()
