"""
Plan Future Hikes - Schedule hikes with driving directions and waypoints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from auth import is_authenticated, get_current_user, restore_session_from_storage
from services import (
    get_all_hikes, get_hike, create_planned_hike, 
    get_user_planned_hikes, update_planned_hike_status,
    add_waypoint_to_planned_hike, delete_planned_hike
)
from nature_theme import apply_nature_theme
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Plan Hike", page_icon="🗓️", layout="wide")
apply_nature_theme()

# Restore session
restore_session_from_storage()

# Mobile responsive CSS
st.markdown("""
    <style>
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
    }
    
    .planned-hike-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #4a6fa5;
    }
    
    .status-planned {
        background: #4a6fa5;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    
    .status-completed {
        background: #51cf66;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    
    .status-cancelled {
        background: #ff6b6b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    
    .waypoint-item {
        background: #f0f7ff;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #4a6fa5;
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to plan hikes")
    if st.button("Go to Login"):
        st.switch_page("pages/0_🔐_Login.py")
    st.stop()

user = get_current_user()

# Header
st.title("🗓️ Plan Your Hike")
st.markdown("**Schedule future hikes with driving directions and waypoints**")

# Tabs
tab1, tab2 = st.tabs(["📅 Plan New Hike", "📋 My Planned Hikes"])

# TAB 1: Plan New Hike
with tab1:
    st.markdown("### Schedule a New Hike")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Select trail
        all_hikes = get_all_hikes()
        hike_options = {f"{h['name']} - {h['location']}": h['id'] for h in all_hikes}
        
        selected_hike_name = st.selectbox(
            "Select Trail",
            list(hike_options.keys()),
            help="Choose the trail you want to hike"
        )
        
        selected_hike_id = hike_options[selected_hike_name]
        selected_hike = get_hike(selected_hike_id)
        
        # Date and time
        col_date, col_time = st.columns(2)
        
        with col_date:
            hike_date = st.date_input(
                "Hike Date",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=7)
            )
        
        with col_time:
            hike_time = st.time_input(
                "Start Time",
                value=datetime.now().replace(hour=7, minute=0).time()
            )
        
        # Transport mode
        transport_mode = st.radio(
            "Transport Mode",
            ["self_drive", "carpool", "public_transport"],
            format_func=lambda x: {
                "self_drive": "🚗 Self Drive",
                "carpool": "👥 Carpool",
                "public_transport": "🚌 Public Transport"
            }[x],
            horizontal=True
        )
        
        # Meeting point
        meeting_point = st.text_input(
            "Meeting Point (optional)",
            placeholder="e.g., Nairobi CBD, Shell Petrol Station"
        )
        
        # Notes
        notes = st.text_area(
            "Notes",
            placeholder="Add any additional details (gear to bring, group size, etc.)",
            height=100
        )
    
    with col2:
        # Trail preview
        st.markdown("#### Trail Details")
        st.image("🏔️", use_column_width=False)
        st.markdown(f"**{selected_hike['name']}**")
        st.caption(f"📍 {selected_hike['location']}")
        st.caption(f"🎯 {selected_hike['difficulty']}")
        st.caption(f"📏 {selected_hike['distance_km']} km")
        st.caption(f"⏱️ ~{selected_hike['estimated_duration_hours']} hours")
    
    # Create button
    st.markdown("---")
    if st.button("📅 Schedule Hike", type="primary", use_container_width=True):
        # Combine date and time
        planned_datetime = datetime.combine(hike_date, hike_time)
        
        result = create_planned_hike(
            user_id=user['id'],
            hike_id=selected_hike_id,
            planned_date=planned_datetime,
            transport_mode=transport_mode,
            notes=notes,
            meeting_point=meeting_point
        )
        
        if 'error' not in result:
            st.success("✅ Hike scheduled successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ {result['error']}")

# TAB 2: My Planned Hikes
with tab2:
    st.markdown("### Your Upcoming Hikes")
    
    # Filter by status
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "planned", "completed", "cancelled"],
        format_func=lambda x: {
            "All": "📋 All",
            "planned": "🗓️ Planned",
            "completed": "✅ Completed",
            "cancelled": "❌ Cancelled"
        }[x]
    )
    
    # Load planned hikes
    if status_filter == "All":
        planned_hikes = get_user_planned_hikes(user['id'])
    else:
        planned_hikes = get_user_planned_hikes(user['id'], status=status_filter)
    
    if not planned_hikes:
        st.info("📭 No planned hikes yet. Schedule your first hike in the 'Plan New Hike' tab!")
    else:
        for hike in planned_hikes:
            with st.container():
                st.markdown('<div class="planned-hike-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Title and status
                    status_class = f"status-{hike['status']}"
                    st.markdown(f"""
                        <h3 style="margin: 0;">{hike['hike_name']}</h3>
                        <p style="margin: 0.5rem 0;">📍 {hike['hike_location']}</p>
                        <span class="{status_class}">{hike['status'].upper()}</span>
                    """, unsafe_allow_html=True)
                    
                    # Date and transport
                    planned_date = datetime.fromisoformat(hike['planned_date'])
                    st.markdown(f"""
                        📅 **Date:** {planned_date.strftime('%B %d, %Y at %I:%M %p')}  
                        🚗 **Transport:** {hike['transport_mode'].replace('_', ' ').title()}
                    """)
                    
                    if hike['meeting_point']:
                        st.markdown(f"📍 **Meeting Point:** {hike['meeting_point']}")
                    
                    if hike['notes']:
                        with st.expander("📝 Notes"):
                            st.write(hike['notes'])
                
                with col2:
                    # Action buttons
                    if hike['status'] == 'planned':
                        if st.button("✅ Complete", key=f"complete_{hike['id']}"):
                            update_planned_hike_status(hike['id'], 'completed')
                            st.success("Marked as completed!")
                            st.rerun()
                        
                        if st.button("❌ Cancel", key=f"cancel_{hike['id']}"):
                            update_planned_hike_status(hike['id'], 'cancelled')
                            st.info("Hike cancelled")
                            st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{hike['id']}"):
                        delete_planned_hike(hike['id'])
                        st.warning("Hike deleted")
                        st.rerun()
                
                # Map with driving directions
                if hike['status'] == 'planned' and hike['hike_latitude'] and hike['hike_longitude']:
                    with st.expander("🗺️ View Map & Add Waypoints"):
                        # Create map centered on trail
                        m = folium.Map(
                            location=[hike['hike_latitude'], hike['hike_longitude']],
                            zoom_start=10
                        )
                        
                        # Add trail marker
                        folium.Marker(
                            [hike['hike_latitude'], hike['hike_longitude']],
                            popup=f"<b>{hike['hike_name']}</b>",
                            tooltip=hike['hike_name'],
                            icon=folium.Icon(color='red', icon='mountain', prefix='fa')
                        ).add_to(m)
                        
                        # Add existing waypoints
                        if hike['driving_directions']:
                            for idx, waypoint in enumerate(hike['driving_directions'], 1):
                                folium.Marker(
                                    [waypoint['lat'], waypoint['lng']],
                                    popup=f"<b>Waypoint {idx}:</b> {waypoint.get('name', 'Stop')}",
                                    tooltip=f"Waypoint {idx}",
                                    icon=folium.Icon(color='blue', icon='info-sign')
                                ).add_to(m)
                        
                        # Display map
                        st_folium(m, width=700, height=400)
                        
                        # Add waypoint form
                        st.markdown("#### Add Waypoint/Stop")
                        col_wp1, col_wp2, col_wp3 = st.columns(3)
                        
                        with col_wp1:
                            wp_name = st.text_input("Name", key=f"wp_name_{hike['id']}", placeholder="e.g., Gas Station")
                        
                        with col_wp2:
                            wp_lat = st.number_input("Latitude", key=f"wp_lat_{hike['id']}", format="%.6f")
                        
                        with col_wp3:
                            wp_lng = st.number_input("Longitude", key=f"wp_lng_{hike['id']}", format="%.6f")
                        
                        if st.button("📍 Add Waypoint", key=f"add_wp_{hike['id']}"):
                            if wp_lat and wp_lng:
                                waypoint = {
                                    "name": wp_name or "Stop",
                                    "lat": wp_lat,
                                    "lng": wp_lng
                                }
                                add_waypoint_to_planned_hike(hike['id'], waypoint)
                                st.success("Waypoint added!")
                                st.rerun()
                            else:
                                st.error("Please enter valid coordinates")
                        
                        # Existing waypoints list
                        if hike['driving_directions']:
                            st.markdown("#### Saved Waypoints")
                            for idx, wp in enumerate(hike['driving_directions'], 1):
                                st.markdown(f"""
                                    <div class="waypoint-item">
                                        <b>Stop {idx}:</b> {wp.get('name', 'Waypoint')}<br>
                                        <small>📍 {wp['lat']:.6f}, {wp['lng']:.6f}</small>
                                    </div>
                                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

# Footer tips
st.markdown("---")
st.markdown("### 🚗 Self-Drive Tips")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Before You Go:**
    - 🔧 Check vehicle condition
    - ⛽ Full tank of fuel
    - 🗺️ Download offline maps
    - 📱 Share route with family
    """)

with col2:
    st.markdown("""
    **On the Road:**
    - 🚗 Start early (6-7 AM)
    - ☕ Plan rest stops
    - 📍 Save key waypoints
    - 🚨 Emergency contacts ready
    """)

with col3:
    st.markdown("""
    **Recommended Apps:**
    - 📱 Google Maps (offline)
    - 🧭 Maps.me
    - 📡 Garmin Explore
    - 🚗 Waze (traffic alerts)
    """)

st.info("""
💡 **Pro Tip:** For remote trails like Mount Kenya or Aberdares, download offline maps 
and carry a physical map as backup. Cell service can be unreliable in highland areas.
""")
