import streamlit as st
from api_client import api_request
from auth import get_current_user

st.set_page_config(page_title="Operations - Kilele", layout="wide")
st.title("Operations")
user = get_current_user()
if not user or not user.get("is_admin"):
    st.info("Administrator access required.")
    st.stop()
if st.button("Refresh status", icon=":material/refresh:"):
    st.rerun()
with st.spinner("Checking operational status..."):
    status = api_request("GET", "/api/v1/admin/operations")
if status.get("error"):
    st.warning(status["error"])
    st.stop()

mail, support, backup = status["mail"], status["support"], status["backup"]
cols = st.columns(4)
cols[0].metric("Open requests", support["open"])
cols[1].metric("Queued emails", mail["pending"])
cols[2].metric("Failed emails", mail["failed"])
cols[3].metric("Sent in 24 hours", mail["sent_today"])
st.subheader("Email delivery")
if not status["email"]["configured"]:
    st.warning("Email is not authorized. Queued notices cannot be delivered yet.")
    st.link_button("Gmail setup checklist", "https://github.com/bryanmunene/kilele-hiking-app/blob/main/INTEGRATIONS.md",
                   icon=":material/open_in_new:")
else:
    st.write(f"Provider: {status['email']['provider']}")
    st.caption(f"Test recipient: {user['email']}")
    if st.button("Send test to my inbox", icon=":material/mail:"):
        result = api_request("POST", "/api/v1/admin/email/test")
        st.error(result["error"]) if result.get("error") else st.success(result["message"])
if mail["oldest_pending"]:
    st.caption(f"Oldest queued notice: {mail['oldest_pending']} UTC")
if st.button("Retry failed mail", icon=":material/replay:", disabled=not mail["pending"] or not status["email"]["configured"]):
    result = api_request("POST", "/api/v1/admin/notifications/retry")
    st.error(result["error"]) if result.get("error") else st.success(result["message"])

st.divider()
st.subheader("Encrypted backups")
latest = backup["latest"]
if not latest:
    st.warning("No recorded backup outcome yet. Check GitHub Actions before relying on recovery.")
elif latest["status"] in {"failure", "cancelled"}:
    st.error(f"The latest backup run ended with status: {latest['status']}.")
elif latest["status"] == "running":
    st.info("The latest backup run has not recorded a completed result.")
if backup["stale"]:
    st.warning("No verified backup recorded in the last 36 hours.")
else:
    st.success(f"Last successful backup and restore check: {backup['last_success']} UTC")
st.caption("Daily at 05:17 Nairobi time. Encrypted artifacts are retained for seven days.")
st.link_button("Backup runs", "https://github.com/bryanmunene/kilele-hiking-app/actions/workflows/backups.yml",
               icon=":material/open_in_new:")
if latest and latest["run_url"]:
    st.link_button("Latest backup run", latest["run_url"], icon=":material/history:")

st.divider()
st.subheader("Support and capacity")
st.page_link("pages/24_Account_and_Support.py", label="Open organizer inbox", icon=":material/inbox:")
if support["oldest_open"]:
    st.caption(f"Oldest open request: {support['oldest_open']} UTC")
size = status["database_bytes"]
st.metric("Database size", f"{size / 1024**2:.1f} MB" if size is not None else "Unavailable")
st.caption("Storage size is not a provider quota reading. Check current compute, storage, and bandwidth limits in the provider dashboards.")
cols = st.columns(2)
cols[0].link_button("Render usage", "https://dashboard.render.com", icon=":material/open_in_new:")
cols[1].link_button("Neon usage", "https://console.neon.tech", icon=":material/open_in_new:")
st.caption(f"Checked: {status['checked_at']} UTC")
