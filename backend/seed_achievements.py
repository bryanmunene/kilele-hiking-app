"""
Seed script for populating achievements in the database.
Achievements for gamifying the hiking experience.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.achievement import Achievement
# Import all models to ensure relationships are registered
import models

# Create tables
Base.metadata.create_all(bind=engine)

def seed_achievements():
    db = SessionLocal()
    
    try:
        # Check if achievements already exist
        existing_count = db.query(Achievement).count()
        if existing_count > 0:
            print(f"Achievements already exist ({existing_count} found). Skipping seed.")
            return
        
        achievements = [
            # First Steps
            Achievement(
                name="First Steps",
                description="Complete your first hike",
                icon="🥾",
                category="milestones",
                requirement="complete_1_hike",
                points=10
            ),
            Achievement(
                name="Trail Enthusiast",
                description="Complete 5 different hikes",
                icon="🏃",
                category="milestones",
                requirement="complete_5_hikes",
                points=25
            ),
            Achievement(
                name="Hiking Champion",
                description="Complete 10 different hikes",
                icon="🏆",
                category="milestones",
                requirement="complete_10_hikes",
                points=50
            ),
            Achievement(
                name="Trail Master",
                description="Complete 25 different hikes",
                icon="👑",
                category="milestones",
                requirement="complete_25_hikes",
                points=100
            ),
            Achievement(
                name="Hiking Legend",
                description="Complete 50 different hikes",
                icon="⭐",
                category="milestones",
                requirement="complete_50_hikes",
                points=250
            ),
            
            # Distance Achievements
            Achievement(
                name="10K Walker",
                description="Cover 10km total distance",
                icon="🚶",
                category="distance",
                requirement="distance_10km",
                points=15
            ),
            Achievement(
                name="Marathon Hiker",
                description="Cover 42km total distance",
                icon="🎯",
                category="distance",
                requirement="distance_42km",
                points=40
            ),
            Achievement(
                name="Century Hiker",
                description="Cover 100km total distance",
                icon="💯",
                category="distance",
                requirement="distance_100km",
                points=100
            ),
            Achievement(
                name="Ultra Distance",
                description="Cover 250km total distance",
                icon="🌟",
                category="distance",
                requirement="distance_250km",
                points=200
            ),
            Achievement(
                name="Distance Dominator",
                description="Cover 500km total distance",
                icon="🔥",
                category="distance",
                requirement="distance_500km",
                points=500
            ),
            
            # Elevation Achievements
            Achievement(
                name="Hill Climber",
                description="Gain 500m total elevation",
                icon="⛰️",
                category="elevation",
                requirement="elevation_500m",
                points=20
            ),
            Achievement(
                name="Peak Seeker",
                description="Gain 1000m total elevation",
                icon="🏔️",
                category="elevation",
                requirement="elevation_1000m",
                points=50
            ),
            Achievement(
                name="Mountain Conqueror",
                description="Gain 2500m total elevation",
                icon="🗻",
                category="elevation",
                requirement="elevation_2500m",
                points=100
            ),
            Achievement(
                name="Summit Master",
                description="Gain 5000m total elevation",
                icon="🏅",
                category="elevation",
                requirement="elevation_5000m",
                points=250
            ),
            Achievement(
                name="Everest Equivalent",
                description="Gain 8848m total elevation (Mount Everest height!)",
                icon="🎖️",
                category="elevation",
                requirement="elevation_8848m",
                points=1000
            ),
            
            # Difficulty Achievements
            Achievement(
                name="Easy Does It",
                description="Complete 5 Easy trails",
                icon="🌿",
                category="difficulty",
                requirement="easy_5_hikes",
                points=20
            ),
            Achievement(
                name="Moderate Explorer",
                description="Complete 5 Moderate trails",
                icon="🌲",
                category="difficulty",
                requirement="moderate_5_hikes",
                points=40
            ),
            Achievement(
                name="Hard Core",
                description="Complete 5 Hard trails",
                icon="🪨",
                category="difficulty",
                requirement="hard_5_hikes",
                points=80
            ),
            Achievement(
                name="Extreme Adventurer",
                description="Complete 3 Extreme trails",
                icon="⚡",
                category="difficulty",
                requirement="extreme_3_hikes",
                points=150
            ),
            Achievement(
                name="All-Rounder",
                description="Complete at least one trail of each difficulty",
                icon="🎨",
                category="difficulty",
                requirement="all_difficulties",
                points=100
            ),
            
            # Social Achievements
            Achievement(
                name="Social Butterfly",
                description="Follow 10 other hikers",
                icon="🦋",
                category="social",
                requirement="follow_10_users",
                points=15
            ),
            Achievement(
                name="Popular Hiker",
                description="Get 25 followers",
                icon="👥",
                category="social",
                requirement="get_25_followers",
                points=50
            ),
            Achievement(
                name="Influencer",
                description="Get 100 followers",
                icon="📢",
                category="social",
                requirement="get_100_followers",
                points=200
            ),
            
            # Review Achievements
            Achievement(
                name="Critic's Choice",
                description="Write 5 trail reviews",
                icon="✍️",
                category="reviews",
                requirement="write_5_reviews",
                points=25
            ),
            Achievement(
                name="Helpful Reviewer",
                description="Get 25 'helpful' votes on your reviews",
                icon="👍",
                category="reviews",
                requirement="helpful_25_votes",
                points=50
            ),
            Achievement(
                name="Top Reviewer",
                description="Write 25 trail reviews",
                icon="📝",
                category="reviews",
                requirement="write_25_reviews",
                points=100
            ),
            Achievement(
                name="Photo Journalist",
                description="Upload 50 trail photos",
                icon="📸",
                category="reviews",
                requirement="upload_50_photos",
                points=75
            ),
            
            # Exploration Achievements
            Achievement(
                name="Explorer",
                description="Bookmark 10 trails to explore later",
                icon="🔖",
                category="exploration",
                requirement="bookmark_10_trails",
                points=15
            ),
            Achievement(
                name="Trail Scout",
                description="Visit trails in 5 different locations",
                icon="🧭",
                category="exploration",
                requirement="visit_5_locations",
                points=40
            ),
            Achievement(
                name="Kenya Explorer",
                description="Visit trails in 10 different locations",
                icon="🗺️",
                category="exploration",
                requirement="visit_10_locations",
                points=100
            ),
            
            # Consistency Achievements
            Achievement(
                name="Weekend Warrior",
                description="Complete 4 hikes in 4 consecutive weekends",
                icon="⚔️",
                category="consistency",
                requirement="weekend_warrior",
                points=50
            ),
            Achievement(
                name="Monthly Hiker",
                description="Complete at least one hike per month for 6 months",
                icon="📅",
                category="consistency",
                requirement="monthly_6_months",
                points=100
            ),
            Achievement(
                name="Year-Round Adventurer",
                description="Complete hikes in all 12 months of a year",
                icon="🌍",
                category="consistency",
                requirement="yearly_complete",
                points=250
            ),
            
            # Special Achievements
            Achievement(
                name="Early Bird",
                description="Start a hike before 6 AM",
                icon="🌅",
                category="special",
                requirement="early_bird",
                points=20
            ),
            Achievement(
                name="Sunrise Chaser",
                description="Complete 5 hikes starting before sunrise",
                icon="🌄",
                category="special",
                requirement="sunrise_5_hikes",
                points=60
            ),
            Achievement(
                name="Season Explorer",
                description="Complete hikes in both dry and rainy seasons",
                icon="🌦️",
                category="special",
                requirement="both_seasons",
                points=40
            ),
            Achievement(
                name="Loop Enthusiast",
                description="Complete 10 loop trails",
                icon="🔄",
                category="special",
                requirement="loop_10_trails",
                points=50
            ),
            Achievement(
                name="Point to Point Pro",
                description="Complete 10 point-to-point trails",
                icon="➡️",
                category="special",
                requirement="p2p_10_trails",
                points=50
            ),
        ]
        
        db.add_all(achievements)
        db.commit()
        
        print(f"✅ Successfully seeded {len(achievements)} achievements!")
        print("\nAchievement Categories:")
        categories = {}
        for ach in achievements:
            categories[ach.category] = categories.get(ach.category, 0) + 1
        
        for category, count in sorted(categories.items()):
            print(f"  - {category.capitalize()}: {count} achievements")
        
    except Exception as e:
        print(f"❌ Error seeding achievements: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏆 Seeding achievements...")
    seed_achievements()
