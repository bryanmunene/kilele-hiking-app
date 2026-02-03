"""
Browser storage helper for persistent login
Uses JavaScript localStorage to persist session tokens across page refreshes
"""
import streamlit as st
import streamlit.components.v1 as components
import json

def save_token_to_browser(token: str):
    """Save session token to browser localStorage"""
    components.html(
        f"""
        <script>
            localStorage.setItem('kilele_session_token', '{token}');
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'saved'}}, '*');
        </script>
        """,
        height=0,
    )

def load_token_from_browser():
    """Load session token from browser localStorage"""
    token = components.html(
        """
        <script>
            const token = localStorage.getItem('kilele_session_token');
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: token || ''}, '*');
        </script>
        """,
        height=0,
    )
    return token if token else None

def clear_token_from_browser():
    """Clear session token from browser localStorage"""
    components.html(
        """
        <script>
            localStorage.removeItem('kilele_session_token');
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'cleared'}, '*');
        </script>
        """,
        height=0,
    )

def restore_session_from_browser():
    """
    Restore session from browser localStorage on page load
    Call this at the start of your app
    """
    # Only try to restore if not already authenticated
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        if "token_loaded" not in st.session_state:
            st.session_state.token_loaded = False
        
        if not st.session_state.token_loaded:
            # Try to load token from browser
            token = load_token_from_browser()
            if token:
                st.session_state.session_token = token
                st.session_state.token_loaded = True
                # The is_authenticated() function will validate and restore the session


def save_to_browser(key: str, value: str):
    """Save generic data to browser localStorage"""
    # Escape single quotes in value
    escaped_value = value.replace("'", "\\'").replace("\n", "\\n")
    components.html(
        f"""
        <script>
            try {{
                localStorage.setItem('{key}', '{escaped_value}');
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'saved'}}, '*');
            }} catch(e) {{
                console.error('Error saving to localStorage:', e);
            }}
        </script>
        """,
        height=0,
    )


def load_from_browser(key: str):
    """Load generic data from browser localStorage"""
    value = components.html(
        f"""
        <script>
            try {{
                const value = localStorage.getItem('{key}');
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: value || ''}}, '*');
            }} catch(e) {{
                console.error('Error loading from localStorage:', e);
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: ''}}, '*');
            }}
        </script>
        """,
        height=0,
    )
    return value if value else None


def clear_from_browser(key: str):
    """Clear specific data from browser localStorage"""
    components.html(
        f"""
        <script>
            try {{
                localStorage.removeItem('{key}');
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'cleared'}}, '*');
            }} catch(e) {{
                console.error('Error clearing from localStorage:', e);
            }}
        </script>
        """,
        height=0,
    )
