import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import (
    get_all_users_admin, get_platform_stats, toggle_user_status, 
    toggle_admin_status, delete_user_admin, delete_hike_admin,
    delete_review_admin, get_all_reviews_admin, get_recent_activity,
    get_all_hikes
)
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

# Initialize database
init_database()

# Page configuration
st.set_page_config(page_title="Admin Dashboard - Kilele", page_icon="👑", layout="wide")
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access the admin dashboard")
    st.info("👈 Navigate to the Login page")
    st.stop()

user = get_current_user()

# Check admin privileges
if not user.get('is_admin', False):
    st.error("🚫 Access Denied")
    st.warning("This page is only accessible to administrators.")
    st.info("If you believe you should have access, please contact the system administrator.")
    st.stop()

# Admin Dashboard Header
st.markdown("""
<div class="admin-header">
    <h1>👑 Admin Dashboard</h1>
    <p>Platform Management & Analytics</p>
</div>
""", unsafe_allow_html=True)

# Dashboard tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "👥 User Management", 
    "🏔️ Trail Management", 
    "⭐ Review Moderation",
    "📈 Recent Activity"
])

# TAB 1: OVERVIEW
with tab1:
    st.header("📊 Platform Overview")
    
    # Fetch platform statistics
    stats = get_platform_stats()
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['total_users']}</h2>
            <p>Total Users</p>
            <small>{stats['active_users']} Active</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['total_hikes']}</h2>
            <p>Total Trails</p>
            <small>{stats['total_reviews']} Reviews</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['total_sessions']}</h2>
            <p>Hiking Sessions</p>
            <small>{stats['total_bookmarks']} Bookmarks</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 User Statistics")
        user_data = {
            "Status": ["Active", "Inactive"],
            "Count": [stats['active_users'], stats['total_users'] - stats['active_users']]
        }
        fig = px.pie(user_data, values='Count', names='Status', 
                     color_discrete_sequence=['#2e7d32', '#d32f2f'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Content Statistics")
        content_data = {
            "Type": ["Trails", "Reviews", "Sessions", "Bookmarks"],
            "Count": [stats['total_hikes'], stats['total_reviews'], 
                     stats['total_sessions'], stats['total_bookmarks']]
        }
        fig = px.bar(content_data, x='Type', y='Count', 
                    color='Type', color_discrete_sequence=['#1976d2', '#2e7d32', '#f57c00', '#7b1fa2'])
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: USER MANAGEMENT
with tab2:
    st.header("👥 User Management")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search users", placeholder="Search by username or email")
    with col2:
        show_inactive = st.checkbox("Show inactive", value=False)
    
    # Fetch all users
    users = get_all_users_admin(limit=1000)
    
    # Filter users
    if search_term:
        users = [u for u in users if search_term.lower() in u['username'].lower() 
                 or search_term.lower() in u['email'].lower()]
    
    if not show_inactive:
        users = [u for u in users if u['is_active']]
    
    st.write(f"**Total Users:** {len(users)}")
    
    # Display users in expandable sections
    for user_data in users:
        with st.expander(f"{'👑' if user_data['is_admin'] else '👤'} {user_data['username']} - {user_data['email']} {'🔴 Inactive' if not user_data['is_active'] else '🟢 Active'}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**User ID:** {user_data['id']}")
                st.write(f"**Full Name:** {user_data.get('full_name', 'N/A')}")
                st.write(f"**Email:** {user_data['email']}")
                st.write(f"**2FA Enabled:** {'✅ Yes' if user_data['two_factor_enabled'] else '❌ No'}")
                st.write(f"**Member Since:** {user_data['created_at'][:10] if user_data['created_at'] else 'N/A'}")
            
            with col2:
                st.write("**Actions:**")
                
                # Toggle active status
                if user_data['is_active']:
                    if st.button(f"🔴 Deactivate", key=f"deactivate_{user_data['id']}"):
                        if toggle_user_status(user_data['id'], False):
                            st.success("User deactivated")
                            st.rerun()
                else:
                    if st.button(f"🟢 Activate", key=f"activate_{user_data['id']}"):
                        if toggle_user_status(user_data['id'], True):
                            st.success("User activated")
                            st.rerun()
                
                # Toggle admin status
                if not user_data['is_admin']:
                    if st.button(f"👑 Make Admin", key=f"make_admin_{user_data['id']}"):
                        if toggle_admin_status(user_data['id'], True):
                            st.success("Admin privileges granted")
                            st.rerun()
                else:
                    if st.button(f"👤 Remove Admin", key=f"remove_admin_{user_data['id']}"):
                        if toggle_admin_status(user_data['id'], False):
                            st.success("Admin privileges revoked")
                            st.rerun()
                
                # Delete user (dangerous)
                st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
                if st.button(f"🗑️ Delete User", key=f"delete_{user_data['id']}"):
                    if user_data['id'] != user['id']:  # Can't delete yourself
                        if st.session_state.get(f"confirm_delete_{user_data['id']}", False):
                            if delete_user_admin(user_data['id']):
                                st.success("User deleted")
                                st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{user_data['id']}"] = True
                            st.warning("⚠️ Click again to confirm deletion")
                    else:
                        st.error("Cannot delete your own account")
                st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: TRAIL MANAGEMENT
with tab3:
    st.header("🏔️ Trail Management")
    
    # Search trails
    search_trail = st.text_input("🔍 Search trails", placeholder="Search by name or location")
    
    # Fetch all hikes
    hikes = get_all_hikes(limit=1000)
    
    # Filter hikes
    if search_trail:
        hikes = [h for h in hikes if search_trail.lower() in h['name'].lower() 
                 or search_trail.lower() in h['location'].lower()]
    
    st.write(f"**Total Trails:** {len(hikes)}")
    
    # Display trails in expandable sections
    for hike in hikes:
        with st.expander(f"🏔️ {hike['name']} - {hike['location']} ({hike['difficulty']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Trail ID:** {hike['id']}")
                st.write(f"**Location:** {hike['location']}")
                st.write(f"**Difficulty:** {hike['difficulty']}")
                st.write(f"**Distance:** {hike['distance_km']} km")
                st.write(f"**Elevation Gain:** {hike['elevation_gain_m']} m")
                st.write(f"**Duration:** {hike['estimated_duration_hours']} hours")
                st.write(f"**Trail Type:** {hike.get('trail_type', 'N/A')}")
                st.write(f"**Best Season:** {hike.get('best_season', 'N/A')}")
            
            with col2:
                st.write(f"**Description:**")
                st.write(hike.get('description', 'No description'))
                
                st.write("**Actions:**")
                
                # Edit trail (link to Add Trail page with edit mode)
                st.info("💡 To edit this trail, use the 'Add Trail' page")
                
                # Delete trail (dangerous)
                st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
                if st.button(f"🗑️ Delete Trail", key=f"delete_trail_{hike['id']}"):
                    if st.session_state.get(f"confirm_delete_trail_{hike['id']}", False):
                        if delete_hike_admin(hike['id']):
                            st.success("Trail deleted")
                            st.rerun()
                    else:
                        st.session_state[f"confirm_delete_trail_{hike['id']}"] = True
                        st.warning("⚠️ Click again to confirm deletion (this will delete all reviews and sessions)")
                st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: REVIEW MODERATION
with tab4:
    st.header("⭐ Review Moderation")
    
    # Filter by rating
    col1, col2 = st.columns([2, 1])
    with col1:
        search_review = st.text_input("🔍 Search reviews", placeholder="Search by user or trail name")
    with col2:
        min_rating = st.selectbox("Minimum Rating", [1, 2, 3, 4, 5], index=0)
    
    # Fetch all reviews
    reviews = get_all_reviews_admin(limit=1000)
    
    # Filter reviews
    if search_review:
        reviews = [r for r in reviews if search_review.lower() in (r['username'] or '').lower() 
                   or search_review.lower() in (r['hike_name'] or '').lower()]
    
    reviews = [r for r in reviews if r['rating'] >= min_rating]
    
    st.write(f"**Total Reviews:** {len(reviews)}")
    
    # Display reviews
    for review in reviews:
        with st.expander(f"⭐ {review['rating']}/5 - {review['hike_name']} by {review['username']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Review ID:** {review['id']}")
                st.write(f"**Trail:** {review['hike_name']}")
                st.write(f"**User:** {review['username']}")
                st.write(f"**Rating:** {'⭐' * review['rating']}")
                st.write(f"**Date:** {review['created_at'][:10] if review['created_at'] else 'N/A'}")
                st.write(f"**Comment:**")
                st.info(review.get('comment', 'No comment'))
            
            with col2:
                st.write("**Actions:**")
                st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
                if st.button(f"🗑️ Delete Review", key=f"delete_review_{review['id']}"):
                    if st.session_state.get(f"confirm_delete_review_{review['id']}", False):
                        if delete_review_admin(review['id']):
                            st.success("Review deleted")
                            st.rerun()
                    else:
                        st.session_state[f"confirm_delete_review_{review['id']}"] = True
                        st.warning("⚠️ Click again to confirm")
                st.markdown('</div>', unsafe_allow_html=True)

# TAB 5: RECENT ACTIVITY
with tab5:
    st.header("📈 Recent Activity")
    
    # Activity limit slider
    activity_limit = st.slider("Show recent activities", 10, 100, 50)
    
    # Fetch recent activity
    activities = get_recent_activity(limit=activity_limit)
    
    st.write(f"**Showing {len(activities)} recent activities**")
    
    # Display activities in timeline format
    for activity in activities:
        if activity['type'] == 'review':
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write("⭐ **Review**")
                with col2:
                    st.write(f"**{activity['user']}** reviewed **{activity['hike']}** - Rating: {activity['rating']}/5")
                    st.caption(f"🕒 {activity['timestamp'][:19] if activity['timestamp'] else 'N/A'}")
                st.markdown("---")
        
        elif activity['type'] == 'session':
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write("🥾 **Session**")
                with col2:
                    duration_text = f"{activity['duration']} min" if activity['duration'] else "Duration N/A"
                    st.write(f"**{activity['user']}** completed **{activity['hike']}** - {duration_text}")
                    st.caption(f"🕒 {activity['timestamp'][:19] if activity['timestamp'] else 'N/A'}")
                st.markdown("---")

# Footer
st.markdown("---")
st.caption("👑 Admin Dashboard - Kilele Hiking Platform")
