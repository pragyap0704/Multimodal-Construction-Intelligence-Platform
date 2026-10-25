"""
Module: Daily Site Assistant & Weather-Aware Advisory (Epic 5)
Provides weather-driven construction safety protocols (crane shutdown, electrical mitigation,
concrete curing per IS 7861 / IS 456), and an interactive multi-turn engineering chatbot.
"""

from datetime import datetime
import streamlit as st
from modules.gemini_client import GeminiMultimodalClient


SITE_ENGINEER_SYSTEM_PROMPT = """
You are a Senior Principal Construction & Structural Engineer with 25+ years of international field experience and certified expertise in OSHA (29 CFR 1926), Indian Standard IS 456:2000 (Plain and Reinforced Concrete - Code of Practice), IS 7861 (Extreme Weather Concreting), IS 13920 (Ductile Detailing), and NBC 2016.

Your demeanor is authoritative, highly practical, technically rigorous, and safety-first.
When answering site engineering questions:
1. Always reference exact relevant codes and clauses where applicable (e.g., IS 456 Clause 11.3 for formwork stripping, Clause 26.2.1 for development length, Table 16 for nominal cover, Table 19 for shear stress; OSHA 1926.1431 for crane wind limits, OSHA 1926.651 for excavations).
2. Provide step-by-step actionable guidance with concrete specifications (grades M20, M25, M30, M40, Fe500D rebar, water-cement ratios).
3. Warn against common jobsite malpractices (e.g. adding excess water to transit mixers on site, stripping props prematurely, poor vibrator compaction).
Keep responses organized with markdown bullet points and clear headings.
"""

WEATHER_ADVISORIES = {
    "High Wind (>38 km/h / 20+ Knots)": {
        "status": "CRITICAL WEATHER ALERT",
        "color": "#ef4444",
        "icon": "💨",
        "crane_protocol": "IMMEDIATE TOWER CRANE SHUTDOWN: Suspend all crane, hoist, and suspended cradle operations immediately per OSHA 1926.1431 and IS 456. Disengage slew brakes to allow jibs to 'weathervane' freely into the wind direction to prevent structural overturn.",
        "height_work": "Halt all work on external scaffolding, perimeter facade glazing, and suspended mast platforms above 6 meters. Tie down loose shuttering sheets, timber planks, and corrugated metal roofing.",
        "concrete_protocol": "High evaporation risk: Slabs exposed to high winds experience accelerated surface moisture loss causing severe plastic shrinkage cracking. Apply aliphatic alcohol anti-evaporant sprays immediately upon screeding; erect windbreaks around pour perimeter.",
        "electrical_safety": "Inspect exterior temporary power masts and overhead service drops. Secure all dangling cables and floodlight stanchions against swaying and mechanical abrasion."
    },
    "Heavy Rain & Monsoon Inundation": {
        "status": "SEVERE WEATHER ADVISORY",
        "color": "#38bdf8",
        "icon": "🌧️",
        "crane_protocol": "Ground load-bearing verification: Heavy precipitation softens crane outrigger pads. Inspect timber/steel mats under mobile crane outriggers for differential ground subsidence. Limit lifting speeds due to reduced rigger visibility and wet tag lines.",
        "height_work": "Slip hazard on steel beams and scaffold deck boards. Postpone all structural steel erection and rebar fixing on wet elevated decks until traction is restored.",
        "concrete_protocol": "MONSOON CONCRETING PROTOCOL (IS 7861 / IS 456): Never cast exposed slabs during active downpours. Fresh concrete will suffer wash-out of cement paste, drastically increasing surface w/c ratio and compromising 28-day characteristic strength. Keep heavy-duty polythene sheeting staged immediately adjacent to pour zones.",
        "electrical_safety": "HIGH ELECTRICAL HAZARD: Immediately de-energize external distribution panels located at grade. Test all 30mA Earth Leakage Circuit Breakers (ELCB / GFCI). Submersible sump pumps must be deployed in basement excavations and lift pits."
    },
    "Extreme Heat (>40°C / 104°F & High UV)": {
        "status": "THERMAL STRESS & HOT WEATHER PROTOCOL",
        "color": "#f97316",
        "icon": "☀️",
        "crane_protocol": "Continuous monitoring of hydraulic fluid temperatures in tower cranes, hoists, and batching plants to prevent seal cavitation and brake slippage.",
        "height_work": "Worker thermal stress: Implement mandatory 15-minute rest rotations every 60 minutes in shaded cooling zones. Provide chilled electrolyte hydration stations at every 3rd floor level per OSHA Heat Illness Prevention standards.",
        "concrete_protocol": "HOT WEATHER CONCRETING PROTOCOL (IS 7861 Part 1 & ACI 305R): Fresh concrete placement temperature must NOT exceed 32°C. Replace mixing water with flake ice (up to 50% replacement). Pre-wet aggregate stockpiles and transit mixer drums. Commence continuous ponding or wet burlap curing immediately after initial set.",
        "electrical_safety": "Inspect portable generators and transformers for overheating; avoid continuous peak load operation during peak solar irradiance (12:00 PM - 3:30 PM)."
    },
    "Normal / Favorable Weather (22°C - 30°C)": {
        "status": "OPTIMAL WORKING CONDITIONS",
        "color": "#10b981",
        "icon": "🌤️",
        "crane_protocol": "Normal crane operations authorized. Conduct routine daily pre-shift limit switch, wire rope, and load moment indicator (LMI) calibration checks.",
        "height_work": "Standard working-at-heights protocols in effect. Enforce 100% tie-off with dual shock-absorbing lanyards and full-body harnesses above 1.8 meters (OSHA 1926.501 / IS 3521).",
        "concrete_protocol": "Standard curing protocols per IS 456:2000 Clause 13.5: Maintain moist curing for a minimum of 7 days for Ordinary Portland Cement (OPC) and 10 days for mineral admixture mixes (Fly ash / GGBS / PPC).",
        "electrical_safety": "Routine weekly inspections of lock-out/tag-out (LOTO) procedures and extension cord continuity."
    }
}

DEMO_CHAT_RESPONSES = {
    "stripping": """### ⏱️ Formwork Stripping Times per IS 456:2000 Clause 11.3

Under normal temperature conditions (ambient temperature above 15°C) and using Ordinary Portland Cement (OPC):

1. **Vertical formwork to columns, walls, and beam sides**:
   - **16 to 24 hours** (after concrete has achieved sufficient surface hardness).
2. **Slab soffits (props left underneath)**:
   - **3 days** (props must remain undisturbed).
3. **Beam soffits (props left underneath)**:
   - **7 days** (props must remain undisturbed).
4. **Removal of props to slabs**:
   - Spanning up to 4.5 meters: **7 days**
   - Spanning over 4.5 meters: **14 days**
5. **Removal of props to beams and arches**:
   - Spanning up to 6 meters: **14 days**
   - Spanning over 6 meters: **21 days**

> ⚠️ **Critical Engineering Warning**: If using Pozzolanic cements (PPC) or Slag cement (PSC), curing and strength gain are slower; add **3 to 5 additional days** to the above stripping schedules unless field cube crushing tests prove 85%+ design strength!""",

    "wind": """### 💨 Tower Crane High Wind Protocols (OSHA 1926.1431 & IS 456)

When sustained wind speeds exceed **38 km/h (20 knots / ~10.5 m/s)** or gusts exceed **45 km/h**:

1. **Immediate Crane Stoppage**:
   - Land any live suspended load safely on the ground immediately.
   - Hoist the empty hook block to within 3 meters below the trolley.
   - Move the trolley close to the tower mast (within minimum working radius).
2. **Engage Weathervaning (Free Slewing Mode)**:
   - **CRITICAL**: Disengage the slew ring brake. The jib must be permitted to rotate freely 360° so that the counter-jib aligns against the wind and the long jib points downwind, reducing aerodynamic drag and overturning moment.
3. **Electrical & Mechanical Isolation**:
   - Secure external operator cabin doors and engage rail clamps if operating on track-mounted bogies.
   - Verify anemometer readout on the central telemetry console.
4. **Site Evacuation**:
   - Clear all ground personnel within the crane’s maximum jib radius fall shadow.""",

    "lap": """### 📐 Development Length ($L_d$) & Lap Length Calculation per IS 456:2000

For **25mm diameter Fe500D TMT bars** in **M30 Grade Concrete** under direct tension:

#### 1. Fundamental Formula (Clause 26.2.1):
$$L_d = \\frac{\\phi \\cdot \\sigma_s}{4 \\cdot \\tau_{bd}}$$

Where:
- Nominal bar diameter $\\phi = 25\\text{ mm}$
- Stress in bar $\\sigma_s = 0.87 \\times f_y = 0.87 \\times 500 = 435\\text{ N/mm}^2$
- Design bond stress $\\tau_{bd}$ for M30 plain bars in tension = $1.5\\text{ N/mm}^2$ (Table from Clause 26.2.1.1)
- For deformed (HYSD/TMT Fe500D) bars, $\\tau_{bd}$ is increased by **60%**:
  $$\\tau_{bd} = 1.5 \\times 1.6 = 2.40\\text{ N/mm}^2$$

#### 2. Calculation:
$$L_d = \\frac{25 \\times 435}{4 \\times 2.40} = \\frac{10875}{9.60} \\approx 1133\\text{ mm} \\approx 45.3\\phi$$

#### 3. Tension Lap Length (Clause 26.2.5.1):
- Lap length in tension must be equal to $L_d$ or $30\\phi$, whichever is greater.
- When staggered splices are used with less than 50% bars spliced at one section:
  **Lap Length = $1.0 \\times L_d \\approx 1,150\\text{ mm}$ (approx. $46\\phi$)**.
- If more than 50% bars spliced at the same section:
  **Lap Length = $1.3 \\times L_d \\approx 1,475\\text{ mm}$ (approx. $59\\phi$)**.

> 💡 **Best Practice**: Stagger laps by at least $1.3 \\times L_d$ (1.5 meters) center-to-center and provide closely spaced stirrups (spacing $\\le 100\\text{ mm}$) throughout the lap zone.""",

    "hot_weather": """### ☀️ Hot Weather Concreting Protocols (IS 7861 Part 1 & ACI 305R)

When ambient temperature exceeds **35°C**:

1. **Placement Temperature Target**:
   - Keep fresh concrete temperature below **32°C** at the time of discharge into formwork.
2. **Batching Modifications**:
   - Substitute chilled batch water and flake ice (up to 40-50% of total mix water by weight).
   - Sprinkler aggregate stock piles to promote evaporative cooling.
3. **Chemical Admixtures**:
   - Incorporate retarding plasticizers (ASTM C494 Type D/G) to counteract premature slump loss and prevent cold joints.
4. **Pouring Timing**:
   - Schedule critical large raft foundation or slab pours during late evening or night shifts (8:00 PM to 6:00 AM).
5. **Curing Regime**:
   - Begin water ponding or saturated double-layer burlap covering within 30 minutes of final finishing. Never allow the concrete surface to dry during the first 72 hours!"""
}


def render_site_assistant_tab(client: GeminiMultimodalClient):
    """Renders Tab 4: Daily Site Assistant & Weather-Aware Advisory."""
    st.markdown("### 🌤️ Daily Site Assistant & Weather-Aware Engineering Advisory (Epic 5)")
    st.caption("Real-time weather mitigation protocols (crane safety, concrete curing per IS 7861, electrical hazard defense) and interactive multi-turn structural AI engineering assistant.")

    # Section 1: Weather Condition Selector & Dynamic Safety Alerts
    st.markdown("#### 1. Weather Telemetry & Automated Safety Directives")
    weather_cond = st.selectbox(
        "Current Site Meteorological Condition:",
        list(WEATHER_ADVISORIES.keys()),
        index=0
    )

    adv = WEATHER_ADVISORIES[weather_cond]
    w_color = adv["color"]
    w_icon = adv["icon"]

    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.9); border: 2px solid {w_color}; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2rem;">{w_icon}</span>
                <h3 style="margin: 0; color: {w_color};">{adv['status']}</h3>
            </div>
            <span style="background: {w_color}22; color: {w_color}; border: 1px solid {w_color}; padding: 4px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.8rem;">
                MANDATORY PROTOCOL
            </span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
            <div style="background: #0f172a; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <b style="color: #f59e0b;">🏗️ Crane & Heavy Lifting Directives:</b>
                <p style="color: #cbd5e1; font-size: 0.88rem; margin: 6px 0 0 0;">{adv['crane_protocol']}</p>
            </div>
            <div style="background: #0f172a; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #38bdf8;">
                <b style="color: #38bdf8;">🧗 Working at Heights & Scaffolding:</b>
                <p style="color: #cbd5e1; font-size: 0.88rem; margin: 6px 0 0 0;">{adv['height_work']}</p>
            </div>
            <div style="background: #0f172a; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #10b981;">
                <b style="color: #10b981;">🧱 Concrete Curing & Pouring (IS 7861 / IS 456):</b>
                <p style="color: #cbd5e1; font-size: 0.88rem; margin: 6px 0 0 0;">{adv['concrete_protocol']}</p>
            </div>
            <div style="background: #0f172a; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #f43f5e;">
                <b style="color: #f43f5e;">⚡ Electrical & Sump Mitigation:</b>
                <p style="color: #cbd5e1; font-size: 0.88rem; margin: 6px 0 0 0;">{adv['electrical_safety']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section 2: Interactive Multi-Turn Construction Engineering Chatbot
    st.divider()
    st.markdown("#### 2. Senior Site Engineering & Standards Chatbot")
    st.caption("Trained on OSHA 1926, IS 456:2000, IS 13920, and NBC 2016. Ask technical questions on structural detailing, curing, formwork stripping, bar bending, or safety.")

    # Initialize chat state
    if "site_assistant_messages" not in st.session_state:
        st.session_state["site_assistant_messages"] = [
            {
                "role": "assistant",
                "content": "👋 Greetings Engineer. I am your Senior Construction & Structural Engineering Intelligence Assistant. How can I assist you with site execution, IS 456 clauses, crane wind limits, or formwork stripping protocols today?"
            }
        ]

    # Quick prompt buttons
    st.markdown("**Quick Technical Engineering Prompts:**")
    qb1, qb2, qb3, qb4 = st.columns(4)
    quick_query = None

    with qb1:
        if st.button("⏱️ Formwork Stripping Times (IS 456)", use_container_width=True):
            quick_query = "What are the minimum formwork stripping times for beam soffits and slabs per IS 456 Clause 11.3?"
    with qb2:
        if st.button("💨 Crane High Wind Limits (OSHA)", use_container_width=True):
            quick_query = "What are the mandatory crane shutdown protocols when wind speeds exceed 38 km/h?"
    with qb3:
        if st.button("📐 Lap Length 25mm Fe500D (IS 456)", use_container_width=True):
            quick_query = "How do I calculate development length and tension lap length for 25mm Fe500D bars in M30 concrete?"
    with qb4:
        if st.button("☀️ Hot Weather Concreting (IS 7861)", use_container_width=True):
            quick_query = "What are the hot weather concreting precautions per IS 7861 to prevent plastic shrinkage cracking?"

    # Display chat history
    for msg in st.session_state["site_assistant_messages"]:
        with st.chat_message(msg["role"], avatar="👷‍♂️" if msg["role"] == "user" else "🏗️"):
            st.markdown(msg["content"])

    # Chat input or quick query trigger
    user_prompt = st.chat_input("Ask a construction, structural, or safety standards question...") or quick_query

    if user_prompt:
        # Append user message
        st.session_state["site_assistant_messages"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user", avatar="👷‍♂️"):
            st.markdown(user_prompt)

        # Generate response
        with st.chat_message("assistant", avatar="🏗️"):
            with st.spinner("Consulting engineering codebooks & structural standards..."):
                reply_text = ""
                if client.is_demo_mode:
                    # Provide rich contextual engineering response from expert corpus
                    u_low = user_prompt.lower()
                    if "stripping" in u_low or "formwork" in u_low or "soffit" in u_low:
                        reply_text = DEMO_CHAT_RESPONSES["stripping"]
                    elif "wind" in u_low or "crane" in u_low or "weathervan" in u_low:
                        reply_text = DEMO_CHAT_RESPONSES["wind"]
                    elif "lap" in u_low or "fe500" in u_low or "development length" in u_low or "m30" in u_low:
                        reply_text = DEMO_CHAT_RESPONSES["lap"]
                    elif "hot" in u_low or "weather" in u_low or "shrinkage" in u_low or "curing" in u_low:
                        reply_text = DEMO_CHAT_RESPONSES["hot_weather"]
                    else:
                        reply_text = (
                            f"### 📋 Engineering Evaluation (Demonstration Mode)\n\n"
                            f"Regarding your query on: *'{user_prompt}'*:\n\n"
                            f"1. **Governing Codes**: IS 456:2000 (Plain and Reinforced Concrete), OSHA 29 CFR 1926 (Construction Safety), and NBC 2016 Part 7.\n"
                            f"2. **Safety & Structural Protocol**: Verify structural drawings and contractor method statements prior to execution. Ensure all work permits (Hot Works / Working at Height / Confined Space) are signed by the certified site safety officer.\n"
                            f"3. **Concrete Quality Control**: Maintain concrete test cube sampling per IS 456 Clause 15.2 (1 set for 1-5 m³, 2 sets for 6-15 m³, 3 sets for 16-30 m³, 4 sets for 31-50 m³, plus 1 set for each additional 50 m³).\n\n"
                            f"> ℹ️ *To unlock real-time Gemini AI chat inference, enter your Google Gemini API key in the sidebar.*"
                        )
                else:
                    success, resp_str = client.generate_chat_response(
                        messages=st.session_state["site_assistant_messages"],
                        system_prompt=SITE_ENGINEER_SYSTEM_PROMPT
                    )
                    if success:
                        reply_text = resp_str
                    else:
                        reply_text = f"⚠️ Gemini Chat Notice: {resp_str}\n\nFalling back to engineering reference:\n\n{DEMO_CHAT_RESPONSES['stripping']}"

                st.markdown(reply_text)
                st.session_state["site_assistant_messages"].append({"role": "assistant", "content": reply_text})
