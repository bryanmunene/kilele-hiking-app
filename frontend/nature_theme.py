"""Reusable Kilele Explorers Streamlit theme."""

NATURE_CSS = """
    <style>
    :root {
        --kilele-ink: #17211c;
        --kilele-muted: #617067;
        --kilele-forest: #1f4f3a;
        --kilele-leaf: #2f7d55;
        --kilele-mist: #d9ece4;
        --kilele-sky: #d8edf2;
        --kilele-sun: #c96f36;
        --kilele-paper: #fffdf8;
        --kilele-stone: #e6e0d3;
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(216, 237, 242, 0.88) 0%, rgba(246, 244, 237, 0.96) 32%, #f6f4ed 100%);
        color: var(--kilele-ink);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    [data-testid="stSidebar"] {
        background: #20352c !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f7f2e8 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: #f7f2e8 !important;
    }

    h1, h2, h3 {
        color: var(--kilele-ink) !important;
        letter-spacing: 0;
    }

    h1 {
        font-size: 3.1rem !important;
        line-height: 1.05 !important;
        margin-bottom: 0.35rem !important;
    }

    h2 {
        font-size: 1.55rem !important;
        margin-top: 1.4rem !important;
    }

    h3 {
        font-size: 1.12rem !important;
    }

    p, li, span, div {
        letter-spacing: 0;
    }

    a {
        color: var(--kilele-forest);
    }

    .hero-section, .header-section, .section-panel {
        background: var(--kilele-paper);
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
        padding: 1.4rem;
        color: var(--kilele-ink);
        box-shadow: 0 18px 42px rgba(23, 33, 28, 0.08);
        margin-bottom: 1.3rem;
    }

    .hero-title {
        color: var(--kilele-ink);
        font-size: 3.6rem;
        font-weight: 800;
        line-height: 0.98;
    }

    .hero-subtitle, .hero-tagline {
        color: var(--kilele-muted);
        font-size: 1rem;
    }

    .content-card,
    .feature-card,
    .stat-card,
    .stats-card,
    .trail-card,
    .hike-card,
    .user-card,
    .activity-card,
    .follow-suggestion-card,
    .achievement-card,
    .planned-hike-card,
    .gear-card {
        background: var(--kilele-paper);
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
        color: var(--kilele-ink);
        box-shadow: 0 12px 28px rgba(23, 33, 28, 0.08);
    }

    .content-card,
    .feature-card,
    .activity-card,
    .follow-suggestion-card,
    .achievement-card,
    .planned-hike-card,
    .gear-card {
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .content-card:hover,
    .feature-card:hover,
    .hike-card:hover,
    .trail-card:hover,
    .user-card:hover,
    .achievement-card:hover,
    .gear-card:hover {
        box-shadow: 0 18px 36px rgba(23, 33, 28, 0.12);
    }

    .stat-box, .metric-box, .stat-card, .stats-card {
        background: #20352c;
        color: #f7f2e8;
        padding: 1rem;
        text-align: center;
    }

    .stat-number, .metric-number, .big-metric {
        color: #f7f2e8;
        font-size: 2rem;
        font-weight: 800;
    }

    .stat-label, .metric-label {
        color: #d9ece4;
        font-size: 0.9rem;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: var(--kilele-forest) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        min-height: 42px;
        transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease !important;
        box-shadow: 0 8px 18px rgba(31, 79, 58, 0.18) !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--kilele-leaf) !important;
        transform: translateY(-1px);
        box-shadow: 0 12px 24px rgba(31, 79, 58, 0.22) !important;
    }

    .stButton > button[kind="secondary"] {
        background: #fffdf8 !important;
        color: var(--kilele-forest) !important;
        border: 1px solid var(--kilele-stone) !important;
        box-shadow: none !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    [data-baseweb="select"] > div {
        border: 1px solid var(--kilele-stone) !important;
        background: rgba(255, 253, 248, 0.98) !important;
        border-radius: 8px !important;
        color: var(--kilele-ink) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: var(--kilele-leaf) !important;
        box-shadow: 0 0 0 3px rgba(47, 125, 85, 0.16) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: rgba(255, 253, 248, 0.68);
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
        padding: 0.35rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: var(--kilele-muted) !important;
        padding: 0.55rem 0.8rem;
    }

    .stTabs [aria-selected="true"] {
        background: var(--kilele-forest) !important;
        color: #ffffff !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 253, 248, 0.86);
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
        padding: 0.85rem;
    }

    [data-testid="stMetricValue"] {
        color: var(--kilele-ink);
        font-weight: 800;
    }

    [data-testid="stExpander"] {
        background: rgba(255, 253, 248, 0.86);
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
    }

    .difficulty-easy { color: #2f7d55; font-weight: 800; }
    .difficulty-moderate { color: #a45f1d; font-weight: 800; }
    .difficulty-hard { color: #b23b3b; font-weight: 800; }
    .difficulty-extreme { color: #694d8e; font-weight: 800; }

    .review-rating {
        color: #a45f1d;
        font-weight: 800;
        font-size: 1rem;
    }

    .review-meta,
    .trail-meta,
    .connection-date,
    .achievement-description {
        color: var(--kilele-muted);
        font-size: 0.9rem;
    }

    .bookmark-notes,
    .waypoint-item {
        background: #edf6f1;
        border-left: 3px solid var(--kilele-leaf);
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.6rem 0;
    }

    .category-header {
        background: #20352c;
        color: #f7f2e8;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin: 1rem 0;
    }

    .category-header h2,
    .category-header h3 {
        color: #f7f2e8 !important;
        margin: 0 !important;
    }

    .achievement-icon {
        font-size: 2.6rem;
        line-height: 1;
        text-align: center;
    }

    .achievement-icon-locked,
    .achievement-locked {
        opacity: 0.64;
    }

    .achievement-name {
        font-weight: 800;
        text-align: center;
        margin-top: 0.5rem;
    }

    .achievement-points,
    .achievement-earned {
        text-align: center;
        color: var(--kilele-muted);
        font-size: 0.88rem;
        margin-top: 0.45rem;
    }

    .progress-bar-container {
        background: #e6e0d3;
        border-radius: 6px;
        overflow: hidden;
        height: 24px;
        margin: 0.7rem 0;
    }

    .progress-bar {
        background: var(--kilele-sun);
        color: #ffffff;
        height: 24px;
        text-align: center;
        font-size: 0.8rem;
        line-height: 24px;
        min-width: 24px;
    }

    .empty-feed {
        background: var(--kilele-paper);
        border: 1px dashed var(--kilele-stone);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }

    .activity-icon {
        display: inline-block;
        margin-right: 0.4rem;
    }

    .activity-user,
    .user-name {
        color: var(--kilele-forest);
        font-weight: 800;
    }

    .activity-time {
        color: var(--kilele-muted);
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }

    .admin-header,
    .danger-zone {
        background: var(--kilele-paper);
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .danger-zone {
        border-left: 4px solid #b23b3b;
    }

    .stAlert {
        border-radius: 8px;
    }

    img {
        border-radius: 8px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        h1 {
            font-size: 2rem !important;
        }

        .hero-title {
            font-size: 2.2rem;
        }

        .hero-section, .header-section, .section-panel {
            padding: 1rem;
        }

        button,
        .stButton button,
        .stDownloadButton button {
            min-height: 46px !important;
        }

        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            margin-bottom: 0.75rem !important;
        }

        table {
            display: block !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
        }
    }
    </style>
"""


def apply_nature_theme():
    """Apply the Kilele theme CSS to any Streamlit page."""
    import streamlit as st

    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(NATURE_CSS, unsafe_allow_html=True)
