"""Shared visual system and navigation for Kilele Explorers."""

import streamlit as st


NATURE_CSS = """
<style>
:root {
    --kilele-forest: #173d32;
    --kilele-forest-2: #245846;
    --kilele-moss: #6f8751;
    --kilele-sun: #d77a43;
    --kilele-sand: #f4f0e6;
    --kilele-paper: #fffdf8;
    --kilele-ink: #17221e;
    --kilele-muted: #66736d;
    --kilele-line: #d9ded8;
}

html { scroll-behavior: smooth; }

.stApp {
    background:
        radial-gradient(circle at 88% 4%, rgba(215, 122, 67, .12), transparent 26rem),
        linear-gradient(180deg, #f8f5ed 0%, var(--kilele-sand) 100%);
    color: var(--kilele-ink);
}

[data-testid="stAppViewContainer"] > .main { background: transparent; }

.block-container {
    max-width: 1240px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

h1, h2, h3, h4 {
    color: var(--kilele-forest) !important;
    letter-spacing: -.025em;
}

h1 { font-weight: 760 !important; }
h2 { margin-top: 1.6rem !important; }
p, li { color: #33413b; }
a { color: var(--kilele-forest-2); }

/* Sidebar */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 20% 0%, rgba(255,255,255,.08), transparent 18rem),
        linear-gradient(180deg, #173d32 0%, #102c25 100%) !important;
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: .75rem .6rem 1.5rem; }
[data-testid="stSidebar"] * { color: #f5f2e9; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.14); }

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: .8rem;
    padding: .55rem .5rem 1rem;
    margin-bottom: .35rem;
    border-bottom: 1px solid rgba(255,255,255,.13);
}

.sidebar-mark {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    background: var(--kilele-sun);
    color: white;
    font-size: 1.35rem;
    font-weight: 800;
    box-shadow: 0 8px 22px rgba(0,0,0,.2);
}

.sidebar-name { font-size: 1.02rem; font-weight: 750; letter-spacing: .02em; }
.sidebar-kicker { font-size: .72rem; color: #b9c9c0; text-transform: uppercase; letter-spacing: .12em; }
.sidebar-section { color: #9fb3a8 !important; font-size: .69rem; font-weight: 750; letter-spacing: .13em; text-transform: uppercase; margin: 1rem .6rem .3rem; }

[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    border-radius: 10px;
    padding: .54rem .65rem;
    transition: background .18s ease, transform .18s ease;
}

[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255,255,255,.09);
    transform: translateX(2px);
}

/* Native surfaces */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,253,248,.86);
    border-color: rgba(23,61,50,.13) !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 28px rgba(25,45,37,.06);
}

[data-testid="stMetric"] {
    background: rgba(255,253,248,.86);
    border: 1px solid rgba(23,61,50,.12);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 8px 24px rgba(25,45,37,.05);
}

[data-testid="stMetricValue"] { color: var(--kilele-forest); font-weight: 760; }
[data-testid="stMetricLabel"] { color: var(--kilele-muted); }

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 2.8rem;
    border-radius: 11px !important;
    border: 1px solid rgba(23,61,50,.18) !important;
    background: var(--kilele-paper) !important;
    color: var(--kilele-forest) !important;
    font-weight: 680 !important;
    box-shadow: 0 5px 14px rgba(25,45,37,.06) !important;
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);
    border-color: var(--kilele-forest-2) !important;
    box-shadow: 0 9px 20px rgba(25,45,37,.11) !important;
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: var(--kilele-forest) !important;
    color: white !important;
    border-color: var(--kilele-forest) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-baseweb="select"] > div,
[data-baseweb="input"] {
    background: rgba(255,253,248,.96) !important;
    border-color: rgba(23,61,50,.2) !important;
    border-radius: 11px !important;
    color: var(--kilele-ink) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: var(--kilele-forest-2) !important;
    box-shadow: 0 0 0 3px rgba(36,88,70,.13) !important;
}

[data-testid="stExpander"] {
    background: rgba(255,253,248,.82);
    border: 1px solid rgba(23,61,50,.13) !important;
    border-radius: 14px !important;
    overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
    gap: .35rem;
    background: rgba(23,61,50,.06);
    border-radius: 12px;
    padding: .28rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: var(--kilele-muted) !important;
    padding: .55rem .9rem;
}

.stTabs [aria-selected="true"] {
    background: var(--kilele-paper) !important;
    color: var(--kilele-forest) !important;
    box-shadow: 0 3px 12px rgba(25,45,37,.08);
}

[data-testid="stAlert"] { border-radius: 13px; }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }

/* Shared custom cards used across feature pages */
.content-card, .feature-card, .stat-box, .metric-box, .metric-card,
.stat-card, .stats-card, .activity-card, .follow-suggestion-card,
.gear-card, .planned-hike-card, .waypoint-item, .upload-section,
.bluetooth-section, .success-box, .warning-box, .admin-header {
    background: rgba(255,253,248,.9);
    border: 1px solid rgba(23,61,50,.13);
    border-radius: 16px;
    padding: 1.15rem;
    box-shadow: 0 8px 26px rgba(25,45,37,.06);
}

.feature-card { min-height: 165px; }
.feature-icon { font-size: 1.65rem; margin-bottom: .55rem; }
.feature-title { color: var(--kilele-forest); font-size: 1.02rem; font-weight: 750; }

.stat-box, .metric-box {
    background: linear-gradient(145deg, var(--kilele-forest), #285e4c);
    color: white;
    text-align: left;
}
.stat-number, .metric-number { color: white; font-size: 2rem; font-weight: 780; }
.stat-label, .metric-label { color: #cbd8d1; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }

.difficulty-easy { color: #477d59; font-weight: 750; }
.difficulty-moderate { color: #a45e2e; font-weight: 750; }
.difficulty-hard { color: #a54037; font-weight: 750; }
.difficulty-extreme { color: #773d6c; font-weight: 750; }
.required-badge, .optional-badge { border-radius: 999px; padding: .18rem .52rem; font-size: .73rem; font-weight: 720; }

.danger-zone { border-color: rgba(165,64,55,.3); background: #fff7f5; }
.progress-bar-container { background: #dfe5df; border-radius: 999px; overflow: hidden; }
.progress-bar { background: var(--kilele-forest-2); border-radius: 999px; }

@media (max-width: 768px) {
    .block-container { padding: 1rem .85rem 3rem; }
    h1 { font-size: 1.9rem !important; }
    h2 { font-size: 1.45rem !important; }
    [data-testid="column"] { min-width: 100% !important; }
    .feature-card { min-height: auto; }
    .stButton > button, .stDownloadButton > button { min-height: 3rem; }
    .stTabs [data-baseweb="tab-list"] { overflow-x: auto; }
}
</style>
"""


def _safe_page_link(path: str, label: str, icon: str) -> None:
    """Render a page link without breaking isolated page tests."""
    try:
        st.page_link(path, label=label, icon=icon)
    except Exception:
        st.markdown(f"<span style='opacity:.78'>{label}</span>", unsafe_allow_html=True)


def render_navigation() -> None:
    """Render Kilele's compact, task-based navigation."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-mark">K</div>
                <div>
                    <div class="sidebar-name">Kilele</div>
                    <div class="sidebar-kicker">Explore higher</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section">Explore</div>', unsafe_allow_html=True)
        _safe_page_link("Home.py", "Discover trails", ":material/landscape:")
        _safe_page_link("pages/1_🗺️_Map_View.py", "Trail map", ":material/map:")
        _safe_page_link("pages/18_🌤️_Trail_Info.py", "Conditions", ":material/cloud:")
        _safe_page_link("pages/19_🎒_Hiking_Gear.py", "Gear guide", ":material/backpack:")

        st.markdown('<div class="sidebar-section">Your adventure</div>', unsafe_allow_html=True)
        _safe_page_link("pages/20_🗓️_Plan_Hike.py", "Plan a hike", ":material/event:")
        _safe_page_link("pages/21_🎫_Register_for_Hikes.py", "Group hikes", ":material/groups:")
        _safe_page_link("pages/5_📍_Track_Hike.py", "Track activity", ":material/route:")

        with st.expander("More tools", expanded=False):
            _safe_page_link("pages/3_📊_Analytics.py", "Trail analytics", ":material/monitoring:")
            _safe_page_link("pages/2_➕_Add_Trail.py", "Add a trail", ":material/add_location:")
            _safe_page_link("pages/17_💬_Trail_Community.py", "Trail community", ":material/forum:")
            _safe_page_link("pages/9_📰_Feed.py", "Community feed", ":material/dynamic_feed:")
            _safe_page_link("pages/13_⌚_Wearables.py", "Wearables", ":material/watch:")
            _safe_page_link("pages/19_🟠_Strava.py", "Strava", ":material/directions_run:")

        try:
            from auth import get_current_user, is_authenticated

            if is_authenticated():
                user = get_current_user() or {}
                st.markdown('<div class="sidebar-section">Account</div>', unsafe_allow_html=True)
                _safe_page_link("pages/4_👤_Profile.py", "Profile", ":material/person:")
                _safe_page_link("pages/8_🔖_Bookmarks.py", "Saved trails", ":material/bookmark:")
                _safe_page_link("pages/15_🎯_Goals.py", "Goals", ":material/flag:")
                if user.get("is_admin"):
                    with st.expander("Admin", expanded=False):
                        _safe_page_link("pages/14_👑_Admin_Dashboard.py", "Dashboard", ":material/admin_panel_settings:")
                        _safe_page_link("pages/22_👑_Manage_Hikes.py", "Manage hikes", ":material/edit_calendar:")
                st.caption(f"Signed in as {user.get('username', 'hiker')}")
            else:
                st.markdown('<div class="sidebar-section">Account</div>', unsafe_allow_html=True)
                _safe_page_link("pages/0_🔐_Login.py", "Sign in", ":material/login:")
        except Exception:
            _safe_page_link("pages/0_🔐_Login.py", "Sign in", ":material/login:")


def apply_nature_theme() -> None:
    """Apply Kilele's shared theme and navigation to the current page."""
    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">',
        unsafe_allow_html=True,
    )
    st.markdown(NATURE_CSS, unsafe_allow_html=True)
    render_navigation()
