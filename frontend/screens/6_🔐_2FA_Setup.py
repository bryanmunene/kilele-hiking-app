"""Authenticator settings with recent credential checks."""
from io import BytesIO
import qrcode
import streamlit as st
from auth import (get_current_user, restore_session_from_storage, setup_2fa,
                  enable_2fa, disable_2fa, logout)
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Account security - Kilele", layout="wide")
apply_nature_theme()
restore_session_from_storage()
user = get_current_user()
if not user:
    st.warning("Sign in to manage account security.")
    st.stop()

st.title("Account security")
enabled = user.get("two_factor_enabled", False)
st.subheader("Authenticator")
st.success("Two-factor authentication is enabled.") if enabled else st.info("Two-factor authentication is not enabled.")

if enabled:
    with st.form("disable_authenticator"):
        password = st.text_input("Password", type="password")
        code = st.text_input("Authenticator code", max_chars=6)
        submitted = st.form_submit_button("Disable authenticator", icon=":material/lock_open:")
    if submitted:
        try:
            if not disable_2fa(user["id"], password, code):
                raise ValueError("Check your password and authenticator code.")
            logout()
            st.success("Authenticator disabled. Sign in again.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
else:
    with st.form("setup_authenticator"):
        password = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Set up authenticator", icon=":material/qr_code:")
    if submitted:
        try:
            st.session_state.authenticator_setup = setup_2fa(user["id"], password)
        except ValueError as exc:
            st.error(str(exc))
    if st.session_state.get("authenticator_setup"):
        secret, uri = st.session_state.authenticator_setup
        image = BytesIO()
        qrcode.make(uri).save(image, format="PNG")
        st.image(image.getvalue(), width=240)
        with st.expander("Manual setup key"):
            st.code(secret, language=None)
        st.warning("Keep your authenticator backup safe. Losing it can lock you out of your account.")
        with st.form("verify_authenticator"):
            code = st.text_input("Authenticator code", max_chars=6)
            submitted = st.form_submit_button("Enable authenticator", type="primary", icon=":material/lock:")
        if submitted:
            try:
                if not enable_2fa(user["id"], code=code):
                    raise ValueError("Check the code in your authenticator.")
                logout()
                st.success("Authenticator enabled. Sign in again.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

