"""Persist wearable exports, including activities not linked to a catalog trail."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from database import get_db
from models import User, Hike, HikeSession
from utils.wearable_parser import WearableDataParser


def import_activity(user_id: int, name: str, content: bytes, hike_id=None) -> dict:
    from kilele_core.activities import save_activity
    with get_db() as db:
        return save_activity(db, User, Hike, HikeSession, WearableDataParser, user_id, name, content, hike_id)


def render_activity_import():
    import streamlit as st
    from auth import get_current_user
    from services import get_all_hikes

    st.subheader("Import an activity")
    with st.form("activity_import"):
        upload = st.file_uploader("GPX, FIT or TCX file", type=["gpx", "fit", "tcx"])
        hikes = get_all_hikes()
        options = {None: "No linked trail", **{h["id"]: h["name"] for h in hikes}}
        hike_id = st.selectbox("Trail", list(options), format_func=options.get)
        submitted = st.form_submit_button("Import activity", type="primary", icon=":material/upload_file:")
    if submitted:
        if upload is None:
            st.error("Choose a file first.")
            return
        try:
            result = import_activity(get_current_user()["id"], upload.name, upload.getvalue(), hike_id)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.info("This activity is already saved.") if result["duplicate"] else st.success("Activity saved.")
        summary = result["summary"]
        cols = st.columns(3)
        cols[0].metric("Distance", f"{summary['total_distance_km']:.2f} km")
        cols[1].metric("Duration", f"{summary['duration_hours'] * 60:.0f} min")
        cols[2].metric("Elevation gain", f"{summary['elevation_gain_m']:.0f} m")
