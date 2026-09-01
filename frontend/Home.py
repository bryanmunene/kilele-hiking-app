import html
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import get_current_user, is_authenticated, restore_session_from_storage
from database import get_db, init_database
from image_utils import display_image
from models import Hike
from nature_theme import apply_nature_theme
from services import create_bookmark, get_all_hikes


st.set_page_config(
    page_title="Kilele Explorers",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_nature_theme()
restore_session_from_storage()


HOME_CSS = """
    <style>
    .home-kicker {
        color: #2f7d55;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .home-subtitle {
        color: #617067;
        font-size: 1.08rem;
        line-height: 1.65;
        max-width: 760px;
        margin-bottom: 1rem;
    }

    .quick-strip {
        background: #fffdf8;
        border: 1px solid #e6e0d3;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0 1.2rem 0;
    }

    .trail-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.2rem 0.65rem;
        color: #ffffff;
        font-size: 0.82rem;
        font-weight: 800;
    }

    .badge-easy { background: #2f7d55; }
    .badge-moderate { background: #a45f1d; }
    .badge-hard { background: #b23b3b; }
    .badge-extreme { background: #694d8e; }

    .trail-description {
        color: #617067;
        line-height: 1.55;
        margin: 0.5rem 0 0.8rem 0;
    }

    .detail-pill {
        display: inline-block;
        background: #edf6f1;
        border: 1px solid #d9ece4;
        border-radius: 999px;
        color: #20352c;
        font-size: 0.84rem;
        font-weight: 700;
        padding: 0.24rem 0.58rem;
        margin: 0 0.32rem 0.32rem 0;
    }

    .featured-copy {
        color: #617067;
        line-height: 1.55;
    }

    @media (max-width: 768px) {
        .home-subtitle {
            font-size: 1rem;
        }
    }
    </style>
"""
st.markdown(HOME_CSS, unsafe_allow_html=True)


def _escape(value) -> str:
    return html.escape(str(value)) if value is not None else ""


def bootstrap_database():
    """Create tables and seed the demo catalogue when starting from an empty DB."""
    init_database()
    try:
        with get_db() as db:
            if db.query(Hike).count() == 0:
                import seed_database

                seed_database.seed_database()
    except Exception as exc:
        st.error(f"Database startup failed: {exc}")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_hikes(difficulty=None):
    selected = None if difficulty in (None, "All") else difficulty
    return get_all_hikes(difficulty=selected)


def filtered_and_sorted_hikes(hikes, search_query, distance_range, sort_by):
    results = list(hikes)
    if search_query:
        needle = search_query.lower()
        results = [
            hike for hike in results
            if needle in hike["name"].lower() or needle in hike["location"].lower()
        ]

    results = [
        hike for hike in results
        if distance_range[0] <= float(hike["distance_km"]) <= distance_range[1]
    ]

    difficulty_order = {"Easy": 1, "Moderate": 2, "Hard": 3, "Extreme": 4}
    sorters = {
        "Name": lambda hike: hike["name"],
        "Distance: low to high": lambda hike: hike["distance_km"],
        "Distance: high to low": lambda hike: -hike["distance_km"],
        "Duration": lambda hike: hike["estimated_duration_hours"],
        "Difficulty": lambda hike: difficulty_order.get(hike["difficulty"], 99),
    }
    results.sort(key=sorters.get(sort_by, sorters["Name"]))
    return results


def badge_class(difficulty):
    return {
        "Easy": "badge-easy",
        "Moderate": "badge-moderate",
        "Hard": "badge-hard",
        "Extreme": "badge-extreme",
    }.get(difficulty, "badge-moderate")


def render_trail_card(hike):
    with st.container(border=True):
        image_col, detail_col, action_col = st.columns([1.15, 2.25, 0.9])

        with image_col:
            if hike.get("image_url"):
                display_image(hike["image_url"], width="stretch")
            else:
                st.markdown("### 🏔️")
                st.caption("Image pending")

        with detail_col:
            st.markdown(f"### {_escape(hike['name'])}")
            st.caption(f"{hike['location']} • {hike.get('trail_type') or 'Trail'}")
            st.markdown(
                f"<span class='trail-badge {badge_class(hike['difficulty'])}'>{_escape(hike['difficulty'])}</span>",
                unsafe_allow_html=True,
            )
            if hike.get("description"):
                preview = hike["description"]
                if len(preview) > 180:
                    preview = f"{preview[:177].rstrip()}..."
                st.markdown(
                    f"<p class='trail-description'>{_escape(preview)}</p>",
                    unsafe_allow_html=True,
                )

            chips = [
                f"{hike['distance_km']:.1f} km",
                f"{hike['estimated_duration_hours']:.1f} hrs",
            ]
            if hike.get("elevation_gain_m"):
                chips.append(f"{hike['elevation_gain_m']:.0f} m gain")
            if hike.get("best_season"):
                chips.append(hike["best_season"])
            st.markdown(
                "".join(f"<span class='detail-pill'>{_escape(chip)}</span>" for chip in chips),
                unsafe_allow_html=True,
            )

        with action_col:
            if hike.get("latitude") and hike.get("longitude"):
                st.link_button(
                    "Open map",
                    f"https://www.google.com/maps?q={hike['latitude']},{hike['longitude']}",
                    width="stretch",
                )

            if st.button(
                "Save trail",
                key=f"save_home_{hike['id']}",
                width="stretch",
                disabled=not is_authenticated(),
                help="Login to save trails" if not is_authenticated() else None,
            ):
                try:
                    user = get_current_user()
                    create_bookmark(user["id"], hike["id"])
                    st.success("Saved to bookmarks")
                except ValueError as exc:
                    st.info(str(exc))


def render_featured_trail(hikes):
    if not hikes:
        return

    featured = max(hikes, key=lambda hike: (hike.get("elevation_gain_m") or 0, hike["distance_km"]))
    with st.container(border=True):
        st.markdown("#### Featured challenge")
        image_col, copy_col = st.columns([1.1, 1.4])
        with image_col:
            display_image(featured.get("image_url"), width="stretch")
        with copy_col:
            st.markdown(f"### {_escape(featured['name'])}")
            st.caption(featured["location"])
            st.markdown(
                f"<p class='featured-copy'>{_escape(featured.get('description') or 'A standout Kenyan trail for your next outdoor plan.')}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='detail-pill'>{featured['distance_km']:.1f} km</span>"
                f"<span class='detail-pill'>{featured['estimated_duration_hours']:.1f} hrs</span>"
                f"<span class='detail-pill'>{featured.get('elevation_gain_m') or 0:.0f} m gain</span>",
                unsafe_allow_html=True,
            )


def render_charts(hikes):
    if not hikes:
        return

    df = pd.DataFrame(hikes)
    df["elevation_gain_m"] = df["elevation_gain_m"].fillna(0)
    color_map = {
        "Easy": "#2f7d55",
        "Moderate": "#a45f1d",
        "Hard": "#b23b3b",
        "Extreme": "#694d8e",
    }

    chart_col, scatter_col = st.columns(2)
    with chart_col:
        difficulty_counts = df["difficulty"].value_counts().reset_index()
        difficulty_counts.columns = ["Difficulty", "Count"]
        fig = px.bar(
            difficulty_counts,
            x="Difficulty",
            y="Count",
            color="Difficulty",
            color_discrete_map=color_map,
            title="Trails by difficulty",
        )
        fig.update_layout(showlegend=False, margin=dict(t=48, r=16, b=24, l=24))
        st.plotly_chart(fig, width="stretch")

    with scatter_col:
        fig = px.scatter(
            df,
            x="distance_km",
            y="estimated_duration_hours",
            size="elevation_gain_m",
            color="difficulty",
            color_discrete_map=color_map,
            labels={
                "distance_km": "Distance (km)",
                "estimated_duration_hours": "Duration (hours)",
                "difficulty": "Difficulty",
            },
            title="Distance and time",
        )
        fig.update_layout(margin=dict(t=48, r=16, b=24, l=24))
        st.plotly_chart(fig, width="stretch")


def main():
    bootstrap_database()

    if is_authenticated():
        user = get_current_user()
        st.success(f"Welcome back, {user['username']}.")

    st.markdown("<div class='home-kicker'>Kenyan trail planner</div>", unsafe_allow_html=True)
    st.title("Kilele Explorers")
    st.markdown(
        "<p class='home-subtitle'>Find a trail, compare effort, check conditions, and save your next hike without digging through the sidebar first.</p>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Search trails")
        search_query = st.text_input("Trail or location", placeholder="Aberdare, forest, hill...")
        difficulty = st.selectbox("Difficulty", ["All", "Easy", "Moderate", "Hard", "Extreme"])
        sort_by = st.selectbox(
            "Sort",
            ["Name", "Distance: low to high", "Distance: high to low", "Duration", "Difficulty"],
        )
        st.markdown("---")
        st.page_link("pages/1_🗺️_Map_View.py", label="Trail map", icon="🗺️")
        st.page_link("pages/2_➕_Add_Trail.py", label="Add trail", icon="➕")
        st.page_link("pages/7_⭐_Reviews.py", label="Reviews", icon="⭐")
        st.page_link("pages/8_🔖_Bookmarks.py", label="Bookmarks", icon="🔖")

    with st.spinner("Loading trails..."):
        hikes = fetch_hikes(difficulty)

    if not hikes:
        st.warning("No trails found in the database.")
        st.info("Run `python seed_database.py` from the frontend folder to populate the local catalogue.")
        return

    max_distance = max(float(hike["distance_km"]) for hike in hikes)
    distance_range = st.sidebar.slider(
        "Distance range (km)",
        min_value=0.0,
        max_value=float(max(10, round(max_distance + 5))),
        value=(0.0, float(max(10, round(max_distance + 5)))),
        step=0.5,
    )

    visible_hikes = filtered_and_sorted_hikes(hikes, search_query, distance_range, sort_by)

    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    with stats_col1:
        st.metric("Matching trails", len(visible_hikes))
    with stats_col2:
        avg_distance = sum(h["distance_km"] for h in visible_hikes) / len(visible_hikes) if visible_hikes else 0
        st.metric("Avg distance", f"{avg_distance:.1f} km")
    with stats_col3:
        avg_duration = sum(h["estimated_duration_hours"] for h in visible_hikes) / len(visible_hikes) if visible_hikes else 0
        st.metric("Avg duration", f"{avg_duration:.1f} hrs")
    with stats_col4:
        hard_count = sum(1 for h in visible_hikes if h["difficulty"] in {"Hard", "Extreme"})
        st.metric("Hard+ routes", hard_count)

    if not visible_hikes:
        st.info("No trails match those filters. Try widening the distance or choosing all difficulties.")
        return

    st.markdown("<div class='quick-strip'>", unsafe_allow_html=True)
    st.markdown("#### Plan faster")
    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if st.button("Open trail map", width="stretch"):
            st.switch_page("pages/1_🗺️_Map_View.py")
    with action_col2:
        if st.button("Track a hike", width="stretch"):
            st.switch_page("pages/5_📍_Track_Hike.py")
    with action_col3:
        if st.button("Plan a future hike", width="stretch"):
            st.switch_page("pages/20_🗓️_Plan_Hike.py")
    st.markdown("</div>", unsafe_allow_html=True)

    render_featured_trail(visible_hikes)

    st.markdown("## Trail catalogue")
    st.caption(f"Showing {len(visible_hikes)} of {len(hikes)} trails")
    for hike in visible_hikes:
        render_trail_card(hike)

    st.markdown("## Trail insights")
    render_charts(visible_hikes)

    export_col1, export_col2, _ = st.columns([1, 1, 2])
    with export_col1:
        csv_data = pd.DataFrame(visible_hikes).to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="kilele_trails.csv",
            mime="text/csv",
            width="stretch",
        )
    with export_col2:
        from io import BytesIO

        excel_buffer = BytesIO()
        pd.DataFrame(visible_hikes).to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)
        st.download_button(
            label="Download Excel",
            data=excel_buffer,
            file_name="kilele_trails.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    main()
