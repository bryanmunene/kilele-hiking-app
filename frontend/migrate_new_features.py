"""
Migration script to add new features tables
Run this to update your database with new features
"""
from database import Base, engine, init_database
from models import TrailComment, Goal, EmergencyContact, TrailCondition, Equipment

def migrate():
    """Create new feature tables"""
    print("Running migration to add new feature tables...")
    
    # Initialize database (creates all tables including new ones)
    init_database()
    
    print("✅ Migration complete!")
    print("   - Trail Comments table created")
    print("   - Goals table created")
    print("   - Emergency Contacts table created")
    print("   - Trail Conditions table created")
    print("   - Equipment table created")
    print("\nNew features now available:")
    print("   🎯 Goal Setting")
    print("   💬 Trail Comments")
    print("   🚨 Emergency Contacts")
    print("   🌤️ Trail Condition Reports")
    print("   🎒 Equipment Checklists")

if __name__ == "__main__":
    migrate()
