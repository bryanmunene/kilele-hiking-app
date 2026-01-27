"""
Social page - Follow/unfollow users and manage connections.
"""
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_followers, get_following, follow_user, unfollow_user, search_users, get_user_stats
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

init_database()

# Page configuration
st.set_page_config(
    page_title="Social Connections - Kilele",
    page_icon="👥",
    layout="wide"
)
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to manage your connections")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Helper functions
def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

@st.cache_data(ttl=30)
def fetch_followers():
    """Fetch user's followers"""
    try:
        user = get_current_user()
        if user:
            return get_followers(user['id'])
        return []
    except Exception as e:
        st.error(f"Error fetching followers: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_following():
    """Fetch users being followed"""
    try:
        user = get_current_user()
        if user:
            return get_following(user['id'])
        return []
    except Exception as e:
        st.error(f"Error fetching following: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_user_statistics():
    """Fetch user statistics"""
    try:
        user = get_current_user()
        if user:
            return get_user_stats(user['id'])
        return {}
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return {}

def unfollow_user_action(follow_id):
    """Unfollow a user"""
    try:
        result = unfollow_user(follow_id)
        if result:
            st.success("✅ Unfollowed successfully")
            st.cache_data.clear()
            return True
        else:
            st.error("❌ Failed to unfollow")
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def format_date(date_str):
    """Format date string"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime('%B %d, %Y')
    except:
        return "Recently"

# Main app
st.title("👥 Social Connections")
st.markdown("### Your hiking community")

# Fetch data
followers = fetch_followers()
following = fetch_following()
stats = fetch_user_statistics()

# Display summary stats
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 Followers", len(followers))

with col2:
    st.metric("👤 Following", len(following))

with col3:
    total_connections = len(followers) + len(following)
    st.metric("🌐 Total Connections", total_connections)

st.markdown("---")

# Tabs for followers and following
tab1, tab2, tab3 = st.tabs(["👥 Followers", "👤 Following", "📊 My Stats"])

# Tab 1: Followers
with tab1:
    st.subheader("Your Followers")
    st.markdown("*People who follow your hiking activities*")
    
    if not followers:
        st.info("You don't have any followers yet. Keep sharing your hikes and reviews!")
    else:
        # Search/filter
        search = st.text_input("Search followers", placeholder="Search by username", key="search_followers")
        
        # Filter followers
        filtered_followers = followers
        if search:
            search_lower = search.lower()
            filtered_followers = [f for f in filtered_followers if search_lower in f['follower_username'].lower()]
        
        if not filtered_followers:
            st.info("No followers match your search")
        else:
            st.markdown(f"**Showing {len(filtered_followers)} follower(s)**")
            st.markdown("---")
            
            # Display followers
            for follower in filtered_followers:
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"<div class='user-name'>👤 {follower['follower_username']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='connection-date'>Following you since {format_date(follower['created_at'])}</div>", unsafe_allow_html=True)
                
                with col2:
                    # Check if we're following them back
                    following_ids = [f['following_user_id'] for f in following]
                    if follower['follower_user_id'] not in following_ids:
                        if st.button("Follow Back", key=f"follow_back_{follower['id']}", use_container_width=True):
                            st.info("Follow back feature coming soon!")
                    else:
                        st.success("✓ Following")
                
                st.markdown("---")

# Tab 2: Following
with tab2:
    st.subheader("Users You Follow")
    st.markdown("*Hikers you're connected with*")
    
    if not following:
        st.info("You're not following anyone yet. Start connecting with other hikers!")
    else:
        # Search/filter
        search = st.text_input("Search following", placeholder="Search by username", key="search_following")
        
        # Filter following
        filtered_following = following
        if search:
            search_lower = search.lower()
            filtered_following = [f for f in filtered_following if search_lower in f['following_username'].lower()]
        
        if not filtered_following:
            st.info("No users match your search")
        else:
            st.markdown(f"**Showing {len(filtered_following)} user(s)**")
            st.markdown("---")
            
            # Display following
            for follow in filtered_following:
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"<div class='user-name'>👤 {follow['following_username']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='connection-date'>Following since {format_date(follow['created_at'])}</div>", unsafe_allow_html=True)
                
                with col2:
                    if st.button("Unfollow", key=f"unfollow_{follow['id']}", use_container_width=True, type="secondary"):
                        if unfollow_user(follow['id']):
                            st.rerun()
                
                st.markdown("---")

# Tab 3: User Statistics
with tab3:
    st.subheader("Your Hiking Statistics")
    
    if not stats:
        st.info("No statistics available yet. Start hiking!")
    else:
        # Display comprehensive stats
        st.markdown("### 🥾 Hiking Activity")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Hikes", stats.get('total_hikes', 0))
        with col2:
            st.metric("Distance", f"{stats.get('total_distance_km', 0):.1f} km")
        with col3:
            st.metric("Elevation", f"{stats.get('total_elevation_m', 0):.0f} m")
        with col4:
            st.metric("Time", f"{stats.get('total_duration_hours', 0):.1f} hrs")
        
        st.markdown("---")
        st.markdown("### ⭐ Reviews & Engagement")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Reviews Written", stats.get('reviews_count', 0))
        with col2:
            st.metric("Photos Uploaded", stats.get('photos_count', 0))
        with col3:
            st.metric("Helpful Votes", stats.get('helpful_received', 0))
        
        st.markdown("---")
        st.markdown("### 🏆 Achievements & Social")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Achievements", stats.get('achievements_earned', 0))
        with col2:
            st.metric("Total Points", stats.get('total_points', 0))
        with col3:
            st.metric("Bookmarks", stats.get('bookmarks_count', 0))
        with col4:
            st.metric("Followers", stats.get('followers_count', 0))
        
        # Progress towards next milestone
        st.markdown("---")
        st.markdown("### 📈 Progress Towards Next Milestones")
        
        # Calculate progress for common achievements
        total_hikes = stats.get('total_hikes', 0)
        milestones = [1, 5, 10, 25, 50]
        next_milestone = next((m for m in milestones if m > total_hikes), 50)
        
        if next_milestone:
            hike_progress = (total_hikes / next_milestone) * 100
            st.progress(min(hike_progress / 100, 1.0))
            st.markdown(f"**Hike Milestone:** {total_hikes}/{next_milestone} hikes ({hike_progress:.0f}%)")
        
        # Distance milestone
        total_distance = stats.get('total_distance_km', 0)
        distance_milestones = [10, 42, 100, 250, 500]
        next_distance_milestone = next((m for m in distance_milestones if m > total_distance), 500)
        
        if next_distance_milestone:
            distance_progress = (total_distance / next_distance_milestone) * 100
            st.progress(min(distance_progress / 100, 1.0))
            st.markdown(f"**Distance Milestone:** {total_distance:.1f}/{next_distance_milestone} km ({distance_progress:.0f}%)")

# Footer
st.markdown("---")
st.markdown("""
### 💡 Tips for Building Your Community

**🌟 Be Active**
- Complete hikes regularly
- Write detailed reviews
- Upload photos

**🤝 Engage**
- Follow hikers with similar interests
- Mark helpful reviews
- Share your achievements

**📱 Stay Connected**
- Check your social feed
- Respond to followers
- Celebrate others' achievements
""")
