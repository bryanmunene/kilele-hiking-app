import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Import new unified modules
from database import init_database, get_db
from services import get_all_hikes, create_bookmark
from auth import is_authenticated, get_current_user, restore_session_from_storage
from image_utils import display_image
from nature_theme import apply_nature_theme
from models import Hike

# Initialize database
init_database()

# Auto-seed if database is empty (for Streamlit Cloud deployment)
with get_db() as db:
    hike_count = db.query(Hike).count()
    if hike_count == 0:
        try:
            import seed_database
            seed_database.seed_database()
        except Exception as e:
            st.error(f"⚠️ Error seeding database: {e}")

# Restore session from browser storage (keeps Nesh logged in on refresh)
restore_session_from_storage()

# Page configuration
st.set_page_config(
    page_title="Kilele Hiking Trails",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply nature theme
apply_nature_theme()

# Additional Home page specific styles (hero animations, etc.)
st.markdown("""
    <style>
    /* Animated Background Logo */
    @keyframes float {
        0%, 100% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-20px) scale(1.05); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.15; }
        50% { opacity: 0.25; }
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 0.85; }
    }
    
    /* Hero Section Enhancements */
    .hero-section {
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 400px;
        height: 400px;
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" font-size="60">🏔️</text></svg>');
        background-size: cover;
        background-position: center;
        opacity: 0.3;
        animation: float 6s ease-in-out infinite, pulse 4s ease-in-out infinite;
        z-index: 0;
        filter: blur(2px) drop-shadow(0 0 10px rgba(255,255,255,0.3));
        border-radius: 50%;
    }
    
    .hero-section::after {
        content: '';
        position: absolute;
        top: 15%;
        right: 5%;
        width: 200px;
        height: 200px;
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" font-size="50">🌲</text></svg>');
        background-size: cover;
        background-position: center;
        opacity: 0.25;
        animation: float 8s ease-in-out infinite reverse;
        z-index: 0;
        filter: blur(1px) drop-shadow(0 0 8px rgba(255,255,255,0.2));
        border-radius: 50%;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-size: 52px;
        font-weight: bold;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: slideInDown 1s ease-out;
    }
    
    .hero-subtitle {
        font-size: 24px;
        margin-bottom: 10px;
        opacity: 0.95;
        animation: slideInUp 1s ease-out 0.2s both;
    }
    
    .hero-tagline {
        font-size: 18px;
        opacity: 0.85;
        font-style: italic;
        animation: fadeIn 1s ease-out 0.4s both;
    }
    
    /* Mobile optimizations for hero */
    @media (max-width: 768px) {
        .hero-section::before {
            width: 200px;
            height: 200px;
        }
        .hero-section::after {
            width: 100px;
            height: 100px;
        }
        .hero-title {
            font-size: 28px !important;
        }
        .hero-subtitle {
            font-size: 16px !important;
        }
        .hero-tagline {
            font-size: 14px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_hikes(difficulty=None):
    """Fetch hikes from the database"""
    try:
        # Convert "All" to None for no filtering
        if difficulty == "All":
            difficulty = None
        hikes = get_all_hikes(difficulty=difficulty)
        print(f"DEBUG: Fetched {len(hikes)} hikes (filter: {difficulty})")  # Debug output
        return hikes
    except Exception as e:
        st.error(f"❌ Error fetching hikes: {str(e)}")
        import traceback
        st.code(traceback.format_exc())  # Show full error
        return []

def get_difficulty_class(difficulty):
    """Return CSS class for difficulty level"""
    return f"difficulty-{difficulty.lower()}"

def display_hike_card(hike):
    """Display a single hike in a card format"""
    # Modern card with smaller image and better layout
    st.markdown(f"""
        <div style="
            background: white;
            border-radius: 15px;
            padding: 0;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        ">
    """, unsafe_allow_html=True)
    
    # Create two-column layout for image and content
    col_img, col_content = st.columns([1, 2])
    
    with col_img:
        # Display smaller image
        if hike.get('image_url'):
            display_image(hike['image_url'], use_column_width=True)
        else:
            # Use unique gradient based on trail name hash
            import hashlib
            hash_val = int(hashlib.md5(hike['name'].encode()).hexdigest(), 16)
            gradients = [
                "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
                "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
                "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
                "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
                "linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%)",
            ]
            emojis = ["🏔️", "🌲", "⛰️", "🏞️", "🌄", "🗻", "🏕️", "🌅"]
            gradient = gradients[hash_val % len(gradients)]
            emoji = emojis[hash_val % len(emojis)]
            
            st.markdown(f"""
                <div style="
                    width: 100%;
                    height: 200px;
                    background: {gradient};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 60px;
                ">{emoji}</div>
            """, unsafe_allow_html=True)
    
    with col_content:
        # Title and location
        st.markdown(f"### {hike['name']}")
        st.markdown(f"📍 **{hike['location']}**")
        
        # Quick stats in compact layout
        col1, col2, col3 = st.columns(3)
        with col1:
            difficulty_colors = {'Easy': '#51cf66', 'Moderate': '#ffd43b', 'Hard': '#ff6b6b'}
            difficulty_color = difficulty_colors.get(hike['difficulty'], '#868e96')
            st.markdown(f"<span style='background: {difficulty_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;'>{hike['difficulty']}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"📍 **{hike['distance_km']} km**")
        with col3:
            st.markdown(f"⏱️ **{hike['estimated_duration_hours']} hrs**")
        
        # Short description
        if hike.get('description'):
            preview = hike['description'][:120] + "..." if len(hike['description']) > 120 else hike['description']
            st.markdown(f"<p style='color: #666; font-size: 0.95rem; margin-top: 0.5rem;'>{preview}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Details in expandable section - compact and clean
    with st.expander("🔍 View Full Trail Details", expanded=False):
        # Two-column layout
        col_specs, col_desc = st.columns([1, 2])
        
        with col_specs:
            st.markdown("#### 📊 Specs")
            st.markdown(f"📏 {hike['distance_km']} km")
            st.markdown(f"⏱️ {hike['estimated_duration_hours']} hrs")
            if hike.get('elevation_gain_m'):
                st.markdown(f"⛰️ {hike['elevation_gain_m']} m")
            st.markdown(f"🗺️ {hike.get('trail_type', 'N/A')}")
            if hike.get('best_season'):
                st.markdown(f"🌤️ {hike['best_season']}")
            
            if hike.get('latitude') and hike.get('longitude'):
                st.markdown(f"""  
                📍 `{hike['latitude']}, {hike['longitude']}`  \n                [View on Map ↗️](https://www.google.com/maps?q={hike['latitude']},{hike['longitude']})\n                """)
        
        with col_desc:
            st.markdown("#### 📝 About")
            if hike.get('description'):
                st.write(hike['description'])
            else:
                st.info("No description available")
        
        # Trail Conditions (compact)
        st.markdown("---")
        st.markdown("#### 🌤️ Recent Trail Conditions")
        from services import get_trail_conditions
        conditions = get_trail_conditions(hike['id'], limit=2)
        if conditions:
            for cond in conditions:
                condition_emoji = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴', 'closed': '⛔'}.get(cond['condition'], '⚪')
                st.markdown(f"{condition_emoji} **{cond['condition'].title()}** - {cond['notes'][:80]}... *({cond['created_at'][:10]})*")
        else:
            st.info("ℹ️ No recent condition reports")
        
        # Quick action buttons
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if is_authenticated():
                if st.button("❤️ Save Trail", key=f"save_{hike['id']}", use_container_width=True):
                    try:
                        user = get_current_user()
                        create_bookmark(user['id'], hike['id'])
                        st.success("✅ Saved!")
                    except ValueError as e:
                        st.info(str(e))
        with col_btn2:
            st.markdown(f"[🗺️ View on Map](javascript:void(0))", unsafe_allow_html=True)
        with col_btn3:
            st.markdown(f"[📝 Add Review](javascript:void(0))", unsafe_allow_html=True)

def main():
    # Hero Section with Animated Background
    st.markdown("""
        <div class='hero-section'>
            <div class='hero-content'>
                <div class='hero-title'>🏔️ KILELE EXPLORERS</div>
                <div class='hero-subtitle'>Discover Kenya's Most Beautiful Hiking Trails</div>
                <div class='hero-tagline'>"Where Every Step Tells a Story"</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Welcome message for authenticated users
    if is_authenticated():
        user = get_current_user()
        st.success(f"👋 Welcome back, **{user['username']}**! Ready for your next adventure?")
    
    # About Kilele Explorers Section
    st.markdown("<h2 style='color: white !important;'>🌍 About Kilele Explorers</h2>", unsafe_allow_html=True)
    col_about1, col_about2 = st.columns([2, 1])
    
    with col_about1:
        st.markdown("""
        <div class='about-section'>
            <h3 style='color: white !important;'>Your Gateway to Kenya's Natural Wonders</h3>
            <p style='font-size: 16px; line-height: 1.8;'>
                <strong>Kilele Explorers</strong> is Kenya's premier hiking trail discovery platform, 
                dedicated to connecting adventure seekers with the most breathtaking trails across the country. 
                Whether you're a seasoned mountaineer or a weekend nature enthusiast, we provide comprehensive 
                trail information to make your hiking experience safe, memorable, and extraordinary.
            </p>
            <p style='font-size: 16px; line-height: 1.8;'>
                From the majestic peaks of Mount Kenya to the serene forests of Karura, 
                we bring you detailed insights, GPS coordinates, difficulty ratings, and real-time tracking 
                to ensure every adventure is perfectly planned.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_about2:
        st.markdown("")
        st.markdown("")
        st.info("**📍 Based in Nairobi, Kenya**\n\n🏔️ Covering 100+ trails\n\n✅ Expert-verified routes")
    
    # Why Choose Kilele Explorers
    st.markdown("## ✨ Why Choose Kilele Explorers?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>🗺️</div>
                <div class='feature-title'>Detailed Trail Maps</div>
                <p>GPS coordinates, elevation profiles, and interactive maps for precise navigation</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>📍</div>
                <div class='feature-title'>Real-Time Tracking</div>
                <p>Track your hike progress with live GPS updates and safety monitoring</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>🏆</div>
                <div class='feature-title'>Verified Trails</div>
                <p>Every trail is verified by expert hikers and local guides</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-icon'>👥</div>
                <div class='feature-title'>Community Driven</div>
                <p>Join thousands of hikers sharing experiences and recommendations</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    
    # Sidebar filters
    st.sidebar.header("🔍 Search & Filters")
    
    # Search box
    search_query = st.sidebar.text_input("🔎 Search trails", placeholder="Enter trail name...")
    
    difficulty_options = ["All", "Easy", "Moderate", "Hard", "Extreme"]
    selected_difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        difficulty_options,
        index=0
    )
    
    # Distance filter
    distance_range = st.sidebar.slider("Distance Range (km)", 0.0, 100.0, (0.0, 100.0))
    
    # Sort options
    sort_by = st.sidebar.selectbox(
        "Sort By",
        ["Name", "Distance (Low to High)", "Distance (High to Low)", "Duration", "Difficulty"]
    )
    
    # Export options
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Data")
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info(
        "This app showcases hiking trails across Kenya. "
        "Use filters to find your perfect adventure!\n\n"
        "🗺️ Check the **Map View** page to see trail locations.\n\n"
        "➕ Visit **Add Trail** to contribute new trails."
    )
    
    # Fetch and display hikes
    with st.spinner("🔄 Loading trails..."):
        hikes = fetch_hikes(selected_difficulty)
    
    if not hikes:
        st.warning("⚠️ No trails found in database.")
        st.info("💡 Run the seed script to add trails:")
        st.code("python seed_database.py", language="bash")
        
        # Check database
        try:
            from database import get_db
            with get_db() as db:
                from models import Hike
                count = db.query(Hike).count()
                st.write(f"Database has {count} trails")
        except Exception as e:
            st.error(f"Database error: {e}")
        return
    
    # Apply search filter
    if search_query:
        hikes = [h for h in hikes if search_query.lower() in h['name'].lower() 
                 or search_query.lower() in h['location'].lower()]
    
    # Apply distance filter
    hikes = [h for h in hikes if distance_range[0] <= h['distance_km'] <= distance_range[1]]
    
    # Sort hikes
    if sort_by == "Name":
        hikes.sort(key=lambda x: x['name'])
    elif sort_by == "Distance (Low to High)":
        hikes.sort(key=lambda x: x['distance_km'])
    elif sort_by == "Distance (High to Low)":
        hikes.sort(key=lambda x: x['distance_km'], reverse=True)
    elif sort_by == "Duration":
        hikes.sort(key=lambda x: x['estimated_duration_hours'])
    elif sort_by == "Difficulty":
        difficulty_order = {"Easy": 1, "Moderate": 2, "Hard": 3, "Extreme": 4}
        hikes.sort(key=lambda x: difficulty_order.get(x['difficulty'], 5))
    
    if not hikes:
        st.warning(f"😕 No trails match your search criteria")
        return
    
    # Platform Statistics
    st.markdown("## 📊 Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class='stat-box'>
                <div class='stat-number'>""" + str(len(hikes)) + """</div>
                <div class='stat-label'>Active Trails</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_distance = sum(h['distance_km'] for h in hikes) / len(hikes)
        st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-number'>{avg_distance:.1f}</div>
                <div class='stat-label'>Avg Distance (km)</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_distance = sum(h['distance_km'] for h in hikes)
        st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-number'>{total_distance:.0f}</div>
                <div class='stat-label'>Total Trail Distance (km)</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    
    # Featured Trails Section - Compact Horizontal Cards
    st.markdown("## 🌟 Featured Trails")
    st.caption("Must-visit trails handpicked by our community")
    
    # Select diverse featured trails (different difficulties)
    featured_hikes = []
    difficulties_shown = set()
    for hike in hikes:
        if hike['difficulty'] not in difficulties_shown and len(featured_hikes) < 3:
            featured_hikes.append(hike)
            difficulties_shown.add(hike['difficulty'])
        if len(featured_hikes) >= 3:
            break
    if len(featured_hikes) < 3:
        featured_hikes = hikes[:3] if len(hikes) >= 3 else hikes
    
    # Display as horizontal cards
    cols = st.columns(3)
    for idx, hike in enumerate(featured_hikes):
        with cols[idx]:
            st.markdown(f"""
                <div style="background: white; border-radius: 12px; overflow: hidden; 
                box-shadow: 0 3px 10px rgba(0,0,0,0.15); margin-bottom: 1rem;">
            """, unsafe_allow_html=True)
            
            if hike.get('image_url'):
                display_image(hike['image_url'], use_column_width=True)
            else:
                import hashlib
                hash_val = int(hashlib.md5(hike['name'].encode()).hexdigest(), 16)
                gradients = ["linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                           "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                           "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"]
                st.markdown(f"""<div style="height: 150px; background: {gradients[hash_val % 3]}; 
                display: flex; align-items: center; justify-content: center; font-size: 50px;">🏔️</div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**{hike['name']}**")
            st.caption(f"📍 {hike['location']}")
            difficulty_colors = {'Easy': '#51cf66', 'Moderate': '#ffd43b', 'Hard': '#ff6b6b', 'Extreme': '#9c27b0'}
            color = difficulty_colors.get(hike['difficulty'], '#868e96')
            st.markdown(f"<span style='background: {color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem;'>{hike['difficulty']}</span>", unsafe_allow_html=True)
            st.markdown(f"📏 {hike['distance_km']} km · ⏱️ {hike['estimated_duration_hours']} hrs")
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("---")
    
    # Services Section
    st.markdown("## 🎯 Our Services")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("""
        ### 🗺️ Trail Discovery
        - Comprehensive trail database
        - Detailed route information
        - Difficulty ratings
        - GPS coordinates
        - Best season recommendations
        """)
    
    with col_s2:
        st.markdown("""
        ### 📱 Hike Tracking
        - Real-time GPS tracking
        - Distance monitoring
        - Duration tracking
        - Performance analytics
        - Safety check-ins
        """)
    
    with col_s3:
        st.markdown("""
        ### 👥 Community Features
        - User profiles
        - Hike history
        - Favorite trails
        - Reviews & ratings
        - Photo sharing
        """)
    
    st.markdown("")
    
    # Call to Action
    st.markdown("## 🚀 Ready to Start Your Adventure?")
    
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    with col_cta2:
        if not is_authenticated():
            st.info("**Sign up today** to unlock personalized trail recommendations, track your hikes, and join our community of explorers!")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔐 Login / Register", type="primary", use_container_width=True):
                    st.switch_page("pages/0_🔐_Login.py")
            with col_btn2:
                if st.button("🗺️ Explore Map", use_container_width=True):
                    st.switch_page("pages/1_🗺️_Map_View.py")
        else:
            st.success("**You're all set!** Start exploring trails or track your next hike.")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📍 Track a Hike", type="primary", use_container_width=True):
                    st.switch_page("pages/5_📍_Track_Hike.py")
            with col_btn2:
                if st.button("👤 My Profile", use_container_width=True):
                    st.switch_page("pages/4_👤_Profile.py")
    
    st.markdown("")
    st.markdown("---")
    
    # Charts
    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Difficulty distribution
        df = pd.DataFrame(hikes)
        difficulty_counts = df['difficulty'].value_counts().reset_index()
        difficulty_counts.columns = ['Difficulty', 'Count']
        
        fig1 = px.pie(difficulty_counts, values='Count', names='Difficulty',
                     title='Trail Difficulty Distribution',
                     color='Difficulty',
                     color_discrete_map={'Easy': '#4caf50', 'Moderate': '#ff9800', 
                                        'Hard': '#f44336', 'Extreme': '#9c27b0'})
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # Distance vs Duration scatter
        fig2 = px.scatter(df, x='distance_km', y='estimated_duration_hours',
                         color='difficulty', size='elevation_gain_m',
                         title='Distance vs Duration',
                         labels={'distance_km': 'Distance (km)', 
                                'estimated_duration_hours': 'Duration (hours)'},
                         color_discrete_map={'Easy': '#4caf50', 'Moderate': '#ff9800', 
                                           'Hard': '#f44336', 'Extreme': '#9c27b0'})
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # Export buttons
    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 2])
    with col_exp1:
        csv_data = pd.DataFrame(hikes).to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="kilele_trails.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_exp2:
        try:
            from io import BytesIO
            excel_buffer = BytesIO()
            pd.DataFrame(hikes).to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer,
                file_name="kilele_trails.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel export error: {str(e)}")
    
    # All Trails Section
    st.markdown("## 🏔️ All Available Trails")
    st.markdown(f"*Showing {len(hikes)} trails matching your criteria*")
    st.markdown("")
    
    # Display hikes
    for hike in hikes:
        display_hike_card(hike)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 30px;'>
            <h3 style='color: #2e7d32;'>🏔️ KILELE EXPLORERS</h3>
            <p style='color: #666; font-size: 16px;'>
                Your trusted companion for hiking adventures in Kenya<br>
                📧 info@kileleexplorers.co.ke | 📞 +254 700 000 000<br>
                📍 Nairobi, Kenya
            </p>
            <p style='color: #999; font-size: 14px;'>
                Built with ❤️ using FastAPI & Streamlit | 
                © 2026 Kilele Explorers. All rights reserved.
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
