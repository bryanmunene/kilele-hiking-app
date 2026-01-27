"""
Quick script to grant admin privileges to a user
"""
from database import get_db
from models import User

def make_admin(username_or_email: str):
    """Grant admin privileges to a user"""
    with get_db() as db:
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            print(f"❌ User '{username_or_email}' not found")
            return False
        
        if user.is_admin:
            print(f"✅ User '{user.username}' is already an admin")
            return True
        
        user.is_admin = True
        db.flush()
        print(f"✅ Successfully granted admin privileges to '{user.username}' ({user.email})")
        return True

if __name__ == "__main__":
    # Make Nesh an admin
    make_admin("Nesh")
    make_admin("bryankinesh@gmail.com")
