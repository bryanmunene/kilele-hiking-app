"""Import wearable exports without requiring a paid API account."""
import pandas as pd
import streamlit as st
from activity_import import render_activity_import
from auth import is_authenticated, get_current_user, restore_session_from_storage
from nature_theme import apply_nature_theme
from services import get_user_sessions

st.set_page_config(page_title="Activities - Kilele", page_icon="⌚", layout="wide")
apply_nature_theme()
restore_session_from_storage()
st.title("Activities")

if not is_authenticated():
    st.info("Sign in to import your activities.")
    st.page_link("pages/0_🔐_Login.py", label="Sign in", icon="🔐")
    st.stop()

upload_tab, history_tab = st.tabs(["Import", "Imported activities"])
with upload_tab:
    render_activity_import()

with history_tab:
    imported = [
        session for session in get_user_sessions(get_current_user()["id"])
        if (session.get("notes") or "").startswith("Activity import SHA256:")
    ]
    if imported:
        st.dataframe(pd.DataFrame([{
            "Date": s["started_at"][:10] if s.get("started_at") else "",
            "Distance (km)": s.get("distance_covered_km", 0),
            "Duration (hours)": s.get("duration_hours", 0),
            "Elevation (m)": s.get("elevation_gain_m", 0),
        } for s in imported]), hide_index=True, width="stretch")
    else:
        st.info("No imported activities yet.")
