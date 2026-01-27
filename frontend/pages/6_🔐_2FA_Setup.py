import streamlit as st
import sys
import os
import qrcode
from io import BytesIO
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from auth import is_authenticated, get_current_user, setup_2fa, verify_2fa_code, enable_2fa, disable_2fa
from nature_theme import apply_nature_theme

init_database()

st.set_page_config(page_title="2FA Setup - Kilele", page_icon="🔐", layout="wide")
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access 2FA settings")
    st.info("👈 Navigate to the Login page to access your account")
    st.stop()

current_user = get_current_user()

st.title("🔐 Two-Factor Authentication (2FA)")
st.markdown("Add an extra layer of security to your account")
st.markdown("---")

# Check current 2FA status
two_fa_enabled = current_user.get('two_factor_enabled', False)

if two_fa_enabled:
    # 2FA is already enabled
    st.success("✅ Two-Factor Authentication is **ENABLED** on your account")
    
    st.markdown("""
    <div class='success-box'>
        <h3>🛡️ Your Account is Protected</h3>
        <p>Two-factor authentication adds an extra layer of security by requiring a verification code from your authenticator app when you log in.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Manage 2FA")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("To disable 2FA, click the button below. You will only need your password to login after disabling.")
    with col2:
        if st.button("🔓 Disable 2FA", type="secondary"):
            if disable_2fa(current_user['id']):
                st.success("✅ 2FA has been disabled")
                st.info("Please refresh the page to see changes")
                st.rerun()
            else:
                st.error("❌ Failed to disable 2FA")

else:
    # 2FA is not enabled
    st.warning("⚠️ Two-Factor Authentication is **NOT ENABLED** on your account")
    
    st.markdown("""
    ### 📱 What is Two-Factor Authentication?
    
    2FA adds an extra layer of security to your account by requiring:
    1. **Something you know** - Your password
    2. **Something you have** - Your phone with an authenticator app
    
    Even if someone gets your password, they won't be able to access your account without the code from your phone.
    """)
    
    st.markdown("### 🚀 Setup Instructions")
    
    with st.expander("📥 Step 1: Install an Authenticator App", expanded=True):
        st.markdown("""
        Install one of these authenticator apps on your smartphone:
        - **Google Authenticator** (Android/iOS)
        - **Microsoft Authenticator** (Android/iOS)  
        - **Authy** (Android/iOS)
        - **FreeOTP** (Android/iOS)
        """)
    
    with st.expander("📷 Step 2: Scan QR Code", expanded=False):
        st.markdown("Generate your unique QR code and scan it with your authenticator app.")
        
        if st.button("🔑 Generate QR Code", type="primary"):
            try:
                # Generate 2FA secret and URI
                secret, provisioning_uri = setup_2fa(current_user['id'])
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(provisioning_uri)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to bytes
                buf = BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                
                # Display QR code
                st.markdown("### 📱 Scan this QR Code")
                st.image(buf, width=300)
                
                st.markdown(f"""
                <div class='warning-box'>
                    <strong>⚠️ Manual Entry Code (if QR doesn't work):</strong><br>
                    <code style='font-size: 1.2em; background: #fff; padding: 5px 10px; border-radius: 4px; color: #333;'>{secret}</code>
                </div>
                """, unsafe_allow_html=True)
                
                # Store secret in session for verification
                st.session_state.temp_2fa_secret = secret
                st.session_state.show_verification = True
                
            except Exception as e:
                st.error(f"❌ Error generating QR code: {str(e)}")
    
    if st.session_state.get('show_verification', False):
        with st.expander("✅ Step 3: Verify and Enable", expanded=True):
            st.markdown("Enter the 6-digit code from your authenticator app to complete setup.")
            
            code = st.text_input("Enter 6-digit code", max_chars=6, key="verification_code")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Verify and Enable 2FA", type="primary"):
                    if not code or len(code) != 6:
                        st.error("❌ Please enter a 6-digit code")
                    else:
                        # Verify the code
                        if verify_2fa_code(current_user['id'], code):
                            # Enable 2FA
                            if enable_2fa(current_user['id'], True):
                                st.success("🎉 2FA has been successfully enabled!")
                                st.balloons()
                                st.info("Please refresh the page to see changes")
                                # Clear session
                                if 'temp_2fa_secret' in st.session_state:
                                    del st.session_state.temp_2fa_secret
                                if 'show_verification' in st.session_state:
                                    del st.session_state.show_verification
                                st.rerun()
                            else:
                                st.error("❌ Failed to enable 2FA")
                        else:
                            st.error("❌ Invalid code. Please try again.")
            
            with col2:
                if st.button("Cancel", type="secondary"):
                    if 'temp_2fa_secret' in st.session_state:
                        del st.session_state.temp_2fa_secret
                    if 'show_verification' in st.session_state:
                        del st.session_state.show_verification
                    st.rerun()

st.markdown("---")
st.markdown("""
### 🔐 Security Tips

- **Keep your recovery codes safe** - Store them in a secure location
- **Don't share your 2FA codes** - Never share the 6-digit codes with anyone
- **Use a strong password** - 2FA works best with a strong password
- **Backup your secret** - Keep the manual entry code in a safe place
""")

