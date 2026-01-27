import streamlit as st
from datetime import datetime
from services import (
    get_all_hikes, 
    add_trail_condition, 
    get_trail_conditions,
    add_equipment,
    get_trail_equipment
)
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Trail Info - Kilele Explorers", page_icon="🌤️", layout="wide")
apply_nature_theme()

# Check if user is logged in
if 'user' not in st.session_state:
    st.warning("⚠️ Please log in to report trail conditions or add equipment")
    st.page_link("pages/3_🔐_Login.py", label="Go to Login", icon="🔐")
    st.stop()

user = st.session_state.user

# Page header
st.title("🌤️ Trail Conditions & Equipment")
st.markdown("Help fellow hikers by sharing trail conditions and equipment recommendations")

# Get all trails
trails = get_all_hikes()

if not trails:
    st.error("No trails found.")
    st.stop()

# Trail selection
selected_trail_id = st.selectbox(
    "Select a Trail",
    options=[t['id'] for t in trails],
    format_func=lambda x: next((t['name'] for t in trails if t['id'] == x), "Unknown")
)

selected_trail = next((t for t in trails if t['id'] == selected_trail_id), None)

if selected_trail:
    # Display trail info
    st.markdown(f"### 🏔️ {selected_trail['name']}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Location", selected_trail['location'])
    with col2:
        st.metric("Difficulty", selected_trail['difficulty'])
    with col3:
        st.metric("Distance", f"{selected_trail['distance_km']} km")
    with col4:
        st.metric("Duration", f"{selected_trail['estimated_duration_hours']} hrs")
    
    st.markdown("---")
    
    # Tabs for Conditions and Equipment
    tab1, tab2 = st.tabs(["🌤️ Trail Conditions", "🎒 Equipment"])
    
    # TAB 1: Trail Conditions
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        # Left: View existing conditions
        with col_left:
            st.markdown("### 📊 Recent Conditions")
            
            conditions = get_trail_conditions(selected_trail_id, limit=10)
            
            if not conditions:
                st.info("No trail conditions reported yet. Be the first!")
            else:
                for cond in conditions:
                    with st.container():
                        # Condition icon
                        condition_emoji = {
                            'excellent': '🟢',
                            'good': '🟡',
                            'fair': '🟠',
                            'poor': '🔴',
                            'closed': '⛔'
                        }.get(cond['condition'], '⚪')
                        
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"{condition_emoji} **{cond['condition'].upper()}**")
                            st.markdown(f"*{cond['notes']}*")
                            if cond.get('weather'):
                                st.markdown(f"🌡️ Weather: {cond['weather']}")
                        
                        with col_b:
                            report_time = datetime.fromisoformat(cond['created_at'])
                            st.markdown(f"**{cond['username']}**")
                            st.markdown(f"*{report_time.strftime('%b %d, %Y')}*")
                        
                        st.markdown("---")
        
        # Right: Report new condition
        with col_right:
            st.markdown("### 📝 Report Condition")
            
            with st.form("report_condition_form"):
                condition = st.selectbox(
                    "Trail Condition",
                    options=['excellent', 'good', 'fair', 'poor', 'closed'],
                    format_func=lambda x: {
                        'excellent': '🟢 Excellent',
                        'good': '🟡 Good',
                        'fair': '🟠 Fair',
                        'poor': '🔴 Poor',
                        'closed': '⛔ Closed'
                    }[x]
                )
                
                weather = st.text_input(
                    "Weather (optional)",
                    placeholder="e.g., Sunny, 25°C"
                )
                
                notes = st.text_area(
                    "Additional Notes*",
                    placeholder="Describe current trail conditions, obstacles, etc.",
                    help="Required - Share helpful details"
                )
                
                submit = st.form_submit_button("Submit Report", type="primary", use_container_width=True)
                
                if submit:
                    if not notes:
                        st.error("Please add notes about the trail condition")
                    elif len(notes) < 10:
                        st.error("Notes too short. Please provide more details.")
                    else:
                        result = add_trail_condition(
                            hike_id=selected_trail_id,
                            user_id=user['id'],
                            condition=condition,
                            weather=weather if weather else None,
                            notes=notes
                        )
                        
                        if result and 'id' in result:
                            st.success("✅ Condition reported!")
                            st.rerun()
                        else:
                            st.error("Failed to submit report")
            
            # Guidelines
            st.markdown("---")
            st.info("""
            **Reporting Tips:**
            - Report recent conditions only
            - Be specific about obstacles
            - Mention weather impacts
            - Update if conditions change
            """)
    
    # TAB 2: Equipment
    with tab2:
        col_left, col_right = st.columns([2, 1])
        
        # Left: View equipment list
        with col_left:
            st.markdown("### 🎒 Recommended Gear")
            
            equipment = get_trail_equipment(selected_trail_id)
            
            if not equipment:
                st.info("No equipment recommendations yet. Add items to help others prepare!")
            else:
                # Separate required and optional
                required = [e for e in equipment if e['is_required']]
                optional = [e for e in equipment if not e['is_required']]
                
                if required:
                    st.markdown("#### ✅ Required Items")
                    for item in required:
                        with st.container():
                            st.markdown(f"**{item['item_name']}**")
                            st.markdown(f"*Category: {item['category']}*")
                            if item.get('notes'):
                                st.markdown(f"📝 {item['notes']}")
                            st.markdown("")
                
                if optional:
                    st.markdown("#### 🔹 Optional Items")
                    for item in optional:
                        with st.container():
                            st.markdown(f"**{item['item_name']}**")
                            st.markdown(f"*Category: {item['category']}*")
                            if item.get('notes'):
                                st.markdown(f"📝 {item['notes']}")
                            st.markdown("")
        
        # Right: Add equipment
        with col_right:
            st.markdown("### ➕ Add Equipment")
            
            # Only admins can add equipment
            if user.get('is_admin'):
                with st.form("add_equipment_form"):
                    item_name = st.text_input("Item Name*", placeholder="e.g., Hiking Boots")
                    
                    category = st.selectbox(
                        "Category",
                        options=['clothing', 'gear', 'safety', 'food', 'other']
                    )
                    
                    is_required = st.checkbox("Required Item", value=True)
                    
                    notes = st.text_area(
                        "Notes (optional)",
                        placeholder="Additional details about this item"
                    )
                    
                    submit = st.form_submit_button("Add Item", type="primary", use_container_width=True)
                    
                    if submit:
                        if not item_name:
                            st.error("Please enter an item name")
                        else:
                            result = add_equipment(
                                hike_id=selected_trail_id,
                                item_name=item_name,
                                category=category,
                                is_required=is_required,
                                notes=notes if notes else None
                            )
                            
                            if result and 'id' in result:
                                st.success("✅ Equipment added!")
                                st.rerun()
                            else:
                                st.error("Failed to add equipment")
            else:
                st.info("👑 Only admins can add equipment items. Contact an admin to suggest additions.")
                
                # Still show a form for suggestions
                st.markdown("**Suggest an item:**")
                suggestion = st.text_area("Item suggestion", placeholder="What gear would you recommend?")
                if st.button("Send Suggestion"):
                    st.success("Thanks for your suggestion! It's been noted.")

# Sidebar: Statistics
with st.sidebar:
    st.markdown("### 📊 Statistics")
    
    if selected_trail:
        conditions = get_trail_conditions(selected_trail_id)
        equipment = get_trail_equipment(selected_trail_id)
        
        st.metric("Condition Reports", len(conditions))
        st.metric("Equipment Items", len(equipment))
        
        if conditions:
            latest = conditions[0]
            condition_emoji = {
                'excellent': '🟢',
                'good': '🟡',
                'fair': '🟠',
                'poor': '🔴',
                'closed': '⛔'
            }.get(latest['condition'], '⚪')
            st.markdown(f"**Latest Status:** {condition_emoji} {latest['condition'].title()}")
    
    st.markdown("---")
    
    st.markdown("### 💡 Quick Tips")
    st.info("""
    **Trail Conditions:**
    - Report after completing a hike
    - Include weather info
    - Note any hazards
    
    **Equipment:**
    - Pack based on difficulty
    - Check weather forecast
    - Bring extra water
    - Don't forget first aid
    """)
