import streamlit as st
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import create_session, get_all_hikes
from auth import is_authenticated, get_current_user
from utils.wearable_parser import WearableDataParser
from nature_theme import apply_nature_theme

init_database()

# Page config
st.set_page_config(page_title="Import from Wearables - Kilele", page_icon="⌚", layout="wide")
apply_nature_theme()

# Check if user is logged in
if not is_authenticated():
    st.warning("⚠️ Please login to import wearable data")
    st.stop()

st.title("⌚ Import from Wearable Devices")
st.markdown("Import your hiking tracks directly from smartwatches and fitness trackers")

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload File", "📱 Supported Devices", "📊 Imported Sessions"])

with tab1:
    st.subheader("Upload Tracking File")
    
    st.markdown("""
        <div class="upload-section">
            <h3>📁 Drag and drop your tracking file</h3>
            <p>Supports GPX, FIT, and TCX formats from all major wearable devices</p>
        </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file from your wearable device",
        type=['gpx', 'fit', 'tcx'],
        help="Export your activity file from your device app (Garmin Connect, Strava, Apple Health, etc.)"
    )
    
    if uploaded_file:
        st.success(f"✅ File selected: **{uploaded_file.name}**")
        
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.info(f"📦 File size: {file_size_mb:.2f} MB")
        
        # Optional: Link to existing hike
        link_to_hike = st.checkbox("Link to an existing trail?", value=False)
        hike_id = None
        
        if link_to_hike:
            try:
                hikes = get_all_hikes()
                if hikes:
                    hike_options = {f"{h['name']} - {h['location']}": h['id'] for h in hikes}
                    selected_hike = st.selectbox("Select trail:", options=list(hike_options.keys()))
                    hike_id = hike_options[selected_hike]
            except:
                st.warning("Could not load trails list")
        
        # Upload button
        if st.button("🚀 Import Data", type="primary", use_container_width=True):
            with st.spinner("Processing your tracking data..."):
                try:
                    # Prepare file for upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    
                    # Add hike_id if selected
                    # Parse the wearable file
                    parsed_data = WearableDataParser.parse_file(uploaded_file)
                    
                    if parsed_data:
                        summary = parsed_data.get("summary", {})
                        
                        # Create a session from the parsed data
                        user = get_current_user()
                        session_data = {
                            "distance_km": summary.get("distance_km", 0),
                            "duration_minutes": summary.get("duration_minutes", 0),
                            "elevation_gain_m": summary.get("elevation_gain_m", 0),
                        }
                        
                        if hike_id:
                            create_session(user['id'], hike_id, **session_data)
                        
                        st.success("✅ File imported successfully!")
                        
                        st.success("🎉 Data imported successfully!")
                        
                        # Display summary
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown(f"### 📊 Import Summary")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("Distance", f"{summary.get('distance_km', 0)} km")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("Elevation Gain", f"{summary.get('elevation_gain_m', 0)} m")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.success("📊 Hiking data imported successfully!")
                        
                        # Show basic statistics
                        if summary.get('center'):
                            st.info(f"**Location:** Lat {summary['center']['latitude']:.4f}, Lon {summary['center']['longitude']:.4f}")
                    else:
                        st.error("❌ Failed to parse wearable file")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    st.subheader("📱 Supported Wearable Devices")
    
    st.markdown("### Supported File Formats")
    st.markdown("""
    Import hiking data from your favorite wearable devices:
    
    **Supported Formats:**
    - 📍 **GPX** - GPS Exchange Format (Garmin, Strava, most devices)
    - ⌚ **FIT** - Flexible and Interoperable Data Transfer (Garmin devices)
    - 🏃 **TCX** - Training Center XML (Garmin Connect, Strava)
    
    **Supported Devices:**
    - Garmin (Forerunner, Fenix, Edge series)
    - Apple Watch (export via Strava or other apps)
    - Suunto watches
    - Polar devices
    - Fitbit (via third-party export)
    - Any device that exports GPX, FIT, or TCX files
    
    ### How to Export Your Data
    
    **From Garmin Connect:**
    1. Log in to Garmin Connect
    2. Select your activity
    3. Click the gear icon ⚙️
    4. Export to GPX or FIT format
    
    **From Strava:**
    1. Open your activity
    2. Click the three dots (...)
    3. Export GPX or TCX
    
    **From Apple Watch (via Strava):**
    1. Sync your workout to Strava
    2. Export from Strava as described above
    """)

with tab3:
    st.subheader("📊 Your Imported Sessions")
    st.info("View your imported wearable data sessions here after uploading files in the Import tab")

# Footer
st.divider()
st.markdown("""
    ### 💡 Tips
    - **Export regularly:** Save your hikes from your device app after each trek
    - **Battery life:** GPS tracking can drain battery - bring a power bank for long hikes
    - **Signal:** GPS works without cell signal, but may take longer to acquire satellites
    - **Accuracy:** Route accuracy depends on your device's GPS quality and terrain
""")
