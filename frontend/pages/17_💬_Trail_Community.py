import streamlit as st
from datetime import datetime
from services import add_trail_comment, get_trail_comments, get_all_hikes
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Trail Community - Kilele Explorers", page_icon="💬", layout="wide")
apply_nature_theme()

# Check if user is logged in
if 'user' not in st.session_state:
    st.warning("⚠️ Please log in to view and post trail comments")
    st.page_link("pages/3_🔐_Login.py", label="Go to Login", icon="🔐")
    st.stop()

user = st.session_state.user

# Page header
st.title("💬 Trail Community")
st.markdown("Share experiences, tips, and connect with fellow hikers")

# Get all trails for selection
trails = get_all_hikes()

if not trails:
    st.error("No trails found. Please add trails first.")
    st.stop()

# Trail selection
selected_trail_id = st.selectbox(
    "Select a Trail",
    options=[t['id'] for t in trails],
    format_func=lambda x: next((t['name'] for t in trails if t['id'] == x), "Unknown"),
    key="trail_select"
)

selected_trail = next((t for t in trails if t['id'] == selected_trail_id), None)

if selected_trail:
    # Display trail info
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
    
    # Two-column layout: Comments and Post New
    col_left, col_right = st.columns([2, 1])
    
    # Left: Display comments
    with col_left:
        st.markdown("### 💭 Community Comments")
        
        # Get comments for this trail
        comments = get_trail_comments(selected_trail_id)
        
        # Separate parent comments and replies
        parent_comments = [c for c in comments if c['parent_id'] is None]
        replies_dict = {}
        for c in comments:
            if c['parent_id']:
                if c['parent_id'] not in replies_dict:
                    replies_dict[c['parent_id']] = []
                replies_dict[c['parent_id']].append(c)
        
        if not parent_comments:
            st.info("👋 No comments yet. Be the first to share your experience!")
        else:
            # Display parent comments and their replies
            for comment in sorted(parent_comments, key=lambda x: x['created_at'], reverse=True):
                with st.container():
                    # Comment header
                    comment_time = datetime.fromisoformat(comment['created_at'])
                    time_str = comment_time.strftime("%B %d, %Y at %I:%M %p")
                    
                    st.markdown(f"**{comment['username']}** · {time_str}")
                    st.markdown(comment['comment'])
                    
                    # Reply button
                    reply_key = f"reply_{comment['id']}"
                    col_reply1, col_reply2 = st.columns([1, 5])
                    with col_reply1:
                        if st.button("💬 Reply", key=reply_key):
                            st.session_state[f"show_reply_{comment['id']}"] = True
                    
                    # Show reply form if button clicked
                    if st.session_state.get(f"show_reply_{comment['id']}", False):
                        with st.form(f"reply_form_{comment['id']}"):
                            reply_text = st.text_area("Your reply", key=f"reply_text_{comment['id']}")
                            col_submit, col_cancel = st.columns(2)
                            
                            with col_submit:
                                submit_reply = st.form_submit_button("Post Reply", type="primary")
                            with col_cancel:
                                cancel_reply = st.form_submit_button("Cancel")
                            
                            if submit_reply and reply_text:
                                result = add_trail_comment(
                                    hike_id=selected_trail_id,
                                    user_id=user['id'],
                                    comment=reply_text,
                                    parent_id=comment['id']
                                )
                                if result and 'id' in result:
                                    st.success("✅ Reply posted!")
                                    st.session_state[f"show_reply_{comment['id']}"] = False
                                    st.rerun()
                            
                            if cancel_reply:
                                st.session_state[f"show_reply_{comment['id']}"] = False
                                st.rerun()
                    
                    # Display replies
                    if comment['id'] in replies_dict:
                        st.markdown("---")
                        for reply in replies_dict[comment['id']]:
                            reply_time = datetime.fromisoformat(reply['created_at'])
                            reply_time_str = reply_time.strftime("%B %d, %Y at %I:%M %p")
                            
                            with st.container():
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↪️ **{reply['username']}** · {reply_time_str}")
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{reply['comment']}")
                    
                    st.markdown("---")
    
    # Right: Post new comment
    with col_right:
        st.markdown("### ✍️ Share Your Experience")
        
        with st.form("new_comment_form", clear_on_submit=True):
            comment_text = st.text_area(
                "Your comment",
                placeholder="Share tips, experiences, or ask questions...",
                height=150,
                help="Be respectful and helpful to fellow hikers"
            )
            
            submit = st.form_submit_button("Post Comment", type="primary", use_container_width=True)
            
            if submit:
                if not comment_text:
                    st.error("Please enter a comment")
                elif len(comment_text) < 10:
                    st.error("Comment too short. Please write at least 10 characters")
                else:
                    result = add_trail_comment(
                        hike_id=selected_trail_id,
                        user_id=user['id'],
                        comment=comment_text
                    )
                    
                    if result and 'id' in result:
                        st.success("✅ Comment posted successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to post comment")
        
        # Guidelines
        st.markdown("---")
        st.markdown("### 📝 Community Guidelines")
        st.info("""
        - Be respectful and courteous
        - Share helpful tips and experiences
        - Ask questions if you're unsure
        - Report safety issues
        - No spam or promotional content
        """)

# Sidebar: Statistics and top trails
with st.sidebar:
    st.markdown("### 📊 Community Stats")
    
    total_comments = len(comments) if selected_trail else 0
    parent_count = len([c for c in comments if c['parent_id'] is None]) if comments else 0
    replies_count = total_comments - parent_count
    
    st.metric("Total Comments", total_comments)
    st.metric("Discussions", parent_count)
    st.metric("Replies", replies_count)
    
    st.markdown("---")
    
    st.markdown("### 🔥 Most Discussed Trails")
    
    # Count comments per trail
    trail_comment_counts = {}
    for trail in trails:
        trail_comments = get_trail_comments(trail['id'])
        trail_comment_counts[trail['id']] = len(trail_comments)
    
    # Sort and display top 5
    top_trails = sorted(trail_comment_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for trail_id, count in top_trails:
        trail = next((t for t in trails if t['id'] == trail_id), None)
        if trail and count > 0:
            st.markdown(f"**{trail['name']}**")
            st.markdown(f"💬 {count} comments")
            st.markdown("")
    
    if not any(count > 0 for _, count in top_trails):
        st.info("No comments yet on any trails")
