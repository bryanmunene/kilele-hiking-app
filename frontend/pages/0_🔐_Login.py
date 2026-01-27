import streamlit as st
import streamlit.components.v1 as components
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import new unified modules
from database import init_database
from auth import authenticate_user, register_user, verify_2fa_code, is_authenticated, get_current_user, logout as auth_logout, create_session_token
from nature_theme import apply_nature_theme

# Initialize database
init_database()

st.set_page_config(page_title="Login - Kilele", page_icon="🔐", layout="wide")
apply_nature_theme()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

def login(username, password, two_fa_token=None, remember_me=True):
    """Login user with direct database access"""
    try:
        # Authenticate user
        user = authenticate_user(username, password)
        
        if not user:
            return False, "Invalid username or password"
        
        # Check if 2FA is enabled
        if user.get('two_factor_enabled'):
            if not two_fa_token:
                return "2fa_required", "Please enter your 2FA code"
            
            # Verify 2FA token
            if not verify_2fa_code(user['id'], two_fa_token):
                return False, "Invalid 2FA code"
        
        # Create persistent session token
        session_token = create_session_token(user['id'], remember_me=remember_me)
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.session_token = session_token  # Save token for persistent login
        
        return True, "Login successful!"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def register(username, email, full_name, password):
    """Register new user"""
    try:
        user = register_user(username, email, password, full_name)
        return True, "Registration successful! Please login."
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def logout():
    """Logout user"""
    auth_logout()
    st.rerun()

# Check if already logged in
if st.session_state.authenticated:
    st.success(f"✅ Already logged in as **{st.session_state.user['username']}**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("### User Profile")
        st.write(f"**Full Name:** {st.session_state.user.get('full_name', 'N/A')}")
        st.write(f"**Email:** {st.session_state.user.get('email', 'N/A')}")
        st.write(f"**Member Since:** {st.session_state.user.get('created_at', 'N/A')[:10]}")
        
        if st.button("🚪 Logout", type="primary"):
            logout()
        
        st.info("👈 Navigate to other pages to explore trails!")
else:
    # Login/Register Tabs
    tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("## 🏔️ Welcome to Kilele")
            st.write("Login to track your hiking adventures")
            
            # Check if 2FA is required
            if 'needs_2fa' not in st.session_state:
                st.session_state.needs_2fa = False
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                # Show 2FA input if needed
                two_fa_code = None
                if st.session_state.needs_2fa:
                    two_fa_code = st.text_input("2FA Code", placeholder="Enter 6-digit code", max_chars=6)
                
                # Remember me checkbox
                remember_me = st.checkbox("Remember me for 30 days", value=True)
                
                submit = st.form_submit_button("🔐 Login", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Please fill in all fields")
                    elif st.session_state.needs_2fa and not two_fa_code:
                        st.error("Please enter your 2FA code")
                    else:
                        with st.spinner("Logging in..."):
                            success, message = login(username, password, two_fa_code, remember_me)
                            if success == "2fa_required":
                                st.session_state.needs_2fa = True
                                st.info("🔐 Please enter your 2FA code")
                                st.rerun()
                            elif success:
                                st.session_state.needs_2fa = False
                                st.success(message)
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(message)
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("## 🎒 Join Kilele")
            st.write("Create an account to start your journey")
            
            with st.form("register_form"):
                reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                reg_email = st.text_input("Email", placeholder="your.email@example.com", key="reg_email")
                reg_fullname = st.text_input("Full Name", placeholder="Your full name", key="reg_name")
                reg_password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="reg_pass")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_conf")
                
                submit_reg = st.form_submit_button("📝 Create Account", use_container_width=True)
                
                if submit_reg:
                    if not all([reg_username, reg_email, reg_fullname, reg_password, reg_confirm]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            success, message = register(reg_username, reg_email, reg_fullname, reg_password)
                            if success:
                                st.success(message)
                                st.info("👈 Switch to Login tab to access your account")
                            else:
                                st.error(message)

# Show tips for demo
if not st.session_state.authenticated:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        ### 💡 Getting Started
        1. Create a new account using the Register tab
        2. Login with your credentials
        3. Explore trails, track hikes, and save favorites!
        
        **Features after login:**
        - 📍 Track active hikes with GPS
        - ❤️ Save favorite trails
        - 📊 View personal statistics
        - 🎯 Rate and review completed hikes
        """)
