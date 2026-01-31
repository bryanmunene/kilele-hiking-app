"""
Register for Upcoming Hikes with M-Pesa Payment
Browse upcoming organized hikes and register with payment
"""
import streamlit as st
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import is_authenticated, get_current_user, restore_session_from_storage
from services import get_all_hikes, get_user_planned_hikes, register_for_hike, create_payment, update_payment_status, get_user_registrations
from image_utils import display_image
from nature_theme import apply_nature_theme
from mpesa_service import initiate_stk_push, format_phone_number_display, validate_mpesa_amount

# Restore session
restore_session_from_storage()

# Page config
st.set_page_config(
    page_title="Register for Hikes - Kilele",
    page_icon="🎫",
    layout="wide"
)
apply_nature_theme()

# Auth check
if not is_authenticated():
    st.warning("⚠️ Please login to register for hikes")
    st.stop()

user = get_current_user()

st.title("🎫 Register for Upcoming Hikes")
st.markdown("Browse and register for organized group hikes. Pay securely via M-Pesa.")

# Tabs for different views
tab1, tab2 = st.tabs(["📅 Available Hikes", "✅ My Registrations"])

with tab1:
    st.markdown("### Upcoming Organized Hikes")
    
    # Get actual upcoming hikes from database (created by admins)
    from database import get_db
    from models import PlannedHike, Hike, HikeRegistration, User
    
    try:
        with get_db() as db:
            # Get all planned hikes that are upcoming and planned status
            planned_hikes_query = db.query(PlannedHike).filter(
                PlannedHike.status == "planned",
                PlannedHike.planned_date >= datetime.now()
            ).order_by(PlannedHike.planned_date.asc()).all()
            
            # Convert to list of dicts
            sample_hikes = []
            for ph in planned_hikes_query:
                hike = db.query(Hike).filter(Hike.id == ph.hike_id).first()
                if not hike:
                    continue
                
                # Count current registrations
                current_registrations = db.query(HikeRegistration).filter(
                    HikeRegistration.planned_hike_id == ph.id,
                    HikeRegistration.status != "cancelled"
                ).count()
                
                # Get organizer
                organizer = db.query(User).filter(User.id == ph.user_id).first()
                
                sample_hikes.append({
                    "id": ph.id,
                    "hike_name": hike.name,
                    "location": hike.location,
                    "date": ph.planned_date.isoformat(),
                    "price": ph.price or 0,
                    "max_participants": ph.max_participants or 20,
                    "current_participants": current_registrations,
                    "organizer": organizer.username if organizer else "Kilele Adventures",
                    "description": ph.notes or hike.description or "Join us for an amazing hiking experience!",
                    "difficulty": hike.difficulty
                })
    
    except Exception as e:
        st.error(f"Error loading hikes: {e}")
        sample_hikes = []
    
    if not sample_hikes:
        st.info("📭 No upcoming organized hikes available yet. Check back soon or contact an admin to schedule one!")
    else:
        # Filter options
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            difficulty_filter = st.selectbox("🎯 Difficulty", ["All", "Easy", "Moderate", "Hard"])
        with col2:
            price_filter = st.selectbox("💰 Price", ["All", "Free", "Under KES 2,000", "Under KES 5,000", "KES 5,000+"])
        with col3:
            availability_filter = st.selectbox("👥 Availability", ["All", "Spots Available", "Almost Full"])
        
        # Filter hikes
        filtered_hikes = sample_hikes
        if difficulty_filter != "All":
            filtered_hikes = [h for h in filtered_hikes if h['difficulty'] == difficulty_filter]
        if price_filter == "Free":
            filtered_hikes = [h for h in filtered_hikes if h['price'] == 0]
        elif price_filter == "Under KES 2,000":
            filtered_hikes = [h for h in filtered_hikes if h['price'] < 2000]
        elif price_filter == "Under KES 5,000":
            filtered_hikes = [h for h in filtered_hikes if h['price'] < 5000]
        elif price_filter == "KES 5,000+":
            filtered_hikes = [h for h in filtered_hikes if h['price'] >= 5000]
        
        if availability_filter == "Spots Available":
            filtered_hikes = [h for h in filtered_hikes if h['current_participants'] < h['max_participants'] * 0.8]
        elif availability_filter == "Almost Full":
            filtered_hikes = [h for h in filtered_hikes if h['current_participants'] >= h['max_participants'] * 0.8]
        
        st.markdown(f"**{len(filtered_hikes)} hikes found**")
        
        if not filtered_hikes:
            st.info("No hikes match your filters. Try adjusting your search criteria.")
        
        # Display hikes
        for hike in filtered_hikes:
            with st.container():
                st.markdown(f"""
                    <div style="
                        background: white;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1.5rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    ">
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Hike details
                    st.markdown(f"### {hike['hike_name']}")
                    st.markdown(f"📍 **{hike['location']}** | 📅 **{datetime.fromisoformat(hike['date']).strftime('%B %d, %Y')}**")
                    
                    # Difficulty badge
                    difficulty_colors = {'Easy': '#51cf66', 'Moderate': '#ffd43b', 'Hard': '#ff6b6b'}
                    color = difficulty_colors.get(hike['difficulty'], '#868e96')
                    st.markdown(f"<span style='background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;'>{hike['difficulty']}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='color: #666; margin-top: 0.5rem;'>{hike['description']}</p>", unsafe_allow_html=True)
                    st.caption(f"👤 Organized by **{hike['organizer']}**")
            
            with col2:
                # Pricing and availability
                if hike['price'] == 0:
                    st.markdown("<h2 style='color: #51cf66; margin-bottom: 0;'>FREE</h2>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h2 style='color: #1e3a5f; margin-bottom: 0;'>KES {hike['price']:,.0f}</h2>", unsafe_allow_html=True)
                
                # Availability indicator
                spots_left = hike['max_participants'] - hike['current_participants']
                availability_pct = (hike['current_participants'] / hike['max_participants']) * 100
                
                if spots_left > 0:
                    color = '#51cf66' if availability_pct < 70 else '#ffd43b' if availability_pct < 90 else '#ff6b6b'
                    st.markdown(f"<p style='color: {color}; font-weight: 600;'>✅ {spots_left} spots left</p>", unsafe_allow_html=True)
                    st.progress(availability_pct / 100)
                    
                    # Registration button
                    if st.button(f"Register Now", key=f"register_{hike['id']}", type="primary"):
                        st.session_state[f'registering_{hike["id"]}'] = True
                        st.rerun()
                else:
                    st.markdown("<p style='color: #ff6b6b; font-weight: 600;'>❌ Fully Booked</p>", unsafe_allow_html=True)
            
            # Registration form (appears when button clicked)
            if st.session_state.get(f'registering_{hike["id"]}', False):
                st.markdown("---")
                st.markdown("#### Complete Your Registration")
                
                with st.form(key=f"registration_form_{hike['id']}"):
                    phone = st.text_input(
                        "📱 M-Pesa Phone Number",
                        placeholder="0712345678 or 254712345678",
                        help="Enter your M-Pesa number to receive payment prompt"
                    )
                    
                    agree = st.checkbox("I agree to the terms and conditions")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        submit = st.form_submit_button("💳 Pay with M-Pesa" if hike['price'] > 0 else "✅ Confirm Registration", type="primary")
                    with col_b:
                        cancel = st.form_submit_button("❌ Cancel")
                    
                    if cancel:
                        st.session_state[f'registering_{hike["id"]}'] = False
                        st.rerun()
                    
                    if submit:
                        if not agree:
                            st.error("Please agree to the terms and conditions")
                        elif hike['price'] > 0 and not phone:
                            st.error("Please enter your M-Pesa phone number")
                        else:
                            # Create registration
                            result = register_for_hike(
                                user_id=user['id'],
                                planned_hike_id=hike['id'],  # In production, use actual planned_hike ID
                                phone_number=phone if hike['price'] > 0 else ""
                            )
                            
                            if "error" in result:
                                st.error(f"❌ {result['error']}")
                            else:
                                if hike['price'] > 0:
                                    # Initiate M-Pesa payment
                                    with st.spinner("Initiating M-Pesa payment..."):
                                        # Create payment record
                                        payment_result = create_payment(
                                            registration_id=result['registration_id'],
                                            user_id=user['id'],
                                            amount=hike['price'],
                                            phone_number=phone
                                        )
                                        
                                        if "error" in payment_result:
                                            st.error(f"❌ {payment_result['error']}")
                                        else:
                                            # Initiate STK Push
                                            mpesa_result = initiate_stk_push(
                                                phone_number=phone,
                                                amount=hike['price'],
                                                account_reference=f"HIKE-{result['registration_id']}",
                                                transaction_desc=f"Registration for {hike['hike_name']}"
                                            )
                                            
                                            if mpesa_result.get("demo_mode"):
                                                st.warning("⚠️ **Demo Mode**: M-Pesa not configured")
                                                st.info("In production, you would receive an M-Pesa prompt on your phone to complete payment.")
                                                # Mark as paid for demo
                                                update_payment_status(
                                                    payment_id=payment_result['payment_id'],
                                                    status="completed",
                                                    transaction_id="DEMO123456"
                                                )
                                                st.success("✅ Registration successful! (Demo mode - no actual payment)")
                                            elif mpesa_result.get("success"):
                                                # Update payment with M-Pesa IDs
                                                update_payment_status(
                                                    payment_id=payment_result['payment_id'],
                                                    status="pending",
                                                    checkout_request_id=mpesa_result['checkout_request_id'],
                                                    merchant_request_id=mpesa_result['merchant_request_id']
                                                )
                                                st.success(f"✅ {mpesa_result.get('customer_message', 'Payment prompt sent!')}")
                                                st.info(f"📱 Check your phone {format_phone_number_display(phone)} for M-Pesa payment prompt")
                                                st.balloons()
                                            else:
                                                st.error(f"❌ Payment failed: {mpesa_result.get('error')}")
                                else:
                                    # Free hike - just confirm
                                    st.success(f"✅ Registration successful for {hike['hike_name']}!")
                                    st.balloons()
                                
                                st.session_state[f'registering_{hike["id"]}'] = False
                                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### My Registrations")
    
    registrations = get_user_registrations(user['id'])
    
    if not registrations:
        st.info("📭 You haven't registered for any hikes yet")
    else:
        for reg in registrations:
            status_colors = {
                'confirmed': '#51cf66',
                'pending': '#ffd43b',
                'cancelled': '#ff6b6b'
            }
            payment_colors = {
                'paid': '#51cf66',
                'unpaid': '#ff6b6b',
                'refunded': '#868e96'
            }
            
            with st.container():
                st.markdown(f"""
                    <div style="
                        background: white;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    ">
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### {reg['hike_name']}")
                    st.caption(f"📍 {reg['hike_location']}")
                    st.caption(f"📅 {datetime.fromisoformat(reg['planned_date']).strftime('%B %d, %Y at %I:%M %p')}")
                
                with col2:
                    status_color = status_colors.get(reg['status'], '#868e96')
                    st.markdown(f"<span style='background: {status_color}; color: white; padding: 6px 14px; border-radius: 12px; font-size: 0.9rem; font-weight: 600;'>{reg['status'].upper()}</span>", unsafe_allow_html=True)
                
                with col3:
                    payment_color = payment_colors.get(reg['payment_status'], '#868e96')
                    st.markdown(f"<span style='background: {payment_color}; color: white; padding: 6px 14px; border-radius: 12px; font-size: 0.9rem; font-weight: 600;'>{reg['payment_status'].upper()}</span>", unsafe_allow_html=True)
                
                if reg['price'] > 0:
                    st.markdown(f"**Amount**: KES {reg['price']:,.0f}")
                
                st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>💳 Secure payments powered by M-Pesa</p>
        <p>📱 Questions? Contact support@kilele-hiking.co.ke</p>
    </div>
""", unsafe_allow_html=True)
