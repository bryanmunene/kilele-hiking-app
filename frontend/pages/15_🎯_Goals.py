import streamlit as st
from datetime import datetime, timedelta
from services import create_goal, get_user_goals, update_goal_progress
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Goals - Kilele Explorers", page_icon="🎯", layout="wide")
apply_nature_theme()

# Check if user is logged in
if 'user' not in st.session_state:
    st.warning("⚠️ Please log in to view your goals")
    st.page_link("pages/3_🔐_Login.py", label="Go to Login", icon="🔐")
    st.stop()

user = st.session_state.user

# Page header
st.title("🎯 Hiking Goals")
st.markdown("Set and track your hiking achievements")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Active Goals", "✅ Completed", "➕ Create New Goal"])

# Get user goals
user_goals = get_user_goals(user['id'])
active_goals = [g for g in user_goals if g['status'] in ['active', 'in_progress']]
completed_goals = [g for g in user_goals if g['status'] == 'completed']

# Tab 1: Active Goals
with tab1:
    if not active_goals:
        st.info("🎯 No active goals yet. Create your first goal in the 'Create New Goal' tab!")
    else:
        for goal in active_goals:
            with st.expander(f"🎯 {goal['title']}", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # Progress bar
                    progress = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
                    st.progress(min(progress / 100, 1.0))
                    st.markdown(f"**Progress:** {goal['current_value']}/{goal['target_value']}")
                    
                    # Goal type details
                    goal_types = {
                        'distance': '🏃 Distance (km)',
                        'elevation': '⛰️ Elevation Gain (m)',
                        'hikes_count': '🥾 Number of Hikes',
                        'duration': '⏱️ Total Duration (hours)'
                    }
                    st.markdown(f"**Type:** {goal_types.get(goal['goal_type'], goal['goal_type'])}")
                
                with col2:
                    if goal['deadline']:
                        deadline = datetime.fromisoformat(goal['deadline'])
                        days_left = (deadline - datetime.now()).days
                        if days_left > 0:
                            st.metric("Days Left", days_left)
                        else:
                            st.metric("Days Left", 0)
                            st.error("⚠️ Deadline passed")
                    else:
                        st.info("No deadline set")
                
                with col3:
                    st.metric("Status", goal['status'].replace('_', ' ').title())
                
                # Update progress
                st.markdown("---")
                st.markdown("**Update Progress:**")
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    new_value = st.number_input(
                        "Current value",
                        min_value=0.0,
                        max_value=float(goal['target_value'] * 2),
                        value=float(goal['current_value']),
                        step=1.0,
                        key=f"goal_{goal['id']}"
                    )
                
                with col_b:
                    if st.button("Update", key=f"update_{goal['id']}", type="primary"):
                        result = update_goal_progress(goal['id'], new_value)
                        if result:
                            st.success("✅ Progress updated!")
                            st.rerun()
                        else:
                            st.error("Failed to update progress")

# Tab 2: Completed Goals
with tab2:
    if not completed_goals:
        st.info("✅ No completed goals yet. Keep pushing!")
    else:
        st.success(f"🎉 You've completed {len(completed_goals)} goal(s)!")
        
        for goal in completed_goals:
            with st.expander(f"✅ {goal['title']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Target:** {goal['target_value']}")
                    st.markdown(f"**Achieved:** {goal['current_value']}")
                    
                    goal_types = {
                        'distance': '🏃 Distance (km)',
                        'elevation': '⛰️ Elevation Gain (m)',
                        'hikes_count': '🥾 Number of Hikes',
                        'duration': '⏱️ Total Duration (hours)'
                    }
                    st.markdown(f"**Type:** {goal_types.get(goal['goal_type'], goal['goal_type'])}")
                
                with col2:
                    if goal['completed_at']:
                        completed_date = datetime.fromisoformat(goal['completed_at'])
                        st.markdown(f"**Completed:** {completed_date.strftime('%B %d, %Y')}")
                    
                    st.success("🏆 Goal Achieved!")

# Tab 3: Create New Goal
with tab3:
    st.markdown("### Create a New Hiking Goal")
    
    with st.form("create_goal_form"):
        goal_title = st.text_input("Goal Title", placeholder="e.g., Conquer Mount Kenya")
        
        goal_type = st.selectbox(
            "Goal Type",
            options=['distance', 'elevation', 'hikes_count', 'duration'],
            format_func=lambda x: {
                'distance': '🏃 Total Distance (km)',
                'elevation': '⛰️ Total Elevation Gain (m)',
                'hikes_count': '🥾 Number of Hikes',
                'duration': '⏱️ Total Duration (hours)'
            }[x]
        )
        
        target_value = st.number_input(
            "Target Value",
            min_value=1.0,
            max_value=10000.0,
            value=10.0,
            step=1.0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            set_deadline = st.checkbox("Set a deadline")
        
        deadline = None
        if set_deadline:
            with col2:
                deadline_date = st.date_input(
                    "Deadline",
                    min_value=datetime.now(),
                    value=datetime.now() + timedelta(days=30)
                )
                deadline = datetime.combine(deadline_date, datetime.min.time())
        
        submitted = st.form_submit_button("Create Goal", type="primary")
        
        if submitted:
            if not goal_title:
                st.error("Please enter a goal title")
            else:
                result = create_goal(
                    user_id=user['id'],
                    title=goal_title,
                    goal_type=goal_type,
                    target_value=target_value,
                    deadline=deadline.isoformat() if deadline else None
                )
                
                if result and 'id' in result:
                    st.success(f"✅ Goal created successfully! ID: {result['id']}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create goal")

# Sidebar statistics
with st.sidebar:
    st.markdown("### 📊 Goal Statistics")
    st.metric("Active Goals", len(active_goals))
    st.metric("Completed Goals", len(completed_goals))
    
    if user_goals:
        total_progress = sum([
            (g['current_value'] / g['target_value'] * 100) 
            for g in active_goals 
            if g['target_value'] > 0
        ])
        avg_progress = total_progress / len(active_goals) if active_goals else 0
        st.metric("Average Progress", f"{avg_progress:.1f}%")
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("""
    - Set realistic, achievable goals
    - Break big goals into smaller milestones
    - Update your progress regularly
    - Celebrate when you complete a goal!
    """)
