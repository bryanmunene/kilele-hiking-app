from datetime import datetime
import streamlit as st
from auth import get_current_user
from booking_service import registrations_for
from booking_ui import BOOKING_PAGE, registration_card
from services import get_user_planned_hikes

st.set_page_config(page_title="My hikes - Kilele", layout="wide")
st.title("My hikes")
user = get_current_user()
if not user:
    st.info("Sign in to view your hikes.")
    st.page_link("pages/0_🔐_Login.py", label="Sign in", icon=":material/login:")
    st.stop()
if st.session_state.get("booking_feedback"):
    st.success(st.session_state.pop("booking_feedback"))
if st.session_state.get("confirmed_booking"):
    reference = st.session_state.pop("confirmed_booking")
    st.success(f"Your place is confirmed. Booking reference #{reference}.")
    st.session_state.pop("booking_return", None)
st.page_link(BOOKING_PAGE, label="Find a group hike", icon=":material/groups:")
registrations = registrations_for(user["id"])
now = datetime.utcnow()
upcoming, past, cancelled, personal = st.tabs(["Upcoming", "Past", "Cancelled", "Personal plans"])
for container, rows in [
    (upcoming, [r for r in registrations if r["status"] != "cancelled" and r["event_status"] == "planned" and datetime.fromisoformat(r["planned_date"]) > now]),
    (past, [r for r in registrations if r["status"] != "cancelled" and (r["event_status"] == "completed" or datetime.fromisoformat(r["planned_date"]) <= now)]),
    (cancelled, [r for r in registrations if r["status"] == "cancelled" or r["event_status"] == "cancelled"]),
]:
    with container:
        if not rows:
            st.caption("No hikes here yet.")
        for registration in rows:
            registration_card(registration)
with personal:
    plans = get_user_planned_hikes(user["id"])
    st.page_link("pages/20_🗓️_Plan_Hike.py", label="Manage personal plans", icon=":material/event_note:")
    for plan in plans:
        st.write(f"**{plan['hike_name']}** | {plan['planned_date'][:10]} | {plan['status'].title()}")
    if not plans:
        st.caption("No personal plans yet.")
