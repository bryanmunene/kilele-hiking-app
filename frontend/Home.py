"""Kilele Explorers home and trail discovery experience."""

from html import escape
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import get_current_user, is_authenticated, restore_session_from_storage
from database import get_db, init_database
from image_utils import image_data_url
from models import Hike
from nature_theme import apply_nature_theme
from services import create_bookmark, get_all_hikes, get_trail_conditions


st.set_page_config(
    page_title="Kilele — Explore Kenya on foot",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_database()

with get_db() as db:
    if db.query(Hike).count() == 0:
        try:
            from seed_database import seed_database

            seed_database()
        except Exception:
            st.error("Trail data could not be prepared. Refresh the app or contact the administrator.")

restore_session_from_storage()
apply_nature_theme()


HOME_CSS = """
<style>
.hero-shell {
    position: relative;
    min-height: 440px;
    display: flex;
    align-items: flex-end;
    overflow: hidden;
    border-radius: 28px;
    padding: clamp(2rem, 6vw, 4.75rem);
    margin: .25rem 0 1rem;
    background-size: cover;
    background-position: center 58%;
    box-shadow: 0 24px 65px rgba(18, 42, 34, .22);
}

.hero-shell::after {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(10, 31, 25, .93) 0%, rgba(10, 31, 25, .67) 45%, rgba(10, 31, 25, .14) 100%),
        linear-gradient(0deg, rgba(10, 31, 25, .48), transparent 50%);
}

.hero-copy { position: relative; z-index: 1; max-width: 670px; }
.hero-eyebrow { color: #efb083; font-size: .78rem; font-weight: 760; letter-spacing: .16em; text-transform: uppercase; margin-bottom: .75rem; }
.hero-title { color: white; font-size: clamp(2.55rem, 6vw, 5.1rem); font-weight: 790; line-height: .96; letter-spacing: -.055em; margin-bottom: 1rem; }
.hero-text { color: rgba(255,255,255,.86); font-size: clamp(1rem, 2vw, 1.25rem); line-height: 1.55; max-width: 590px; }

.action-label { color: #66736d; font-size: .72rem; font-weight: 760; letter-spacing: .11em; text-transform: uppercase; margin: 1.2rem 0 .45rem; }
.section-kicker { color: #b85f31; font-size: .74rem; font-weight: 780; letter-spacing: .14em; text-transform: uppercase; margin-top: 2.3rem; }
.section-copy { color: #66736d; max-width: 720px; margin-top: -.45rem; }

.trail-photo {
    position: relative;
    height: 230px;
    border-radius: 14px;
    background-color: #dfe6df;
    background-size: cover;
    background-position: center;
    margin-bottom: .9rem;
    overflow: hidden;
}
.trail-photo::after { content: ""; position: absolute; inset: 0; background: linear-gradient(0deg, rgba(9,28,22,.45), transparent 50%); }
.trail-badge {
    position: absolute;
    z-index: 1;
    left: .8rem;
    bottom: .75rem;
    padding: .28rem .65rem;
    border-radius: 999px;
    background: rgba(255,253,248,.92);
    color: #173d32;
    font-size: .73rem;
    font-weight: 760;
    backdrop-filter: blur(8px);
}
.trail-location { color: #6a766f; font-size: .86rem; margin: -.55rem 0 .75rem; }
.trail-description { color: #48554f; font-size: .92rem; line-height: 1.55; min-height: 2.9rem; }
.meta-line { display: flex; gap: .65rem; flex-wrap: wrap; margin: .7rem 0 .35rem; }
.meta-chip { color: #33413b; background: #edf0e9; border-radius: 8px; padding: .28rem .48rem; font-size: .77rem; font-weight: 650; }

.footer-lockup { text-align: center; color: #65736c; padding: 2.5rem 1rem 0; font-size: .84rem; }
.footer-lockup strong { color: #173d32; }

@media (max-width: 768px) {
    .hero-shell { min-height: 390px; border-radius: 20px; background-position: 62% center; }
    .hero-shell::after { background: linear-gradient(90deg, rgba(10,31,25,.94), rgba(10,31,25,.52)); }
    .trail-photo { height: 210px; }
}
</style>
"""
st.markdown(HOME_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_hikes(difficulty: str | None = None) -> list[dict]:
    """Load trails from the unified database."""
    try:
        return get_all_hikes(difficulty=None if difficulty == "All" else difficulty)
    except Exception:
        return []


def render_hero() -> None:
    cover = image_data_url("Cover.jpg")
    background = f"url('{cover}')" if cover else "linear-gradient(135deg, #173d32, #4f7658)"
    st.markdown(
        f"""
        <section class="hero-shell" style="background-image:{background}">
            <div class="hero-copy">
                <div class="hero-eyebrow">Kenya, one trail at a time</div>
                <div class="hero-title">Go where the road ends.</div>
                <div class="hero-text">
                    Find honest route details, plan around the terrain, and head out with
                    the information you need—not the noise you do not.
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_quick_actions() -> None:
    st.markdown('<div class="action-label">Start here</div>', unsafe_allow_html=True)
    map_col, plan_col, group_col, account_col = st.columns(4)
    with map_col:
        if st.button("Explore the map", icon=":material/map:", width="stretch"):
            st.switch_page("pages/1_🗺️_Map_View.py")
    with plan_col:
        if st.button("Plan a hike", icon=":material/event:", width="stretch"):
            st.switch_page("pages/20_🗓️_Plan_Hike.py")
    with group_col:
        if st.button("Find group hikes", icon=":material/groups:", width="stretch"):
            st.switch_page("pages/21_🎫_Register_for_Hikes.py")
    with account_col:
        destination = "pages/4_👤_Profile.py" if is_authenticated() else "pages/0_🔐_Login.py"
        label = "Open profile" if is_authenticated() else "Sign in"
        icon = ":material/person:" if is_authenticated() else ":material/login:"
        if st.button(label, icon=icon, width="stretch"):
            st.switch_page(destination)


def difficulty_class(difficulty: str) -> str:
    return f"difficulty-{difficulty.lower()}"


def save_trail(hike_id: int) -> None:
    if not is_authenticated():
        st.info("Sign in to save trails to your profile.")
        return

    user = get_current_user()
    try:
        create_bookmark(user["id"], hike_id)
        st.toast("Trail saved", icon="✓")
    except ValueError as exc:
        st.toast(str(exc))
    except Exception:
        st.error("This trail could not be saved right now.")


def render_trail_card(hike: dict) -> None:
    image = image_data_url(hike.get("image_url") or "")
    image_style = f"background-image:url('{image}')" if image else "background:linear-gradient(145deg,#6f8751,#173d32)"
    name = escape(str(hike.get("name", "Unnamed trail")))
    location = escape(str(hike.get("location", "Location unavailable")))
    difficulty = escape(str(hike.get("difficulty", "Unrated")))
    description = escape(str(hike.get("description") or "Trail notes are being prepared."))
    preview = description if len(description) <= 145 else description[:142].rstrip() + "…"
    distance_km = float(hike.get("distance_km") or 0)
    duration_hours = float(hike.get("estimated_duration_hours") or 0)
    elevation_gain = float(hike.get("elevation_gain_m") or 0)

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="trail-photo" style="{image_style}">
                <span class="trail-badge {difficulty_class(difficulty)}">{difficulty}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"### {name}")
        st.markdown(f'<div class="trail-location">{location}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="meta-line">
                <span class="meta-chip">{distance_km:g} km</span>
                <span class="meta-chip">{duration_hours:g} hours</span>
                <span class="meta-chip">{elevation_gain:g} m gain</span>
            </div>
            <p class="trail-description">{preview}</p>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Route details"):
            spec_col, note_col = st.columns([1, 1.7])
            with spec_col:
                st.markdown(f"**Route**  \n{hike.get('trail_type') or 'Not specified'}")
                st.markdown(f"**Best season**  \n{hike.get('best_season') or 'Check local conditions'}")
                if hike.get("latitude") is not None and hike.get("longitude") is not None:
                    st.markdown(f"**Coordinates**  \n`{hike['latitude']:.4f}, {hike['longitude']:.4f}`")
            with note_col:
                st.markdown("**What to expect**")
                st.write(hike.get("description") or "No detailed notes yet.")

            conditions = get_trail_conditions(hike["id"], limit=2)
            if conditions:
                st.markdown("**Latest condition reports**")
                for condition in conditions:
                    notes = condition.get("notes") or "No notes provided"
                    st.caption(f"{condition.get('condition', 'unknown').title()} — {notes}")

        action_a, action_b, action_c = st.columns(3)
        with action_a:
            if st.button("Map", icon=":material/map:", key=f"map_{hike['id']}", width="stretch"):
                st.session_state["selected_hike_id"] = hike["id"]
                st.switch_page("pages/1_🗺️_Map_View.py")
        with action_b:
            if st.button("Save", icon=":material/bookmark:", key=f"save_{hike['id']}", width="stretch"):
                save_trail(hike["id"])
        with action_c:
            if st.button("Review", icon=":material/rate_review:", key=f"review_{hike['id']}", width="stretch"):
                st.session_state["selected_hike_id"] = hike["id"]
                st.switch_page("pages/7_⭐_Reviews.py")


def render_insights(hikes: list[dict]) -> None:
    if not hikes:
        return

    data = pd.DataFrame(hikes)
    with st.expander("Compare the current trail selection"):
        chart_col, export_col = st.columns([1.65, 1])
        with chart_col:
            figure = px.scatter(
                data,
                x="distance_km",
                y="estimated_duration_hours",
                color="difficulty",
                size="elevation_gain_m",
                hover_name="name",
                labels={"distance_km": "Distance (km)", "estimated_duration_hours": "Estimated time (hours)"},
                color_discrete_map={
                    "Easy": "#5e8b62",
                    "Moderate": "#d77a43",
                    "Hard": "#a94c43",
                    "Extreme": "#714367",
                },
                template="simple_white",
            )
            figure.update_layout(margin=dict(l=10, r=10, t=15, b=10), legend_title_text="Difficulty")
            st.plotly_chart(figure, width="stretch")
        with export_col:
            st.markdown("#### Take the list with you")
            st.caption("Export the filtered routes for planning or offline reference.")
            csv_data = data.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                "kilele_trails.csv",
                "text/csv",
                icon=":material/download:",
                width="stretch",
            )
            excel_buffer = BytesIO()
            data.to_excel(excel_buffer, index=False, engine="openpyxl")
            st.download_button(
                "Download Excel",
                excel_buffer.getvalue(),
                "kilele_trails.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                icon=":material/table_view:",
                width="stretch",
            )


def main() -> None:
    render_hero()
    render_quick_actions()

    if is_authenticated():
        user = get_current_user() or {}
        st.caption(f"Welcome back, {user.get('username', 'hiker')}. Your next route is below.")

    all_hikes = fetch_hikes()
    total_distance = sum(float(h.get("distance_km") or 0) for h in all_hikes)
    avg_gain = sum(float(h.get("elevation_gain_m") or 0) for h in all_hikes) / len(all_hikes) if all_hikes else 0

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Mapped trails", len(all_hikes))
    metric_b.metric("Combined distance", f"{total_distance:.0f} km")
    metric_c.metric("Average climb", f"{avg_gain:.0f} m")
    metric_d.metric("Counties represented", len({h.get("location", "").split(",")[-1].strip() for h in all_hikes}))

    st.markdown('<div class="section-kicker">Trail finder</div>', unsafe_allow_html=True)
    st.markdown("## Choose the day you want to have")
    st.markdown(
        '<p class="section-copy">Filter by effort, distance, or place. Every result includes route facts, planning context, and a direct path to the map.</p>',
        unsafe_allow_html=True,
    )

    search_col, difficulty_col, distance_col, sort_col = st.columns([1.45, 1, 1.35, 1])
    with search_col:
        query = st.text_input("Search", placeholder="Trail or county", label_visibility="collapsed")
    with difficulty_col:
        difficulty = st.selectbox(
            "Difficulty",
            ["All", "Easy", "Moderate", "Hard", "Extreme"],
            label_visibility="collapsed",
        )
    with distance_col:
        distance = st.slider("Distance", 0.0, 25.0, (0.0, 25.0), label_visibility="collapsed")
    with sort_col:
        sort_by = st.selectbox(
            "Sort",
            ["Recommended", "Shortest", "Longest", "Most climbing"],
            label_visibility="collapsed",
        )

    hikes = fetch_hikes(difficulty)
    if query:
        lowered = query.casefold()
        hikes = [h for h in hikes if lowered in h.get("name", "").casefold() or lowered in h.get("location", "").casefold()]
    hikes = [h for h in hikes if distance[0] <= float(h.get("distance_km") or 0) <= distance[1]]

    if sort_by == "Shortest":
        hikes.sort(key=lambda h: h.get("distance_km") or 0)
    elif sort_by == "Longest":
        hikes.sort(key=lambda h: h.get("distance_km") or 0, reverse=True)
    elif sort_by == "Most climbing":
        hikes.sort(key=lambda h: h.get("elevation_gain_m") or 0, reverse=True)
    else:
        difficulty_order = {"Easy": 0, "Moderate": 1, "Hard": 2, "Extreme": 3}
        hikes.sort(key=lambda h: (difficulty_order.get(h.get("difficulty"), 4), h.get("distance_km") or 0))

    st.caption(f"{len(hikes)} trail{'s' if len(hikes) != 1 else ''} match this view")

    if not hikes:
        st.info("No trails match those filters. Widen the distance range or clear the search.")
    else:
        for start in range(0, len(hikes), 2):
            columns = st.columns(2)
            for offset, column in enumerate(columns):
                index = start + offset
                if index < len(hikes):
                    with column:
                        render_trail_card(hikes[index])

    render_insights(hikes)

    st.markdown(
        """
        <div class="footer-lockup">
            <strong>Kilele Explorers</strong><br>
            Built in Kenya for people who would rather be outside.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
