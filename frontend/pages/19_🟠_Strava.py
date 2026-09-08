import streamlit as st
import pandas as pd
from auth import is_authenticated, get_current_user, restore_session_from_storage
from api_client import api_request
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Strava - Kilele", page_icon="🟠", layout="wide")
apply_nature_theme()
restore_session_from_storage()
st.title("Strava")

if "code" in st.query_params:
    st.session_state.strava_callback = {
        key: st.query_params.get(key, "") for key in ("code", "state", "scope")
    }
    st.query_params.clear()
if "error" in st.query_params:
    st.query_params.clear()
    st.info("Strava authorization was cancelled. Your account has not changed.")

if not is_authenticated():
    st.info("Sign in to connect your Strava account.")
    st.page_link("pages/0_🔐_Login.py", label="Sign in", icon="🔐")
    st.stop()

if st.session_state.get("strava_callback"):
    callback = st.session_state.pop("strava_callback")
    with st.spinner("Connecting Strava..."):
        result = api_request("POST", "/api/strava/callback", json=callback)
    if result.get("error"):
        st.error(result["error"])
    else:
        st.success("Strava connected.")

with st.spinner("Checking connection..."):
    stats = api_request("GET", "/api/strava/stats")

if stats.get("error"):
    st.warning(stats["error"])
    if st.button("Retry", icon=":material/refresh:"):
        st.rerun()
elif stats.get("is_connected"):
    st.success("Connected to Strava")
    cols = st.columns(3)
    cols[0].metric("Activities", stats["total_activities"])
    cols[1].metric("Distance", f"{stats['total_distance_km']:.1f} km")
    cols[2].metric("Time", f"{stats['total_time_hours']:.1f} hours")
    sync_col, settings_col = st.columns(2)
    with sync_col:
        days = st.slider("Activity history (days)", 7, 365, 30)
        if st.button("Sync activities", icon=":material/sync:", type="primary"):
            with st.spinner("Importing activities..."):
                result = api_request("POST", "/api/strava/sync", params={"days": days})
            if result.get("error"):
                st.error(result["error"])
            else:
                st.success(result["message"])
                st.rerun()
        if stats.get("last_synced"):
            st.caption("Last synced: " + stats["last_synced"].replace("T", " ")[:19] + " UTC")
    with settings_col:
        enabled = st.toggle("Automatic sync", value=stats.get("sync_enabled", False))
        if enabled != stats.get("sync_enabled", False):
            result = api_request("POST", "/api/strava/toggle-autosync", params={"enabled": enabled})
            if result.get("error"):
                st.error(result["error"])
            else:
                st.rerun()
        disconnect = st.checkbox("Disconnect and remove imported Strava activities")
        if st.button("Disconnect", icon=":material/link_off:", disabled=not disconnect):
            result = api_request("DELETE", "/api/strava/disconnect")
            if result.get("error"):
                st.error(result["error"])
            else:
                st.rerun()
    st.subheader("Recent activities")
    activities = api_request("GET", "/api/strava/activities", params={"limit": 50})
    if isinstance(activities, dict):
        st.warning(activities.get("error", "Activities unavailable."))
    elif activities:
        st.dataframe(pd.DataFrame([{
            "Activity": item["name"], "Date": item["date"][:10],
            "Distance (km)": item["distance_km"], "Minutes": item["duration_minutes"],
            "Trail": item.get("matched_trail_name") or "Unmatched",
        } for item in activities]), hide_index=True, width="stretch")
    else:
        st.info("No Strava activities imported yet.")
elif stats.get("configured"):
    if st.button("Connect Strava", type="primary", icon=":material/link:"):
        result = api_request("GET", "/api/strava/connect")
        if result.get("error"):
            st.error(result["error"])
        else:
            st.session_state.strava_authorization_url = result["authorization_url"]
    if st.session_state.get("strava_authorization_url"):
        st.link_button("Authorize with Strava", st.session_state.strava_authorization_url)
    st.caption("Access is limited to your profile and activities visible to Everyone or Followers. You can disconnect anytime.")
else:
    st.info("Strava connection is not available yet. Activity-file imports are available.")

st.page_link("pages/13_⌚_Wearables.py", label="Import an activity file", icon=":material/upload_file:")
