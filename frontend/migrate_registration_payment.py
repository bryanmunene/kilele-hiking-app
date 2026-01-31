"""
Migration script to add new models for hike registration and M-Pesa payments
Run this to update existing databases
"""
from database import engine, Base, SessionLocal
from models import HikeRegistration, Payment, PlannedHike
import sqlite3

def migrate():
    """Add new tables and columns for registration and payments"""
    print("Creating new tables...")
    
    # Create all tables (only creates if they don't exist)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables created")
    
    # Add new columns to existing planned_hikes table
    print("Adding new columns to planned_hikes table...")
    
    try:
        conn = sqlite3.connect('kilele.db')
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(planned_hikes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add price column if it doesn't exist
        if 'price' not in columns:
            cursor.execute("ALTER TABLE planned_hikes ADD COLUMN price REAL DEFAULT 0")
            print("  ✅ Added 'price' column")
        else:
            print("  ℹ️  'price' column already exists")
        
        # Add max_participants column if it doesn't exist
        if 'max_participants' not in columns:
            cursor.execute("ALTER TABLE planned_hikes ADD COLUMN max_participants INTEGER")
            print("  ✅ Added 'max_participants' column")
        else:
            print("  ℹ️  'max_participants' column already exists")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration complete!")
        print("New tables:")
        print("  - hike_registrations")
        print("  - payments")
        print("New columns in planned_hikes:")
        print("  - price")
        print("  - max_participants")
    
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate()
