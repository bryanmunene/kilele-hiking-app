"""Import hiking activities from wearables and BLE heart-rate sensors."""

import json
from datetime import datetime

import streamlit as st

from auth import get_current_user, is_authenticated
from database import init_database
from nature_theme import apply_nature_theme
from services import create_session, get_all_hikes, get_user_sessions
from utils.wearable_parser import WearableDataParser


st.set_page_config(page_title="Wearables — Kilele", page_icon="⌚", layout="wide")
init_database()
apply_nature_theme()


BLUETOOTH_HTML = """
<button id="scan">Scan and connect</button>
<div id="status" class="status">Ready to find a nearby Bluetooth Low Energy device.</div>
<div id="reading" class="reading" hidden>
    <div><span>Device</span><strong id="device">—</strong></div>
    <div><span>Heart rate</span><strong id="heart-rate">—</strong></div>
    <div><span>Battery</span><strong id="battery">—</strong></div>
</div>
"""

BLUETOOTH_CSS = """
:host { color: #17221e; font-family: sans-serif; }
#scan {
    width: 100%; min-height: 48px; border: 0; border-radius: 12px;
    background: #173d32; color: white; font-weight: 700; cursor: pointer;
}
#scan:hover { background: #245846; }
#scan:disabled { opacity: .65; cursor: default; }
.status { margin-top: 14px; padding: 14px; border-radius: 12px; background: #edf0e9; line-height: 1.45; }
.status.error { background: #fff0ed; color: #8f342e; }
.status.success { background: #e6f1ea; color: #173d32; }
.reading { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 12px; }
.reading div { padding: 14px; border: 1px solid #d9ded8; border-radius: 12px; background: #fffdf8; }
.reading span { display: block; color: #66736d; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
.reading strong { display: block; margin-top: 6px; color: #173d32; font-size: 18px; }
@media (max-width: 540px) { .reading { grid-template-columns: 1fr; } }
"""

BLUETOOTH_JS = """
export default function(component) {
    const { parentElement, setStateValue } = component;
    const scanButton = parentElement.querySelector('#scan');
    const status = parentElement.querySelector('#status');
    const readingPanel = parentElement.querySelector('#reading');
    const deviceField = parentElement.querySelector('#device');
    const heartRateField = parentElement.querySelector('#heart-rate');
    const batteryField = parentElement.querySelector('#battery');
    let device = null;
    let heartRateCharacteristic = null;

    const showStatus = (message, kind = '') => {
        status.textContent = message;
        status.className = `status ${kind}`;
    };

    const connect = async () => {
        if (!navigator.bluetooth) {
            showStatus('Web Bluetooth is not available in this browser. Use Chrome or Edge over HTTPS, or import an activity file instead.', 'error');
            return;
        }

        try {
            showStatus('Choose your sensor from the browser device picker.');
            device = await navigator.bluetooth.requestDevice({
                acceptAllDevices: true,
                optionalServices: ['heart_rate', 'battery_service', 'device_information']
            });
            const server = await device.gatt.connect();
            deviceField.textContent = device.name || 'Unnamed BLE device';
            readingPanel.hidden = false;
            scanButton.disabled = true;
            scanButton.textContent = 'Connected';
            showStatus(`Connected to ${device.name || 'your device'}. Keep this page open for live readings.`, 'success');

            try {
                const batteryService = await server.getPrimaryService('battery_service');
                const batteryCharacteristic = await batteryService.getCharacteristic('battery_level');
                const batteryValue = await batteryCharacteristic.readValue();
                batteryField.textContent = `${batteryValue.getUint8(0)}%`;
            } catch (_) {
                batteryField.textContent = 'Not shared';
            }

            try {
                const heartRateService = await server.getPrimaryService('heart_rate');
                heartRateCharacteristic = await heartRateService.getCharacteristic('heart_rate_measurement');
                await heartRateCharacteristic.startNotifications();
                heartRateCharacteristic.addEventListener('characteristicvaluechanged', (event) => {
                    const flags = event.target.value.getUint8(0);
                    const heartRate = flags & 0x01
                        ? event.target.value.getUint16(1, true)
                        : event.target.value.getUint8(1);
                    heartRateField.textContent = `${heartRate} bpm`;
                    setStateValue('reading', {
                        device: device.name || 'BLE device',
                        heartRate,
                        timestamp: new Date().toISOString()
                    });
                });
            } catch (_) {
                heartRateField.textContent = 'Not shared';
            }
        } catch (error) {
            const message = error.name === 'NotFoundError'
                ? 'No device was selected. Start another scan when the device is ready.'
                : `Connection failed: ${error.message}`;
            showStatus(message, 'error');
        }
    };

    scanButton.addEventListener('click', connect);
    return () => {
        scanButton.removeEventListener('click', connect);
        if (heartRateCharacteristic) heartRateCharacteristic.stopNotifications().catch(() => {});
        if (device?.gatt?.connected) device.gatt.disconnect();
    };
}
"""

bluetooth_component = st.components.v2.component(
    "kilele_bluetooth_monitor",
    html=BLUETOOTH_HTML,
    css=BLUETOOTH_CSS,
    js=BLUETOOTH_JS,
)


def _no_op() -> None:
    """State callback for the Bluetooth component."""


def parse_iso_datetime(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


if not is_authenticated():
    st.warning("Sign in to import and save wearable activities.")
    st.page_link("pages/0_🔐_Login.py", label="Go to sign in", icon=":material/login:")
    st.stop()

user = get_current_user()

st.title("Wearables")
st.markdown("Bring activity data into Kilele from a tracking file or a nearby heart-rate sensor.")

connect_tab, import_tab, sessions_tab, devices_tab = st.tabs(
    ["Live sensor", "Import activity", "Imported sessions", "Device guide"]
)

with connect_tab:
    st.subheader("Live Bluetooth sensor")
    st.caption("Best for compatible Bluetooth Low Energy heart-rate straps and sensors. GPS routes still require a file import.")
    result = bluetooth_component(
        key="wearable_bluetooth",
        default={"reading": None},
        on_reading_change=_no_op,
        height=330,
    )
    if result.reading:
        reading = result.reading
        metric_a, metric_b = st.columns(2)
        metric_a.metric("Live heart rate", f"{reading['heartRate']} bpm")
        metric_b.metric("Connected device", reading["device"])

    st.info("Bluetooth device access requires Chrome or Edge, HTTPS, and a device in pairing mode. Firefox and Safari do not currently expose Web Bluetooth.")

with import_tab:
    st.subheader("Import an activity file")
    st.caption("Supported formats: GPX, FIT, and TCX. Maximum file size: 10 MB.")

    uploaded_file = st.file_uploader("Activity file", type=["gpx", "fit", "tcx"])
    hikes = get_all_hikes()
    hike_options = {"Unlinked activity": None}
    hike_options.update({f"{hike['name']} — {hike['location']}": hike["id"] for hike in hikes})
    selected_label = st.selectbox("Link to a Kilele trail", list(hike_options))

    if uploaded_file and st.button("Import activity", type="primary", icon=":material/upload_file:", width="stretch"):
        file_bytes = uploaded_file.getvalue()
        if len(file_bytes) > 10 * 1024 * 1024:
            st.error("This file is larger than 10 MB.")
        else:
            extension = uploaded_file.name.rsplit(".", 1)[-1]
            with st.spinner("Reading activity data…"):
                parsed = WearableDataParser.parse_file(file_bytes, extension)

            if not parsed.get("success"):
                st.error(parsed.get("error", "The activity file could not be read."))
            else:
                session_data = {
                    "hike_id": hike_options[selected_label],
                    "started_at": parse_iso_datetime(parsed.get("start_time")) or datetime.utcnow(),
                    "ended_at": parse_iso_datetime(parsed.get("end_time")),
                    "duration_hours": float(parsed.get("duration_hours") or 0),
                    "distance_covered_km": float(parsed.get("total_distance_km") or 0),
                    "elevation_gain_m": float(parsed.get("elevation_gain_m") or 0),
                    "status": "completed",
                    "route_data": json.dumps(parsed.get("route_coordinates") or [], default=str),
                    "notes": f"Imported from {parsed.get('source', extension.upper())}: {uploaded_file.name}",
                }
                create_session(user["id"], session_data)
                st.success("Activity imported and added to your hiking history.")

                metric_a, metric_b, metric_c, metric_d = st.columns(4)
                metric_a.metric("Distance", f"{session_data['distance_covered_km']:.2f} km")
                metric_b.metric("Duration", f"{session_data['duration_hours']:.2f} h")
                metric_c.metric("Elevation", f"{session_data['elevation_gain_m']:.0f} m")
                metric_d.metric("Track points", parsed.get("total_points", 0))

with sessions_tab:
    st.subheader("Imported sessions")
    sessions = get_user_sessions(user["id"])
    imported_sessions = [session for session in sessions if (session.get("notes") or "").startswith("Imported from")]

    if not imported_sessions:
        st.info("No imported activities yet.")
    else:
        for session in sorted(imported_sessions, key=lambda item: item.get("started_at") or "", reverse=True):
            title = session.get("hike_name") or "Unlinked activity"
            with st.container(border=True):
                st.markdown(f"#### {title}")
                st.caption(session.get("notes") or "Wearable import")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Distance", f"{session.get('distance_covered_km') or 0:.2f} km")
                col_b.metric("Duration", f"{session.get('duration_hours') or 0:.2f} h")
                col_c.metric("Elevation", f"{session.get('elevation_gain_m') or 0:.0f} m")

with devices_tab:
    st.subheader("Export guide")
    guide_a, guide_b, guide_c = st.columns(3)
    with guide_a:
        with st.container(border=True):
            st.markdown("#### Garmin")
            st.markdown("Open an activity in Garmin Connect, use the settings menu, and export the original FIT file or GPX route.")
    with guide_b:
        with st.container(border=True):
            st.markdown("#### Strava")
            st.markdown("Open the activity on the Strava website, select the overflow menu, and choose Export GPX.")
    with guide_c:
        with st.container(border=True):
            st.markdown("#### Apple Watch and others")
            st.markdown("Export through the companion app or sync to a service that can produce GPX, FIT, or TCX.")

    st.markdown("#### Format coverage")
    st.dataframe(
        [
            {"Format": "GPX", "Route": "Yes", "Time": "Usually", "Elevation": "Usually", "Typical source": "Strava, Garmin, Komoot"},
            {"Format": "FIT", "Route": "Yes", "Time": "Yes", "Elevation": "Yes", "Typical source": "Garmin and fitness watches"},
            {"Format": "TCX", "Route": "Yes", "Time": "Yes", "Elevation": "Usually", "Typical source": "Garmin, legacy fitness apps"},
        ],
        hide_index=True,
        width="stretch",
    )
