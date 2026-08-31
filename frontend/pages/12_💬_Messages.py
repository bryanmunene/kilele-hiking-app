import streamlit as st
from datetime import datetime
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_user_conversations, get_conversation_messages, send_message, create_conversation, search_users
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

# Initialize database
init_database()

# Page config
st.set_page_config(page_title="Messages - Kilele Hiking", page_icon="💬", layout="wide")
apply_nature_theme()

# Check if user is logged in
if not is_authenticated():
    st.warning("⚠️ Please login to access messages")
    st.stop()

current_user = get_current_user()
current_user_id = current_user["id"]

# Helper function to format time ago
def time_ago(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timestamp.tzinfo)
        diff = now - timestamp
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}d ago"
        else:
            return timestamp.strftime("%b %d, %Y")
    except:
        return ""

st.title("💬 Messages")

# Tabs
tab1, tab2 = st.tabs(["📬 Conversations", "✉️ New Message"])

with tab1:
    st.subheader("Your Conversations")
    
    st.info("🚧 Messaging functionality is being migrated to the new architecture")
    st.markdown("""
    ### Direct Messaging
    
    Connect with other hikers, share experiences, and plan adventures together.
    
    **Note:** This feature is currently being updated and will be available soon.
    
    In the meantime, you can:
    - 👥 Follow other users from the Social page
    - ⭐ Leave reviews on trails
    - 📰 View activity feed
    """)

with tab2:
    st.subheader("Start a New Conversation")
    st.info("Coming soon - messaging system being migrated")

# Auto-refresh option
st.divider()
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Refresh", width="stretch"):
        st.rerun()
