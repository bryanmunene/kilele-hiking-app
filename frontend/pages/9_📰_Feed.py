"""
Social Feed page - View activities from followed hikers.
"""
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_user_sessions, get_following, get_reviews
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

init_database()

# Page configuration
st.set_page_config(
    page_title="Social Feed - Kilele",
    page_icon="📰",
    layout="wide"
)
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to view your social feed")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Helper functions
def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

@st.cache_data(ttl=30)
def fetch_activity_feed():
    """Fetch activity feed from followed users"""
    try:
        user = get_current_user()
        if user:
            sessions = get_user_sessions(user['id'])
            reviews = get_reviews()
            # Combine activities (simplified)
            return sessions[:10]  # Return recent sessions as feed
        return []
    except Exception as e:
        st.error(f"Error fetching feed: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_following():
    """Fetch list of users being followed"""
    try:
        user = get_current_user()
        if user:
            return get_following(user['id'])
        return []
    except Exception as e:
        st.error(f"Error fetching following: {e}")
        return []

def get_activity_icon(activity_type):
    """Get icon for activity type"""
    icons = {
        "completed_hike": "🥾",
        "review": "⭐",
        "achievement": "🏆",
        "bookmark": "🔖"
    }
    return icons.get(activity_type, "📌")

def format_time_ago(created_at):
    """Format time ago string"""
    try:
        activity_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(activity_time.tzinfo)
        diff = now - activity_time
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Recently"

# Main app
st.title("📰 Social Feed")
st.markdown("### See what other hikers are up to")

# Sidebar - Following info
with st.sidebar:
    st.markdown("### 👥 Following")
    following = fetch_following()
    
    if following:
        st.metric("Following", len(following))
        st.markdown("---")
        st.markdown("**Your connections:**")
        for user in following[:10]:  # Show first 10
            st.markdown(f"• {user['following_username']}")
        
        if len(following) > 10:
            st.markdown(f"*...and {len(following) - 10} more*")
    else:
        st.info("You're not following anyone yet")
        if st.button("Find Users to Follow"):
            st.switch_page("pages/9_👥_Social.py")

# Main feed
activities = fetch_activity_feed()

if not activities:
    # Empty feed state
    st.markdown("""
    <div class='empty-feed'>
        <h2>👋 Your feed is empty!</h2>
        <p>Start following other hikers to see their activities here.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Find Hikers to Follow", use_container_width=True):
            st.switch_page("pages/9_👥_Social.py")
else:
    # Filter options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        activity_filter = st.multiselect(
            "Filter by activity type",
            ["completed_hike", "review", "achievement", "bookmark"],
            default=["completed_hike", "review", "achievement", "bookmark"],
            format_func=lambda x: {
                "completed_hike": "🥾 Completed Hikes",
                "review": "⭐ Reviews",
                "achievement": "🏆 Achievements",
                "bookmark": "🔖 Bookmarks"
            }[x]
        )
    
    with col2:
        sort_order = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First"]
        )
    
    # Filter activities
    filtered_activities = [a for a in activities if a['activity_type'] in activity_filter]
    
    # Sort activities
    filtered_activities.sort(
        key=lambda x: x['created_at'],
        reverse=(sort_order == "Newest First")
    )
    
    if not filtered_activities:
        st.info("No activities match your filter")
    else:
        st.markdown(f"**Showing {len(filtered_activities)} activities**")
        st.markdown("---")
        
        # Display activities
        for activity in filtered_activities:
            icon = get_activity_icon(activity['activity_type'])
            time_ago = format_time_ago(activity['created_at'])
            
            # Activity card
            col1, col2 = st.columns([12, 1])
            
            with col1:
                # Header
                st.markdown(
                    f"<div class='activity-card'>"
                    f"<span class='activity-icon'>{icon}</span>"
                    f"<span class='activity-user'>{activity['username']}</span> "
                    f"{activity['description']}"
                    f"<div class='activity-time'>{time_ago}</div>",
                    unsafe_allow_html=True
                )
                
                # Details based on activity type
                if activity['activity_type'] == 'completed_hike' and activity.get('hike_name'):
                    st.markdown(f"**Trail:** {activity['hike_name']}")
                    if activity.get('hike_location'):
                        st.markdown(f"📍 {activity['hike_location']}")
                
                elif activity['activity_type'] == 'review' and activity.get('hike_name'):
                    st.markdown(f"**Trail:** {activity['hike_name']}")
                    if st.button(f"Read Review", key=f"review_{activity['id']}", type="secondary"):
                        st.switch_page("pages/7_⭐_Reviews.py")
                
                elif activity['activity_type'] == 'achievement':
                    st.markdown("🎉 *Congratulations!*")
                    if st.button(f"View Achievements", key=f"achievement_{activity['id']}", type="secondary"):
                        st.switch_page("pages/10_🏆_Achievements.py")
                
                elif activity['activity_type'] == 'bookmark' and activity.get('hike_name'):
                    st.markdown(f"**Trail:** {activity['hike_name']}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")

# Footer with suggestions
st.markdown("### 💡 Tips for a Better Feed")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='follow-suggestion-card'>
        <h4>👥 Follow More Hikers</h4>
        <p>Connect with active hikers to see more updates</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Find Hikers", use_container_width=True):
        st.switch_page("pages/9_👥_Social.py")

with col2:
    st.markdown("""
    <div class='follow-suggestion-card'>
        <h4>✍️ Share Your Activities</h4>
        <p>Write reviews and complete hikes to engage</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Write Review", use_container_width=True):
        st.switch_page("pages/7_⭐_Reviews.py")

with col3:
    st.markdown("""
    <div class='follow-suggestion-card'>
        <h4>🏆 Earn Achievements</h4>
        <p>Complete challenges to unlock badges</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Achievements", use_container_width=True):
        st.switch_page("pages/10_🏆_Achievements.py")
