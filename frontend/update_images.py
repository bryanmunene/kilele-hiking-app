"""
Update image URLs in database to use local images
"""
from database import init_database, get_db
from models import Hike

init_database()

# Map trail names to local image files
image_map = {
    "Mount Kenya Trek": "Gatamaiyu.jpg",
    "Ngong Hills": "Elephant Hill.jpg",
    "Hell's Gate Gorge": "Karirana.jpg",
    "Karura Forest Loop": "Kieni Forest.jpg",
    "Elephant Hill": "Elephant Hill.jpg",
    "Ol Donyo Sabuk": "Table Top Mountain.jpg",
    "Menengai Crater": "Eburru Hill.jpg"
}

with get_db() as db:
    hikes = db.query(Hike).all()
    
    for hike in hikes:
        if hike.name in image_map:
            hike.image_url = image_map[hike.name]
            print(f"✅ Updated {hike.name} -> {image_map[hike.name]}")
    
    db.commit()
    print("\n✅ All images updated to use local files!")
