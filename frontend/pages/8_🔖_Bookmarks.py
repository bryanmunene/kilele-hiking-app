"""
Bookmarks page - View and manage your saved favorite trails.
"""
import streamlit as st
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_user_bookmarks, delete_bookmark, get_hike
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="My Bookmarks - Kilele",
    page_icon="🔖",
    layout="wide"
)
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to view your bookmarks")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Helper functions
@st.cache_data(ttl=30)
def fetch_bookmarks():
    """Fetch user's bookmarked trails"""
    try:
        user = get_current_user()
        return get_user_bookmarks(user['id'])
    except Exception as e:
        st.error(f"Error fetching bookmarks: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_hikes():
    """Fetch all hikes for adding new bookmarks"""
    try:
        from services import get_all_hikes
        return get_all_hikes()
    except Exception as e:
        st.error(f"Error fetching hikes: {e}")
        return []

def remove_bookmark_trail(hike_id):
    """Remove a trail from bookmarks"""
    try:
        user = get_current_user()
        result = delete_bookmark(user['id'], hike_id)
        if result:
            st.success("✅ Bookmark removed")
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Error removing bookmark: {e}")
        return False

def add_bookmark(hike_id, notes=None):
    """Add a trail to bookmarks"""
    try:
        from services import create_bookmark
        user = get_current_user()
        bookmark = create_bookmark(user['id'], hike_id, notes)
        if bookmark:
            st.success("✅ Trail bookmarked successfully!")
            st.cache_data.clear()
            return True
        else:
            st.error("❌ Failed to bookmark trail")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def remove_bookmark(bookmark_id):
    """Remove a trail from bookmarks"""
    try:
        result = delete_bookmark(bookmark_id)
        if result:
            st.success("✅ Bookmark removed")
            st.cache_data.clear()
            return True
        else:
            st.error("❌ Failed to remove bookmark")
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def get_difficulty_class(difficulty):
    """Get CSS class for difficulty level"""
    difficulty_map = {
        "Easy": "difficulty-easy",
        "Moderate": "difficulty-moderate",
        "Hard": "difficulty-hard",
        "Extreme": "difficulty-extreme"
    }
    return difficulty_map.get(difficulty, "")

# Main app
st.title("🔖 My Bookmarked Trails")
st.markdown("### Your saved hiking destinations")

# Tabs
tab1, tab2 = st.tabs(["📚 My Bookmarks", "➕ Add Bookmark"])

# Tab 1: View Bookmarks
with tab1:
    bookmarks = fetch_bookmarks()
    
    if not bookmarks:
        st.info("📭 No bookmarked trails yet. Start exploring and bookmark your favorites!")
    else:
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Bookmarks", len(bookmarks))
        with col2:
            total_distance = sum(b['hike']['distance_km'] for b in bookmarks)
            st.metric("Total Distance", f"{total_distance:.1f} km")
        with col3:
            with_notes = sum(1 for b in bookmarks if b.get('notes'))
            st.metric("With Notes", with_notes)
        
        st.markdown("---")
        
        # Filter and sort options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            difficulty_filter = st.selectbox(
                "Filter by Difficulty",
                ["All", "Easy", "Moderate", "Hard", "Extreme"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Recently Added", "Trail Name", "Distance", "Difficulty"]
            )
        
        with col3:
            search = st.text_input("Search trails", placeholder="Search by name or location")
        
        # Filter bookmarks
        filtered_bookmarks = bookmarks
        
        if difficulty_filter != "All":
            filtered_bookmarks = [b for b in filtered_bookmarks if b['hike']['difficulty'] == difficulty_filter]
        
        if search:
            search_lower = search.lower()
            filtered_bookmarks = [
                b for b in filtered_bookmarks 
                if search_lower in b['hike']['name'].lower() or search_lower in b['hike']['location'].lower()
            ]
        
        # Sort bookmarks
        if sort_by == "Recently Added":
            filtered_bookmarks.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == "Trail Name":
            filtered_bookmarks.sort(key=lambda x: x['hike']['name'])
        elif sort_by == "Distance":
            filtered_bookmarks.sort(key=lambda x: x['hike']['distance_km'], reverse=True)
        elif sort_by == "Difficulty":
            difficulty_order = {"Easy": 1, "Moderate": 2, "Hard": 3, "Extreme": 4}
            filtered_bookmarks.sort(key=lambda x: difficulty_order.get(x['hike']['difficulty'], 0))
        
        if not filtered_bookmarks:
            st.info("No trails match your filters")
        else:
            st.markdown(f"**Showing {len(filtered_bookmarks)} trail(s)**")
            st.markdown("---")
            
            # Display bookmarks
            for bookmark in filtered_bookmarks:
                hike = bookmark['hike']
                
                # Trail card
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"### 🥾 {hike['name']}")
                    st.markdown(f"📍 **Location:** {hike['location']}")
                    
                    # Trail details
                    detail_cols = st.columns(4)
                    with detail_cols[0]:
                        difficulty_class = get_difficulty_class(hike['difficulty'])
                        st.markdown(f"<span class='{difficulty_class}'>Difficulty: {hike['difficulty']}</span>", unsafe_allow_html=True)
                    with detail_cols[1]:
                        st.markdown(f"📏 **Distance:** {hike['distance_km']} km")
                    with detail_cols[2]:
                        st.markdown(f"⛰️ **Elevation:** {hike.get('elevation_gain_m', 'N/A')} m")
                    with detail_cols[3]:
                        st.markdown(f"⏱️ **Duration:** {hike['estimated_duration_hours']} hrs")
                    
                    # Description
                    if hike.get('description'):
                        with st.expander("📖 Trail Description"):
                            st.write(hike['description'])
                    
                    # Personal notes
                    if bookmark.get('notes'):
                        st.markdown(
                            f"<div class='bookmark-notes'>📝 <strong>My Notes:</strong> {bookmark['notes']}</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Bookmark date
                    bookmark_date = datetime.fromisoformat(bookmark['created_at'].replace('Z', '+00:00'))
                    st.markdown(f"<div class='trail-meta'>Bookmarked: {bookmark_date.strftime('%B %d, %Y at %I:%M %p')}</div>", unsafe_allow_html=True)
                
                with col2:
                    # Action buttons
                    if st.button("🗺️ View", key=f"view_{bookmark['id']}", use_container_width=True):
                        st.session_state['selected_trail'] = hike
                        st.switch_page("pages/1_🗺️_Map_View.py")
                    
                    if st.button("🗑️ Remove", key=f"remove_{bookmark['id']}", use_container_width=True, type="secondary"):
                        if remove_bookmark(bookmark['id']):
                            st.rerun()
                
                st.markdown("---")

# Tab 2: Add Bookmark
with tab2:
    st.subheader("➕ Add New Bookmark")
    st.markdown("Save a trail to your bookmarks to revisit later!")
    
    # Fetch all hikes
    hikes = fetch_hikes()
    
    if not hikes:
        st.error("No trails available")
    else:
        # Get already bookmarked hike IDs
        bookmarked_ids = {b['hike']['id'] for b in fetch_bookmarks()}
        
        # Filter out already bookmarked trails
        available_hikes = [h for h in hikes if h['id'] not in bookmarked_ids]
        
        if not available_hikes:
            st.info("✅ You've bookmarked all available trails!")
        else:
            with st.form("add_bookmark_form"):
                # Select trail
                selected_hike = st.selectbox(
                    "Select a trail",
                    options=available_hikes,
                    format_func=lambda x: f"{x['name']} - {x['location']} ({x['difficulty']}, {x['distance_km']} km)"
                )
                
                # Display trail details
                if selected_hike:
                    st.markdown("---")
                    st.markdown(f"### {selected_hike['name']}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Distance", f"{selected_hike['distance_km']} km")
                    with col2:
                        st.metric("Difficulty", selected_hike['difficulty'])
                    with col3:
                        st.metric("Elevation", f"{selected_hike.get('elevation_gain_m', 0)} m")
                    with col4:
                        st.metric("Duration", f"{selected_hike['estimated_duration_hours']} hrs")
                    
                    if selected_hike.get('description'):
                        st.info(selected_hike['description'])
                    
                    st.markdown("---")
                
                # Add personal notes
                notes = st.text_area(
                    "Personal Notes (Optional)",
                    placeholder="Why do you want to hike this trail? Any specific preparations needed? Planning to go with friends?",
                    height=150,
                    max_chars=500,
                    help="Add notes to remember why you bookmarked this trail or any plans you have"
                )
                
                submitted = st.form_submit_button("🔖 Bookmark Trail", use_container_width=True)
                
                if submitted and selected_hike:
                    if add_bookmark(selected_hike['id'], notes):
                        st.balloons()
                        st.success(f"✅ {selected_hike['name']} has been added to your bookmarks!")

# Footer
st.markdown("---")
st.markdown("*💡 Tip: Use bookmarks to create your personal hiking bucket list!*")
