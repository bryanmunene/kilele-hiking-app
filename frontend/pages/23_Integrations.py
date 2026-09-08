import streamlit as st
from api_client import api_request
from auth import is_authenticated, get_current_user, restore_session_from_storage
from config import settings
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Integrations - Kilele", layout="wide")
apply_nature_theme()
restore_session_from_storage()
st.title("Integrations")
if not is_authenticated() or not get_current_user().get("is_admin"):
    st.info("Administrator access required.")
    st.stop()
if st.button("Refresh", icon=":material/refresh:"):
    st.rerun()
status = api_request("GET", "/api/integrations/status")
if status.get("error"):
    st.warning(status["error"])
else:
    rows = [{"Integration": name.title(), "Configuration": "Configured; provider verification still required" if values["configured"] else "Not configured", "Mode": values.get("environment") or values.get("provider") or "OAuth"} for name, values in status.items()]
    rows.append({"Integration": "Image uploads", "Configuration": "Available", "Mode": "Cloudinary" if settings.has_cloudinary else "Database storage"})
    st.dataframe(rows, hide_index=True, width="stretch")
st.link_button("Account setup guide", "https://github.com/bryanmunene/kilele-hiking-app/blob/main/INTEGRATIONS.md", icon=":material/open_in_new:")
