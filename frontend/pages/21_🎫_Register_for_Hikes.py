"""Browse group hikes and manage bookings with verified M-Pesa checkout."""
from datetime import datetime
import streamlit as st
from sqlalchemy import func
from auth import is_authenticated, get_current_user, restore_session_from_storage
from api_client import api_request
from database import get_db
from models import PlannedHike, Hike, HikeRegistration
from nature_theme import apply_nature_theme
from services import register_for_hike, get_user_registrations

st.set_page_config(page_title="Register for Hikes - Kilele", page_icon="🎫", layout="wide")
apply_nature_theme()
restore_session_from_storage()
st.title("Register for hikes")

if not is_authenticated():
    st.info("Sign in to book a hike.")
    st.page_link("pages/0_🔐_Login.py", label="Sign in", icon="🔐")
    st.stop()
user = get_current_user()

with get_db() as db:
    counts = db.query(
        HikeRegistration.planned_hike_id,
        func.count(HikeRegistration.id).label("total"),
    ).filter(HikeRegistration.status != "cancelled").group_by(HikeRegistration.planned_hike_id).subquery()
    rows = db.query(PlannedHike, Hike, counts.c.total).join(Hike, PlannedHike.hike_id == Hike.id).outerjoin(
        counts, counts.c.planned_hike_id == PlannedHike.id
    ).filter(PlannedHike.status == "planned", PlannedHike.planned_date > datetime.utcnow()).order_by(PlannedHike.planned_date).all()
    upcoming = [{
        "id": ph.id, "name": hike.name, "location": hike.location, "date": ph.planned_date,
        "price": ph.price or 0, "capacity": ph.max_participants,
        "count": count or 0, "description": ph.notes or hike.description or "",
        "difficulty": hike.difficulty,
    } for ph, hike, count in rows]
registrations = get_user_registrations(user["id"])

@st.cache_data(ttl=60, show_spinner=False)
def payment_configuration(session_token):
    return api_request("GET", "/api/payments/config")

config = {"available": False, "sandbox_available": False}
if any(h["price"] > 0 for h in upcoming) or any(r["price"] > 0 for r in registrations):
    with st.spinner("Checking checkout availability..."):
        config = payment_configuration(st.session_state.get("session_token"))
checkout_enabled = config.get("available") or config.get("sandbox_available")
if config.get("sandbox_available"):
    st.warning("Sandbox mode: test payments cannot confirm a paid booking.")
if config.get("error"):
    st.warning(config["error"])
if st.session_state.get("booking_feedback"):
    st.info(st.session_state.pop("booking_feedback"))

def start_payment(hike_id, phone):
    with st.spinner("Requesting payment..."):
        result = api_request("POST", "/api/payments/checkout", json={
            "planned_hike_id": hike_id, "phone_number": phone,
        })
    if result.get("error"):
        st.error(result["error"])
    else:
        st.session_state.booking_feedback = result.get("message") or "Payment status updated."
        st.rerun()

available_tab, bookings_tab = st.tabs(["Available hikes", "My registrations"])
with available_tab:
    difficulty_col, price_col = st.columns(2)
    difficulty = difficulty_col.selectbox("Difficulty", ["All", "Easy", "Moderate", "Hard", "Extreme"])
    price = price_col.selectbox("Price", ["All", "Free", "Under KES 2,000", "Under KES 5,000", "KES 5,000+"])
    filtered = [h for h in upcoming if difficulty == "All" or h["difficulty"] == difficulty]
    if price == "Free":
        filtered = [h for h in filtered if h["price"] == 0]
    elif price.startswith("Under"):
        filtered = [h for h in filtered if h["price"] < (2000 if "2,000" in price else 5000)]
    elif price == "KES 5,000+":
        filtered = [h for h in filtered if h["price"] >= 5000]
    if not filtered:
        st.info("No upcoming hikes match these filters.")
    for hike in filtered:
        with st.container(border=True):
            detail, booking = st.columns([2, 1])
            with detail:
                st.subheader(hike["name"])
                st.caption(f"{hike['location']} · {hike['date']:%d %B %Y} · {hike['difficulty']}")
                st.write(hike["description"])
            with booking:
                st.metric("Hike fee", f"KES {hike['price']:,.0f}" if hike["price"] else "Free")
                spots = None if not hike["capacity"] else max(0, hike["capacity"] - hike["count"])
                st.caption(f"{spots} spots available" if spots is not None else f"{hike['count']} registered")
            existing = next((r for r in registrations if r["planned_hike_id"] == hike["id"] and r["status"] != "cancelled"), None)
            if existing:
                st.info("You have a registration for this hike. Its payment and booking status are under My registrations.")
            elif spots == 0:
                st.info("Fully booked")
            elif hike["price"] and not checkout_enabled:
                st.info("Online payment is currently unavailable for this hike.")
            else:
                with st.expander("Book this hike"):
                    with st.form(f"book_{hike['id']}"):
                        phone = st.text_input("M-Pesa phone number", placeholder="0712345678") if hike["price"] else ""
                        agreed = st.checkbox(f"Confirm booking for KES {hike['price']:,.0f}" if hike["price"] else "Confirm my place")
                        submitted = st.form_submit_button(
                            "Send test payment" if config.get("sandbox_available") and hike["price"] else "Pay with M-Pesa" if hike["price"] else "Register",
                            type="primary", icon=":material/event_available:",
                        )
                        if submitted:
                            if not agreed:
                                st.error("Confirm your booking before continuing.")
                            elif hike["price"]:
                                start_payment(hike["id"], phone)
                            else:
                                result = register_for_hike(user["id"], hike["id"], "")
                                if result.get("error"):
                                    st.error(result["error"])
                                else:
                                    st.session_state.booking_feedback = "Your place is confirmed."
                                    st.rerun()

with bookings_tab:
    from services import cancel_registration
    if not registrations:
        st.info("No registrations yet.")
    for registration in registrations:
        with st.container(border=True):
            st.subheader(registration["hike_name"])
            st.caption(f"{registration['hike_location']} · {registration['planned_date'][:10]}")
            cols = st.columns(3)
            cols[0].metric("Booking", registration["status"].title())
            cols[1].metric("Payment", registration["payment_status"].title())
            cols[2].metric("Fee", f"KES {registration['price']:,.0f}")
            if registration["status"] != "cancelled":
                with st.expander("Cancel registration"):
                    confirmed = st.checkbox("Cancel my place", key=f"cancel_confirm_{registration['registration_id']}")
                    if st.button("Cancel booking", disabled=not confirmed, key=f"cancel_{registration['registration_id']}", icon=":material/event_busy:"):
                        result = cancel_registration(user["id"], registration["registration_id"])
                        if result.get("error"):
                            st.error(result["error"])
                        else:
                            st.session_state.booking_feedback = result["message"]
                            st.rerun()
            if registration["price"] and registration["payment_status"] != "paid":
                if st.button("Check payment status", key=f"check_{registration['registration_id']}", icon=":material/refresh:"):
                    with st.spinner("Checking with M-Pesa..."):
                        result = api_request("POST", f"/api/payments/registrations/{registration['registration_id']}/status")
                    if result.get("error"):
                        st.error(result["error"])
                    elif result.get("status") == "completed" and result.get("environment") == "production":
                        st.session_state.booking_feedback = "Payment received. Your booking is confirmed."
                        st.rerun()
                    else:
                        st.info("Test payment completed; booking remains unpaid." if result.get("status") == "completed" else f"Payment status: {result.get('status', 'pending')}.")
                if checkout_enabled and datetime.fromisoformat(registration["planned_date"]) > datetime.utcnow():
                    with st.form(f"retry_{registration['registration_id']}"):
                        phone = st.text_input("M-Pesa phone number", value=registration["phone_number"])
                        if st.form_submit_button("Pay / retry payment", icon=":material/payments:"):
                            start_payment(registration["planned_hike_id"], phone)
