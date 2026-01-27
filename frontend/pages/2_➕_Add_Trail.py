import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import create_hike, get_all_hikes
from nature_theme import apply_nature_theme

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="Add Trail - Kilele",
    page_icon="➕",
    layout="wide"
)
apply_nature_theme()

def create_hike(hike_data):
    """Create a new hike via database"""
    try:
        result = create_hike(hike_data)
        return True, result
    except Exception as e:
        return False, str(e)

def main():
    st.title("➕ Add New Hiking Trail")
    st.markdown("*Contribute a new trail to the Kilele collection*")
    st.markdown("---")
    
    with st.form("add_trail_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Basic Information")
            name = st.text_input("Trail Name *", placeholder="e.g., Mount Longonot Crater Trek")
            location = st.text_input("Location *", placeholder="e.g., Mount Longonot National Park, Rift Valley")
            
            difficulty = st.selectbox("Difficulty *", ["Easy", "Moderate", "Hard", "Extreme"])
            
            col_a, col_b = st.columns(2)
            with col_a:
                distance_km = st.number_input("Distance (km) *", min_value=0.1, value=5.0, step=0.1)
            with col_b:
                duration = st.number_input("Duration (hours) *", min_value=0.1, value=2.0, step=0.1)
            
            elevation_gain = st.number_input("Elevation Gain (meters)", min_value=0, value=0, step=10)
            
            trail_type = st.selectbox("Trail Type", ["Loop", "Out and Back", "Point to Point"])
            
        with col2:
            st.subheader("📝 Details")
            description = st.text_area(
                "Description",
                height=150,
                placeholder="Describe the trail, what hikers can expect, highlights, etc."
            )
            
            best_season = st.text_input(
                "Best Season",
                placeholder="e.g., June-September, December-February"
            )
            
            st.subheader("📍 GPS Coordinates")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=-0.0236, step=0.0001, format="%.4f")
            with col_lon:
                longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=37.9062, step=0.0001, format="%.4f")
            
            st.info("💡 Tip: Use Google Maps to find coordinates. Right-click on a location and copy the coordinates.")
            
            image_url = st.text_input("Image URL (optional)", placeholder="https://example.com/image.jpg")
        
        # Submit button
        st.markdown("---")
        col_submit, col_cancel = st.columns([1, 4])
        with col_submit:
            submitted = st.form_submit_button("✅ Add Trail", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not name or not location:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                # Prepare data
                hike_data = {
                    "name": name,
                    "location": location,
                    "difficulty": difficulty,
                    "distance_km": float(distance_km),
                    "elevation_gain_m": float(elevation_gain) if elevation_gain else None,
                    "estimated_duration_hours": float(duration),
                    "description": description if description else None,
                    "trail_type": trail_type,
                    "best_season": best_season if best_season else None,
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "image_url": image_url if image_url else None
                }
                
                # Submit to API
                with st.spinner("Adding trail..."):
                    success, result = create_hike(hike_data)
                
                if success:
                    st.success(f"✅ Successfully added trail: **{name}**!")
                    st.balloons()
                    st.info("🔄 Go to the Home page to see your new trail!")
                    
                    # Display created trail
                    with st.expander("View Created Trail"):
                        st.json(result)
                else:
                    st.error(f"❌ Failed to add trail: {result}")
    
    # Existing trails count
    st.markdown("---")
    try:
        trails = get_all_hikes()
        trails_count = len(trails)
        st.info(f"📊 Currently **{trails_count}** trails in the database")
    except:
        pass
    
    # Tips section
    st.markdown("---")
    st.markdown("### 💡 Tips for Adding Trails")
    col_tip1, col_tip2 = st.columns(2)
    
    with col_tip1:
        st.markdown("""
        **Good Trail Descriptions Include:**
        - Terrain type (rocky, forested, etc.)
        - Notable landmarks or viewpoints
        - Wildlife you might encounter
        - Difficulty notes (steep sections, etc.)
        - Water availability
        """)
    
    with col_tip2:
        st.markdown("""
        **Finding GPS Coordinates:**
        1. Open Google Maps
        2. Right-click on the trailhead
        3. Click the coordinates to copy
        4. Paste here!
        
        Or use your phone's GPS while on the trail.
        """)

if __name__ == "__main__":
    main()
