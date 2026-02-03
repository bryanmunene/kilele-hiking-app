"""
Admin: Manage Upcoming Organized Hikes
Create, edit, and manage group hikes with pricing
"""
import streamlit as st
import sys
import os
import csv
from datetime import datetime, timedelta
from io import StringIO
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

# Mobile responsive CSS
st.markdown("""
    <style>
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 14px;
        }
    }
    /* Better card styling */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    /* Quick action buttons */
    .quick-actions {
        display: flex;
        gap: 8px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

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

# Initialize session state for pagination and bulk selection
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 10
if 'selected_hikes' not in st.session_state:
    st.session_state.selected_hikes = set()

# Tabs for different actions
tab1, tab2, tab3 = st.tabs(["📋 All Upcoming Hikes", "➕ Create New Hike", "📊 Analytics"])

with tab1:
    st.markdown("### All Upcoming Organized Hikes")
    
    # Search and filter controls
    col_search, col_filter, col_per_page, col_export = st.columns([2, 1, 1, 1])
    with col_search:
        search_term = st.text_input("🔍 Search hikes", placeholder="Search by trail name or location...", label_visibility="collapsed")
    with col_filter:
        status_filter = st.selectbox("Filter by status", ["All", "planned", "completed", "cancelled"], label_visibility="collapsed")
    with col_per_page:
        st.session_state.items_per_page = st.selectbox("Per page", [5, 10, 20, 50], index=1, label_visibility="collapsed")
    with col_export:
        export_btn = st.button("📥 Export CSV", use_container_width=True)
    
    # Bulk operations toolbar
    if len(st.session_state.selected_hikes) > 0:
        st.info(f"✅ {len(st.session_state.selected_hikes)} hike(s) selected")
        bulk_col1, bulk_col2, bulk_col3, bulk_col4 = st.columns(4)
        with bulk_col1:
            if st.button("✅ Mark as Completed", use_container_width=True):
                with get_db() as db:
                    for hike_id in st.session_state.selected_hikes:
                        ph = db.query(PlannedHike).filter(PlannedHike.id == hike_id).first()
                        if ph:
                            ph.status = "completed"
                    db.commit()
                st.session_state.selected_hikes.clear()
                st.success("Hikes marked as completed!")
                st.rerun()
        with bulk_col2:
            if st.button("❌ Cancel Selected", use_container_width=True):
                with get_db() as db:
                    for hike_id in st.session_state.selected_hikes:
                        ph = db.query(PlannedHike).filter(PlannedHike.id == hike_id).first()
                        if ph:
                            ph.status = "cancelled"
                    db.commit()
                st.session_state.selected_hikes.clear()
                st.success("Hikes cancelled!")
                st.rerun()
        with bulk_col3:
            if st.button("🗑️ Delete Selected", use_container_width=True, type="secondary"):
                with get_db() as db:
                    # Check for registrations
                    from models import HikeRegistration
                    has_registrations = False
                    for hike_id in st.session_state.selected_hikes:
                        count = db.query(HikeRegistration).filter(HikeRegistration.planned_hike_id == hike_id).count()
                        if count > 0:
                            has_registrations = True
                            break
                    
                    if has_registrations:
                        st.error("❌ Cannot delete: Some hikes have registrations")
                    else:
                        for hike_id in st.session_state.selected_hikes:
                            ph = db.query(PlannedHike).filter(PlannedHike.id == hike_id).first()
                            if ph:
                                db.delete(ph)
                        db.commit()
                        st.session_state.selected_hikes.clear()
                        st.success("Hikes deleted!")
                        st.rerun()
        with bulk_col4:
            if st.button("🔄 Clear Selection", use_container_width=True):
                st.session_state.selected_hikes.clear()
                st.rerun()
    
    st.markdown("---")
    
    # Get all planned hikes from database
    try:
        with st.spinner("Loading hikes..."):
            with get_db() as db:
                # Query with filters
                query = db.query(PlannedHike)
                
                # Apply status filter
                if status_filter != "All":
                    query = query.filter(PlannedHike.status == status_filter)
                
                planned_hikes = query.order_by(PlannedHike.planned_date.desc()).all()
                
                # Apply search filter (client-side for simplicity)
                if search_term:
                    filtered_hikes = []
                    for ph in planned_hikes:
                        hike = db.query(Hike).filter(Hike.id == ph.hike_id).first()
                        if hike and (search_term.lower() in hike.name.lower() or search_term.lower() in hike.location.lower()):
                            filtered_hikes.append(ph)
                    planned_hikes = filtered_hikes
                
                # Pagination
                total_items = len(planned_hikes)
                total_pages = max(1, (total_items + st.session_state.items_per_page - 1) // st.session_state.items_per_page)
                
                # Reset page number if it exceeds total pages
                if st.session_state.page_number > total_pages:
                    st.session_state.page_number = 1
                
                start_idx = (st.session_state.page_number - 1) * st.session_state.items_per_page
                end_idx = start_idx + st.session_state.items_per_page
                paginated_hikes = planned_hikes[start_idx:end_idx]
            
            # Handle export
            if export_btn and planned_hikes:
                import csv
                from io import StringIO
                
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow(["Trail Name", "Location", "Date", "Status", "Price", "Max Participants", "Registered", "Paid", "Revenue"])
                
                for ph in planned_hikes:
                    hike = db.query(Hike).filter(Hike.id == ph.hike_id).first()
                    from models import HikeRegistration
                    registrations = db.query(HikeRegistration).filter(
                        HikeRegistration.planned_hike_id == ph.id,
                        HikeRegistration.status != "cancelled"
                    ).all()
                    paid_count = sum(1 for r in registrations if r.payment_status == "paid")
                    revenue = paid_count * (ph.price or 0)
                    
                    csv_writer.writerow([
                        hike.name if hike else "Unknown",
                        hike.location if hike else "Unknown",
                        ph.planned_date.strftime("%Y-%m-%d %H:%M"),
                        ph.status,
                        ph.price or 0,
                        ph.max_participants or 0,
                        len(registrations),
                        paid_count,
                        revenue
                    ])
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"hikes_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            if not planned_hikes:
                st.info("📭 No hikes found. Try adjusting your filters or create a new hike.")
            else:
                # Display pagination info and select all
                col_info, col_select = st.columns([3, 1])
                with col_info:
                    st.caption(f"Showing {start_idx + 1}-{min(end_idx, total_items)} of {total_items} hike(s) | Page {st.session_state.page_number} of {total_pages}")
                with col_select:
                    select_all = st.checkbox("Select all on page", key="select_all_hikes")
                    if select_all:
                        for ph in paginated_hikes:
                            st.session_state.selected_hikes.add(ph.id)
                    elif not select_all and 'select_all_hikes' in st.session_state:
                        for ph in paginated_hikes:
                            st.session_state.selected_hikes.discard(ph.id)
                
                for ph in paginated_hikes:
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
                    
                    # Status emoji
                    status_emoji = {"planned": "📅", "completed": "✅", "cancelled": "❌"}.get(ph.status, "📅")
                    
                    # Calculate days until hike
                    days_until = (ph.planned_date.date() - datetime.now().date()).days
                    time_info = ""
                    if ph.status == "planned":
                        if days_until < 0:
                            time_info = " (PAST DUE)"
                        elif days_until == 0:
                            time_info = " (TODAY)"
                        elif days_until == 1:
                            time_info = " (TOMORROW)"
                        elif days_until <= 7:
                            time_info = f" (in {days_until} days)"
                    
                    with st.expander(f"{status_emoji} {hike.name} - {ph.planned_date.strftime('%b %d, %Y')}{time_info}", expanded=False):
                        # Checkbox for bulk selection
                        is_selected = st.checkbox(
                            f"Select this hike",
                            value=ph.id in st.session_state.selected_hikes,
                            key=f"select_{ph.id}"
                        )
                        if is_selected:
                            st.session_state.selected_hikes.add(ph.id)
                        else:
                            st.session_state.selected_hikes.discard(ph.id)
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Display hike image if available
                            if hike.image_url:
                                from image_utils import display_image
                                display_image(hike.image_url, caption=None, width=300)
                            
                            st.markdown(f"**Trail:** {hike.name}")
                            st.markdown(f"**Location:** {hike.location}")
                            st.markdown(f"**Date:** {ph.planned_date.strftime('%B %d, %Y at %I:%M %p')}")
                            st.markdown(f"**Status:** {ph.status.upper()}")
                            
                            if ph.transport_mode:
                                st.markdown(f"**Transport:** {ph.transport_mode.replace('_', ' ').title()}")
                            if ph.meeting_point:
                                st.markdown(f"**Meeting Point:** {ph.meeting_point}")
                            
                            # Quick status change buttons
                            st.markdown("##### Quick Actions")
                            quick_col1, quick_col2, quick_col3 = st.columns(3)
                            with quick_col1:
                                if st.button("✅ Complete", key=f"complete_{ph.id}", use_container_width=True, disabled=(ph.status == "completed")):
                                    ph.status = "completed"
                                    db.commit()
                                    st.success("Status updated!")
                                    st.rerun()
                            with quick_col2:
                                if st.button("❌ Cancel", key=f"cancel_{ph.id}", use_container_width=True, disabled=(ph.status == "cancelled")):
                                    ph.status = "cancelled"
                                    db.commit()
                                    st.success("Status updated!")
                                    st.rerun()
                            with quick_col3:
                                if st.button("🔄 Reopen", key=f"reopen_{ph.id}", use_container_width=True, disabled=(ph.status == "planned")):
                                    ph.status = "planned"
                                    db.commit()
                                    st.success("Status updated!")
                                    st.rerun()
                            
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
                                    try:
                                        new_datetime = datetime.combine(new_date, new_time)
                                        ph.price = new_price
                                        ph.max_participants = new_max
                                        ph.planned_date = new_datetime
                                        ph.status = new_status
                                        ph.notes = new_notes
                                        ph.updated_at = datetime.utcnow()
                                        db.commit()
                                        
                                        st.success("✅ Hike updated successfully!")
                                        st.rerun()
                                    except Exception as update_error:
                                        db.rollback()
                                        st.error(f"Failed to update hike: {update_error}")
                                
                                if delete:
                                    if len(registrations) > 0:
                                        st.error(f"❌ Cannot delete: {len(registrations)} people are registered")
                                    else:
                                        try:
                                            db.delete(ph)
                                            db.commit()
                                            st.success("✅ Hike deleted successfully!")
                                            st.rerun()
                                        except Exception as delete_error:
                                            db.rollback()
                                            st.error(f"Failed to delete hike: {delete_error}")
                        
                        with col2:
                            st.markdown("#### Registration Stats")
                            st.metric("Total Registered", len(registrations))
                            st.metric("Paid", paid_count, delta=f"{paid_count}/{len(registrations)}" if len(registrations) > 0 else None)
                            st.metric("Unpaid", len(registrations) - paid_count)
                            
                            if ph.price and ph.price > 0:
                                revenue = paid_count * ph.price
                                potential_revenue = len(registrations) * ph.price
                                st.metric("Revenue (KES)", f"{revenue:,.0f}", delta=f"Potential: {potential_revenue:,.0f}")
                            
                            if ph.max_participants:
                                capacity_pct = (len(registrations) / ph.max_participants) * 100
                                st.progress(min(capacity_pct / 100, 1.0))
                                spots_left = ph.max_participants - len(registrations)
                                st.caption(f"{capacity_pct:.0f}% full - {spots_left} spots left")
                        
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
                                    "Status": f"{reg.status} {'✅' if reg.status == 'confirmed' else ''}",
                                    "Payment": f"{reg.payment_status} {'💰' if reg.payment_status == 'paid' else '⏳'}",
                                    "Registered": reg.created_at.strftime("%b %d, %Y")
                                })
                            
                            st.dataframe(reg_data, use_container_width=True, hide_index=True)
                            
                            # Add download button for participants list
                            csv_buffer = StringIO()
                            csv_writer = csv.writer(csv_buffer)
                            csv_writer.writerow(["Name", "Phone", "Status", "Payment", "Registered"])
                            for reg in reg_data:
                                csv_writer.writerow([reg["Name"], reg["Phone"], reg["Status"], reg["Payment"], reg["Registered"]])
                            
                            st.download_button(
                                label="📥 Download Participants",
                                data=csv_buffer.getvalue(),
                                file_name=f"participants_{hike.name.replace(' ', '_')}_{ph.planned_date.strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key=f"download_participants_{ph.id}"
                            )
                
                # Pagination controls
                if total_pages > 1:
                    st.markdown("---")
                    col_prev, col_page, col_next = st.columns([1, 2, 1])
                    
                    with col_prev:
                        if st.button("◀️ Previous", disabled=(st.session_state.page_number == 1), use_container_width=True):
                            st.session_state.page_number -= 1
                            st.rerun()
                    
                    with col_page:
                        # Page selector
                        new_page = st.selectbox(
                            "Go to page",
                            options=list(range(1, total_pages + 1)),
                            index=st.session_state.page_number - 1,
                            label_visibility="collapsed",
                            key="page_selector"
                        )
                        if new_page != st.session_state.page_number:
                            st.session_state.page_number = new_page
                            st.rerun()
                    
                    with col_next:
                        if st.button("Next ▶️", disabled=(st.session_state.page_number == total_pages), use_container_width=True):
                            st.session_state.page_number += 1
                            st.rerun()
    
    except Exception as e:
        st.error(f"Error loading hikes: {e}")

with tab2:
    st.markdown("### Create New Upcoming Hike")
    st.caption("Create a custom organized hike with any destination and details")
    
    # Show quick stats
    with get_db() as db:
        upcoming_count = db.query(PlannedHike).filter(PlannedHike.status == "planned", PlannedHike.planned_date > datetime.utcnow()).count()
        st.info(f"ℹ️ You currently have {upcoming_count} upcoming hike(s) scheduled")
    
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
        
        # Image upload
        st.markdown("#### Optional: Add Hike Image")
        uploaded_image = st.file_uploader(
            "📷 Upload hike image",
            type=["jpg", "jpeg", "png"],
            help="Upload a banner image for this hike (optional)",
            label_visibility="collapsed"
        )
        
        submit = st.form_submit_button("✅ Create Hike", type="primary")
        
        if submit:
            # Validation
            if use_existing and not selected_hike_name:
                st.error("Please select a trail")
            elif not use_existing and (not custom_name or not custom_location or not custom_difficulty):
                st.error("Please fill in all required fields (Name, Location, Difficulty)")
            else:
                # Validate date is in future
                hike_datetime = datetime.combine(hike_date, hike_time)
                
                if hike_datetime <= datetime.now():
                    st.error("❌ Hike date must be in the future")
                    st.stop()
                
                try:
                    with st.spinner("Creating hike..."):
                        with get_db() as db:
                        # Handle image upload
                        image_url = None
                        if uploaded_image is not None:
                            # Save image to static folder
                            import hashlib
                            from pathlib import Path
                            
                            # Create unique filename
                            image_hash = hashlib.md5(uploaded_image.getvalue()).hexdigest()[:10]
                            file_extension = uploaded_image.name.split('.')[-1]
                            filename = f"hike_{image_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
                            
                            # Save to static/hikes folder
                            static_dir = Path(__file__).parent.parent / "static" / "hikes"
                            static_dir.mkdir(parents=True, exist_ok=True)
                            image_path = static_dir / filename
                            
                            with open(image_path, "wb") as f:
                                f.write(uploaded_image.getvalue())
                            
                            image_url = f"/static/hikes/{filename}"
                            st.success(f"✅ Image uploaded: {filename}")
                        
                        # If custom hike, create trail entry first
                        if not use_existing:
                            new_trail = Hike(
                                name=custom_name,
                                location=custom_location,
                                difficulty=custom_difficulty,
                                distance_km=0,  # Can be updated later
                                description=notes or f"Organized hike to {custom_name}",
                                trail_type="Organized Group Hike",
                                image_url=image_url  # Add image to trail
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
                        db.commit()
                        db.refresh(new_hike)
                        
                        st.success(f"✅ Upcoming hike created successfully!")
                        st.balloons()
                        st.info(f"📋 Hike ID: {new_hike.id} | 📅 Scheduled for {hike_datetime.strftime('%B %d, %Y at %I:%M %p')}")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error creating hike: {e}")
                    if 'db' in locals():
                        db.rollback()

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
