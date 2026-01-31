"""
Database Migration Script for Streamlit Cloud
Run this ONCE after deployment to add new Equipment and PlannedHike tables

This script:
1. Checks if new tables exist
2. Creates them if missing
3. Seeds gear catalog data
4. Reports status

Usage: python migrate_new_models.py
"""
import sys
from database import get_db, Base, engine
from models import Equipment, PlannedHike, Hike, User
from sqlalchemy import inspect

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_database():
    """Add new tables and seed data"""
    print("🔧 Starting database migration...")
    print("=" * 50)
    
    # Check existing tables
    equipment_exists = check_table_exists("equipment")
    planned_hikes_exists = check_table_exists("planned_hikes")
    
    print(f"✓ Equipment table exists: {equipment_exists}")
    print(f"✓ PlannedHike table exists: {planned_hikes_exists}")
    print()
    
    if equipment_exists and planned_hikes_exists:
        print("✅ All new tables already exist!")
        print("   No migration needed.")
        return
    
    # Create missing tables
    print("📦 Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    print()
    
    # Seed gear catalog data
    print("🌱 Seeding gear catalog...")
    with get_db() as db:
        # Check if gear already exists
        existing_gear = db.query(Equipment).filter(Equipment.hike_id.is_(None)).count()
        
        if existing_gear > 0:
            print(f"⚠️  Gear catalog already has {existing_gear} items. Skipping seed.")
        else:
            gear_items = [
                # Footwear
                Equipment(item_name="Salomon Quest 4 GTX Boots", category="footwear", price=24000, 
                         vendor="Adventure Zone Nairobi", brand="Salomon", is_required=True,
                         notes="Waterproof hiking boots with Gore-Tex. Perfect for Kenyan trails."),
                Equipment(item_name="Merrell Moab 2 Mid", category="footwear", price=18000,
                         vendor="Outdoor Ventures", brand="Merrell", is_required=True,
                         notes="Durable hiking boots with Vibram soles."),
                Equipment(item_name="Trail Running Shoes", category="footwear", price=12000,
                         vendor="Sports Planet", brand="Nike", is_required=False,
                         notes="Lightweight option for easier trails."),
                
                # Clothing
                Equipment(item_name="Quick-Dry Hiking Pants", category="clothing", price=4500,
                         vendor="Decathlon Nairobi", brand="Forclaz", is_required=True,
                         notes="Breathable and quick-drying. Essential for tropical climate."),
                Equipment(item_name="Moisture-Wicking Base Layer", category="clothing", price=2500,
                         vendor="Sportsman Kenya", brand="Columbia", is_required=True,
                         notes="Keeps you dry and comfortable."),
                Equipment(item_name="Waterproof Rain Jacket", category="clothing", price=8500,
                         vendor="Adventure Zone Nairobi", brand="The North Face", is_required=True,
                         notes="Essential for sudden weather changes in highlands."),
                Equipment(item_name="Sun Hat with Neck Flap", category="clothing", price=1500,
                         vendor="Outdoor Kenya", brand="Columbia", is_required=True,
                         notes="UV protection for sun-exposed trails."),
                
                # Safety Equipment
                Equipment(item_name="First Aid Kit", category="safety", price=3500,
                         vendor="Pharmacies nationwide", brand="Adventure Medical", is_required=True,
                         notes="Comprehensive kit for trail emergencies."),
                Equipment(item_name="Headlamp with Extra Batteries", category="safety", price=2800,
                         vendor="Adventure Zone Nairobi", brand="Petzl", is_required=True,
                         notes="Essential for early starts and emergencies."),
                Equipment(item_name="Emergency Whistle", category="safety", price=500,
                         vendor="Outdoor Ventures", brand="Generic", is_required=True,
                         notes="Signal for help in emergencies."),
                Equipment(item_name="GPS Device / Satellite Messenger", category="safety", price=35000,
                         vendor="Safari Store Nairobi", brand="Garmin", is_required=False,
                         notes="For remote trails. Consider renting."),
                
                # Navigation
                Equipment(item_name="Trail Map and Compass", category="navigation", price=1200,
                         vendor="Bookstores / Outdoor shops", brand="Local", is_required=True,
                         notes="Don't rely solely on phone GPS."),
                Equipment(item_name="Smartphone Power Bank (20,000mAh)", category="navigation", price=2500,
                         vendor="Electronics shops", brand="Anker", is_required=True,
                         notes="Keep your GPS and camera charged."),
                
                # Hydration & Food
                Equipment(item_name="Hydration Pack (2L)", category="food", price=4500,
                         vendor="Adventure Zone Nairobi", brand="CamelBak", is_required=True,
                         notes="Hands-free hydration on the move."),
                Equipment(item_name="Water Purification Tablets", category="food", price=800,
                         vendor="Pharmacies", brand="Aquatabs", is_required=True,
                         notes="For refilling from streams."),
                Equipment(item_name="Energy Bars & Snacks", category="food", price=1500,
                         vendor="Supermarkets", brand="Nature Valley", is_required=True,
                         notes="High-calorie snacks for sustained energy."),
                
                # Camping (Optional)
                Equipment(item_name="2-Person Tent", category="camping", price=18000,
                         vendor="Outdoor Ventures", brand="Coleman", is_required=False,
                         notes="For multi-day hikes."),
                Equipment(item_name="Sleeping Bag (0°C Rating)", category="camping", price=12000,
                         vendor="Adventure Zone Nairobi", brand="Marmot", is_required=False,
                         notes="For highland camping (Mount Kenya, Aberdares)."),
                Equipment(item_name="Camping Stove & Fuel", category="camping", price=6500,
                         vendor="Safari Store Nairobi", brand="MSR", is_required=False,
                         notes="Lightweight stove for hot meals."),
                
                # Accessories
                Equipment(item_name="Trekking Poles (Pair)", category="safety", price=5500,
                         vendor="Outdoor Kenya", brand="Black Diamond", is_required=False,
                         notes="Reduce knee strain on steep descents."),
                Equipment(item_name="Daypack (30L)", category="clothing", price=7000,
                         vendor="Decathlon Nairobi", brand="Forclaz", is_required=True,
                         notes="Comfortable pack with hydration sleeve."),
                Equipment(item_name="Insect Repellent", category="safety", price=900,
                         vendor="Supermarkets", brand="Autan", is_required=True,
                         notes="Mosquito and fly protection."),
                Equipment(item_name="Sunscreen SPF 50+", category="safety", price=1200,
                         vendor="Pharmacies", brand="Nivea", is_required=True,
                         notes="High-altitude sun protection."),
            ]
            
            db.add_all(gear_items)
            db.flush()
            print(f"✅ Added {len(gear_items)} gear items to catalog")
    
    print()
    print("=" * 50)
    print("🎉 Migration completed successfully!")
    print()
    print("New features available:")
    print("  🎒 Hiking Gear Catalog (Page 19)")
    print("  🗓️ Plan Future Hikes (Page 20)")

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
