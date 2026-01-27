import sqlite3

# Connect to database
conn = sqlite3.connect('kilele.db')
cursor = conn.cursor()

# Update all image URLs to use backend static server
updates = [
    ("http://localhost:8000/static/Elephant Hill.jpg", "Elephant Hill Trail"),
    ("http://localhost:8000/static/Table Top Mountain.jpg", "Table Top Mountain"),
    ("http://localhost:8000/static/Kieni Forest.jpg", "Kieni Forest"),
    ("http://localhost:8000/static/Kenze Gorges.jpg", "Kenze Gorges"),
    ("http://localhost:8000/static/Karirana.jpg", "Karirana"),
    ("http://localhost:8000/static/Kamweti Falls.jpg", "Kamweti Falls"),
    ("http://localhost:8000/static/Gatamaiyu.jpg", "Gatamaiyu Forest"),
    ("http://localhost:8000/static/Eburru Hill.jpg", "Eburru Hill"),
]

for image_url, name in updates:
    cursor.execute("UPDATE hikes SET image_url = ? WHERE name = ?", (image_url, name))
    print(f"Updated {name}")

conn.commit()
print(f"\nUpdated {cursor.rowcount} trails with local images")
conn.close()
print("Done!")
