import streamlit as st
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_all_hikes, create_session, get_user_sessions
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme
from offline_cache import (
    prepare_offline_hike_ui, 
    show_offline_indicator, 
    OfflineCache,
    check_internet_connection
)

init_database()

st.set_page_config(page_title="Track Hike - Kilele", page_icon="📍", layout="wide")
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to track your hikes")
    st.info("👈 Navigate to the Login page to access this feature")
    st.stop()

st.title("📍 Track Your Hike")
st.markdown("Start tracking your adventure in real-time!")

# Show offline indicator if no internet
is_offline = show_offline_indicator()

st.markdown("---")

# Fetch available hikes
@st.cache_data(ttl=300)
def fetch_all_hikes():
    try:
        return get_all_hikes()
    except Exception as e:
        st.error(f"Error fetching hikes: {e}")
        return []

def fetch_active_sessions():
    try:
        user = get_current_user()
        if user:
            all_sessions = get_user_sessions(user['id'])
            return [s for s in all_sessions if s.get('status') == 'in_progress']
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def start_hike(hike_id):
    try:
        user = get_current_user()
        session_data = {
            "hike_id": hike_id,
            "status": "in_progress"
        }
        session = create_session(user['id'], session_data)
        if session:
            return True, session
        return False, "Failed to start session"
    except Exception as e:
        return False, str(e)

def update_session(session_id, data):
    try:
        from database import get_db
        from models import HikeSession
        with get_db() as db:
            session = db.query(HikeSession).filter(HikeSession.id == session_id).first()
            if session:
                for key, value in data.items():
                    setattr(session, key, value)
                db.commit()
                return True, {"id": session.id}
            return False, "Session not found"
    except Exception as e:
        return False, str(e)

# Check for active sessions
active_sessions = fetch_active_sessions()

if active_sessions:
    st.success("🏃 You have active hikes in progress!")
    
    for session in active_sessions:
        st.write("### 🎯 Active Hike")
        
        # Hike info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏔️ Trail", session.get('hike_name', 'Unknown'))
        with col2:
            duration = session.get('duration_hours') or 0
            st.metric("⏱️ Duration", f"{duration:.1f} hrs")
        with col3:
            distance = session.get('distance_covered_km') or 0
            st.metric("🚶 Distance", f"{distance:.2f} km")
        
        st.write(f"**Started:** {session['started_at'][:16]}")
        
        # Update form
        with st.expander("📝 Update Progress", expanded=True):
            with st.form(f"update_form_{session['id']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_distance = st.number_input(
                        "Distance Covered (km)",
                        value=float(session.get('distance_covered_km') or 0),
                        min_value=0.0,
                        step=0.1
                    )
                    new_elevation = st.number_input(
                        "Elevation Gain (m)",
                        value=float(session.get('elevation_gain_m') or 0),
                        min_value=0.0,
                        step=10.0
                    )
                
                with col2:
                    new_duration = st.number_input(
                        "Duration (hours)",
                        value=float(session.get('duration_hours') or 0),
                        min_value=0.0,
                        step=0.1
                    )
                
                notes = st.text_area("Notes", value=session.get('notes', '') or '')
                
                col_a, col_b = st.columns(2)
                with col_a:
                    update_btn = st.form_submit_button("💾 Update Progress", use_container_width=True)
                with col_b:
                    complete_btn = st.form_submit_button("✅ Complete Hike", use_container_width=True)
                
                if update_btn:
                    update_data = {
                        "distance_covered_km": new_distance,
                        "elevation_gain_m": new_elevation,
                        "duration_hours": new_duration,
                        "notes": notes
                    }
                    
                    success, result = update_session(session['id'], update_data)
                    if success:
                        st.success("✅ Progress updated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
                
                if complete_btn:
                    # Complete the hike
                    st.write("### ⭐ Rate Your Hike")
                    rating = st.slider("Rating", 1, 5, 3)
                    
                    complete_data = {
                        "distance_covered_km": new_distance,
                        "elevation_gain_m": new_elevation,
                        "duration_hours": new_duration,
                        "notes": notes,
                        "status": "completed",
                        "ended_at": datetime.utcnow()
                    }
                    
                    success, result = update_session(session['id'], complete_data)
                    if success:
                        st.success("🎉 Hike completed! Great job!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
        
        st.markdown("---")

else:
    st.info("👋 No active hikes. Start tracking a new adventure below!")

# Start New Hike
st.write("### 🚀 Start New Hike")

hikes = fetch_all_hikes()

if hikes:
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        difficulty_filter = st.selectbox(
            "Filter by Difficulty",
            ["All"] + list(set(h['difficulty'] for h in hikes))
        )
    with col2:
        search = st.text_input("🔍 Search trails", placeholder="Type to search...")
    
    # Filter hikes
    filtered_hikes = hikes
    if difficulty_filter != "All":
        filtered_hikes = [h for h in filtered_hikes if h['difficulty'] == difficulty_filter]
    if search:
        filtered_hikes = [h for h in filtered_hikes if search.lower() in h['name'].lower()]
    
    # Display hikes
    for hike in filtered_hikes:
        with st.expander(f"🏔️ {hike['name']} - {hike['difficulty']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Location:** {hike['location']}")
                st.write(f"**Distance:** {hike['distance_km']} km")
                st.write(f"**Elevation Gain:** {hike['elevation_gain_m']} m")
                st.write(f"**Est. Duration:** {hike['estimated_duration_hours']} hours")
                st.write(f"**Trail Type:** {hike['trail_type']}")
                st.write(f"**Best Season:** {hike['best_season']}")
            
            with col2:
                if st.button(f"▶️ Start Tracking", key=f"start_{hike['id']}", use_container_width=True):
                    success, result = start_hike(hike['id'])
                    if success:
                        st.success(f"✅ Started tracking {hike['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
            
            # Offline preparation feature
            st.markdown("---")
            prepare_offline_hike_ui(hike['id'], hike)
else:
    st.warning("No hikes available")

# Instructions
st.markdown("---")
st.info("""
### 📱 How to Track Your Hike

1. **Start Tracking:** Select a trail and click "Start Tracking"
2. **Update Progress:** Periodically update your GPS location, distance, and time
3. **Add Notes:** Record interesting observations or challenges
4. **Complete:** When finished, mark the hike as complete and rate your experience

💡 **Tips:**
- Update your location at key points (summit, waterfall, viewpoints)
- Track distance using your phone's GPS or fitness app
- Take breaks and stay hydrated!
- Share your adventure on social media 📸
""")
