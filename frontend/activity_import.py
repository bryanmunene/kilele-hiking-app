"""Persist wearable exports, including activities not linked to a catalog trail."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from database import get_db
from models import User, Hike, HikeSession
from utils.wearable_parser import WearableDataParser


def import_activity(user_id: int, name: str, content: bytes, hike_id=None) -> dict:
    if not content or len(content) > 10 * 1024 * 1024:
        raise ValueError("Choose an activity file smaller than 10 MB.")
    parsed = WearableDataParser.parse_file(content, Path(name).suffix)
    if not parsed.get("success"):
        raise ValueError(parsed.get("error", "The activity file could not be read."))
    if not parsed.get("total_points"):
        raise ValueError("This file has no GPS track points.")
    fingerprint = "Activity import SHA256:" + hashlib.sha256(content).hexdigest()

    def timestamp(value):
        if not value:
            return None
        result = datetime.fromisoformat(value)
        return result.astimezone(timezone.utc).replace(tzinfo=None) if result.tzinfo else result

    with get_db() as db:
        user = db.query(User).filter_by(id=user_id, is_active=True).with_for_update().first()
        if not user:
            raise ValueError("Sign in to import an activity.")
        existing = db.query(HikeSession).filter_by(user_id=user_id, notes=fingerprint).first()
        if existing:
            return {"session_id": existing.id, "duplicate": True, "summary": parsed}
        if hike_id is not None and not db.get(Hike, hike_id):
            raise ValueError("The selected trail no longer exists.")
        ended_at = timestamp(parsed.get("end_time")) or datetime.utcnow()
        session = HikeSession(
            user_id=user_id, hike_id=hike_id, started_at=timestamp(parsed.get("start_time")) or ended_at,
            ended_at=ended_at, completed_at=ended_at, status="completed", is_active=False,
            distance_covered_km=parsed.get("total_distance_km", 0),
            duration_hours=parsed.get("duration_hours", 0),
            duration_minutes=round(parsed.get("duration_hours", 0) * 60),
            elevation_gain_m=parsed.get("elevation_gain_m", 0),
            route_data=json.dumps(parsed["route_coordinates"], default=str), notes=fingerprint,
        )
        db.add(session)
        db.flush()
        return {"session_id": session.id, "duplicate": False, "summary": parsed}


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
