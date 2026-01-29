"""
Achievements page - View badges, progress, and unlock new achievements.
"""
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_user_achievements, get_all_achievements, get_user_stats
from auth import is_authenticated, get_current_user
from nature_theme import apply_nature_theme

init_database()

# Page configuration
st.set_page_config(
    page_title="Achievements - Kilele",
    page_icon="🏆",
    layout="wide"
)
apply_nature_theme()

# Mobile responsive styles for achievements
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .achievement-card {
            width: 100% !important;
            margin: 10px 0 !important;
            padding: 15px !important;
        }
        .achievement-icon {
            font-size: 48px !important;
        }
        .achievement-name {
            font-size: 18px !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to view your achievements")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Helper functions
def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

@st.cache_data(ttl=30)
def fetch_achievements():
    """Fetch user achievements"""
    try:
        user = get_current_user()
        if user:
            return get_user_achievements(user['id'])
        return []
    except Exception as e:
        st.error(f"Error fetching achievements: {e}")
        return []

def render_achievement_card(achievement):
    """Render an achievement card"""
    is_earned = achievement.get('earned', False)
    progress = achievement.get('progress', 0)
    
    card_class = "achievement-card" if is_earned else "achievement-card achievement-locked"
    icon_class = "achievement-icon" if is_earned else "achievement-icon achievement-icon-locked"
    
    # Card container
    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
    
    # Icon
    st.markdown(f"<div class='{icon_class}'>{achievement['icon']}</div>", unsafe_allow_html=True)
    
    # Name
    st.markdown(f"<div class='achievement-name'>{achievement['name']}</div>", unsafe_allow_html=True)
    
    # Description
    st.markdown(f"<div class='achievement-description'>{achievement['description']}</div>", unsafe_allow_html=True)
    
    # Progress bar (for locked achievements with progress)
    if not is_earned and progress > 0:
        st.markdown(f"""
        <div class='progress-bar-container'>
            <div class='progress-bar' style='width: {progress}%'>{progress}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Points
    st.markdown(f"<div class='achievement-points'>🎯 {achievement['points']} points</div>", unsafe_allow_html=True)
    
    # Earned date (for completed achievements)
    if is_earned and achievement.get('earned_at'):
        earned_date = datetime.fromisoformat(achievement['earned_at'].replace('Z', '+00:00'))
        st.markdown(
            f"<div class='achievement-earned'>✅ Earned: {earned_date.strftime('%B %d, %Y')}</div>",
            unsafe_allow_html=True
        )
    elif not is_earned:
        st.markdown("<div class='achievement-earned'>🔒 Locked</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main app
st.title("🏆 Achievements & Badges")
st.markdown("### Your hiking accomplishments")

# Fetch achievements
achievements = fetch_achievements()

if not achievements:
    st.info("No achievements data available")
    st.stop()

# Calculate stats
earned_achievements = [a for a in achievements if a.get('earned', False)]
total_points = sum(a['points'] for a in earned_achievements)
total_possible_points = sum(a['points'] for a in achievements)

# Display overall stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='stats-card'>
        <h2>{len(earned_achievements)}/{len(achievements)}</h2>
        <p>Achievements Unlocked</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='stats-card'>
        <h2>{total_points}</h2>
        <p>Total Points</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    completion_pct = (len(earned_achievements) / len(achievements) * 100) if achievements else 0
    st.markdown(f"""
    <div class='stats-card'>
        <h2>{completion_pct:.1f}%</h2>
        <p>Completion Rate</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # Group by category
    categories = set(a['category'] for a in achievements)
    st.markdown(f"""
    <div class='stats-card'>
        <h2>{len(categories)}</h2>
        <p>Categories</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Filter and sort options
col1, col2, col3 = st.columns(3)

with col1:
    show_filter = st.selectbox(
        "Show",
        ["All Achievements", "Earned Only", "Locked Only"]
    )

with col2:
    category_filter = st.selectbox(
        "Category",
        ["All Categories"] + sorted(set(a['category'] for a in achievements))
    )

with col3:
    sort_by = st.selectbox(
        "Sort by",
        ["Category", "Points (High to Low)", "Points (Low to High)", "Name"]
    )

# Filter achievements
filtered_achievements = achievements

if show_filter == "Earned Only":
    filtered_achievements = [a for a in filtered_achievements if a.get('earned', False)]
elif show_filter == "Locked Only":
    filtered_achievements = [a for a in filtered_achievements if not a.get('earned', False)]

if category_filter != "All Categories":
    filtered_achievements = [a for a in filtered_achievements if a['category'] == category_filter]

# Sort achievements
if sort_by == "Points (High to Low)":
    filtered_achievements.sort(key=lambda x: x['points'], reverse=True)
elif sort_by == "Points (Low to High)":
    filtered_achievements.sort(key=lambda x: x['points'])
elif sort_by == "Name":
    filtered_achievements.sort(key=lambda x: x['name'])
else:  # Category
    filtered_achievements.sort(key=lambda x: (x['category'], x['name']))

# Display achievements by category
if sort_by == "Category":
    # Group by category
    categories_dict = {}
    for achievement in filtered_achievements:
        category = achievement['category']
        if category not in categories_dict:
            categories_dict[category] = []
        categories_dict[category].append(achievement)
    
    # Display each category
    for category in sorted(categories_dict.keys()):
        category_achievements = categories_dict[category]
        earned_in_category = sum(1 for a in category_achievements if a.get('earned', False))
        
        st.markdown(
            f"<div class='category-header'>"
            f"<h3>{category.capitalize()} ({earned_in_category}/{len(category_achievements)})</h3>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Display achievements in 3 columns
        cols_per_row = 3
        for i in range(0, len(category_achievements), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(category_achievements):
                    with col:
                        render_achievement_card(category_achievements[i + j])
else:
    # Display all filtered achievements
    if not filtered_achievements:
        st.info("No achievements match your filters")
    else:
        st.markdown(f"**Showing {len(filtered_achievements)} achievement(s)**")
        
        # Display achievements in 3 columns
        cols_per_row = 3
        for i in range(0, len(filtered_achievements), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered_achievements):
                    with col:
                        render_achievement_card(filtered_achievements[i + j])

# Footer with tips
st.markdown("---")
st.markdown("### 💡 How to Earn Achievements")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🥾 Complete Hikes**
    - Track your hikes to unlock milestones
    - Try different difficulty levels
    - Explore various locations
    """)

with col2:
    st.markdown("""
    **✍️ Write Reviews**
    - Share your experiences
    - Help other hikers
    - Upload trail photos
    """)

with col3:
    st.markdown("""
    **👥 Be Social**
    - Follow other hikers
    - Build your community
    - Stay consistent
    """)
