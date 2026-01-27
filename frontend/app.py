import streamlit as st
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Kilele Hiking Trails",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown("""
    <style>
    .hike-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #2e7d32;
    }
    .hike-title {
        color: #1b5e20;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .hike-location {
        color: #666;
        font-size: 16px;
        margin-bottom: 15px;
    }
    .difficulty-easy { color: #4caf50; font-weight: bold; }
    .difficulty-moderate { color: #ff9800; font-weight: bold; }
    .difficulty-hard { color: #f44336; font-weight: bold; }
    .difficulty-extreme { color: #9c27b0; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def get_difficulty_class(difficulty):
    """Return CSS class for difficulty level"""
    return f"difficulty-{difficulty.lower()}"

def fetch_hikes(difficulty=None):
    """Fetch hikes from the API"""
    try:
        params = {}
        if difficulty and difficulty != "All":
            params['difficulty'] = difficulty
        
        response = requests.get(f"{API_BASE_URL}/hikes", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Make sure the FastAPI server is running at http://localhost:8000")
        return []
    except Exception as e:
        st.error(f"❌ Error fetching hikes: {str(e)}")
        return []

def display_hike_card(hike):
    """Display a single hike in a card format"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### 🏔️ {hike['name']}")
            st.markdown(f"📍 *{hike['location']}*")
        
        with col2:
            difficulty_class = get_difficulty_class(hike['difficulty'])
            st.markdown(f"<span class='{difficulty_class}'>{hike['difficulty']}</span>", unsafe_allow_html=True)
        
        # Details in expandable section
        with st.expander("View Details"):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Distance", f"{hike['distance_km']} km")
            with col_b:
                st.metric("Duration", f"{hike['estimated_duration_hours']} hrs")
            with col_c:
                if hike.get('elevation_gain_m'):
                    st.metric("Elevation Gain", f"{hike['elevation_gain_m']} m")
            
            if hike.get('description'):
                st.write("**Description:**")
                st.write(hike['description'])
            
            if hike.get('trail_type'):
                st.write(f"**Trail Type:** {hike['trail_type']}")
            
            if hike.get('best_season'):
                st.write(f"**Best Season:** {hike['best_season']}")
            
            if hike.get('latitude') and hike.get('longitude'):
                st.write(f"**Coordinates:** {hike['latitude']}, {hike['longitude']}")
        
        st.markdown("---")

def main():
    # Header
    st.title("🏔️ Kilele Hiking Trails")
    st.markdown("*Discover the best hiking trails in Kenya*")
    st.markdown("")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    difficulty_options = ["All", "Easy", "Moderate", "Hard", "Extreme"]
    selected_difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        difficulty_options,
        index=0
    )
    
    # Sort options
    sort_by = st.sidebar.selectbox(
        "Sort By",
        ["Name", "Distance", "Duration", "Difficulty"]
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 About")
    st.sidebar.info(
        "This app showcases hiking trails across Kenya. "
        "Use the filters to find your perfect adventure!"
    )
    
    # Fetch and display hikes
    with st.spinner("Loading hikes..."):
        hikes = fetch_hikes(selected_difficulty)
    
    if not hikes:
        if selected_difficulty != "All":
            st.warning(f"No hikes found with difficulty: {selected_difficulty}")
        else:
            st.info("Start the backend server to see hiking trails!")
        return
    
    # Sort hikes
    if sort_by == "Name":
        hikes.sort(key=lambda x: x['name'])
    elif sort_by == "Distance":
        hikes.sort(key=lambda x: x['distance_km'])
    elif sort_by == "Duration":
        hikes.sort(key=lambda x: x['estimated_duration_hours'])
    elif sort_by == "Difficulty":
        difficulty_order = {"Easy": 1, "Moderate": 2, "Hard": 3, "Extreme": 4}
        hikes.sort(key=lambda x: difficulty_order.get(x['difficulty'], 5))
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trails", len(hikes))
    with col2:
        avg_distance = sum(h['distance_km'] for h in hikes) / len(hikes)
        st.metric("Avg Distance", f"{avg_distance:.1f} km")
    with col3:
        avg_duration = sum(h['estimated_duration_hours'] for h in hikes) / len(hikes)
        st.metric("Avg Duration", f"{avg_duration:.1f} hrs")
    
    st.markdown("---")
    
    # Display hikes
    for hike in hikes:
        display_hike_card(hike)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using FastAPI & Streamlit | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
