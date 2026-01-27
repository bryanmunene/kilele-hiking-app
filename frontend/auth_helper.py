"""
Simple authentication persistence using browser localStorage
Call restore_auth() at the start of pages that need authentication
"""
import streamlit as st
import streamlit.components.v1 as components
import json

def restore_auth():
    """
    Restore authentication from browser localStorage.
    Call this at the start of every protected page.
    """
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "token" not in st.session_state:
        st.session_state.token = None
    
    # If already authenticated, return
    if st.session_state.authenticated:
        return
    
    # Try to get auth from localStorage via query params
    if "auth_token" in st.query_params and "auth_user" in st.query_params:
        try:
            token = st.query_params["auth_token"]
            user = json.loads(st.query_params["auth_user"])
            
            st.session_state.authenticated = True
            st.session_state.token = token
            st.session_state.user = user
            
            # Clear query params after restoring
            st.query_params.clear()
            st.rerun()
        except:
            pass
    else:
        # Inject JS to check localStorage and add to URL if found
        html_code = """
        <script>
        (function() {
            const token = localStorage.getItem('kilele_token');
            const userStr = localStorage.getItem('kilele_user');
            
            if (token && userStr && !window.location.search.includes('auth_token')) {
                const params = new URLSearchParams(window.location.search);
                params.set('auth_token', token);
                params.set('auth_user', userStr);
                window.location.search = params.toString();
            }
        })();
        </script>
        """
        components.html(html_code, height=0)

def save_auth(token, user):
    """Save authentication to browser localStorage"""
    user_json = json.dumps(user)
    
    html_code = f"""
    <script>
    localStorage.setItem('kilele_token', '{token}');
    localStorage.setItem('kilele_user', '{user_json.replace("'", "\\'")}');
    </script>
    """
    components.html(html_code, height=0)

def clear_auth():
    """Clear authentication from browser storage"""
    html_code = """
    <script>
    localStorage.removeItem('kilele_token');
    localStorage.removeItem('kilele_user');
    </script>
    """
    components.html(html_code, height=0)
