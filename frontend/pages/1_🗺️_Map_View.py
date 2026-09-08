import streamlit as st
import folium
from streamlit_folium import st_folium
import sys
import os
from html import escape

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_all_hikes
from nature_theme import apply_nature_theme

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="Trail Map - Kilele",
    page_icon="🗺️",
    layout="wide"
)
apply_nature_theme()

@st.cache_data(ttl=300)
def fetch_hikes():
    """Fetch all hikes from database"""
    try:
        return get_all_hikes()
    except Exception as e:
        st.error(f"Error fetching hikes: {str(e)}")
        return []

def create_difficulty_color(difficulty):
    """Return marker color based on difficulty"""
    colors = {
        'Easy': 'green',
        'Moderate': 'orange',
        'Hard': 'red',
        'Extreme': 'purple'
    }
    return colors.get(difficulty, 'blue')

def main():
    st.title("🗺️ Trail Location Map")
    st.markdown("*Interactive map showing all hiking trails across Kenya*")
    
    # Fetch hikes
    hikes = fetch_hikes()
    
    if not hikes:
        st.warning("No trails available to display on map")
        return
    
    # Filter trails with valid coordinates
    trails_with_coords = [h for h in hikes if h.get('latitude') is not None and h.get('longitude') is not None]
    
    if not trails_with_coords:
        st.warning("No trails have GPS coordinates yet")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Map Filters")
    
    difficulty_filter = st.sidebar.multiselect(
        "Show Difficulties",
        ["Easy", "Moderate", "Hard", "Extreme"],
        default=["Easy", "Moderate", "Hard", "Extreme"]
    )
    
    # Filter by difficulty
    filtered_trails = [h for h in trails_with_coords if h['difficulty'] in difficulty_filter]
    
    # Calculate map center (center of Kenya approximately)
    if filtered_trails:
        avg_lat = sum(h['latitude'] for h in filtered_trails) / len(filtered_trails)
        avg_lon = sum(h['longitude'] for h in filtered_trails) / len(filtered_trails)
    else:
        avg_lat, avg_lon = -0.0236, 37.9062  # Nairobi
    
    # Create map
    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Add markers for each trail
    for hike in filtered_trails:
        color = create_difficulty_color(hike['difficulty'])
        
        popup_html = f"""
        <div style="width: 210px; max-width: 100%; overflow-wrap: anywhere;">
            <h4 style="color: #2e7d32;">{escape(hike['name'])}</h4>
            <p><strong>📍 Location:</strong> {escape(hike['location'])}</p>
            <p><strong>⚠️ Difficulty:</strong> <span style="color: {color};">{hike['difficulty']}</span></p>
            <p><strong>📏 Distance:</strong> {hike['distance_km']} km</p>
            <p><strong>⏱️ Duration:</strong> {hike['estimated_duration_hours']} hours</p>
            {f"<p><strong>⛰️ Elevation:</strong> {hike['elevation_gain_m']} m</p>" if hike.get('elevation_gain_m') else ""}
            <p><em>{escape((hike.get('description') or '')[:150])}...</em></p>
        </div>
        """
        
        folium.Marker(
            location=[hike['latitude'], hike['longitude']],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=escape(hike['name']),
            icon=folium.Icon(color=color, icon='mountain', prefix='fa')
        ).add_to(m)
    
    # Display map stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🗺️ Trails on Map", len(filtered_trails))
    with col2:
        total_dist = sum(h['distance_km'] for h in filtered_trails)
        st.metric("📏 Total Distance", f"{total_dist:.1f} km")
    with col3:
        total_time = sum(h['estimated_duration_hours'] for h in filtered_trails)
        st.metric("⏱️ Total Time", f"{total_time:.1f} hrs")
    
    # Display the map
    st.markdown("---")
    st_folium(m, use_container_width=True, height=480, returned_objects=[], key="trail_map")
    
    # Legend
    st.markdown("---")
    st.markdown("### 🏷️ Legend")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🟢 **Easy**")
    with col2:
        st.markdown("🟠 **Moderate**")
    with col3:
        st.markdown("🔴 **Hard**")
    with col4:
        st.markdown("🟣 **Extreme**")
    
    # Trail list
    st.markdown("---")
    st.markdown("### 📋 Trails on Map")
    for hike in filtered_trails:
        with st.expander(f"{hike['name']} - {hike['difficulty']}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Location:** {hike['location']}")
                st.write(f"**Distance:** {hike['distance_km']} km")
                st.write(f"**Duration:** {hike['estimated_duration_hours']} hours")
            with col_b:
                if hike.get('elevation_gain_m'):
                    st.write(f"**Elevation Gain:** {hike['elevation_gain_m']} m")
                st.write(f"**Coordinates:** {hike['latitude']}, {hike['longitude']}")
                st.markdown(f"[Open in Google Maps](https://www.google.com/maps?q={hike['latitude']},{hike['longitude']})")

if __name__ == "__main__":
    main()
