"""
Offline Cache Manager
Handles caching trail data for offline use during hikes
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class OfflineCache:
    """Manage offline caching of trail data"""
    
    @staticmethod
    def cache_hike_data(hike_data: Dict[str, Any], trail_details: Dict[str, Any]) -> None:
        """
        Cache hike data for offline use
        
        Args:
            hike_data: Basic hike information
            trail_details: Detailed trail information including conditions, comments, etc.
        """
        cached_data = {
            'hike': hike_data,
            'trail': trail_details,
            'cached_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=2)).isoformat(),
            'version': '1.0'
        }
        
        # Save to session state
        st.session_state.offline_hike = cached_data
        
        # Also save to browser localStorage via JavaScript
        from browser_storage import save_to_browser
        save_to_browser('kilele_offline_hike', json.dumps(cached_data))
        
    @staticmethod
    def get_cached_hike() -> Optional[Dict[str, Any]]:
        """
        Retrieve cached hike data
        
        Returns:
            Cached hike data if available and not expired, None otherwise
        """
        # Try session state first
        if 'offline_hike' in st.session_state:
            cached = st.session_state.offline_hike
            expires_at = datetime.fromisoformat(cached['expires_at'])
            
            if datetime.now() < expires_at:
                return cached
        
        # Try browser localStorage
        from browser_storage import load_from_browser
        cached_str = load_from_browser('kilele_offline_hike')
        
        if cached_str:
            try:
                cached = json.loads(cached_str)
                expires_at = datetime.fromisoformat(cached['expires_at'])
                
                if datetime.now() < expires_at:
                    st.session_state.offline_hike = cached
                    return cached
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        
        return None
    
    @staticmethod
    def clear_cache() -> None:
        """Clear cached offline data"""
        if 'offline_hike' in st.session_state:
            del st.session_state.offline_hike
        
        from browser_storage import clear_from_browser
        clear_from_browser('kilele_offline_hike')
    
    @staticmethod
    def is_data_fresh() -> bool:
        """Check if cached data is still fresh"""
        cached = OfflineCache.get_cached_hike()
        
        if not cached:
            return False
        
        cached_at = datetime.fromisoformat(cached['cached_at'])
        age_hours = (datetime.now() - cached_at).total_seconds() / 3600
        
        # Consider data fresh if less than 12 hours old
        return age_hours < 12


def check_internet_connection() -> bool:
    """
    Check if internet connection is available
    
    Returns:
        True if online, False if offline
    """
    try:
        import requests
        response = requests.get('https://www.google.com', timeout=3)
        return response.status_code == 200
    except:
        return False


def show_offline_indicator():
    """Display offline mode indicator"""
    if not check_internet_connection():
        st.warning("📡 **Offline Mode** - Using cached data. GPS tracking will still work!", icon="⚠️")
        return True
    return False


def prepare_offline_hike_ui(hike_id: int, hike_data: Dict[str, Any]):
    """
    UI component for preparing hike for offline use
    
    Args:
        hike_id: ID of the hike to prepare
        hike_data: Hike data to cache
    """
    st.markdown("### 📥 Prepare for Offline Hiking")
    
    with st.expander("ℹ️ What gets downloaded for offline use?"):
        st.markdown("""
        When you prepare a hike for offline use, we cache:
        
        - ✅ **Trail details** (name, location, difficulty, distance)
        - ✅ **Route information** (elevation, terrain type)
        - ✅ **Trail conditions** (weather, crowd levels, safety notes)
        - ✅ **Emergency contacts** (your saved contacts)
        - ✅ **Equipment checklist** (recommended gear)
        - ✅ **Trail comments** (recent discussions)
        - ✅ **Static map image** (non-interactive)
        
        **What still needs internet:**
        - ❌ Interactive maps (use static map instead)
        - ❌ Real-time updates
        - ❌ Uploading photos during hike
        - ❌ Social features
        
        **GPS tracking works completely offline!** Your route will be recorded
        and automatically synced when you're back online.
        """)
    
    # Check if already cached
    cached = OfflineCache.get_cached_hike()
    is_cached = cached and cached['hike'].get('id') == hike_id
    is_fresh = OfflineCache.is_data_fresh() if is_cached else False
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if is_cached and is_fresh:
            cached_at = datetime.fromisoformat(cached['cached_at'])
            time_ago = datetime.now() - cached_at
            hours_ago = int(time_ago.total_seconds() / 3600)
            
            if hours_ago < 1:
                time_str = "just now"
            elif hours_ago == 1:
                time_str = "1 hour ago"
            else:
                time_str = f"{hours_ago} hours ago"
            
            st.success(f"✅ Trail data is cached and ready for offline use (downloaded {time_str})")
            
            if st.button("🔄 Refresh Cached Data", use_container_width=True):
                fetch_and_cache_trail_data(hike_id, hike_data)
                st.rerun()
        else:
            st.info("💡 Download trail data to use this hike offline")
    
    with col2:
        if st.button("📥 Download", type="primary", use_container_width=True):
            with st.spinner("Downloading trail data..."):
                fetch_and_cache_trail_data(hike_id, hike_data)
                st.success("✅ Ready for offline use!")
                st.balloons()
                st.rerun()


def fetch_and_cache_trail_data(hike_id: int, hike_data: Dict[str, Any]):
    """
    Fetch all trail data and cache it for offline use
    
    Args:
        hike_id: ID of the hike
        hike_data: Basic hike data
    """
    from services import (
        get_trail_conditions, 
        get_trail_comments, 
        get_equipment_list,
        get_user_emergency_contacts
    )
    from auth import get_current_user
    
    user = get_current_user()
    
    # Gather all relevant data
    trail_details = {
        'conditions': get_trail_conditions(hike_id) or [],
        'comments': get_trail_comments(hike_id) or [],
        'equipment': get_equipment_list() or [],
        'emergency_contacts': get_user_emergency_contacts(user['id']) if user else [],
        'user_bookmarked': True,  # Assume bookmarked if preparing offline
    }
    
    # Cache everything
    OfflineCache.cache_hike_data(hike_data, trail_details)
