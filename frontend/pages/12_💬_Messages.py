import os
import sys
from datetime import datetime

import streamlit as st

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_user, is_authenticated, restore_session_from_storage
from database import init_database
from nature_theme import apply_nature_theme
from services import (
    create_conversation,
    get_conversation_messages,
    get_user_conversations,
    search_users,
    send_message,
)


st.set_page_config(page_title="Messages - Kilele Hiking", page_icon="💬", layout="wide")
apply_nature_theme()
restore_session_from_storage()
init_database()


if not is_authenticated():
    st.warning("⚠️ Please login to access messages")
    st.stop()


current_user = get_current_user()
current_user_id = current_user["id"]


def time_ago(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timestamp.tzinfo)
        diff = now - timestamp

        seconds = diff.total_seconds()
        if seconds < 60:
            return "Just now"
        if seconds < 3600:
            return f"{int(seconds / 60)}m ago"
        if seconds < 86400:
            return f"{int(seconds / 3600)}h ago"
        if seconds < 604800:
            return f"{int(seconds / 86400)}d ago"
        return timestamp.strftime("%b %d, %Y")
    except Exception:
        return ""


def participant_label(conversation: dict) -> str:
    participants = conversation.get("participants") or []
    if not participants:
        return "Conversation"
    names = [
        participant.get("full_name") or participant.get("username") or "Hiker"
        for participant in participants
    ]
    return ", ".join(names)


st.title("💬 Messages")
st.caption("Connect with hikers, share trail notes, and plan adventures together.")

if "selected_conversation_id" not in st.session_state:
    st.session_state.selected_conversation_id = None

tab1, tab2 = st.tabs(["📬 Conversations", "✉️ New Message"])

with tab1:
    conversations = get_user_conversations(current_user_id)

    if not conversations:
        st.info("No conversations yet. Start one from the New Message tab.")
    else:
        if st.session_state.selected_conversation_id is None:
            st.session_state.selected_conversation_id = conversations[0]["id"]

        conversation_col, message_col = st.columns([0.9, 1.7])

        with conversation_col:
            st.subheader("Your Conversations")
            for conversation in conversations:
                label = participant_label(conversation)
                last_message = conversation.get("last_message")
                preview = last_message["content"] if last_message else "No messages yet"
                if len(preview) > 56:
                    preview = f"{preview[:53].rstrip()}..."
                unread = conversation.get("unread_count", 0)
                button_label = f"{'● ' if unread else ''}{label}\n{preview}"
                if st.button(
                    button_label,
                    key=f"conversation_{conversation['id']}",
                    width="stretch",
                    type="primary"
                    if conversation["id"] == st.session_state.selected_conversation_id
                    else "secondary",
                ):
                    st.session_state.selected_conversation_id = conversation["id"]
                    st.rerun()

        with message_col:
            selected_id = st.session_state.selected_conversation_id
            selected_conversation = next(
                (conversation for conversation in conversations if conversation["id"] == selected_id),
                conversations[0],
            )
            st.subheader(participant_label(selected_conversation))

            try:
                messages = get_conversation_messages(selected_conversation["id"], current_user_id)
            except ValueError as exc:
                st.error(str(exc))
                messages = []

            if not messages:
                st.info("No messages in this conversation yet.")
            else:
                for message in messages:
                    mine = message["sender_id"] == current_user_id
                    with st.chat_message("user" if mine else "assistant"):
                        sender = "You" if mine else message.get("sender_username", "Hiker")
                        st.caption(f"{sender} · {time_ago(message.get('created_at', ''))}")
                        st.write(message["content"])

            with st.form("reply_form", clear_on_submit=True):
                reply = st.text_area("Reply", max_chars=2000, placeholder="Write a message...")
                submitted = st.form_submit_button("Send Reply", type="primary")
                if submitted:
                    try:
                        send_message(current_user_id, selected_conversation["id"], reply)
                        st.success("Message sent.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

with tab2:
    st.subheader("Start a New Conversation")
    query = st.text_input("Search hikers", placeholder="Type a username or name")

    if len(query.strip()) < 2:
        st.info("Type at least 2 characters to find another hiker.")
    else:
        users = search_users(query, exclude_user_id=current_user_id)
        if not users:
            st.warning("No hikers matched that search.")
        else:
            user_options = {
                f"{user.get('full_name') or user['username']} (@{user['username']})": user["id"]
                for user in users
            }
            selected_label = st.selectbox("Recipient", list(user_options.keys()))

            with st.form("new_message_form", clear_on_submit=True):
                content = st.text_area("Message", max_chars=2000, placeholder="Say hello or share trail plans...")
                submitted = st.form_submit_button("Send Message", type="primary")
                if submitted:
                    try:
                        conversation = create_conversation([current_user_id, user_options[selected_label]])
                        send_message(current_user_id, conversation["id"], content)
                        st.session_state.selected_conversation_id = conversation["id"]
                        st.success("Message sent.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

st.divider()
_, refresh_col = st.columns([3, 1])
with refresh_col:
    if st.button("🔄 Refresh", width="stretch"):
        st.rerun()
