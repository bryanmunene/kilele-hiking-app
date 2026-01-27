"""
Seed script to populate the database with initial Kenyan hiking trails
Run with: python seed_data.py
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.hike import Hike
# Import all models to ensure relationships are registered
import models

# Create tables
Base.metadata.create_all(bind=engine)

def seed_hikes():
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Hike).count() > 0:
        print("Database already contains hikes. Skipping seed.")
        db.close()
        return
    
    hikes = [
        Hike(
            name="Elephant Hill Trail",
            location="Aberdare National Park",
            difficulty="Moderate",
            distance_km=18.0,
            elevation_gain_m=800.0,
            estimated_duration_hours=6.0,
            description="Scenic trail through montane forest with excellent wildlife viewing opportunities. Named for the resident elephant herds.",
            trail_type="Out and Back",
            best_season="June-October",
            latitude=-0.3500,
            longitude=36.7500,
            image_url="http://localhost:8000/static/Elephant Hill.jpg"
        ),
        Hike(
            name="Table Top Mountain",
            location="Aberdare National Park",
            difficulty="Hard",
            distance_km=25.0,
            elevation_gain_m=1500.0,
            estimated_duration_hours=10.0,
            description="Highland moorland trek through bamboo forests and open grasslands. Home to elephants, buffalo, and rare bongo antelope. Requires park guide.",
            trail_type="Loop",
            best_season="June-September, December-February",
            latitude=-0.4000,
            longitude=36.7000,
            image_url="http://localhost:8000/static/Table Top Mountain.jpg"
        ),
        Hike(
            name="Kieni Forest",
            location="Kieni Forest, Central Kenya",
            difficulty="Easy",
            distance_km=8.0,
            elevation_gain_m=100.0,
            estimated_duration_hours=2.5,
            description="Urban forest sanctuary with waterfall, caves, and abundant wildlife. Family-friendly trails with well-maintained paths. Perfect for beginners.",
            trail_type="Loop",
            best_season="All year",
            latitude=-0.2504,
            longitude=36.8402,
            image_url="http://localhost:8000/static/Kieni Forest.jpg"
        ),
        Hike(
            name="Kenze Gorges",
            location="Kenze, Rift Valley",
            difficulty="Moderate",
            distance_km=15.0,
            elevation_gain_m=200.0,
            estimated_duration_hours=5.0,
            description="Unique walking safari through dramatic gorges and towering cliffs. Wildlife includes zebras, giraffes, and rock hyrax. Cycling also permitted.",
            trail_type="Out and Back",
            best_season="All year",
            latitude=-0.9167,
            longitude=36.3167,
            image_url="http://localhost:8000/static/Kenze Gorges.jpg"
        ),
        Hike(
            name="Karirana",
            location="Karirana Hills, Rift Valley",
            difficulty="Moderate",
            distance_km=12.0,
            elevation_gain_m=600.0,
            estimated_duration_hours=4.0,
            description="Scenic ridge walk with panoramic views of the Great Rift Valley and Nairobi skyline. Popular weekend destination with stunning vistas.",
            trail_type="Out and Back",
            best_season="All year (avoid heavy rain months)",
            latitude=-1.3833,
            longitude=36.6500,
            image_url="http://localhost:8000/static/Karirana.jpg"
        ),
        Hike(
            name="Kamweti Falls",
            location="Aberdare National Park",
            difficulty="Moderate",
            distance_km=10.0,
            elevation_gain_m=400.0,
            estimated_duration_hours=4.5,
            description="Beautiful waterfall trail through lush montane forest. Perfect for photography and nature lovers seeking tranquility.",
            trail_type="Out and Back",
            best_season="March-May, October-December",
            latitude=-0.3800,
            longitude=36.7200,
            image_url="http://localhost:8000/static/Kamweti Falls.jpg"
        ),
        Hike(
            name="Gatamaiyu Forest",
            location="Gatamaiyu, Central Kenya",
            difficulty="Easy",
            distance_km=7.0,
            elevation_gain_m=150.0,
            estimated_duration_hours=3.0,
            description="Serene forest trail with diverse birdlife and peaceful atmosphere. Ideal for families and beginner hikers.",
            trail_type="Loop",
            best_season="All year",
            latitude=-0.8500,
            longitude=36.5500,
            image_url="http://localhost:8000/static/Gatamaiyu.jpg"
        ),
        Hike(
            name="Eburru Hill",
            location="Eburru Volcanic Complex, Rift Valley",
            difficulty="Moderate",
            distance_km=13.0,
            elevation_gain_m=1000.0,
            estimated_duration_hours=5.0,
            description="Dormant volcano with spectacular crater rim walk. Steep ascent rewarded with 360° views of the Great Rift Valley and geothermal features.",
            trail_type="Loop",
            best_season="June-March",
            latitude=-0.9150,
            longitude=36.4464,
            image_url="http://localhost:8000/static/Eburru Hill.jpg"
        ),
    ]
    
    db.add_all(hikes)
    db.commit()
    print(f"Successfully seeded {len(hikes)} hikes into the database!")
    db.close()

if __name__ == "__main__":
    seed_hikes()
