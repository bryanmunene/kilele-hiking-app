import streamlit as st
from services import add_emergency_contact, get_emergency_contacts, delete_emergency_contact
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Emergency Contacts - Kilele Explorers", page_icon="🚨", layout="wide")
apply_nature_theme()

# Check if user is logged in
if 'user' not in st.session_state:
    st.warning("⚠️ Please log in to manage emergency contacts")
    st.page_link("pages/3_🔐_Login.py", label="Go to Login", icon="🔐")
    st.stop()

user = st.session_state.user

# Page header
st.title("🚨 Emergency Contacts")
st.markdown("Stay safe on the trails - add emergency contacts who can be reached if needed")

# Safety information banner
st.info("""
🔒 **Your Safety Matters**
- Add trusted contacts who should be notified in case of emergency
- Mark one as primary contact for first notification
- Keep phone numbers up to date
- Share your hiking plans with these contacts
""")

# Get current emergency contacts
contacts = get_emergency_contacts(user['id'])

# Two columns layout
col1, col2 = st.columns([2, 1])

# Left column: List of contacts
with col1:
    st.markdown("### 📱 Your Emergency Contacts")
    
    if not contacts:
        st.warning("No emergency contacts added yet. Add your first contact below!")
    else:
        for contact in contacts:
            with st.container():
                # Contact card
                contact_col1, contact_col2, contact_col3 = st.columns([3, 2, 1])
                
                with contact_col1:
                    st.markdown(f"### {contact['name']}")
                    if contact['is_primary']:
                        st.markdown("⭐ **Primary Contact**")
                    if contact['relation']:
                        st.markdown(f"*{contact['relation']}*")
                
                with contact_col2:
                    st.markdown(f"📞 **{contact['phone']}**")
                
                with contact_col3:
                    if st.button("🗑️", key=f"delete_{contact['id']}", help="Delete contact"):
                        if delete_emergency_contact(contact['id']):
                            st.success("Contact deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
                
                st.markdown("---")

# Right column: Add new contact
with col2:
    st.markdown("### ➕ Add New Contact")
    
    with st.form("add_contact_form", clear_on_submit=True):
        name = st.text_input("Full Name*", placeholder="e.g., John Doe")
        phone = st.text_input("Phone Number*", placeholder="e.g., +254 712 345 678")
        relation = st.text_input("Relationship", placeholder="e.g., Spouse, Friend, Parent")
        is_primary = st.checkbox("Set as primary contact", help="This contact will be notified first")
        
        submit = st.form_submit_button("Add Contact", type="primary", use_container_width=True)
        
        if submit:
            if not name or not phone:
                st.error("Name and phone number are required")
            else:
                result = add_emergency_contact(
                    user_id=user['id'],
                    name=name,
                    phone=phone,
                    relation=relation,
                    is_primary=is_primary
                )
                
                if result and 'id' in result:
                    st.success("✅ Contact added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add contact")

# Bottom section: Safety tips
st.markdown("---")
st.markdown("## 🛡️ Hiking Safety Tips")

col_tip1, col_tip2, col_tip3 = st.columns(3)

with col_tip1:
    st.markdown("""
    **Before You Go:**
    - Share your hiking plan
    - Check weather forecast
    - Pack essentials
    - Charge your phone
    """)

with col_tip2:
    st.markdown("""
    **On the Trail:**
    - Stay on marked paths
    - Keep phone accessible
    - Take regular breaks
    - Monitor weather changes
    """)

with col_tip3:
    st.markdown("""
    **In Emergency:**
    - Stay calm and assess
    - Call emergency services: 112/999
    - Use location sharing
    - Signal for help if needed
    """)

# Statistics in sidebar
with st.sidebar:
    st.markdown("### 📊 Contact Statistics")
    st.metric("Total Contacts", len(contacts))
    
    primary_count = sum(1 for c in contacts if c['is_primary'])
    st.metric("Primary Contacts", primary_count)
    
    st.markdown("---")
    
    st.markdown("### 🌍 Kenya Emergency Numbers")
    st.markdown("""
    - **General Emergency:** 999 / 112
    - **Kenya Red Cross:** 1199
    - **Police:** 999
    - **Ambulance:** 999
    - **KWS (Wildlife):** +254 20 600 0800
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Quick Tips")
    st.info("""
    - Add at least 2 emergency contacts
    - Keep contact information updated
    - Share your location before hikes
    - Tell contacts your expected return time
    """)
