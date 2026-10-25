"""
UI Components and Custom CSS Styling for Multimodal Construction Intelligence Platform.
Engineered for modern high-tech construction analytics with OSHA & IS 456 themes.
"""

import streamlit as st


def inject_custom_css():
    """Injects high-end, responsive CSS styling into the Streamlit application."""
    css = """
    <style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-main: #0b1120;
        --card-bg: #1e293b;
        --card-border: #334155;
        --primary-amber: #f59e0b;
        --primary-amber-glow: rgba(245, 158, 11, 0.25);
        --accent-blue: #38bdf8;
        --success-emerald: #10b981;
        --warning-orange: #f97316;
        --danger-rose: #f43f5e;
        --text-bright: #f8fafc;
        --text-muted: #94a3b8;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Header Styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(180deg, #f59e0b, #ef4444);
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.025em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 8px;
        line-height: 1.5;
    }

    .badge-capstone {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    /* Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #f59e0b;
    }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }

    .metric-val {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }

    .metric-desc {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Status Pills */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .pill-compliant, .pill-low, .pill-normal {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    .pill-action, .pill-medium, .pill-moderate {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }

    .pill-critical, .pill-high, .pill-severe {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.35);
    }

    .pill-info {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
    }

    /* Safety & Structural Diagnostic Cards */
    .diagnostic-panel {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }

    .hazard-item {
        background: rgba(15, 23, 42, 0.75);
        border-left: 4px solid #ef4444;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 10px;
    }

    .remedy-box {
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid #10b981;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-top: 6px;
        font-size: 0.88rem;
    }

    /* Weather alert ribbon */
    .weather-banner-severe {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.2) 0%, rgba(245, 158, 11, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 16px;
    }

    /* Monospace Code / JSON preview container */
    pre, code {
        font-family: 'JetBrains Mono', Consolas, Monaco, monospace !important;
    }

    /* Sidebar aesthetics */
    [data-testid="stSidebar"] {
        background-color: #0d1527;
        border-right: 1px solid #1e293b;
    }

    /* Tab bar clean styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #334155;
        padding-bottom: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        color: #94a3b8;
    }

    .stTabs [aria-selected="true"] {
        color: #f59e0b !important;
        border-bottom: 3px solid #f59e0b !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_hero_header():
    """Renders the top branding header with Capstone project badges."""
    html = """
    <div class="hero-container">
        <div class="badge-capstone">Skill Wallet Capstone Project 1 • Production Ready</div>
        <h1 class="hero-title">
            <span>🏗️ Multimodal Construction Intelligence Platform</span>
        </h1>
        <p class="hero-subtitle">
            Next-generation AI telemetry for site safety compliance (OSHA & IS 456), computer vision crack diagnostics,
            real estate CapEx valuation & material planning, and weather-aware site engineering intelligence.
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str = "", delta: str = None, delta_color: str = "normal"):
    """Renders a styled metric card container."""
    delta_html = ""
    if delta:
        color = "#10b981" if delta_color == "positive" else ("#ef4444" if delta_color == "negative" else "#f59e0b")
        delta_html = f'<div style="color: {color}; font-size: 0.82rem; font-weight: 600; margin-top: 4px;">{delta}</div>'
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-val">{value}</div>
        {delta_html}
        <div class="metric-desc">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def status_pill(status: str, variant: str = "compliant") -> str:
    """Returns HTML for an inline pill badge."""
    v_class = f"pill-{variant.lower()}"
    return f'<span class="pill {v_class}">{status}</span>'
