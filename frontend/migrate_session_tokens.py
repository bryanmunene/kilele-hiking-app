"""
Migration script to add session_tokens table
Run this once to update your database
"""
from database import Base, engine, init_database
from models import SessionToken

def migrate():
    """Create session_tokens table"""
    print("Running migration to add session_tokens table...")
    
    # Initialize database (creates all tables including new SessionToken)
    init_database()
    
    print("✅ Migration complete! session_tokens table created.")
    print("You can now use persistent login sessions.")

if __name__ == "__main__":
    migrate()
