"""
Seed script for the unified Streamlit database
Run this once to populate the database with initial data
"""
import sys
from database import init_database, get_db
from models import Hike, User
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
                username="demo",
                email="demo@kilele.ke",
                hashed_password=hash_password("demo123"),
                full_name="Demo Hiker"
            )
        ]
        
        db.add_all(test_users)
        print(f"✅ Added {len(test_users)} test users")
        print("\n🎉 Database seeding completed successfully!")
        print("\n📝 Test Accounts:")
        print("   Admin: username='admin', password='admin123'")
        print("   Demo:  username='demo', password='demo123'")

if __name__ == "__main__":
    seed_database()
