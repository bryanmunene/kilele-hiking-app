from database import SessionLocal
from models import User

db = SessionLocal()
user = db.query(User).filter(User.username == "Nesh").first()

if user:
    user.is_admin = True
    db.commit()
    print(f"✅ {user.username} is now an admin!")
else:
    print("❌ User 'Nesh' not found")

db.close()
