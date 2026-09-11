"""Presentation shared by discovery, checkout, and the member's itinerary."""
from datetime import datetime
from urllib.parse import urlencode
import streamlit as st
from api_client import api_request
from auth import get_current_user
from booking_service import cancel
from services import get_trail_equipment

BOOKING_PAGE = "pages/21_🎫_Register_for_Hikes.py"
SUPPORT = "kileleexplorers@gmail.com"


def positive_id(value):
    try:
        number = int(value)
        return number if 0 < number < 2**31 else None
    except (TypeError, ValueError):
        return None


def event_summary(event):
    st.caption(f"{event['location']} | {datetime.fromisoformat(event['planned_date']):%d %B %Y} | {event['difficulty']}")
    st.write(event["description"])
    cols = st.columns(3)
    cols[0].metric("Fee", f"KES {event['price']:,.0f}" if event["price"] else "Free")
    cols[1].metric("Available places", event["spots"] if event["spots"] is not None else "Open")
    cols[2].metric("Distance", f"{event['distance_km']:g} km")
    st.write("**Meeting point:** " + (event["meeting_point"] or "Awaiting organizer confirmation"))
    st.write("**Transport:** " + (event["transport_mode"] or "self_drive").replace("_", " ").title())
    st.write("**Organizer:** " + event["organizer"])


def equipment_list(trail_id):
    items = get_trail_equipment(trail_id)
    if items:
        for item in items:
            st.write(f"- {item['item_name']}" + (" (required)" if item.get("is_required") else ""))
    else:
        st.caption("No trail-specific equipment list has been published.")
    st.page_link("pages/19_🎒_Hiking_Gear.py", label="Equipment catalogue", icon=":material/backpack:")


def support_link(reference=None):
    subject = f"Kilele booking #{reference}" if reference else "Kilele hike enquiry"
    st.link_button("Contact organizer", f"mailto:{SUPPORT}?" + urlencode({"subject": subject}),
                   icon=":material/mail:")


def registration_card(registration):
    r = registration
    with st.container(border=True, key=f"registration_card_{r['registration_id']}"):
        st.subheader(r["hike_name"])
        st.caption(f"{r['hike_location']} | {datetime.fromisoformat(r['planned_date']):%d %B %Y} | Reference #{r['registration_id']}")
        cols = st.columns(3)
        cols[0].metric("Booking", r["status"].title())
        cols[1].metric("Payment", "Not required" if not r["price"] else r["payment_status"].title())
        cols[2].metric("Fee", f"KES {r['price']:,.0f}" if r["price"] else "Free")
        st.write("**Meeting point:** " + (r["meeting_point"] or "Awaiting organizer confirmation"))
        st.write("**Transport:** " + (r["transport_mode"] or "self_drive").replace("_", " ").title())
        if r["notes"]:
            st.write(r["notes"])
        with st.expander("Equipment and trail details"):
            equipment_list(r["hike_id"])
            st.page_link("views/trail.py", label="View trail", query_params={"trail": str(r["hike_id"])},
                         icon=":material/hiking:")
        support_link(r["registration_id"])
        future = datetime.fromisoformat(r["planned_date"]) > datetime.utcnow()
        if r["status"] != "cancelled" and future and not r["price"]:
            with st.expander("Cancel my place"):
                with st.form(f"cancel_{r['registration_id']}"):
                    agreed = st.checkbox("Cancel this booking")
                    submitted = st.form_submit_button("Cancel booking", icon=":material/event_busy:")
                if submitted:
                    if not agreed:
                        st.error("Confirm cancellation before continuing.")
                    else:
                        result = cancel(get_current_user()["id"], r["registration_id"])
                        if result.get("error"):
                            st.error(result["error"])
                        else:
                            st.session_state.booking_feedback = result["message"]
                            st.rerun()
        elif r["price"] and r["status"] != "cancelled":
            st.caption("Paid cancellations and refunds require organizer reconciliation.")
        if r["price"] and r["payment_status"] != "paid" and r["status"] != "cancelled":
            if st.button("Check payment status", key=f"payment_{r['registration_id']}", icon=":material/refresh:"):
                result = api_request("POST", f"/api/payments/registrations/{r['registration_id']}/status")
                if result.get("error"):
                    st.error(result["error"])
                elif result.get("status") == "completed" and result.get("environment") == "production":
                    st.session_state.booking_feedback = "Payment received. Your booking is confirmed."
                    st.rerun()
                else:
                    st.info(f"Payment status: {result.get('status', 'pending')}.")
            if future:
                st.page_link(BOOKING_PAGE, label="Continue checkout", icon=":material/payments:",
                             query_params={"event": str(r["planned_hike_id"])})
