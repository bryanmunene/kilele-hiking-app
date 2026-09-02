import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_user_profile, get_user_stats, get_user_sessions, get_user_bookmarks, delete_bookmark, update_user_profile
from auth import is_authenticated, get_current_user
from cloudinary_service import cloudinary_service, uploaded_image_to_data_url
from nature_theme import apply_nature_theme

# Initialize database
init_database()

# Page configuration
st.set_page_config(page_title="Profile - Kilele", page_icon="👤", layout="wide")
apply_nature_theme()

# Mobile responsive styles for profile page
st.markdown("""
    <style>
    /* Profile picture responsive sizing */
    @media (max-width: 768px) {
        img {
            max-width: 150px !important;
            height: auto !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            margin-bottom: 15px !important;
        }
        /* Stack profile sections vertically */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to view your profile")
    st.info("👈 Navigate to the Login page to access your account")
    st.stop()

user = get_current_user()

st.title(f"👤 {user['username']}'s Profile")
st.markdown("---")

# Profile Picture Section
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Profile Picture")
    # Display current profile picture
    profile_picture = user.get('profile_picture')
    if profile_picture and profile_picture.startswith(("http://", "https://", "data:image/")):
        st.image(profile_picture, width=200)
    elif profile_picture and os.path.exists(profile_picture):
        st.image(user['profile_picture'], width=200)
    else:
        # Default placeholder
        st.image("https://via.placeholder.com/200x200/667eea/ffffff?text=" + user['username'][0].upper(), width=200)
    
    uploaded_file = st.file_uploader("Upload new profile picture", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        if st.button("💾 Save Profile Picture"):
            try:
                profile_url = None
                if cloudinary_service.enabled:
                    profile_url = cloudinary_service.upload_profile_picture(uploaded_file, user['id'])

                if not profile_url:
                    profile_url = uploaded_image_to_data_url(
                        uploaded_file,
                        max_size=(400, 400),
                        quality=85,
                        max_bytes=600_000,
                    )

                if not profile_url:
                    st.error("❌ Image upload failed. Try a smaller JPG or PNG file.")
                    st.stop()

                update_user_profile(user['id'], {'profile_picture': profile_url})
                
                st.success("✅ Profile picture uploaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error uploading profile picture: {str(e)}")

with col2:
    st.subheader("Account Information")
    info_data = {
        "Username": user['username'],
        "Email": user['email'],
        "Full Name": user.get('full_name', 'N/A'),
        "Member Since": user.get('created_at', 'N/A')
    }
    
    for key, value in info_data.items():
        st.text(f"{key}: {value}")

st.markdown("---")

# Fetch user statistics
@st.cache_data(ttl=30)
def fetch_user_stats():
    try:
        user = get_current_user()
        if user:
            return get_user_stats(user['id'])
        return None
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_hike_sessions(active_only=False):
    try:
        user = get_current_user()
        if user:
            all_sessions = get_user_sessions(user['id'])
            if active_only:
                return [s for s in all_sessions if not s.get('end_time')]
            return all_sessions
        return []
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_saved_hikes():
    try:
        user = get_current_user()
        if user:
            return get_user_bookmarks(user['id'])
        return []
    except Exception as e:
        st.error(f"Error fetching saved hikes: {e}")
        return []

# Display Statistics
stats = fetch_user_stats()

if stats:
    st.subheader("📊 Your Hiking Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏔️ Total Hikes", stats['total_hikes'])
    with col2:
        st.metric("⭐ Reviews", stats['reviews_count'])
    with col3:
        st.metric("🔖 Bookmarks", stats['bookmarks_count'])
    with col4:
        st.metric("⛰️ Elevation", f"{stats['total_elevation']:.0f} m")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("🚶 Total Distance", f"{stats['total_distance']:.1f} km")
    with col6:
        st.metric("⏱️ Total Time", f"{stats['total_duration']:.1f} hrs")
    
    st.markdown("---")

# Active Hikes
st.subheader("📍 Active Hikes")
active_sessions = fetch_hike_sessions(active_only=True)

if active_sessions:
    for session in active_sessions:
        with st.expander(f"🏃 {session.get('hike_name', 'Unknown Hike')} - In Progress"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Started:** {session['started_at'][:16]}")
                st.write(f"**Distance Covered:** {session.get('distance_covered_km', 0):.2f} km")
            with col2:
                st.write(f"**Duration:** {session.get('duration_minutes', 0)} minutes")
                if session.get('current_latitude') and session.get('current_longitude'):
                    st.write(f"**Location:** {session['current_latitude']:.4f}, {session['current_longitude']:.4f}")
            
            # Quick update button
            if st.button(f"✏️ Update Progress", key=f"update_{session['id']}"):
                st.info("👈 Go to 'Track Hike' page to update this session")
else:
    st.info("No active hikes. Start tracking a hike from the Track Hike page!")

st.markdown("---")

# Hike History
st.subheader("📜 Hike History")
all_sessions = fetch_hike_sessions(active_only=False)
completed_sessions = [s for s in all_sessions if not s.get('is_active', True)]

if completed_sessions:
    # Create DataFrame for visualization
    df = pd.DataFrame(completed_sessions)
    
    # Rating distribution
    if 'rating' in df.columns and df['rating'].notna().any():
        st.write("### ⭐ Your Ratings Distribution")
        rating_counts = df['rating'].value_counts().sort_index()
        fig = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            labels={'x': 'Rating', 'y': 'Count'},
            title='Hike Ratings'
        )
        st.plotly_chart(fig, width="stretch")
    
    # Display recent hikes
    st.write("### 🕒 Recent Completed Hikes")
    for session in completed_sessions[:5]:  # Show last 5
        with st.expander(f"✅ {session.get('hike_name', 'Unknown Hike')} - {session.get('completed_at', '')[:10]}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Started:** {session['started_at'][:16]}")
                st.write(f"**Completed:** {session.get('completed_at', 'N/A')[:16]}")
                st.write(f"**Distance:** {session.get('distance_covered_km', 0):.2f} km")
            with col2:
                st.write(f"**Duration:** {session.get('duration_minutes', 0)} minutes")
                if session.get('rating'):
                    st.write(f"**Rating:** {'⭐' * session['rating']}")
                if session.get('notes'):
                    st.write(f"**Notes:** {session['notes']}")
else:
    st.info("No completed hikes yet. Complete your first hike to see history!")

st.markdown("---")

# Saved Hikes
st.subheader("❤️ Favorite Trails")
saved = fetch_saved_hikes()

if saved:
    cols = st.columns(3)
    for idx, item in enumerate(saved):
        with cols[idx % 3]:
            st.write(f"**{item.get('hike_name', 'Unknown')}**")
            st.write(f"Saved: {item['saved_at'][:10]}")
            if st.button(f"💔 Remove", key=f"unsave_{item['id']}"):
                try:
                    result = delete_bookmark(item['id'])
                    if result:
                        st.success("Removed from favorites")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.info("No saved trails yet. Save your favorites from the Home page!")

# Logout button
st.markdown("---")
if st.button("🚪 Logout", type="secondary"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.success("Logged out successfully")
    st.rerun()
