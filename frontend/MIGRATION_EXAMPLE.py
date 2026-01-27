"""
EXAMPLE: How to convert API-based pages to direct database access
This shows the pattern for updating all 14 page files

BEFORE (API-based):
    import requests
    response = requests.get(f"{API_BASE_URL}/hikes")
    hikes = response.json()

AFTER (Direct database):
    from services import get_all_hikes
    hikes = get_all_hikes()
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import the new modules
from database import init_database
from services import get_all_hikes, get_hike, create_bookmark, get_user_bookmarks
from auth import is_authenticated, get_current_user

# Page configuration
st.set_page_config(
    page_title="Kilele Hiking Trails - Updated",
    page_icon="🏔️",
    layout="wide"
)

# Initialize database (do this once at startup)
init_database()

# Custom CSS (same as before)
st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        padding: 60px 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .hero-title {
        font-size: 52px;
        font-weight: bold;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .difficulty-easy { color: #4caf50; font-weight: bold; }
    .difficulty-moderate { color: #ff9800; font-weight: bold; }
    .difficulty-hard { color: #f44336; font-weight: bold; }
    .difficulty-extreme { color: #9c27b0; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def main():
    # Hero Section
    st.markdown("""
        <div class='hero-section'>
            <div class='hero-title'>🏔️ KILELE EXPLORERS</div>
            <div>Discover Kenya's Most Beautiful Hiking Trails</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Welcome authenticated users
    if is_authenticated():
        user = get_current_user()
        st.success(f"👋 Welcome back, **{user['username']}**!")
    else:
        st.info("🔐 Login to unlock personalized features!")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    difficulty_options = ["All", "Easy", "Moderate", "Hard", "Extreme"]
    selected_difficulty = st.sidebar.selectbox("Difficulty", difficulty_options)
    
    # Fetch hikes using direct database access (NO MORE API CALLS)
    with st.spinner("🔄 Loading trails..."):
        difficulty_filter = None if selected_difficulty == "All" else selected_difficulty
        hikes = get_all_hikes(difficulty=difficulty_filter)
    
    if not hikes:
        st.warning("⚠️ No trails found. Check database initialization.")
        return
    
    # Display statistics
    st.markdown("## 📊 Trail Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trails", len(hikes))
    with col2:
        avg_distance = sum(h['distance_km'] for h in hikes) / len(hikes)
        st.metric("Avg Distance", f"{avg_distance:.1f} km")
    with col3:
        total_distance = sum(h['distance_km'] for h in hikes)
        st.metric("Total Distance", f"{total_distance:.0f} km")
    with col4:
        st.metric("Active Hikers", "5K+")
    
    st.markdown("---")
    
    # Display trails
    st.markdown("## 🏔️ Available Trails")
    
    for hike in hikes:
        with st.container():
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                if hike.get('image_url'):
                    st.image(hike['image_url'])
            
            with col_info:
                st.markdown(f"### 🏔️ {hike['name']}")
                st.markdown(f"📍 {hike['location']}")
                
                difficulty_class = f"difficulty-{hike['difficulty'].lower()}"
                st.markdown(
                    f"**Difficulty:** <span class='{difficulty_class}'>{hike['difficulty']}</span>",
                    unsafe_allow_html=True
                )
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Distance", f"{hike['distance_km']} km")
                with col_b:
                    st.metric("Duration", f"{hike['estimated_duration_hours']} hrs")
                with col_c:
                    if hike.get('elevation_gain_m'):
                        st.metric("Elevation", f"{hike['elevation_gain_m']} m")
                
                if hike.get('description'):
                    st.write(hike['description'][:200] + "...")
                
                # Bookmark button (authenticated users only)
                if is_authenticated():
                    if st.button(f"❤️ Bookmark", key=f"bookmark_{hike['id']}"):
                        try:
                            user = get_current_user()
                            create_bookmark(user['id'], hike['id'])
                            st.success("✅ Bookmarked!")
                        except ValueError as e:
                            st.info(str(e))
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            st.markdown("---")
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        df = pd.DataFrame(hikes)
        difficulty_counts = df['difficulty'].value_counts().reset_index()
        difficulty_counts.columns = ['Difficulty', 'Count']
        
        fig = px.pie(
            difficulty_counts, 
            values='Count', 
            names='Difficulty',
            title='Trail Difficulty Distribution',
            color='Difficulty',
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        fig2 = px.scatter(
            df, 
            x='distance_km', 
            y='estimated_duration_hours',
            color='difficulty',
            title='Distance vs Duration',
            labels={
                'distance_km': 'Distance (km)',
                'estimated_duration_hours': 'Duration (hours)'
            },
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            }
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 30px;'>
            <h3 style='color: #2e7d32;'>🏔️ KILELE EXPLORERS</h3>
            <p>Your trusted companion for hiking adventures in Kenya</p>
            <p style='color: #999;'>Built with ❤️ using Streamlit | © 2026</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

"""
CONVERSION CHECKLIST FOR EACH PAGE:

1. Remove these imports:
   ❌ import requests
   ❌ API_BASE_URL configuration

2. Add these imports:
   ✅ from database import init_database
   ✅ from services import (import needed functions)
   ✅ from auth import is_authenticated, get_current_user

3. Replace API calls:
   BEFORE: requests.get(f"{API_BASE_URL}/hikes")
   AFTER:  get_all_hikes()
   
   BEFORE: requests.post(f"{API_BASE_URL}/reviews", json=data, headers={"Authorization": f"Bearer {token}"})
   AFTER:  create_review(user_id=user['id'], hike_id=hike_id, rating=rating, comment=comment)

4. Replace authentication checks:
   BEFORE: if st.session_state.get('authenticated')
   AFTER:  if is_authenticated()
   
   BEFORE: st.session_state.user
   AFTER:  get_current_user()

5. Remove token handling:
   ❌ st.session_state.token
   ❌ headers = {"Authorization": f"Bearer {token}"}

6. Update error handling:
   BEFORE: try/except for network errors
   AFTER:  try/except for database errors (ValueError, etc.)

7. Call init_database() once at the top of each page
"""
