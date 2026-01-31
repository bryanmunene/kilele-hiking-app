"""
Seed script for the unified Streamlit database
Run this once to populate the database with initial data
"""
import sys
from database import init_database, get_db
from models import Hike, User, Equipment
from auth import hash_password
from datetime import datetime

def seed_database():
    """Seed the database with initial hiking trails and test users"""
    
    print("🌱 Starting database seeding...")
    
    # Initialize database
    init_database()
    print("✅ Database tables created")
    
    with get_db() as db:
        # Check if data already exists
        existing_hikes = db.query(Hike).count()
        if existing_hikes > 0:
            print(f"⚠️  Database already has {existing_hikes} hikes. Skipping seeding.")
            return
        
        # Seed hikes
        hikes = [
            Hike(
                name="Elephant Hill",
                location="Aberdare National Park",
                difficulty="Hard",
                distance_km=15.0,
                elevation_gain_m=800.0,
                estimated_duration_hours=6.0,
                description="Challenging ascent through bamboo forests to moorland. Excellent views of Mount Kenya.",
                trail_type="Out and Back",
                best_season="January-March, July-October",
                latitude=-0.4167,
                longitude=36.7667,
                image_url="static/Elephant Hill.jpg"
            ),
            Hike(
                name="Gatamaiyu Forest",
                location="Gatamaiyu, Kiambu County",
                difficulty="Moderate",
                distance_km=8.0,
                elevation_gain_m=300.0,
                estimated_duration_hours=3.5,
                description="Beautiful forest trail with streams and diverse flora. Popular for nature walks and bird watching.",
                trail_type="Loop",
                best_season="Year-round",
                latitude=-0.9500,
                longitude=36.6500,
                image_url="static/Gatamaiyu.jpg"
            ),
            Hike(
                name="Kenze Gorges",
                location="Muranga County",
                difficulty="Hard",
                distance_km=12.0,
                elevation_gain_m=650.0,
                estimated_duration_hours=5.0,
                description="Spectacular gorge walk with dramatic cliffs and waterfalls. Challenging terrain with rewarding views.",
                trail_type="Out and Back",
                best_season="Dry season (January-March, July-October)",
                latitude=-0.7500,
                longitude=36.9500,
                image_url="static/Kenze Gorges.jpg"
            ),
            Hike(
                name="Kieni Forest Trail",
                location="Kieni, Nyeri County",
                difficulty="Moderate",
                distance_km=10.0,
                elevation_gain_m=400.0,
                estimated_duration_hours=4.0,
                description="Serene forest walk through indigenous trees and bamboo. Great for wildlife spotting.",
                trail_type="Loop",
                best_season="Year-round",
                latitude=-0.3500,
                longitude=36.9000,
                image_url="static/Kieni Forest.jpg"
            ),
            Hike(
                name="Table Top Mountain",
                location="Nyandarua County",
                difficulty="Extreme",
                distance_km=18.0,
                elevation_gain_m=1200.0,
                estimated_duration_hours=8.0,
                description="Summit the distinctive flat-topped mountain with 360-degree views. A true mountaineering challenge.",
                trail_type="Out and Back",
                best_season="Dry season (January-March, July-October)",
                latitude=-0.5167,
                longitude=36.6333,
                image_url="static/Table Top Mountain.jpg"
            ),
            Hike(
                name="Karirana Forest",
                location="Nyahururu, Laikipia County",
                difficulty="Easy",
                distance_km=6.0,
                elevation_gain_m=150.0,
                estimated_duration_hours=2.5,
                description="Gentle forest walk with beautiful scenery. Perfect for beginners and families.",
                trail_type="Loop",
                best_season="Year-round",
                latitude=0.0500,
                longitude=36.3667,
                image_url="static/Karirana.jpg"
            ),
            Hike(
                name="Eburru Hill",
                location="Naivasha, Nakuru County",
                difficulty="Moderate",
                distance_km=9.0,
                elevation_gain_m=500.0,
                estimated_duration_hours=4.0,
                description="Volcanic hill with fumaroles and hot springs. Unique geothermal features and stunning views of Lake Naivasha.",
                trail_type="Out and Back",
                best_season="Year-round",
                latitude=-0.6333,
                longitude=36.2667,
                image_url="static/Eburru Hill.jpg"
            )
        ]
        
        db.add_all(hikes)
        print(f"✅ Added {len(hikes)} hiking trails")
        
        # Create test users (optional)
        test_users = [
            User(
                username="admin",
                email="admin@kilele.ke",
                hashed_password=hash_password("admin123"),
                full_name="Admin User",
                is_admin=True
            ),
            User(
                username="Nesh",
                email="nesh@kilele.ke",
                hashed_password=hash_password("password123"),
                full_name="Nesh",
                is_admin=True
            ),
            User(
                username="demo",
                email="demo@kilele.ke",
                hashed_password=hash_password("demo123"),
                full_name="Demo Hiker"
            )
        ]
        
        db.add_all(test_users)
        print(f"✅ Added {len(test_users)} test users")
        
        # Seed hiking gear catalog
        gear_items = [
            # Footwear
            Equipment(item_name="Salomon Quest 4 GTX Boots", category="footwear", price=24000, 
                     vendor="Adventure Zone Nairobi", brand="Salomon", is_required=True,
                     notes="Waterproof hiking boots with Gore-Tex. Perfect for Kenyan trails.",
                     image_url="static/gear/salomon_boots.jpg"),
            Equipment(item_name="Merrell Moab 2 Mid", category="footwear", price=18000,
                     vendor="Outdoor Ventures", brand="Merrell", is_required=True,
                     notes="Durable hiking boots with Vibram soles.",
                     image_url="static/gear/merrell_boots.jpg"),
            Equipment(item_name="Trail Running Shoes", category="footwear", price=12000,
                     vendor="Sports Planet", brand="Nike", is_required=False,
                     notes="Lightweight option for easier trails.",
                     image_url="static/gear/trail_shoes.jpg"),
            
            # Clothing
            Equipment(item_name="Quick-Dry Hiking Pants", category="clothing", price=4500,
                     vendor="Decathlon Nairobi", brand="Forclaz", is_required=True,
                     notes="Breathable and quick-drying. Essential for tropical climate.",
                     image_url="static/gear/hiking_pants.jpg"),
            Equipment(item_name="Moisture-Wicking Base Layer", category="clothing", price=2500,
                     vendor="Sportsman Kenya", brand="Columbia", is_required=True,
                     notes="Keeps you dry and comfortable.",
                     image_url="static/gear/base_layer.jpg"),
            Equipment(item_name="Waterproof Rain Jacket", category="clothing", price=8500,
                     vendor="Adventure Zone Nairobi", brand="The North Face", is_required=True,
                     notes="Essential for sudden weather changes in highlands.",
                     image_url="static/gear/rain_jacket.jpg"),
            Equipment(item_name="Sun Hat with Neck Flap", category="clothing", price=1500,
                     vendor="Outdoor Kenya", brand="Columbia", is_required=True,
                     notes="UV protection for sun-exposed trails.",
                     image_url="static/gear/sun_hat.jpg"),
            
            # Safety Equipment
            Equipment(item_name="First Aid Kit", category="safety", price=3500,
                     vendor="Pharmacies nationwide", brand="Adventure Medical", is_required=True,
                     notes="Comprehensive kit for trail emergencies.",
                     image_url="static/gear/first_aid.jpg"),
            Equipment(item_name="Headlamp with Extra Batteries", category="safety", price=2800,
                     vendor="Adventure Zone Nairobi", brand="Petzl", is_required=True,
                     notes="Essential for early starts and emergencies.",
                     image_url="static/gear/headlamp.jpg"),
            Equipment(item_name="Emergency Whistle", category="safety", price=500,
                     vendor="Outdoor Ventures", brand="Generic", is_required=True,
                     notes="Signal for help in emergencies.",
                     image_url="static/gear/whistle.jpg"),
            Equipment(item_name="GPS Device / Satellite Messenger", category="safety", price=35000,
                     vendor="Safari Store Nairobi", brand="Garmin", is_required=False,
                     notes="For remote trails. Consider renting.",
                     image_url="static/gear/gps_device.jpg"),
            
            # Navigation
            Equipment(item_name="Trail Map and Compass", category="navigation", price=1200,
                     vendor="Bookstores / Outdoor shops", brand="Local", is_required=True,
                     notes="Don't rely solely on phone GPS.",
                     image_url="static/gear/compass.jpg"),
            Equipment(item_name="Smartphone Power Bank (20,000mAh)", category="navigation", price=2500,
                     vendor="Electronics shops", brand="Anker", is_required=True,
                     notes="Keep your GPS and camera charged.",
                     image_url="static/gear/power_bank.jpg"),
            
            # Hydration & Food
            Equipment(item_name="Hydration Pack (2L)", category="food", price=4500,
                     vendor="Adventure Zone Nairobi", brand="CamelBak", is_required=True,
                     notes="Hands-free hydration on the move.",
                     image_url="static/gear/hydration_pack.jpg"),
            Equipment(item_name="Water Purification Tablets", category="food", price=800,
                     vendor="Pharmacies", brand="Aquatabs", is_required=True,
                     notes="For refilling from streams.",
                     image_url="static/gear/water_tablets.jpg"),
            Equipment(item_name="Energy Bars & Snacks", category="food", price=1500,
                     vendor="Supermarkets", brand="Nature Valley", is_required=True,
                     notes="High-calorie snacks for sustained energy.",
                     image_url="static/gear/energy_bars.jpg"),
            
            # Camping (Optional)
            Equipment(item_name="2-Person Tent", category="camping", price=18000,
                     vendor="Outdoor Ventures", brand="Coleman", is_required=False,
                     notes="For multi-day hikes.",
                     image_url="static/gear/tent.jpg"),
            Equipment(item_name="Sleeping Bag (0°C Rating)", category="camping", price=12000,
                     vendor="Adventure Zone Nairobi", brand="Marmot", is_required=False,
                     notes="For highland camping (Mount Kenya, Aberdares).",
                     image_url="static/gear/sleeping_bag.jpg"),
            Equipment(item_name="Camping Stove & Fuel", category="camping", price=6500,
                     vendor="Safari Store Nairobi", brand="MSR", is_required=False,
                     notes="Lightweight stove for hot meals.",
                     image_url="static/gear/camping_stove.jpg"),
            
            # Accessories
            Equipment(item_name="Trekking Poles (Pair)", category="safety", price=5500,
                     vendor="Outdoor Kenya", brand="Black Diamond", is_required=False,
                     notes="Reduce knee strain on steep descents.",
                     image_url="static/gear/trekking_poles.jpg"),
            Equipment(item_name="Daypack (30L)", category="clothing", price=7000,
                     vendor="Decathlon Nairobi", brand="Forclaz", is_required=True,
                     notes="Comfortable pack with hydration sleeve.",
                     image_url="static/gear/daypack.jpg"),
            Equipment(item_name="Insect Repellent", category="safety", price=900,
                     vendor="Supermarkets", brand="Autan", is_required=True,
                     notes="Mosquito and fly protection.",
                     image_url="static/gear/insect_repellent.jpg"),
            Equipment(item_name="Sunscreen SPF 50+", category="safety", price=1200,
                     vendor="Pharmacies", brand="Nivea", is_required=True,
                     notes="High-altitude sun protection.",
                     image_url="static/gear/sunscreen.jpg"),
        ]
        
        db.add_all(gear_items)
        print(f"✅ Added {len(gear_items)} gear items to catalog")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📝 Test Accounts:")
        print("   Admin: username='admin', password='admin123'")
        print("   Nesh:  username='Nesh', password='password123' (ADMIN)")
        print("   Demo:  username='demo', password='demo123'")

if __name__ == "__main__":
    seed_database()
