import streamlit as st
import json
import sys
import os
import streamlit.components.v1 as components

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
tab1, tab2, tab3, tab4 = st.tabs(["🔵 Bluetooth Connect", "📤 Upload File", "📱 Supported Devices", "📊 Imported Sessions"])

with tab1:
    st.subheader("🔵 Connect via Bluetooth")
    
    st.markdown("""
        <div class="bluetooth-section">
            <h3>📡 Connect Your Wearable Device</h3>
            <p>Connect directly to your smartwatch or fitness tracker via Bluetooth to sync your hiking data in real-time</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Requirements:**
    - Your device must support Bluetooth Low Energy (BLE)
    - Your browser must support Web Bluetooth (Chrome, Edge, Opera)
    - Your wearable must be in pairing mode
    """)
    
    # Bluetooth connection component
    bluetooth_html = """
    <div id="bluetooth-container">
        <button id="scanBtn" style="
            background: linear-gradient(135deg, #4a6fa5 0%, #5b7ea8 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
            width: 100%;
            margin: 10px 0;
        ">
            🔍 Scan for Devices
        </button>
        <div id="deviceList" style="
            margin-top: 15px;
            display: none;
        "></div>
        <div id="status" style="
            margin-top: 15px;
            padding: 15px;
            border-radius: 8px;
            background: #e3f2fd;
            display: none;
        "></div>
        <div id="deviceInfo" style="
            margin-top: 15px;
            padding: 20px;
            border-radius: 8px;
            background: white;
            border: 2px solid #90caf9;
            display: none;
        "></div>
    </div>

    <script>
        let bluetoothDevice = null;
        let heartRateCharacteristic = null;
        let discoveredDevices = [];

        document.getElementById('scanBtn').addEventListener('click', async () => {
            try {
                const statusDiv = document.getElementById('status');
                const deviceListDiv = document.getElementById('deviceList');
                const scanBtn = document.getElementById('scanBtn');
                
                // Detect Brave browser
                const isBrave = navigator.brave && typeof navigator.brave.isBrave === 'function';
                
                // Check if Web Bluetooth is supported
                if (!navigator.bluetooth) {
                    statusDiv.style.display = 'block';
                    statusDiv.style.background = '#f8d7da';
                    
                    if (isBrave) {
                        statusDiv.innerHTML = `
                            <strong>❌ Web Bluetooth is disabled in Brave</strong><br><br>
                            <strong>To enable Bluetooth in Brave:</strong><br>
                            1. Click the <strong>Brave icon</strong> (lion) in the address bar<br>
                            2. Click <strong>Advanced Controls</strong><br>
                            3. Enable <strong>Web Bluetooth</strong><br>
                            4. Refresh this page and try again<br><br>
                            <em>Or use Chrome/Edge for easier setup</em>
                        `;
                    } else {
                        statusDiv.innerHTML = '❌ <strong>Web Bluetooth not supported</strong><br>Please use Chrome, Edge, or Opera browser.<br>Your current browser does not support Bluetooth connectivity.';
                    }
                    return;
                }
                
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#fff3cd';
                statusDiv.innerHTML = '🔍 Opening device picker... Please select a device from the list.';
                
                // Request Bluetooth device - this will show a list of available devices
                bluetoothDevice = await navigator.bluetooth.requestDevice({
                    acceptAllDevices: true,
                    optionalServices: [
                        'heart_rate',
                        'battery_service', 
                        'device_information',
                        'cycling_speed_and_cadence',
                        'running_speed_and_cadence',
                        'generic_access'
                    ]
                });
                
                // Device was selected, now connect
                await connectToDevice(bluetoothDevice);
                
            } catch (error) {
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                
                if (error.name === 'NotFoundError') {
                    statusDiv.style.background = '#fff3cd';
                    statusDiv.innerHTML = 'ℹ️ No device was selected. Click the button above to try again.';
                } else if (error.name === 'SecurityError') {
                    statusDiv.style.background = '#f8d7da';
                    statusDiv.innerHTML = '❌ Bluetooth access denied. Please enable Bluetooth in your browser settings.';
                } else {
                    statusDiv.style.background = '#f8d7da';
                    statusDiv.innerHTML = '❌ Error: ' + error.message;
                }
            }
        });
        
        async function connectToDevice(device) {
            try {
                const statusDiv = document.getElementById('status');
                const deviceInfoDiv = document.getElementById('deviceInfo');
                const scanBtn = document.getElementById('scanBtn');
                
                statusDiv.innerHTML = '🔗 Connecting to ' + device.name + '...';
                
                const server = await device.gatt.connect();
                
                statusDiv.style.background = '#d4edda';
                statusDiv.innerHTML = '✅ Connected to ' + device.name + '!';
                scanBtn.innerHTML = '✅ Connected - ' + device.name;
                scanBtn.disabled = true;
                
                deviceInfoDiv.style.display = 'block';
                deviceInfoDiv.innerHTML = '<h4>📱 Device Information</h4>';
                deviceInfoDiv.innerHTML += '<p><strong>Name:</strong> ' + device.name + '</p>';
                deviceInfoDiv.innerHTML += '<p><strong>ID:</strong> ' + device.id + '</p>';
                
                // Try to read heart rate service
                try {
                    const heartRateService = await server.getPrimaryService('heart_rate');
                    heartRateCharacteristic = await heartRateService.getCharacteristic('heart_rate_measurement');
                    
                    deviceInfoDiv.innerHTML += '<p><strong>Heart Rate Monitor:</strong> ✅ Available</p>';
                    deviceInfoDiv.innerHTML += '<div id="heartRate" style="font-size: 24px; color: #e74c3c; margin: 15px 0;">❤️ --</div>';
                    
                    // Start notifications
                    await heartRateCharacteristic.startNotifications();
                    heartRateCharacteristic.addEventListener('characteristicvaluechanged', (event) => {
                        const value = event.target.value;
                        const heartRate = value.getUint8(1);
                        document.getElementById('heartRate').innerHTML = '❤️ ' + heartRate + ' bpm';
                        
                        // Send data to Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: {
                                device: device.name,
                                heartRate: heartRate,
                                timestamp: new Date().toISOString()
                            }
                        }, '*');
                    });
                } catch (error) {
                    deviceInfoDiv.innerHTML += '<p><strong>Heart Rate Monitor:</strong> ❌ Not available</p>';
                }
                
                // Try to read battery level
                try {
                    const batteryService = await server.getPrimaryService('battery_service');
                    const batteryCharacteristic = await batteryService.getCharacteristic('battery_level');
                    const batteryValue = await batteryCharacteristic.readValue();
                    const batteryLevel = batteryValue.getUint8(0);
                    deviceInfoDiv.innerHTML += '<p><strong>Battery:</strong> 🔋 ' + batteryLevel + '%</p>';
                } catch (error) {
                    deviceInfoDiv.innerHTML += '<p><strong>Battery:</strong> ❌ Not available</p>';
                }
                
                // Try to read device info
                try {
                    const deviceInfoService = await server.getPrimaryService('device_information');
                    
                    try {
                        const manufacturerCharacteristic = await deviceInfoService.getCharacteristic('manufacturer_name_string');
                        const manufacturerValue = await manufacturerCharacteristic.readValue();
                        const manufacturer = new TextDecoder().decode(manufacturerValue);
                        deviceInfoDiv.innerHTML += '<p><strong>Manufacturer:</strong> ' + manufacturer + '</p>';
                    } catch (e) {}
                    
                    try {
                        const modelCharacteristic = await deviceInfoService.getCharacteristic('model_number_string');
                        const modelValue = await modelCharacteristic.readValue();
                        const model = new TextDecoder().decode(modelValue);
                        deviceInfoDiv.innerHTML += '<p><strong>Model:</strong> ' + model + '</p>';
                    } catch (e) {}
                } catch (error) {}
                
                deviceInfoDiv.innerHTML += '<p style="margin-top: 20px; color: #4a6fa5;"><strong>💡 Tip:</strong> Keep this page open to continue receiving data from your device</p>';
                
            } catch (error) {
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#f8d7da';
                statusDiv.innerHTML = '❌ Connection Error: ' + error.message;
            }
        }
        
        // Disconnect on page unload
        window.addEventListener('beforeunload', () => {
            if (bluetoothDevice && bluetoothDevice.gatt.connected) {
                bluetoothDevice.gatt.disconnect();
            }
        });
    </script>
    """
    
    bluetooth_data = components.html(bluetooth_html, height=400)
    
    if bluetooth_data and isinstance(bluetooth_data, dict):
        st.success(f"📡 Receiving data from: **{bluetooth_data.get('device', 'Unknown')}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if 'heartRate' in bluetooth_data:
                st.metric("Heart Rate", f"{bluetooth_data['heartRate']} bpm", delta=None)
        with col2:
            if 'timestamp' in bluetooth_data:
                st.text(f"Last update: {bluetooth_data['timestamp'][:19]}")
    
    st.markdown("---")
    st.warning("""
    **Browser Compatibility:**
    - ✅ Chrome 56+ (recommended)
    - ✅ Edge 79+
    - ✅ Opera 43+
    - ⚠️ **Brave** (requires enabling Web Bluetooth in settings - see instructions above if you see an error)
    - ❌ Firefox (not supported yet)
    - ❌ Safari (not supported yet)
    
    **For Brave Users:**
    1. Click the Brave shield icon in the address bar
    2. Go to Advanced Controls
    3. Enable "Web Bluetooth"
    4. Refresh the page
    
    **Note:** Web Bluetooth is an experimental feature. For full functionality, export files from your device's companion app.
    """)

with tab2:
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

with tab3:
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
    
    ### 🔵 Bluetooth Direct Connection
    
    **Supported via Bluetooth:**
    - Heart rate monitors (most BLE-enabled devices)
    - Some Garmin devices (limited functionality)
    - Polar H10, H9 heart rate sensors
    - Wahoo TICKR sensors
    
    **Note:** Full activity tracking (GPS routes, elevation) requires file export. Bluetooth provides real-time heart rate and basic metrics during your hike.
    """)

with tab4:
    st.subheader("📊 Your Imported Sessions")
    st.info("View your imported wearable data sessions here after uploading files in the Import tab")

# Footer
st.divider()
st.markdown("""
    ### 💡 Tips
    - **🔵 Bluetooth:** Great for real-time heart rate monitoring during your hike
    - **📁 File Upload:** Best for complete activity data including GPS routes and elevation
    - **Export regularly:** Save your hikes from your device app after each trek
    - **Battery life:** GPS tracking can drain battery - bring a power bank for long hikes
    - **Signal:** GPS works without cell signal, but may take longer to acquire satellites
    - **Accuracy:** Route accuracy depends on your device's GPS quality and terrain
    - **Browser:** Use Chrome, Edge, or Opera for best Bluetooth support
""")
