"""
Production database migration script
Migrates data from SQLite to PostgreSQL
"""
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Source database (SQLite)
SOURCE_DB = "sqlite:///./kilele.db"

# Target database (PostgreSQL - set via environment variable)
import os
from dotenv import load_dotenv
load_dotenv()

TARGET_DB = os.getenv("DATABASE_URL")

if not TARGET_DB or "sqlite" in TARGET_DB:
    print("❌ Error: Set DATABASE_URL environment variable to PostgreSQL connection string")
    print("Example: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
    sys.exit(1)

print("=" * 60)
print("  Kilele Database Migration: SQLite → PostgreSQL")
print("=" * 60)
print(f"\n📦 Source: {SOURCE_DB}")
print(f"🎯 Target: {TARGET_DB[:50]}...")
print()

# Create engines
source_engine = create_engine(SOURCE_DB)
target_engine = create_engine(TARGET_DB)

# Import models
from models import Base, user, hike, review, achievement, activity, bookmark, follow, hike_session, message

# Create all tables in target database
print("🔧 Creating tables in PostgreSQL...")
Base.metadata.create_all(bind=target_engine)
print("✅ Tables created")

# Create sessions
SourceSession = sessionmaker(bind=source_engine)
TargetSession = sessionmaker(bind=target_engine)

source_session = SourceSession()
target_session = TargetSession()

# Models to migrate (in dependency order)
models_to_migrate = [
    ("User", user.User),
    ("Hike", hike.Hike),
    ("Review", review.Review),
    ("HikeSession", hike_session.HikeSession),
    ("Bookmark", bookmark.Bookmark),
    ("Achievement", achievement.Achievement),
    ("UserAchievement", achievement.UserAchievement),
    ("Follow", follow.Follow),
    ("Activity", activity.Activity),
    ("Conversation", message.Conversation),
    ("ConversationParticipant", message.ConversationParticipant),
    ("Message", message.Message),
    ("SessionToken", user.SessionToken),
]

try:
    total_migrated = 0
    
    for model_name, Model in models_to_migrate:
        print(f"\n📊 Migrating {model_name}...", end=" ")
        
        try:
            # Get all records from source
            records = source_session.query(Model).all()
            
            if not records:
                print(f"(empty)")
                continue
            
            # Add to target database
            for record in records:
                # Create new object with same data
                target_session.merge(record)
            
            target_session.commit()
            print(f"✅ {len(records)} records")
            total_migrated += len(records)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            target_session.rollback()
            continue
    
    print("\n" + "=" * 60)
    print(f"✅ Migration complete! {total_migrated} total records migrated")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    target_session.rollback()
    sys.exit(1)
finally:
    source_session.close()
    target_session.close()

print("\n✅ PostgreSQL database is ready for production!")
print("\n📝 Next steps:")
print("  1. Update .env file with DATABASE_URL (PostgreSQL)")
print("  2. Test backend: python main.py")
print("  3. Deploy to Railway/Render")
