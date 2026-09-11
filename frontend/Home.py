"""Application entrypoint shared by Render and Streamlit Community Cloud."""
import streamlit as st
from auth import get_current_user, restore_session_from_storage
from navigation import page_groups
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Kilele Explorers", page_icon=":material/hiking:", layout="wide")
apply_nature_theme()
st.session_state._navigation_manages_auth = True
restore_session_from_storage(force=True)
user = get_current_user()
st.navigation(page_groups(bool(user and user.get("is_admin"))), position="top").run()
