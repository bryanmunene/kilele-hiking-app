"""Make Nesh a permanent admin user"""
from database import get_db
from models import User

def make_nesh_admin():
    """Ensure Nesh user has is_admin=True"""
    with get_db() as db:
        user = db.query(User).filter(User.username == 'Nesh').first()
        
        if user:
            print(f"Found user: {user.username}")
            print(f"Current is_admin status: {user.is_admin}")
            
            if not user.is_admin:
                user.is_admin = True
                db.commit()
                print("✅ Updated Nesh to admin!")
            else:
                print("✅ Nesh is already an admin!")
        else:
            print("❌ User 'Nesh' not found in database.")
            print("Please run seed_database.py first to create the user.")

if __name__ == "__main__":
    make_nesh_admin()
