"""Account privacy controls and the community support/moderation queue."""
import json
import streamlit as st
from sqlalchemy import select, update
from datetime import datetime
from auth import get_current_user, logout, restore_session_from_storage
from database import get_db, init_database
from models import User, SessionToken
from nature_theme import apply_nature_theme
from kilele_core.security import require_admin, throttle, verify_password, verify_second_factor
from kilele_core.operations import blocks, reports, outbox, export_account, erase_account, set_block, submit_report

st.set_page_config(page_title="Account and support - Kilele", page_icon=":material/manage_accounts:", layout="wide")
init_database()
apply_nature_theme()
restore_session_from_storage()
st.title("Account and support")
st.write("Kilele Explorers")
st.markdown("[kileleexplorers@gmail.com](mailto:kileleexplorers@gmail.com)")
user = get_current_user()
if not user:
    st.page_link("pages/0_🔐_Login.py", label="Sign in", icon=":material/login:")
    st.page_link("pages/25_Privacy_and_Terms.py", label="Privacy and terms", icon=":material/policy:")
    st.stop()

account, safety, support = st.tabs(["My account", "Blocked accounts", "Support requests"])
with account:
    from api_client import api_request
    st.caption("Email verified" if user.get("email_verified") else "Email not yet verified")
    if not user.get("email_verified") and st.button("Verify email", icon=":material/mark_email_read:"):
        result = api_request("POST", "/api/v1/auth/request-verification")
        st.error(result["error"]) if result.get("error") else st.info(result["message"])
    st.subheader("Your data")
    if st.button("Prepare data export", icon=":material/download:"):
        with get_db() as db:
            actor = db.get(User, user["id"])
            data = export_account(db, actor)
        st.download_button("Download my data", json.dumps(data, default=str, indent=2),
            "kilele-account.json", "application/json", icon=":material/download:")
    st.page_link("pages/6_🔐_2FA_Setup.py", label="Authenticator settings", icon=":material/security:")
    st.page_link("pages/25_Privacy_and_Terms.py", label="Privacy and terms", icon=":material/policy:")
    with st.expander("Delete account"):
        st.warning("This permanently removes your profile, private hike records and contacts, and anonymizes your posts. Limited booking/payment records remain for reconciliation. Cancel upcoming hikes you organize first. Backups may retain older records until they expire.")
        with st.form("delete_account"):
            password = st.text_input("Current password", type="password")
            code = st.text_input("Authenticator code", max_chars=6) if user.get("two_factor_enabled") else ""
            confirm = st.checkbox("Permanently delete my account")
            submitted = st.form_submit_button("Delete my account", icon=":material/delete_forever:")
        if submitted:
            try:
                if not confirm:
                    raise ValueError("Confirm deletion before continuing.")
                with get_db() as db:
                    throttle(db, "account_delete", str(user["id"]), limit=5)
                    actor = db.get(User, user["id"])
                    if not verify_password(password, actor.hashed_password) or not verify_second_factor(actor, code):
                        raise ValueError("Invalid password or authenticator code.")
                    erase_account(db, actor)
                logout()
                st.success("Account deleted.")
                st.stop()
            except ValueError as exc:
                st.error(str(exc))

with safety:
    st.subheader("Blocked accounts")
    with get_db() as db:
        blocked = db.execute(select(blocks.c.blocked_id).where(blocks.c.user_id == user["id"])).scalars().all()
        names = {item.id: item.username for item in db.query(User).filter(User.id.in_(blocked)).all()}
    if not names:
        st.info("No blocked accounts.")
    for target_id, name in names.items():
        left, right = st.columns([3, 1])
        left.write(name)
        if right.button("Unblock", key=f"unblock_{target_id}", icon=":material/person_add:"):
            with get_db() as db:
                set_block(db, user["id"], target_id, False)
            st.rerun()
    with st.form("block_user"):
        username = st.text_input("Username to block")
        block = st.form_submit_button("Block account", icon=":material/block:")
    if block:
        try:
            with get_db() as db:
                target = db.query(User).filter_by(username=username.strip(), is_active=True).first()
                if not target:
                    raise ValueError("Account not found.")
                set_block(db, user["id"], target.id, True)
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

with support:
    st.subheader("Contact the organizers")
    st.caption("Not an emergency service. Do not include passwords or payment PINs.")
    with st.form("support_request", clear_on_submit=True):
        category = st.selectbox("Category", ["support", "abuse", "privacy", "trail", "booking"])
        target_name = st.text_input("Related username (optional)")
        details = st.text_area("Request details", max_chars=4000)
        sent = st.form_submit_button("Submit request", icon=":material/send:")
    if sent:
        try:
            with get_db() as db:
                throttle(db, "report", str(user["id"]), limit=5)
                target = db.query(User).filter_by(username=target_name.strip()).first() if target_name.strip() else None
                if target_name.strip() and not target:
                    raise ValueError("Related username not found.")
                reference = submit_report(db, user["id"], category, details, target.id if target else None)
            st.success(f"Request #{reference} recorded.")
        except ValueError as exc:
            st.error(str(exc))
    with get_db() as db:
        mine = db.execute(select(reports).where(reports.c.user_id == user["id"]).order_by(reports.c.id.desc())).mappings().all()
    for row in mine:
        with st.expander(f"#{row['id']} - {row['category'].title()} - {row['status'].title()}"):
            st.write(row["details"])
            if row["resolution"]:
                st.write(row["resolution"])

if user.get("is_admin"):
    st.divider()
    st.subheader("Organizer inbox")
    with get_db() as db:
        require_admin(db, User, user["id"])
        open_reports = db.execute(select(reports).where(reports.c.status == "open").order_by(reports.c.created_at)).mappings().all()
        waiting_mail = len(db.execute(select(outbox.c.key).where(outbox.c.sent_at.is_(None))).all())
    st.caption(f"{waiting_mail} emails awaiting delivery")
    if st.button("Retry email delivery", icon=":material/refresh:", disabled=not waiting_mail):
        result = api_request("POST", "/api/v1/admin/notifications/retry")
        st.error(result["error"]) if result.get("error") else st.success(result["message"])
    if not open_reports:
        st.info("No open support requests.")
    for row in open_reports:
        with st.expander(f"#{row['id']} - {row['category'].title()} - account {row['user_id']}"):
            st.write(row["details"])
            with st.form(f"resolve_{row['id']}"):
                resolution = st.text_area("Reply / resolution", max_chars=4000)
                suspend = st.checkbox("Suspend reported account", disabled=not row["target_id"])
                resolve = st.form_submit_button("Resolve request", icon=":material/task_alt:")
            if resolve:
                try:
                    if not resolution.strip():
                        raise ValueError("Enter a resolution for the requester.")
                    with get_db() as db:
                        require_admin(db, User, user["id"])
                        if suspend:
                            target = db.get(User, row["target_id"])
                            if not target or target.is_admin:
                                raise ValueError("An administrator cannot be suspended here.")
                            target.is_active = False
                            target.password_changed_at = datetime.utcnow()
                            db.query(SessionToken).filter_by(user_id=target.id).delete()
                        db.execute(update(reports).where(reports.c.id == row["id"]).values(
                            status="resolved", resolution=resolution.strip(), resolved_at=datetime.utcnow()))
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
