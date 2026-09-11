import streamlit as st
from auth import (
    authenticate_user, register_user, verify_2fa_code, is_authenticated,
    get_current_user, logout, create_session_token, save_token_to_browser,
    restore_session_from_storage,
    TooManyAttempts, TwoFactorRequired,
)
from api_client import api_request
from database import init_database
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Sign in - Kilele", page_icon="🔐", layout="wide")
init_database()
apply_nature_theme()
restore_session_from_storage()

if st.query_params.get("verify_token"):
    token = st.query_params["verify_token"]
    st.query_params.clear()
    result = api_request("POST", "/api/v1/auth/verify-email", json={"token": token})
    st.error(result["error"]) if result.get("error") else st.success(result["message"])

if st.query_params.get("reset_token"):
    st.session_state.password_reset_token = st.query_params["reset_token"]
    st.query_params.clear()

with st.container(key="auth_form"):
    st.title("Kilele account")
    if st.session_state.get("password_reset_token"):
        st.subheader("Choose a new password")
        with st.form("reset_password"):
            password = st.text_input("New password", type="password")
            confirm = st.text_input("Confirm new password", type="password")
            submit = st.form_submit_button("Update password", type="primary")
        if submit:
            if password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 8 or len(password.encode("utf-8")) > 72:
                st.error("Use at least 8 characters and at most 72 UTF-8 bytes.")
            else:
                result = api_request("POST", "/api/v1/auth/reset-password", json={
                    "token": st.session_state.password_reset_token, "password": password,
                })
                if result.get("error"):
                    st.error(result["error"])
                else:
                    logout()
                    st.session_state.password_reset_feedback = result["message"]
                    st.rerun()
        st.stop()

    if st.session_state.get("password_reset_feedback"):
        st.success(st.session_state.pop("password_reset_feedback"))
    if is_authenticated():
        user = get_current_user()
        st.success(f"Signed in as {user['username']}")
        if st.session_state.get("strava_callback"):
            st.page_link("pages/19_🟠_Strava.py", label="Finish connecting Strava")
        if st.session_state.get("booking_return"):
            st.page_link("pages/21_🎫_Register_for_Hikes.py", label="Continue booking", icon=":material/event_available:",
                         query_params={"event": str(st.session_state.booking_return)})
        st.page_link("views/explore.py", label="Explore trails", icon=":material/landscape:")
        if st.button("Sign out", icon=":material/logout:"):
            logout()
            st.rerun()
        st.stop()

    login_tab, register_tab, recovery_tab = st.tabs(["Sign in", "Create account", "Reset password"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            otp = st.text_input("Authenticator code", max_chars=6) if st.session_state.get("needs_2fa") else ""
            remember = st.checkbox("Remember me", value=True)
            submit = st.form_submit_button("Sign in", type="primary", width="stretch")
        if submit:
            if not username or not password:
                st.error("Enter your username and password.")
            else:
                with st.spinner("Signing in..."):
                    try:
                        user = authenticate_user(username.strip(), password, otp)
                    except TwoFactorRequired:
                        st.session_state.needs_2fa = True
                        st.rerun()
                    except TooManyAttempts as exc:
                        st.error(str(exc))
                        st.stop()
                if not user:
                    st.error("Invalid username or password.")
                else:
                    token = create_session_token(user["id"], remember)
                    st.session_state.update(authenticated=True, user=user, session_token=token, needs_2fa=False)
                    save_token_to_browser(token)
                    st.rerun()

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full name")
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password", key="register_password")
            confirm = st.text_input("Confirm password", type="password")
            submit = st.form_submit_button("Create account", type="primary", width="stretch")
        if submit:
            if not all([full_name.strip(), username.strip(), email.strip(), password]):
                st.error("Complete all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 8 or len(password.encode("utf-8")) > 72:
                st.error("Use at least 8 characters and at most 72 UTF-8 bytes.")
            elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                st.error("Enter a valid email address.")
            else:
                try:
                    with st.spinner("Creating account..."):
                        register_user(username.strip(), email.strip().lower(), password, full_name.strip())
                    st.success("Account created. You can now sign in.")
                except ValueError as exc:
                    st.error(str(exc))

    with recovery_tab:
        with st.form("request_password_reset"):
            email = st.text_input("Account email")
            submit = st.form_submit_button("Send reset link", icon=":material/mail:", width="stretch")
        if submit:
            if not email.strip():
                st.error("Enter your account email.")
            else:
                with st.spinner("Requesting reset link..."):
                    result = api_request("POST", "/api/v1/auth/forgot-password", json={"email": email.strip()})
                st.error(result["error"]) if result.get("error") else st.info(result["message"])
