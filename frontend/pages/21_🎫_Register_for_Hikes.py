"""Discover a group hike, review details, then confirm a place."""
import streamlit as st
from auth import get_current_user, restore_session_from_storage
from api_client import api_request
from booking_service import upcoming_events, register_free, registrations_for
from booking_ui import BOOKING_PAGE, positive_id, event_summary, equipment_list, support_link
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Group hikes - Kilele", layout="wide")
apply_nature_theme()
restore_session_from_storage()
st.title("Group hikes")
user = get_current_user()
event_id = positive_id(st.query_params.get("event"))
events = upcoming_events(event_id=event_id)
if st.query_params.get("event") and not event_id:
    st.warning("That hike link is invalid.")
    st.page_link(BOOKING_PAGE, label="All group hikes", icon=":material/arrow_back:")
    st.stop()
if not events:
    st.info("This hike is no longer available." if event_id else "No upcoming group hikes have been published yet.")
    st.page_link("views/my_hikes.py", label="My hikes", icon=":material/event:")
    st.page_link("views/explore.py", label="Explore trails", icon=":material/landscape:")
    st.stop()
if not event_id:
    cols = st.columns(2)
    difficulty = cols[0].selectbox("Difficulty", ["All", "Easy", "Moderate", "Hard", "Extreme"])
    price = cols[1].selectbox("Fee", ["All", "Free", "Paid"])
    events = [e for e in events if (difficulty == "All" or e["difficulty"] == difficulty)
              and (price == "All" or (price == "Free") == (e["price"] == 0))]
    if not events:
        st.info("No group hikes match these filters.")
    for event in events:
        with st.container(border=True, key=f"event_card_{event['id']}"):
            st.subheader(event["name"])
            event_summary(event)
            st.page_link(BOOKING_PAGE, label="Review and book", icon=":material/event_available:",
                         query_params={"event": str(event["id"])}, disabled=event["spots"] == 0)
    st.page_link("views/my_hikes.py", label="My hikes", icon=":material/event:")
    st.stop()

event = events[0]
st.page_link(BOOKING_PAGE, label="All group hikes", icon=":material/arrow_back:")
st.subheader(event["name"])
event_summary(event)
with st.expander("Equipment and trail details"):
    equipment_list(event["hike_id"])
    st.page_link("views/trail.py", label="View trail", icon=":material/hiking:",
                 query_params={"trail": str(event["hike_id"])})
support_link()
st.divider()
st.subheader("Confirm your place")
if not user:
    st.session_state.booking_return = event_id
    st.info("Sign in to continue with this booking.")
    st.page_link("pages/0_🔐_Login.py", label="Sign in to book", icon=":material/login:")
    st.stop()

existing = next((r for r in registrations_for(user["id"])
                 if r["planned_hike_id"] == event_id and r["status"] != "cancelled"), None)
if existing and existing["payment_status"] == "paid":
    st.success(f"You already have a place. Booking reference #{existing['registration_id']}.")
    st.page_link("views/my_hikes.py", label="View my booking", icon=":material/event_available:")
    st.stop()
if event["spots"] == 0 and not existing:
    st.info("This hike is fully booked.")
    st.stop()
config = {"available": False, "sandbox_available": False}
if event["price"]:
    with st.spinner("Checking checkout availability..."):
        config = api_request("GET", "/api/payments/config")
    if not (config.get("available") or config.get("sandbox_available")):
        st.info("Paid bookings are currently unavailable. No payment will be collected.")
        if config.get("error"):
            st.warning(config["error"])
        st.stop()
    if config.get("sandbox_available"):
        st.warning("Sandbox payment: a test payment does not confirm a real booking.")
    st.caption("Paid cancellations and refunds require organizer reconciliation.")
else:
    st.caption("You can cancel a free upcoming booking from My hikes.")
with st.form(f"booking_{event_id}"):
    phone = st.text_input("M-Pesa phone number", placeholder="0712345678") if event["price"] else ""
    agreed = st.checkbox("Confirm my place" if not event["price"] else f"Confirm payment of KES {event['price']:,.0f}")
    submitted = st.form_submit_button("Confirm free booking" if not event["price"] else
        "Send test payment" if config.get("sandbox_available") else "Pay with M-Pesa",
        icon=":material/event_available:", type="primary", width="stretch")
if submitted:
    if not agreed:
        st.error("Confirm your place before continuing.")
    else:
        with st.spinner("Submitting booking..."):
            result = register_free(user["id"], event_id) if not event["price"] else api_request(
                "POST", "/api/payments/checkout", json={"planned_hike_id": event_id, "phone_number": phone})
        if result.get("error"):
            st.error(result["error"])
        else:
            if not event["price"]:
                st.session_state.confirmed_booking = result["registration_id"]
            else:
                st.session_state.booking_feedback = result.get("message") or "Payment requested. Check its status below."
            st.switch_page("views/my_hikes.py")
