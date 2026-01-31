"""
Migration script to add new models for hike registration and M-Pesa payments
Run this to update existing databases
"""
from database import engine, Base, SessionLocal
from models import HikeRegistration, Payment

def migrate():
    """Add new tables for registration and payments"""
    print("Creating new tables...")
    
    # Create all tables (only creates if they don't exist)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Migration complete!")
    print("New tables:")
    print("  - hike_registrations")
    print("  - payments")

if __name__ == "__main__":
    migrate()
