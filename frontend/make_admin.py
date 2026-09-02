"""
Quick script to grant admin privileges to a user
"""
import argparse

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
    parser = argparse.ArgumentParser(description="Grant admin privileges to an existing Kilele user.")
    parser.add_argument("username_or_email", help="Username or email for the user to promote.")
    args = parser.parse_args()
    make_admin(args.username_or_email)
