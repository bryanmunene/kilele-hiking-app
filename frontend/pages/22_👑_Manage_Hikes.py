"""
Admin: Manage Upcoming Organized Hikes
Create, edit, and manage group hikes with pricing
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import is_authenticated, get_current_user, restore_session_from_storage
from services import (
    get_all_hikes, create_planned_hike, get_user_planned_hikes, 
    update_planned_hike_status, delete_planned_hike, get_hike_registrations
)
from database import get_db
from models import PlannedHike, Hike
from nature_theme import apply_nature_theme

# Restore session
restore_session_from_storage()

# Page config
st.set_page_config(
    page_title="Manage Hikes - Admin",
    page_icon="👑",
    layout="wide"
)
apply_nature_theme()

# Auth check
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.stop()

user = get_current_user()

# Admin check
if not user.get('is_admin', False):
    st.error("🚫 Access Denied - Admins only")
    st.stop()

st.title("👑 Manage Upcoming Hikes")
st.markdown("Create and manage organized group hikes with pricing")

# Tabs for different actions
tab1, tab2, tab3 = st.tabs(["📋 All Upcoming Hikes", "➕ Create New Hike", "📊 Analytics"])

with tab1:
    st.markdown("### All Upcoming Organized Hikes")
    
    # Get all planned hikes from database
    try:
        with get_db() as db:
            planned_hikes = db.query(PlannedHike).order_by(PlannedHike.planned_date.desc()).all()
            
            if not planned_hikes:
                st.info("📭 No upcoming hikes created yet. Create one in the 'Create New Hike' tab.")
            else:
                for ph in planned_hikes:
                    hike = db.query(Hike).filter(Hike.id == ph.hike_id).first()
                    if not hike:
                        continue
                    
                    # Get registration count
                    from models import HikeRegistration
                    registrations = db.query(HikeRegistration).filter(
                        HikeRegistration.planned_hike_id == ph.id,
                        HikeRegistration.status != "cancelled"
                    ).all()
                    
                    paid_count = sum(1 for r in registrations if r.payment_status == "paid")
                    
                    with st.expander(f"🏔️ {hike.name} - {ph.planned_date.strftime('%b %d, %Y')}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Trail:** {hike.name}")
                            st.markdown(f"**Location:** {hike.location}")
                            st.markdown(f"**Date:** {ph.planned_date.strftime('%B %d, %Y at %I:%M %p')}")
                            st.markdown(f"**Status:** {ph.status}")
                            
                            if ph.notes:
                                st.markdown(f"**Notes:** {ph.notes}")
                            
                            # Edit form
                            with st.form(key=f"edit_hike_{ph.id}"):
                                st.markdown("#### Edit Hike Details")
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    new_price = st.number_input(
                                        "Price (KES)",
                                        min_value=0.0,
                                        value=float(ph.price or 0),
                                        step=100.0,
                                        key=f"price_{ph.id}"
                                    )
                                    new_max = st.number_input(
                                        "Max Participants",
                                        min_value=1,
                                        value=ph.max_participants or 20,
                                        step=1,
                                        key=f"max_{ph.id}"
                                    )
                                
                                with col_b:
                                    new_date = st.date_input(
                                        "Date",
                                        value=ph.planned_date.date(),
                                        key=f"date_{ph.id}"
                                    )
                                    new_time = st.time_input(
                                        "Time",
                                        value=ph.planned_date.time(),
                                        key=f"time_{ph.id}"
                                    )
                                
                                new_status = st.selectbox(
                                    "Status",
                                    ["planned", "completed", "cancelled"],
                                    index=["planned", "completed", "cancelled"].index(ph.status),
                                    key=f"status_{ph.id}"
                                )
                                
                                new_notes = st.text_area(
                                    "Notes",
                                    value=ph.notes or "",
                                    key=f"notes_{ph.id}"
                                )
                                
                                col_save, col_delete = st.columns(2)
                                with col_save:
                                    save = st.form_submit_button("💾 Save Changes", type="primary")
                                with col_delete:
                                    delete = st.form_submit_button("🗑️ Delete Hike", type="secondary")
                                
                                if save:
                                    # Update in database
                                    new_datetime = datetime.combine(new_date, new_time)
                                    ph.price = new_price
                                    ph.max_participants = new_max
                                    ph.planned_date = new_datetime
                                    ph.status = new_status
                                    ph.notes = new_notes
                                    ph.updated_at = datetime.utcnow()
                                    db.flush()
                                    
                                    st.success("✅ Hike updated successfully!")
                                    st.rerun()
                                
                                if delete:
                                    if len(registrations) > 0:
                                        st.error(f"❌ Cannot delete: {len(registrations)} people are registered")
                                    else:
                                        db.delete(ph)
                                        db.flush()
                                        st.success("✅ Hike deleted successfully!")
                                        st.rerun()
                        
                        with col2:
                            st.markdown("#### Registration Stats")
                            st.metric("Total Registered", len(registrations))
                            st.metric("Paid", paid_count)
                            st.metric("Unpaid", len(registrations) - paid_count)
                            
                            if ph.price:
                                revenue = paid_count * ph.price
                                st.metric("Revenue (KES)", f"{revenue:,.0f}")
                            
                            if ph.max_participants:
                                capacity_pct = (len(registrations) / ph.max_participants) * 100
                                st.progress(min(capacity_pct / 100, 1.0))
                                st.caption(f"{capacity_pct:.0f}% full")
                        
                        # Show registrations
                        if registrations:
                            st.markdown("#### Registered Participants")
                            reg_data = []
                            for reg in registrations:
                                from models import User
                                u = db.query(User).filter(User.id == reg.user_id).first()
                                reg_data.append({
                                    "Name": u.username if u else "Unknown",
                                    "Phone": reg.phone_number or "N/A",
                                    "Status": reg.status,
                                    "Payment": reg.payment_status,
                                    "Registered": reg.created_at.strftime("%b %d, %Y")
                                })
                            
                            st.dataframe(reg_data, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Error loading hikes: {e}")

with tab2:
    st.markdown("### Create New Upcoming Hike")
    st.caption("Create a custom organized hike with any destination and details")
    
    with st.form(key="create_hike_form"):
        # Option to use existing trail or create custom
        use_existing = st.checkbox("📍 Use existing trail from database", value=False)
        
        if use_existing:
            # Select from existing trails
            all_hikes = get_all_hikes()
            hike_options = {h['name']: h['id'] for h in all_hikes}
            
            selected_hike_name = st.selectbox(
                "🏔️ Select Trail",
                options=list(hike_options.keys()),
                help="Choose which trail this organized hike will follow"
            )
            hike_id = hike_options[selected_hike_name]
            custom_name = None
            custom_location = None
            custom_difficulty = None
        else:
            # Custom hike details
            st.markdown("#### Custom Hike Details")
            col_a, col_b = st.columns(2)
            with col_a:
                custom_name = st.text_input(
                    "🏔️ Hike Name *",
                    placeholder="e.g., Mount Kenya Summit Trek",
                    help="Enter the name of the hiking destination"
                )
                custom_location = st.text_input(
                    "📍 Location *",
                    placeholder="e.g., Central Kenya, Nanyuki",
                    help="Where is this hike located?"
                )
            with col_b:
                custom_difficulty = st.selectbox(
                    "🎯 Difficulty *",
                    ["Easy", "Moderate", "Hard"],
                    help="How challenging is this hike?"
                )
            
            hike_id = None  # Will create as standalone organized hike
        
        st.markdown("---")
        st.markdown("#### Schedule & Pricing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hike_date = st.date_input(
                "📅 Date",
                value=datetime.now() + timedelta(days=7),
                min_value=datetime.now().date()
            )
            hike_time = st.time_input(
                "⏰ Time",
                value=datetime.strptime("06:00", "%H:%M").time()
            )
            price = st.number_input(
                "💰 Price (KES)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                help="Set to 0 for free hikes"
            )
        
        with col2:
            max_participants = st.number_input(
                "👥 Max Participants",
                min_value=1,
                value=20,
                step=1
            )
            transport = st.selectbox(
                "🚗 Transport Mode",
                ["self_drive", "carpool", "public_transport", "organized_bus"],
                format_func=lambda x: x.replace("_", " ").title()
            )
            meeting_point = st.text_input(
                "📍 Meeting Point",
                placeholder="e.g., Nairobi CBD, ABC Place"
            )
        
        notes = st.text_area(
            "📝 Notes & Description",
            placeholder="Add any special instructions, what's included, what to bring, etc.",
            height=120
        )
        
        submit = st.form_submit_button("✅ Create Hike", type="primary")
        
        if submit:
            # Validation
            if use_existing and not selected_hike_name:
                st.error("Please select a trail")
            elif not use_existing and (not custom_name or not custom_location or not custom_difficulty):
                st.error("Please fill in all required fields (Name, Location, Difficulty)")
            else:
                # Create planned hike
                hike_datetime = datetime.combine(hike_date, hike_time)
                
                try:
                    with get_db() as db:
                        # If custom hike, create trail entry first
                        if not use_existing:
                            new_trail = Hike(
                                name=custom_name,
                                location=custom_location,
                                difficulty=custom_difficulty,
                                distance_km=0,  # Can be updated later
                                description=notes or f"Organized hike to {custom_name}",
                                trail_type="Organized Group Hike"
                            )
                            db.add(new_trail)
                            db.flush()
                            db.refresh(new_trail)
                            hike_id = new_trail.id
                            st.info(f"✨ Created new trail: {custom_name}")
                        
                        new_hike = PlannedHike(
                            user_id=user['id'],
                            hike_id=hike_id,
                            planned_date=hike_datetime,
                            status="planned",
                            notes=notes,
                            transport_mode=transport,
                            meeting_point=meeting_point,
                            price=price,
                            max_participants=max_participants,
                            participants=[]
                        )
                        db.add(new_hike)
                        db.flush()
                        db.refresh(new_hike)
                        
                        st.success(f"✅ Upcoming hike created successfully!")
                        st.balloons()
                        st.info(f"Hike ID: {new_hike.id}")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error creating hike: {e}")

with tab3:
    st.markdown("### Hike Analytics")
    
    try:
        with get_db() as db:
            # Get all planned hikes
            all_planned = db.query(PlannedHike).all()
            
            if not all_planned:
                st.info("No data yet")
            else:
                from models import HikeRegistration, Payment
                
                # Calculate stats
                total_hikes = len(all_planned)
                upcoming = sum(1 for h in all_planned if h.status == "planned" and h.planned_date > datetime.utcnow())
                completed = sum(1 for h in all_planned if h.status == "completed")
                
                total_registrations = db.query(HikeRegistration).count()
                paid_registrations = db.query(HikeRegistration).filter(HikeRegistration.payment_status == "paid").count()
                
                total_revenue = db.query(Payment).filter(Payment.status == "completed").count()
                revenue_amount = sum(p.amount for p in db.query(Payment).filter(Payment.status == "completed").all())
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Hikes", total_hikes)
                with col2:
                    st.metric("Upcoming", upcoming)
                with col3:
                    st.metric("Total Registrations", total_registrations)
                with col4:
                    st.metric("Revenue (KES)", f"{revenue_amount:,.0f}")
                
                # Revenue by hike
                st.markdown("#### Revenue by Hike")
                revenue_data = []
                for ph in all_planned:
                    if ph.price and ph.price > 0:
                        hike = db.query(Hike).filter(Hike.id == ph.hike_id).first()
                        paid = db.query(HikeRegistration).filter(
                            HikeRegistration.planned_hike_id == ph.id,
                            HikeRegistration.payment_status == "paid"
                        ).count()
                        revenue_data.append({
                            "Hike": hike.name if hike else "Unknown",
                            "Date": ph.planned_date.strftime("%b %d"),
                            "Price": ph.price,
                            "Paid": paid,
                            "Revenue": paid * ph.price
                        })
                
                if revenue_data:
                    st.dataframe(revenue_data, use_container_width=True, hide_index=True)
                else:
                    st.info("No paid hikes yet")
    
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

st.markdown("---")
st.caption("💼 Admin Dashboard - Manage upcoming organized hikes")
