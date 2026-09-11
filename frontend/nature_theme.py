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
        --kilele-paper: #ffffff;
        --kilele-stone: #dce3e5;
    }

    .stApp {
        background: #f5f7f9;
        color: var(--kilele-ink);
    }

    .block-container {
        padding-top: 3.5rem;
        padding-bottom: 3rem;
        max-width: 1440px;
        padding-inline: 2rem;
        min-width: 0;
        container: kilele-page / inline-size;
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

    [data-testid="stSidebar"] :is(input, textarea),
    [data-testid="stSidebar"] [data-testid="stSelectbox"] button,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] button *,
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: var(--kilele-ink) !important;
    }

    [data-testid="stElementContainer"]:has(iframe[title="auth.kilele_session_storage"]) {
        display: none;
    }

    h1, h2, h3 {
        color: var(--kilele-ink) !important;
        letter-spacing: 0;
    }

    h1 {
        font-size: 2rem !important;
        line-height: 1.25 !important;
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
        background: transparent;
        border: 0;
        border-bottom: 1px solid var(--kilele-stone);
        border-radius: 0;
        padding: 1rem 0;
        color: var(--kilele-ink);
        box-shadow: none;
        margin-bottom: 1.3rem;
    }

    .hero-title {
        color: var(--kilele-ink);
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.25;
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
        box-shadow: 0 1px 3px rgba(23, 33, 28, 0.04);
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
        transition: background 0.16s ease, border-color 0.16s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--kilele-leaf) !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: var(--kilele-forest) !important;
        border: 1px solid var(--kilele-stone) !important;
        box-shadow: none !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    [data-baseweb="select"] > div {
        border: 1px solid var(--kilele-stone) !important;
        background: #ffffff !important;
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
        background: transparent;
        border-bottom: 1px solid var(--kilele-stone);
        gap: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: var(--kilele-muted) !important;
        padding: 0.55rem 0.8rem;
    }

    .stTabs [aria-selected="true"] {
        background: #e8f2ed !important;
        color: var(--kilele-forest) !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--kilele-stone);
        border-radius: 8px;
        padding: 0.85rem;
    }

    [data-testid="stMetricValue"] {
        color: var(--kilele-ink);
        font-weight: 800;
    }

    [data-testid="stExpander"] {
        background: #ffffff;
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

    [data-testid="stImage"] img {
        border-radius: 8px;
        max-width: 100%;
        height: auto;
    }

    /* Size to the available content area, including an open sidebar. */
    [data-testid="stMain"], [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"], [data-testid="stColumn"],
    [data-testid="stElementContainer"], [data-testid="stTabs"] {
        min-width: 0;
        max-width: 100%;
    }

    [data-testid="stMarkdownContainer"] :is(h1, h2, h3, h4, p, li, a),
    [data-testid="stWidgetLabel"], [data-testid="stMetricValue"] > div,
    .hero-title, .hero-subtitle, .user-name {
        overflow-wrap: anywhere;
        white-space: normal;
    }

    [data-testid="stMetricValue"] { font-size: 1.75rem; }
    [data-testid="stMetricLabel"] p { white-space: normal; }

    .stButton button, .stDownloadButton button, .stLinkButton a,
    [data-testid="stFormSubmitButton"] button {
        min-height: 44px;
        max-width: 100%;
        height: auto;
        white-space: normal;
    }

    .stButton button p, .stLinkButton a p,
    [data-testid="stFormSubmitButton"] button p {
        overflow-wrap: anywhere;
        white-space: normal;
    }

    .stTabs [data-baseweb="tab-list"] {
        max-width: 100%;
        overflow-x: auto;
        overscroll-behavior-inline: contain;
        scrollbar-width: thin;
    }
    .stTabs [data-baseweb="tab"] { flex-shrink: 0; min-height: 44px; }
    .stTabs [data-baseweb="tab"] p { white-space: nowrap; }
    [data-testid="stDataFrame"], [data-testid="stPlotlyChart"],
    [data-testid="stCustomComponentV1"] { max-width: 100%; min-width: 0; }
    [data-testid="stCustomComponentV1"] iframe { max-width: 100%; }
    [data-testid="stTable"] { overflow-x: auto; }
    [data-testid="stForm"] { border-radius: 8px; }
    .st-key-trail_photo img { max-height: 360px; object-fit: contain; }
    [class*="st-key-registration_card_"] [data-testid="stMetric"],
    [class*="st-key-event_card_"] [data-testid="stMetric"] {
        background: transparent;
        border: 0;
        padding: 0.25rem 0;
    }
    :is(button, a, input, textarea, select):focus-visible {
        outline: 3px solid #087eaa !important;
        outline-offset: 3px !important;
    }
    [data-testid="stTopNav"] { letter-spacing: 0; }
    .st-key-auth_form { max-width: 520px; margin-inline: auto; }

    @container kilele-page (max-width: 980px) {
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: min(100%, 15rem);
        }
    }

    @container kilele-page (max-width: 640px) {
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 0 !important;
        }
    }

    @media (max-width: 768px) {
        .block-container { padding: 3.5rem 1rem 2rem; }
        input, textarea, select { font-size: 16px !important; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
        }
    }
    </style>
"""


def apply_nature_theme():
    """Apply the Kilele theme CSS to any Streamlit page."""
    import streamlit as st

    st.html(NATURE_CSS)
