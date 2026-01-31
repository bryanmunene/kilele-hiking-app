import streamlit as st
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Strava Connect - Kilele", page_icon="🟠", layout="wide")
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to connect Strava")
    st.stop()

user = get_current_user()

st.title("🟠 Connect to Strava")
st.markdown("*Automatically sync your hiking activities from Strava*")
st.markdown("---")

# API base URL (update this for production)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Check connection status
@st.cache_data(ttl=60)
def get_strava_stats(user_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/strava/stats",
            headers={"user-id": str(user_id)}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

stats = get_strava_stats(user['id'])
is_connected = stats and stats.get('is_connected', False)

# Main content
if is_connected:
    st.success("✅ Your Strava account is connected!")
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Activities", stats['total_activities'])
        st.metric("Distance", f"{stats['total_distance_km']:.1f} km")
    
    with col2:
        st.metric("Time", f"{stats['total_time_hours']:.1f} hrs")
        st.metric("Elevation", f"{stats['total_elevation_m']:.0f} m")
    
    with col3:
        st.metric("Kudos", stats['total_kudos'])
        st.metric("Matched Trails", stats['matched_trails'])
    
    if stats.get('last_synced'):
        last_sync = datetime.fromisoformat(stats['last_synced'])
        st.info(f"⏰ Last synced: {last_sync.strftime('%B %d, %Y at %I:%M %p')}")
    
    st.markdown("---")
    
    # Sync controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Sync Activities")
        
        days = st.slider("Sync activities from last X days", 7, 365, 30)
        
        if st.button("🔄 Sync Now", type="primary", use_container_width=True):
            with st.spinner("Syncing activities from Strava..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/strava/sync?days={days}",
                        headers={"user-id": str(user['id'])}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Sync failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("⚙️ Settings")
        
        # Auto-sync toggle
        sync_enabled = st.toggle("Enable auto-sync", value=True)
        
        if st.button("💾 Save Settings", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/strava/toggle-autosync?enabled={sync_enabled}",
                    headers={"user-id": str(user['id'])}
                )
                
                if response.status_code == 200:
                    st.success("✅ Settings saved")
                else:
                    st.error("❌ Failed to save settings")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        
        if st.button("🔌 Disconnect Strava", type="secondary", use_container_width=True):
            try:
                response = requests.delete(
                    f"{API_BASE_URL}/api/strava/disconnect",
                    headers={"user-id": str(user['id'])}
                )
                
                if response.status_code == 200:
                    st.success("✅ Strava disconnected")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to disconnect")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Recent activities
    st.subheader("📋 Recent Activities")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/strava/activities?limit=20",
            headers={"user-id": str(user['id'])}
        )
        
        if response.status_code == 200:
            activities = response.json()
            
            if activities:
                # Create dataframe
                df = pd.DataFrame([{
                    "Activity": act['name'],
                    "Type": act['activity_type'],
                    "Date": datetime.fromisoformat(act['date']).strftime('%b %d, %Y'),
                    "Distance": f"{act['distance_km']:.2f} km",
                    "Duration": f"{act['duration_minutes']:.0f} min",
                    "Kudos": act['kudos_count'],
                    "Trail Match": "✅ " + act['matched_trail_name'] if act['is_matched'] else "❌ Not matched"
                } for act in activities])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No activities synced yet. Click 'Sync Now' above.")
    except Exception as e:
        st.error(f"❌ Failed to load activities: {str(e)}")

else:
    # Not connected - show connect button
    st.info("Connect your Strava account to automatically sync hiking activities")
    
    # Benefits
    st.subheader("✨ What you get:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - 🔄 **Auto-sync hikes** from Strava
        - 📊 **Import activity data** (GPS, stats, photos)
        - 🏔️ **Match trails** automatically
        - 🏆 **Track achievements** across platforms
        """)
    
    with col2:
        st.markdown("""
        - ⏱️ **Real-time updates** via webhooks
        - 📈 **Combined stats** with Kilele data
        - 👥 **Social features** integration
        - 💪 **Never lose your progress**
        """)
    
    st.markdown("---")
    
    # Connect button
    if st.button("🟠 Connect Strava", type="primary", use_container_width=True):
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/strava/connect",
                headers={"user-id": str(user['id'])}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.markdown(f"""
                ### 🔗 Click to authorize:
                <a href="{data['authorization_url']}" target="_blank" style="
                    display: inline-block;
                    background: linear-gradient(135deg, #FC4C02, #FF6B35);
                    color: white;
                    padding: 15px 30px;
                    border-radius: 10px;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 18px;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(252, 76, 2, 0.3);
                ">
                    🟠 Authorize Strava Access
                </a>
                
                <p style="color: #666; font-size: 14px; margin-top: 10px;">
                You'll be redirected to Strava to authorize access. After authorization, 
                return here and refresh the page.
                </p>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to get authorization URL")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Privacy notice
    with st.expander("🔒 Privacy & Permissions"):
        st.markdown("""
        ### What we access:
        - Your public profile information
        - Activity data (GPS routes, stats, photos)
        - Activity updates in real-time
        
        ### What we DON'T access:
        - Your private activities (if marked private)
        - Your Strava password
        - Your followers or following list
        - Any payment information
        
        ### You can:
        - Disconnect anytime
        - Control auto-sync settings
        - Choose which activities to import
        
        **We respect your privacy and follow Strava's API Terms of Service.**
        """)
    
    # Setup instructions
    with st.expander("⚙️ Setup Instructions for Developers"):
        st.markdown("""
        ### Required Environment Variables:
        
        ```bash
        # Backend (.env file)
        STRAVA_CLIENT_ID=your_client_id
        STRAVA_CLIENT_SECRET=your_client_secret
        STRAVA_REDIRECT_URI=http://localhost:8501/strava/callback
        STRAVA_WEBHOOK_VERIFY_TOKEN=your_verify_token
        ```
        
        ### Steps to get Strava API credentials:
        1. Go to [strava.com/settings/api](https://www.strava.com/settings/api)
        2. Create a new app
        3. Set Authorization Callback Domain to your domain
        4. Copy Client ID and Client Secret
        5. Add to backend `.env` file
        6. Restart backend server
        
        ### Webhook Setup (Optional - for real-time sync):
        ```bash
        # Subscribe to webhook
        curl -X POST https://www.strava.com/api/v3/push_subscriptions \\
          -F client_id=YOUR_CLIENT_ID \\
          -F client_secret=YOUR_CLIENT_SECRET \\
          -F callback_url=https://your-domain.com/api/strava/webhook \\
          -F verify_token=YOUR_VERIFY_TOKEN
        ```
        """)

# Footer
st.markdown("---")
st.caption("🟠 Powered by Strava API • Automatically syncs your outdoor activities")
