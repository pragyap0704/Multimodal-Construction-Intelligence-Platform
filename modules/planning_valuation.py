"""
Module: Planning & Real Estate Valuation (Epic 3)
Calculates project budgets, CapEx incurred, asset valuation in INR (Lakhs/Crores),
IS 456 material quantity surveying (steel/cement/RMC), milestone tracking,
and integrates conceptual 3D architectural rendering via Pollinations AI.
"""

import urllib.parse
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import requests
from io import BytesIO
from PIL import Image

from modules.ui_components import render_metric_card


def format_inr(amount_inr: float) -> str:
    """Formats amount in Indian Rupees into Lakhs and Crores."""
    if amount_inr >= 10_000_000: # 1 Crore = 10,000,000
        crores = amount_inr / 10_000_000
        return f"₹ {crores:.2f} Cr"
    elif amount_inr >= 100_000: # 1 Lakh = 100,000
        lakhs = amount_inr / 100_000
        return f"₹ {lakhs:.2f} Lakh"
    else:
        return f"₹ {amount_inr:,.0f}"


# Benchmark costs per sqft based on structure type, city tier, and grade (in INR)
BASE_CONSTRUCTION_RATES = {
    "Residential High-Rise (RCC G+20)": {"Tier 1": 2800, "Tier 2": 2300, "Tier 3": 1950},
    "Commercial Grade-A Office Tower": {"Tier 1": 3800, "Tier 2": 3100, "Tier 3": 2500},
    "Industrial Pre-Engineered Warehouse": {"Tier 1": 1850, "Tier 2": 1550, "Tier 3": 1300},
    "Mixed-Use Retail & Residential": {"Tier 1": 3400, "Tier 2": 2800, "Tier 3": 2300},
    "Luxury Gated Villa Community": {"Tier 1": 4200, "Tier 2": 3400, "Tier 3": 2800}
}

GRADE_MULTIPLIERS = {
    "Standard (Economy Grade)": 1.0,
    "Premium (High-End Finishes)": 1.25,
    "Ultra-Luxury (Italian Marble / Smart Automation)": 1.60
}

# Market Selling price per sqft by Tier (for asset valuation)
MARKET_SELLING_RATES = {
    "Tier 1 (Mumbai / Bengaluru / Delhi NCR / Pune)": {"base": 12500, "land_factor": 1.4},
    "Tier 2 (Ahmedabad / Kochi / Chandigarh / Jaipur)": {"base": 6800, "land_factor": 1.2},
    "Tier 3 (Coimbatore / Nagpur / Bhubaneswar / Indore)": {"base": 4200, "land_factor": 1.1}
}


def render_planning_valuation_tab():
    """Renders the Tab 3: Planning & Real Estate Valuation view."""
    st.markdown("### 🏗️ Planning, Material Surveying & Real Estate Valuation (Epic 3)")
    st.caption("Comprehensive CapEx tracking, IS 456 material quantity estimations (Steel/Cement/RMC), market asset valuation in INR, and 3D architectural AI rendering.")

    # 1. Inputs Section
    st.markdown("#### 1. Project Specifications & Construction Parameters")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        structure_type = st.selectbox(
            "Structure Classification:",
            list(BASE_CONSTRUCTION_RATES.keys()),
            index=0
        )

    with c2:
        tier_choice = st.selectbox(
            "Location Tier (Indian Market):",
            [
                "Tier 1 (Mumbai / Bengaluru / Delhi NCR / Pune)",
                "Tier 2 (Ahmedabad / Kochi / Chandigarh / Jaipur)",
                "Tier 3 (Coimbatore / Nagpur / Bhubaneswar / Indore)"
            ],
            index=0
        )
        tier_key = "Tier 1" if "Tier 1" in tier_choice else ("Tier 2" if "Tier 2" in tier_choice else "Tier 3")

    with c3:
        spec_grade = st.selectbox(
            "Specification Grade:",
            list(GRADE_MULTIPLIERS.keys()),
            index=1
        )

    with c4:
        built_up_sqft = st.number_input(
            "Total Built-up Area (Sq.Ft):",
            min_value=1000,
            max_value=2000000,
            value=75000,
            step=5000
        )

    # Completion slider
    st.markdown("#### 2. Milestone Execution Stage")
    completion_pct = st.slider(
        "Current Physical Completion Milestone (%):",
        min_value=0,
        max_value=100,
        value=62,
        format="%d%%"
    )

    # Determine Phase name
    if completion_pct < 15:
        curr_phase = "Phase 1: Substructure, Piling & Deep Excavation"
        phase_color = "#38bdf8"
    elif completion_pct < 45:
        curr_phase = "Phase 2: RCC Framing & Superstructure Casting"
        phase_color = "#f59e0b"
    elif completion_pct < 70:
        curr_phase = "Phase 3: Masonry, MEP Infrastructure & Internal Plaster"
        phase_color = "#fbbf24"
    elif completion_pct < 90:
        curr_phase = "Phase 4: Façade Glazing, Architectural Finishes & Flooring"
        phase_color = "#10b981"
    else:
        curr_phase = "Phase 5: Final MEP Testing, Snagging & Occupancy Certificate (OC)"
        phase_color = "#34d399"

    st.markdown(f"""
    <div style="background: #1e293b; border-left: 5px solid {phase_color}; padding: 12px 18px; border-radius: 0 8px 8px 0; margin-bottom: 16px;">
        <span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Current Milestone Phase:</span>
        <div style="color: #f8fafc; font-size: 1.1rem; font-weight: 700;">{curr_phase} ({completion_pct}% Complete)</div>
    </div>
    """, unsafe_allow_html=True)

    # Financial & Engineering Calculations
    base_rate = BASE_CONSTRUCTION_RATES[structure_type][tier_key]
    rate_mult = GRADE_MULTIPLIERS[spec_grade]
    effective_cost_per_sqft = base_rate * rate_mult

    total_capex_budget = built_up_sqft * effective_cost_per_sqft
    capex_incurred = total_capex_budget * (completion_pct / 100.0)
    capex_remaining = total_capex_budget - capex_incurred

    # Valuation dynamics
    market_rate_data = MARKET_SELLING_RATES[tier_choice]
    market_selling_rate_sqft = market_rate_data["base"] * (1.2 if "Premium" in spec_grade else (1.45 if "Luxury" in spec_grade else 1.0))
    full_project_market_val = built_up_sqft * market_selling_rate_sqft

    # Current asset valuation based on work done + land value contribution
    land_equity_pct = 0.35  # Land equity factor
    current_asset_valuation = (full_project_market_val * land_equity_pct) + (full_project_market_val * (1 - land_equity_pct) * (completion_pct / 100.0))
    net_equity_value = current_asset_valuation - capex_incurred

    # Material quantities per IS 456 benchmarks
    # Steel: ~ 4.2 kg/sqft for standard RCC high-rise
    steel_factor = 4.2 if "High-Rise" in structure_type else (3.6 if "Commercial" in structure_type else 2.8)
    total_steel_kg = built_up_sqft * steel_factor
    total_steel_mt = total_steel_kg / 1000.0
    consumed_steel_mt = total_steel_mt * (min(completion_pct * 1.3, 100.0) / 100.0)
    remaining_steel_mt = max(0.0, total_steel_mt - consumed_steel_mt)

    # Cement: ~ 0.42 bags/sqft (50kg bag)
    total_cement_bags = int(built_up_sqft * 0.42)
    total_cement_mt = (total_cement_bags * 50) / 1000.0
    consumed_cement_bags = int(total_cement_bags * (completion_pct / 100.0))
    remaining_cement_bags = total_cement_bags - consumed_cement_bags

    # RMC (Ready Mix Concrete M25/M30): ~ 0.052 cu.m per sqft
    total_rmc_cum = built_up_sqft * 0.052
    consumed_rmc_cum = total_rmc_cum * (min(completion_pct * 1.25, 100.0) / 100.0)
    remaining_rmc_cum = max(0.0, total_rmc_cum - consumed_rmc_cum)

    # Display Financial Metrics Row
    st.markdown("#### 3. Capital Expenditure & Market Valuation Analytics")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        render_metric_card("Total Project CapEx", format_inr(total_capex_budget), f"Cost: ₹ {effective_cost_per_sqft:,.0f}/sq.ft")
    with f2:
        render_metric_card("CapEx Incurred", format_inr(capex_incurred), f"{completion_pct}% of total capital deployed", delta=f"{completion_pct}% Disbursed")
    with f3:
        render_metric_card("Current Asset Value", format_inr(current_asset_valuation), f"Work-in-progress + Land Equity", delta="+18.4% Appreciation", delta_color="positive")
    with f4:
        render_metric_card("Projected Completion Value", format_inr(full_project_market_val), f"Sale rate: ₹ {market_selling_rate_sqft:,.0f}/sq.ft", delta="Full OC Market Target", delta_color="positive")

    # Plotly Charts: S-Curve CapEx vs Asset Value Trajectory
    pct_range = list(range(0, 105, 5))
    capex_curve = [total_capex_budget * (p / 100.0) for p in pct_range]
    val_curve = [(full_project_market_val * land_equity_pct) + (full_project_market_val * (1 - land_equity_pct) * (p / 100.0)) for p in pct_range]

    fig_curves = go.Figure()
    fig_curves.add_trace(go.Scatter(
        x=pct_range, y=[v / 10_000_000 for v in val_curve],
        mode='lines+markers', name='Asset Market Valuation (₹ Cr)',
        line=dict(color='#10b981', width=3)
    ))
    fig_curves.add_trace(go.Scatter(
        x=pct_range, y=[c / 10_000_000 for c in capex_curve],
        mode='lines', name='Cumulative CapEx Incurred (₹ Cr)',
        line=dict(color='#f59e0b', width=3, dash='dash')
    ))
    # Add milestone marker
    fig_curves.add_vline(x=completion_pct, line_width=2, line_dash="dot", line_color="#38bdf8",
                         annotation_text=f"Current: {completion_pct}%", annotation_position="top left",
                         annotation_font_color="#38bdf8")

    fig_curves.update_layout(
        title="CapEx Deployment vs Asset Market Valuation Trajectory (₹ Crores)",
        xaxis_title="Construction Completion Milestone (%)",
        yaxis_title="Valuation / Expenditure (₹ Crores)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.6)',
        font={'color': '#f8fafc', 'family': 'Inter'},
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curves, use_container_width=True)

    # Material Quantity Surveying (IS 456 Benchmarks)
    st.markdown("#### 4. Material Quantity Surveying & Bill of Quantities (BOQ)")
    st.caption("Structural reinforcement (Fe500D TMT), Grade 53 cement, and RMC batching forecasts aligned with IS 456 specifications.")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="diagnostic-panel">
            <h4 style="margin: 0; color: #38bdf8;">🔩 Structural Steel (Fe500D)</h4>
            <div style="font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin: 8px 0;">{total_steel_mt:,.1f} MT Total</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">Consumed: <b>{consumed_steel_mt:,.1f} MT</b></div>
            <div style="font-size: 0.85rem; color: #f59e0b;">Balance Requisition: <b>{remaining_steel_mt:,.1f} MT</b></div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(consumed_steel_mt / max(total_steel_mt, 1.0), 1.0))

    with m2:
        st.markdown(f"""
        <div class="diagnostic-panel">
            <h4 style="margin: 0; color: #10b981;">🧱 Cement (OPC 53 / PPC)</h4>
            <div style="font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin: 8px 0;">{total_cement_bags:,} Bags</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">Consumed: <b>{consumed_cement_bags:,} Bags</b> ({total_cement_mt * (completion_pct/100):,.1f} MT)</div>
            <div style="font-size: 0.85rem; color: #f59e0b;">Balance Requisition: <b>{remaining_cement_bags:,} Bags</b></div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(consumed_cement_bags / max(total_cement_bags, 1), 1.0))

    with m3:
        st.markdown(f"""
        <div class="diagnostic-panel">
            <h4 style="margin: 0; color: #fbbf24;">🏗️ Ready-Mix Concrete (RMC)</h4>
            <div style="font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin: 8px 0;">{total_rmc_cum:,.0f} m³ Total</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">Cast to Date: <b>{consumed_rmc_cum:,.0f} m³</b></div>
            <div style="font-size: 0.85rem; color: #f59e0b;">Balance Pours: <b>{remaining_rmc_cum:,.0f} m³</b></div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(consumed_rmc_cum / max(total_rmc_cum, 1.0), 1.0))

    # Conceptual 3D Architectural Rendering via Pollinations AI
    st.divider()
    st.markdown("#### 5. Conceptual 3D Architectural Rendering (Pollinations AI Integration)")
    st.caption("Generate high-definition photorealistic 3D architectural visualizations of the proposed structure in its urban setting.")

    r_col1, r_col2 = st.columns([1.2, 1])

    with r_col1:
        arch_style = st.selectbox(
            "Architectural Design Style:",
            [
                "Biophilic Futuristic with Vertical Terraces and Lush Greenery",
                "Parametric Glass Curtain Wall & Sleek Steel Modernism",
                "Contemporary Indian Neo-Classical with Terracotta Jali Screens",
                "Sustainable Net-Zero Timber-Concrete Hybrid Architecture",
                "Bold Post-Modern Geometric Tower with Cantilevered Balconies"
            ],
            index=0
        )
        time_setting = st.selectbox(
            "Lighting & Environment:",
            ["Dramatic Sunset Golden Hour with Warm Interior Glow", "Crystal Clear Crisp Daylight Blue Sky", "Atmospheric Blue Twilight with Facade Architectural Spotlights"],
            index=0
        )

        # Dynamic architectural prompt generator
        default_prompt = (
            f"Photorealistic 3D architectural visualization of a luxury {structure_type.lower()}, "
            f"style: {arch_style}, located in modern metropolitan Indian city, {time_setting}, "
            f"unreal engine 5 architectural render, 8k resolution, octane render, architectural photography, hyper-detailed, award-winning building design"
        )

        custom_prompt = st.text_area("Generated Architectural Prompt (Editable):", value=default_prompt, height=100)
        generate_render_btn = st.button("🎨 Render 3D Architectural Concept", type="primary", use_container_width=True)

    with r_col2:
        st.markdown("**Render Preview**")
        
        # State for render image
        if "pollinations_render_url" not in st.session_state:
            st.session_state["pollinations_render_url"] = None

        if generate_render_btn:
            encoded_prompt = urllib.parse.quote(custom_prompt)
            # Pollinations AI image endpoint with flux model & seed
            render_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true&seed=42"
            st.session_state["pollinations_render_url"] = render_url
            st.session_state["pollinations_render_prompt"] = custom_prompt

        curr_url = st.session_state.get("pollinations_render_url")
        if curr_url:
            with st.spinner("Fetching 3D render from Pollinations AI..."):
                try:
                    # Download image for display and download button
                    resp = requests.get(curr_url, timeout=20)
                    if resp.status_code == 200:
                        render_img = Image.open(BytesIO(resp.content))
                        st.image(render_img, caption="AI-Synthesized 3D Architectural Elevation", use_container_width=True)
                        
                        st.download_button(
                            label="📥 Download High-Res Render (PNG)",
                            data=resp.content,
                            file_name=f"architectural_3d_render_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    else:
                        st.image(curr_url, caption="3D Architectural Visualization", use_container_width=True)
                except Exception as e:
                    # Direct URL fallback
                    st.image(curr_url, caption="3D Architectural Visualization (Direct Stream)", use_container_width=True)
        else:
            # Show placeholder visual
            st.markdown("""
            <div style="background: #1e293b; border: 2px dashed #475569; border-radius: 12px; height: 260px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; text-align: center; padding: 20px;">
                <span style="font-size: 2.5rem; margin-bottom: 8px;">🏢</span>
                <div style="font-weight: 600; color: #cbd5e1;">Click "Render 3D Architectural Concept"</div>
                <div style="font-size: 0.8rem; margin-top: 4px;">Generates photo-realistic conceptual elevation powered by Pollinations AI Flux engine.</div>
            </div>
            """, unsafe_allow_html=True)
