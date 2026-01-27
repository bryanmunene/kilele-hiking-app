"""
Reviews page - View and write trail reviews.
"""
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_all_hikes, get_reviews, create_review
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

init_database()

# Page configuration
st.set_page_config(
    page_title="Trail Reviews - Kilele",
    page_icon="⭐",
    layout="wide"
)
apply_nature_theme()

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to view and write reviews")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Helper functions
def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

@st.cache_data(ttl=30)
def fetch_hikes():
    """Fetch all hikes"""
    try:
        return get_all_hikes()
    except Exception as e:
        st.error(f"Error fetching hikes: {e}")
        return []

def fetch_hike_reviews(hike_id):
    """Fetch reviews for a specific hike"""
    try:
        return get_reviews(hike_id)
    except Exception as e:
        st.error(f"Error fetching reviews: {e}")
        return []

def submit_review(hike_id, rating, title, comment, difficulty_rating, conditions, visited_date):
    """Submit a new review"""
    try:
        user = get_current_user()
        
        # Check if user already reviewed
        existing_reviews = get_reviews(hike_id, user_id=user['id'])
        if any(r['user_id'] == user['id'] for r in existing_reviews):
            st.error("❌ You have already reviewed this trail")
            return False
        
        review = create_review(
            user_id=user['id'],
            hike_id=hike_id,
            rating=rating,
            comment=f"**{title}**\\n\\n{comment}\\n\\nDifficulty: {difficulty_rating}/5\\nConditions: {conditions}",
            visited_date=visited_date
        )
        
        if review:
            st.success("✅ Review submitted successfully!")
            st.cache_data.clear()
            return True
        
        st.error("❌ Failed to submit review")
        return False
    except Exception as e:
        st.error(f"Error submitting review: {e}")
        return False

def mark_review_helpful(review_id):
    """Mark a review as helpful"""
    try:
        from database import get_db
        from models import Review
        with get_db() as db:
            review = db.query(Review).filter(Review.id == review_id).first()
            if review:
                review.helpful_count = (review.helpful_count or 0) + 1
                db.commit()
                st.cache_data.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def render_star_rating(rating):
    """Render star rating display"""
    stars = "⭐" * int(rating)
    empty_stars = "☆" * (5 - int(rating))
    return f"{stars}{empty_stars} ({rating}/5)"

# Main app
st.title("⭐ Trail Reviews")
st.markdown("### Read and share your hiking experiences")

# Tabs
tab1, tab2 = st.tabs(["📖 Browse Reviews", "✍️ Write Review"])

# Tab 1: Browse Reviews
with tab1:
    st.subheader("Browse Trail Reviews")
    
    # Fetch hikes
    hikes = fetch_hikes()
    
    if not hikes:
        st.info("No trails available")
        st.stop()
    
    # Filter options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_hike = st.selectbox(
            "Select a trail to view reviews",
            options=hikes,
            format_func=lambda x: f"{x['name']} - {x['location']} ({x['difficulty']})",
            key="browse_hike_select"
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest", "Highest Rated", "Most Helpful"],
            key="sort_reviews"
        )
    
    if selected_hike:
        # Display trail info
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Distance", f"{selected_hike['distance_km']} km")
        with col2:
            st.metric("Difficulty", selected_hike['difficulty'])
        with col3:
            st.metric("Elevation", f"{selected_hike.get('elevation_gain_m', 0)} m")
        with col4:
            st.metric("Duration", f"{selected_hike['estimated_duration_hours']} hrs")
        
        st.markdown("---")
        
        # Fetch and display reviews
        reviews = fetch_hike_reviews(selected_hike['id'])
        
        if reviews:
            # Sort reviews
            if sort_by == "Newest":
                reviews.sort(key=lambda x: x['created_at'], reverse=True)
            elif sort_by == "Highest Rated":
                reviews.sort(key=lambda x: x['rating'], reverse=True)
            elif sort_by == "Most Helpful":
                reviews.sort(key=lambda x: x['helpful_count'], reverse=True)
            
            # Calculate average rating
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
            
            # Display summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='stat-card'><h3>{len(reviews)}</h3><p>Total Reviews</p></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='stat-card'><h3>{avg_rating:.1f}/5</h3><p>Average Rating</p></div>", unsafe_allow_html=True)
            with col3:
                difficulty_ratings = [r.get('difficulty_rating') for r in reviews if r.get('difficulty_rating')]
                avg_difficulty = sum(difficulty_ratings) / len(difficulty_ratings) if difficulty_ratings else 0
                st.markdown(f"<div class='stat-card'><h3>{avg_difficulty:.1f}/5</h3><p>Difficulty Rating</p></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display each review
            for review in reviews:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {review['title']}")
                    st.markdown(f"<div class='review-rating'>{render_star_rating(review['rating'])}</div>", unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"👍 Helpful ({review['helpful_count']})", key=f"helpful_{review['id']}"):
                        if mark_review_helpful(review['id']):
                            st.rerun()
                
                # Review metadata
                visited_date = datetime.fromisoformat(review['visited_date'].replace('Z', '+00:00')).strftime('%B %d, %Y') if review.get('visited_date') else 'N/A'
                st.markdown(f"<div class='review-meta'>By {review['username']} • Visited: {visited_date}</div>", unsafe_allow_html=True)
                
                # Review details
                if review.get('difficulty_rating'):
                    st.markdown(f"**Difficulty Rating:** {render_star_rating(review['difficulty_rating'])}")
                
                if review.get('conditions'):
                    st.markdown(f"**Trail Conditions:** {review['conditions']}")
                
                st.markdown(f"**Review:**")
                st.markdown(review['comment'])
                
                # Photos (if any)
                if review.get('photos') and len(review['photos']) > 0:
                    st.markdown("**Photos:**")
                    photo_cols = st.columns(min(len(review['photos']), 3))
                    for idx, photo in enumerate(review['photos'][:3]):
                        with photo_cols[idx]:
                            st.image(photo['photo_url'], caption=photo.get('caption', ''), use_column_width=True)
                
                st.markdown("---")
        else:
            st.info("No reviews yet for this trail. Be the first to review!")

# Tab 2: Write Review
with tab2:
    st.subheader("Write a Trail Review")
    st.markdown("Share your experience to help other hikers!")
    
    # Select trail
    hikes = fetch_hikes()
    
    selected_hike = st.selectbox(
        "Select the trail you hiked",
        options=hikes,
        format_func=lambda x: f"{x['name']} - {x['location']}",
        key="write_review_hike_select"
    )
    
    if selected_hike:
        # Review form
        with st.form("review_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                rating = st.slider(
                    "Overall Rating ⭐",
                    min_value=1,
                    max_value=5,
                    value=5,
                    help="Rate your overall experience"
                )
                
                difficulty_rating = st.slider(
                    "Difficulty Rating 🏔️",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="How difficult was the trail? (1=Very Easy, 5=Very Hard)"
                )
            
            with col2:
                visited_date = st.date_input(
                    "Date Visited 📅",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
                
                conditions = st.selectbox(
                    "Trail Conditions 🌤️",
                    [
                        "Excellent - Well maintained",
                        "Good - Minor issues",
                        "Fair - Some obstacles",
                        "Poor - Difficult to navigate",
                        "Muddy - Recent rain",
                        "Dry and dusty",
                        "Rocky and uneven",
                        "Overgrown - Needs clearing"
                    ]
                )
            
            title = st.text_input(
                "Review Title",
                placeholder="e.g., Amazing views and well-marked trail!",
                max_chars=100
            )
            
            comment = st.text_area(
                "Your Review",
                placeholder="Share details about your experience, what you enjoyed, tips for future hikers, etc.",
                height=200,
                max_chars=2000
            )
            
            submitted = st.form_submit_button("Submit Review", use_container_width=True)
            
            if submitted:
                if not title or not comment:
                    st.error("Please fill in both title and review")
                elif len(comment) < 20:
                    st.error("Please write a more detailed review (minimum 20 characters)")
                else:
                    success = submit_review(
                        hike_id=selected_hike['id'],
                        rating=rating,
                        title=title,
                        comment=comment,
                        difficulty_rating=difficulty_rating,
                        conditions=conditions,
                        visited_date=visited_date
                    )
                    
                    if success:
                        st.balloons()
                        st.success("✅ Your review has been submitted!")

# Footer
st.markdown("---")
st.markdown("*💡 Tip: Detailed reviews with photos help other hikers plan their adventures!*")
