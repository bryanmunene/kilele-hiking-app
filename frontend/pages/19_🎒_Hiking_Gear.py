"""
Hiking Gear Catalog - Browse and discover essential hiking equipment with prices
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from auth import is_authenticated, get_current_user, restore_session_from_storage
from services import get_all_gear, get_gear_categories
from nature_theme import apply_nature_theme
from image_utils import display_image

st.set_page_config(page_title="Hiking Gear Catalog", page_icon="🎒", layout="wide")
apply_nature_theme()

# Restore session
restore_session_from_storage()

# Mobile responsive CSS
st.markdown("""
    <style>
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        .gear-card {
            margin-bottom: 1rem;
        }
    }
    
    .gear-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .gear-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .gear-price {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1e3a5f;
    }
    
    .gear-vendor {
        color: #4a6fa5;
        font-style: italic;
    }
    
    .required-badge {
        background: #ff6b6b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .optional-badge {
        background: #95e1d3;
        color: #1e3a5f;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .category-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #4a6fa5 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🎒 Hiking Gear Catalog")
st.markdown("**Essential equipment for your Kenyan hiking adventures**")

# Check authentication
if not is_authenticated():
    st.info("🔐 Login to bookmark gear and create shopping lists!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Login"):
            st.switch_page("pages/0_🔐_Login.py")

# Sidebar filters
st.sidebar.header("🔍 Filter Gear")

# Get all categories
categories = get_gear_categories()
selected_category = st.sidebar.selectbox(
    "Category",
    ["All"] + sorted(categories),
    index=0
)

# Price range filter
max_price = st.sidebar.slider(
    "Max Price (KES)",
    min_value=0,
    max_value=50000,
    value=50000,
    step=1000
)

show_required_only = st.sidebar.checkbox("Show required items only", value=False)

# Load gear
with st.spinner("Loading gear catalog..."):
    if selected_category == "All":
        all_gear = get_all_gear()
    else:
        all_gear = get_all_gear(category=selected_category)
    
    # Apply filters
    filtered_gear = [g for g in all_gear if (g['price'] or 0) <= max_price]
    
    if show_required_only:
        filtered_gear = [g for g in filtered_gear if g['is_required']]

# Summary stats
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Items", len(filtered_gear))

with col2:
    required_count = sum(1 for g in filtered_gear if g['is_required'])
    st.metric("Required Items", required_count)

with col3:
    total_required_cost = sum(g['price'] for g in filtered_gear if g['is_required'] and g['price'])
    st.metric("Essential Kit Cost", f"KES {total_required_cost:,.0f}")

with col4:
    avg_price = sum(g['price'] for g in filtered_gear if g['price']) / len([g for g in filtered_gear if g['price']]) if filtered_gear else 0
    st.metric("Avg. Price", f"KES {avg_price:,.0f}")

st.markdown("---")

# Group gear by category
gear_by_category = {}
for gear in filtered_gear:
    category = gear['category'] or 'Other'
    if category not in gear_by_category:
        gear_by_category[category] = []
    gear_by_category[category].append(gear)

# Display gear by category
if not filtered_gear:
    st.warning("No gear items found matching your filters.")
else:
    for category, items in sorted(gear_by_category.items()):
        # Category header
        st.markdown(f"""
            <div class="category-header">
                <h2 style="margin: 0;">{category.upper()}</h2>
                <p style="margin: 0; opacity: 0.9;">{len(items)} items</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Display items in grid
        cols = st.columns(3)
        for idx, gear in enumerate(items):
            with cols[idx % 3]:
                with st.container():
                    st.markdown('<div class="gear-card">', unsafe_allow_html=True)
                    
                    # Image
                    if gear['image_url']:
                        display_image(gear['image_url'], caption="", use_column_width=True)
                    else:
                        st.markdown("🎒")
                    
                    # Name and brand
                    st.markdown(f"**{gear['item_name']}**")
                    if gear['brand']:
                        st.caption(f"Brand: {gear['brand']}")
                    
                    # Required badge
                    if gear['is_required']:
                        st.markdown('<span class="required-badge">REQUIRED</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="optional-badge">OPTIONAL</span>', unsafe_allow_html=True)
                    
                    # Price
                    if gear['price']:
                        st.markdown(f'<div class="gear-price">KES {gear["price"]:,.0f}</div>', unsafe_allow_html=True)
                    
                    # Vendor
                    if gear['vendor']:
                        st.markdown(f'<div class="gear-vendor">📍 {gear["vendor"]}</div>', unsafe_allow_html=True)
                    
                    # Notes in expander
                    if gear['notes']:
                        with st.expander("📝 Details"):
                            st.write(gear['notes'])
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

# Shopping tips
st.markdown("---")
st.markdown("### 🛒 Shopping Tips")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Where to Buy in Nairobi:**
    - **Adventure Zone Nairobi** - Westlands (High-end gear)
    - **Outdoor Ventures** - Kilimani (Mid-range options)
    - **Decathlon Nairobi** - Rosslyn Mall (Budget-friendly)
    - **Safari Store Nairobi** - CBD (Specialized equipment)
    - **Sportsman Kenya** - Various locations (General outdoor)
    """)

with col2:
    st.markdown("""
    **Money-Saving Tips:**
    - 💰 Start with essentials, add optional gear later
    - 🤝 Consider renting expensive items (GPS, camping gear)
    - 👥 Share costs with hiking buddies (tents, stoves)
    - 🔄 Check second-hand options on Facebook groups
    - ⏰ Watch for sales during off-peak seasons (March-May)
    """)

# Footer
st.markdown("---")
st.info("""
💡 **Planning Your First Hike?**  
Focus on the "REQUIRED" items first. These cover safety essentials, proper footwear, 
hydration, and protection from the elements. Optional items enhance comfort but aren't 
critical for day hikes.
""")

# Quick shopping list generator
if is_authenticated():
    st.markdown("---")
    st.subheader("📋 My Shopping List")
    
    if 'shopping_list' not in st.session_state:
        st.session_state.shopping_list = []
    
    st.write("Coming soon: Create and save your custom shopping list!")
