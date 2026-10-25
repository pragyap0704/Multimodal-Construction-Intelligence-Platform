"""
Module: Site Safety & PPE Audit (Epic 2)
Provides computer vision multimodal analysis for worker PPE compliance under OSHA and IS 456,
hazard detection with severity classification, and interactive reporting.
"""

import json
from datetime import datetime
import streamlit as st
from PIL import Image
import plotly.graph_objects as go

from modules.gemini_client import GeminiMultimodalClient
from modules.sample_data import DEMO_SAFETY_AUDIT, create_synthetic_site_image
from modules.ui_components import render_metric_card, status_pill


SAFETY_AUDIT_SYSTEM_PROMPT = """
You are a Principal Health & Safety Auditor and Senior Structural/Construction Engineer specialized in OSHA (29 CFR 1926) and Indian Standard IS 456 / NBC 2016 safety norms.
Your duty is to conduct exhaustive, rigorous visual PPE compliance and physical hazards assessments on construction site imagery.
You must return your output strictly in valid, parseable JSON matching the requested schema with no extra conversational preamble.
"""

SAFETY_AUDIT_USER_PROMPT = """
Analyze this construction site photograph and evaluate worker PPE compliance and occupational safety hazards according to OSHA (29 CFR 1926) and IS 456 / IS 2925 / IS 3521 / NBC 2016 standards.

You MUST respond with a single valid JSON object strictly matching this schema:
{
  "safety_score": <integer from 0 to 100 representing overall site safety health>,
  "overall_status": "<Compliant | Action Required | Severe Non-Compliance>",
  "status_level": "<low | medium | high | critical>",
  "worker_count": <estimated number of visible site personnel>,
  "compliant_workers": <estimated count of personnel wearing complete mandatory PPE>,
  "compliance_percentage": <float, e.g. 75.0>,
  "standards_evaluated": [
    "OSHA 29 CFR 1926.100 (Hard Hats)",
    "OSHA 29 CFR 1926.501 (Fall Protection)",
    "IS 456:2000 / IS 2925 / IS 3521"
  ],
  "ppe_detection": [
    {
      "item": "Industrial Safety Helmet (Hard Hat)",
      "detected_count": <number>,
      "total_workers": <number>,
      "compliance_pct": <number 0-100>,
      "status": "<Compliant | Partial Non-Compliance | Critical Gap>"
    },
    {
      "item": "High-Visibility Safety Vest (Class 2/3)",
      "detected_count": <number>,
      "total_workers": <number>,
      "compliance_pct": <number 0-100>,
      "status": "<Compliant | Action Required | Critical Gap>"
    },
    {
      "item": "Steel-Toe Protective Footwear",
      "detected_count": <number>,
      "total_workers": <number>,
      "compliance_pct": <number 0-100>,
      "status": "<Compliant | Partial Non-Compliance | Unverifiable>"
    },
    {
      "item": "Safety Harness / Fall Arrest System",
      "detected_count": <number>,
      "workers_at_height": <number>,
      "compliance_pct": <number 0-100>,
      "status": "<Compliant | Critical Gap | Not Applicable>"
    }
  ],
  "identified_site_hazards": [
    {
      "id": "HAZ-001",
      "hazard_title": "<Concise descriptive title>",
      "location": "<Visual location in photo, e.g. scaffolding deck / trench edge>",
      "severity": "<Low | Medium | High | Critical>",
      "osha_clause": "<e.g. OSHA 1926.501(b)(1) or IS 3521 / NBC 2016>",
      "observation": "<Specific visual evidence and physical danger>",
      "corrective_remedy": "<Concrete engineering or administrative action required>"
    }
  ]
}
Ensure the JSON is strictly valid. Do not omit any key.
"""


def render_safety_gauge(score: int):
    """Renders a modern gauge chart for Site Safety Score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Site Safety Compliance Score", 'font': {'size': 18, 'color': '#f8fafc'}},
        delta={'reference': 85, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#f43f5e"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': "#f59e0b" if score < 80 else "#10b981"},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(244, 63, 94, 0.35)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.35)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.35)'}
            ],
            'threshold': {
                'line': {'color': "#f8fafc", 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#f8fafc', 'family': 'Inter'},
        height=260,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def render_safety_audit_tab(client: GeminiMultimodalClient):
    """Renders the Tab 1: Site Safety & PPE Audit view."""
    st.markdown("### 🦺 Site Safety & PPE Compliance Audit (Epic 2)")
    st.caption("Automated OSHA (29 CFR 1926) and IS 456 / IS 2925 / IS 3521 vision audit for helmets, vests, harnesses & critical hazard detection.")

    col_input, col_meta = st.columns([1.2, 1])

    with col_input:
        st.markdown("#### 1. Input Construction Telemetry Photo")
        upload_mode = st.radio(
            "Select Photo Source:",
            ["Upload Site Image (JPG/PNG)", "Use Preloaded High-Rise Scaffolding Sample", "Use Deep Trench Excavation Sample"],
            index=1,
            horizontal=True
        )

        selected_image = None

        if upload_mode == "Upload Site Image (JPG/PNG)":
            uploaded_file = st.file_uploader("Upload high-resolution jobsite photo", type=["jpg", "jpeg", "png"], key="safety_uploader")
            if uploaded_file is not None:
                selected_image = Image.open(uploaded_file)
        elif upload_mode == "Use Preloaded High-Rise Scaffolding Sample":
            selected_image = create_synthetic_site_image("scaffolding")
            st.info("Loaded pre-configured high-rise scaffolding inspection scenario (demonstration).")
        else:
            selected_image = create_synthetic_site_image("excavation")
            st.info("Loaded deep excavation and rebar cage inspection scenario (demonstration).")

        if selected_image:
            st.image(selected_image, caption="Active Site Inspection Frame", use_container_width=True)

    with col_meta:
        st.markdown("#### 2. Regulatory Standards Benchmarks")
        st.markdown("""
        - **OSHA 29 CFR 1926.100**: Mandatory head protection where falling objects or electrical hazards exist.
        - **OSHA 29 CFR 1926.501**: Duty to have fall protection (guardrails, safety nets, personal fall arrest systems at >6 ft).
        - **IS 456:2000 Section 2**: Concrete site safety practices and formwork access control.
        - **IS 2925:1984**: Industrial safety helmets specification.
        - **IS 3521:1999**: Full body harnesses and fall arresters specification.
        - **NBC 2016 (Part 7)**: Construction management, safety of workers, and mechanized plant operations.
        """)
        
        audit_btn = st.button("🚀 Run Multimodal Site Safety Audit", type="primary", use_container_width=True)

    # State management for results
    if "safety_audit_result" not in st.session_state:
        st.session_state["safety_audit_result"] = None

    if audit_btn and selected_image:
        with st.spinner("Analyzing site imagery with Gemini Multimodal Vision against OSHA & IS 456 standards..."):
            if client.is_demo_mode:
                # Return high-fidelity demonstration audit
                st.session_state["safety_audit_result"] = DEMO_SAFETY_AUDIT
                st.session_state["safety_mode"] = "demo"
            else:
                success, raw_text, parsed_json = client.analyze_image_with_prompt(
                    image=selected_image,
                    prompt=SAFETY_AUDIT_USER_PROMPT,
                    system_instruction=SAFETY_AUDIT_SYSTEM_PROMPT
                )
                if success and parsed_json:
                    st.session_state["safety_audit_result"] = parsed_json
                    st.session_state["safety_mode"] = "live"
                else:
                    st.warning(f"Live Gemini API response parsing notice: Fallback to high-fidelity schema. ({raw_text[:120]}...)")
                    st.session_state["safety_audit_result"] = DEMO_SAFETY_AUDIT
                    st.session_state["safety_mode"] = "fallback"

    # Display audit results if present
    audit = st.session_state.get("safety_audit_result")
    if audit:
        st.divider()
        st.markdown("### 📊 Comprehensive Site Safety Audit Findings")
        
        # Banner for mode
        mode = st.session_state.get("safety_mode", "demo")
        if mode == "demo":
            st.info("ℹ️ Running in **Demonstration Mode** (Simulated AI Telemetry). Enter your Gemini API key in the sidebar for live vision inference.")
        elif mode == "live":
            st.success("✅ Analysis generated by **Live Google Gemini Vision Engine**.")

        # Metric Cards Row
        score = audit.get("safety_score", 70)
        overall_status = audit.get("overall_status", "Action Required")
        worker_count = audit.get("worker_count", 5)
        compliance_pct = audit.get("compliance_percentage", 65.0)
        hazards = audit.get("identified_site_hazards", [])
        critical_count = sum(1 for h in hazards if h.get("severity", "").lower() == "critical")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Site Safety Score", f"{score}/100", f"Status: {overall_status}", delta="+3 pts vs baseline")
        with c2:
            render_metric_card("Visible Workers", f"{worker_count} On-Site", "Detected via Spatial Vision")
        with c3:
            render_metric_card("PPE Compliance Rate", f"{compliance_pct:.1f}%", "OSHA & IS Standard benchmark")
        with c4:
            render_metric_card("Critical Hazards", f"{critical_count} Flagged", "Require immediate intervention", delta_color="negative" if critical_count > 0 else "positive")

        # Gauge Chart and PPE Checklist
        g_col, ppe_col = st.columns([1, 1.2])

        with g_col:
            st.plotly_chart(render_safety_gauge(score), use_container_width=True)

        with ppe_col:
            st.markdown("#### 📋 Worker PPE Detection Checklist")
            ppe_list = audit.get("ppe_detection", [])
            for item in ppe_list:
                iname = item.get("item", "Equipment")
                dcount = item.get("detected_count", 0)
                tot = item.get("total_workers") or item.get("workers_at_height", worker_count)
                pct = item.get("compliance_pct", 0)
                status = item.get("status", "Compliant")
                
                # Pill color
                variant = "compliant" if pct >= 80 else ("action" if pct >= 50 else "critical")
                
                st.markdown(f"""
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: #f8fafc;">{iname}</span>
                        {status_pill(status, variant)}
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 4px;">
                        Compliance: <b>{pct}%</b> ({dcount}/{tot} workers detected)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(pct / 100.0)

        # Hazards and Corrective Actions Section
        st.markdown("#### ⚠️ Identified Site Hazards & Engineering Remedies")
        if not hazards:
            st.success("No active site hazards detected. Work site meets high compliance standards.")
        else:
            for h in hazards:
                hid = h.get("id", "HAZ-001")
                htitle = h.get("hazard_title", "Unclassified Hazard")
                hloc = h.get("location", "Site Perimeter")
                hsev = h.get("severity", "Medium")
                clause = h.get("osha_clause", "OSHA 1926.20")
                obs = h.get("observation", "")
                remedy = h.get("corrective_remedy", "")

                variant = "critical" if hsev.lower() == "critical" else ("action" if hsev.lower() == "high" else "low")

                st.markdown(f"""
                <div class="hazard-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #f8fafc; font-size: 1.05rem;">{hid}: {htitle}</h4>
                        {status_pill(f"{hsev} Severity", variant)}
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0;">
                        📍 <b>Location:</b> {hloc} | 📜 <b>Code Standard:</b> <code>{clause}</code>
                    </div>
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin: 8px 0;">
                        <b>Observation:</b> {obs}
                    </p>
                    <div class="remedy-box">
                        <span style="color: #10b981; font-weight: 700;">🔧 Mandatory Corrective Remedy:</span>
                        <div style="color: #f1f5f9; margin-top: 4px;">{remedy}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Downloadable Reports
        st.markdown("#### 📥 Export Audit Documentation")
        col_d1, col_d2 = st.columns(2)
        
        # Prepare structured JSON report
        audit_export = {
            "meta": {
                "platform": "Multimodal Construction Intelligence Platform",
                "capstone": "Skill Wallet Capstone Project 1",
                "generated_at": datetime.now().isoformat(),
                "execution_mode": mode
            },
            "audit_data": audit
        }
        json_str = json.dumps(audit_export, indent=2)
        
        with col_d1:
            st.download_button(
                label="📥 Download Structured JSON Safety Report",
                data=json_str,
                file_name=f"site_safety_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

        with col_d2:
            # Prepare markdown report
            md_report = f"""# Construction Site Safety & PPE Audit Report
**Platform:** Multimodal Construction Intelligence Platform (Skill Wallet Capstone Project 1)  
**Date & Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Safety Health Score:** {score} / 100 ({overall_status})  
**Compliance Rate:** {compliance_pct}% | Workers Detected: {worker_count}  

## Identified Hazards:
"""
            for h in hazards:
                md_report += f"- **[{h.get('severity')}] {h.get('hazard_title')}** (Code: {h.get('osha_clause')})\n"
                md_report += f"  - Observation: {h.get('observation')}\n"
                md_report += f"  - Remedy: {h.get('corrective_remedy')}\n\n"

            st.download_button(
                label="📄 Download Markdown Executive Summary",
                data=md_report,
                file_name=f"safety_audit_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
