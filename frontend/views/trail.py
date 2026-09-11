import streamlit as st
from booking_service import upcoming_events
from booking_ui import BOOKING_PAGE, positive_id, event_summary, equipment_list, support_link
from image_utils import display_image
from services import get_hike

st.set_page_config(page_title="Trail details - Kilele", layout="wide")
trail_id = positive_id(st.query_params.get("trail"))
trail = get_hike(trail_id) if trail_id else None
if not trail:
    st.title("Trail not found")
    st.page_link("views/explore.py", label="Browse trails", icon=":material/arrow_back:")
    st.stop()
st.page_link("views/explore.py", label="All trails", icon=":material/arrow_back:")
st.title(trail["name"])
st.caption(f"{trail['location']} | {trail['difficulty']} | {trail.get('trail_type') or 'Trail'}")
with st.container(key="trail_photo"):
    display_image(trail.get("image_url"), width="stretch")
st.write(trail.get("description") or "")
cols = st.columns(3)
cols[0].metric("Distance", f"{trail['distance_km']:g} km")
cols[1].metric("Duration", f"{trail['estimated_duration_hours']:g} hours")
cols[2].metric("Elevation gain", f"{trail.get('elevation_gain_m') or 0:g} m")
with st.expander("Equipment", expanded=False):
    equipment_list(trail_id)
if trail.get("latitude") is not None and trail.get("longitude") is not None:
    st.link_button("Open trail location", f"https://www.google.com/maps?q={trail['latitude']},{trail['longitude']}",
                   icon=":material/map:")
st.subheader("Upcoming group hikes")
events = upcoming_events(trail_id=trail_id)
if not events:
    st.info("No upcoming group hikes have been published for this trail.")
    st.page_link("pages/20_🗓️_Plan_Hike.py", label="Plan a personal hike", icon=":material/event_note:")
for event in events:
    with st.container(border=True):
        event_summary(event)
        st.page_link(BOOKING_PAGE, label="Review and book", icon=":material/event_available:",
                     query_params={"event": str(event["id"])}, disabled=event["spots"] == 0)
support_link()
