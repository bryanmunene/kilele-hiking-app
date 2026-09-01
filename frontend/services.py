"""
Service layer for database operations
Replaces all API calls with direct database access
"""
from database import get_db
from models import (
    Hike, User, Review, HikeSession, Bookmark, Achievement, 
    UserAchievement, Follow, Conversation, ConversationParticipant, Message,
    Equipment, PlannedHike
)
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import func, or_


def _iso(value):
    return value.isoformat() if value else None


def _hike_to_dict(hike: Hike) -> dict:
    return {
        "id": hike.id,
        "name": hike.name,
        "location": hike.location,
        "difficulty": hike.difficulty,
        "distance_km": hike.distance_km,
        "elevation_gain_m": hike.elevation_gain_m,
        "estimated_duration_hours": hike.estimated_duration_hours,
        "description": hike.description,
        "trail_type": hike.trail_type,
        "best_season": hike.best_season,
        "latitude": hike.latitude,
        "longitude": hike.longitude,
        "image_url": hike.image_url,
        "created_at": _iso(hike.created_at),
        "updated_at": _iso(getattr(hike, "updated_at", None)),
    }


def _normalize_photos(photos) -> list:
    if not photos:
        return []
    if isinstance(photos, list):
        return [
            photo if isinstance(photo, dict) else {"photo_url": str(photo), "caption": ""}
            for photo in photos
        ]
    return [{"photo_url": str(photos), "caption": ""}]


def _as_datetime(value):
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


def _review_to_dict(review: Review) -> dict:
    conditions = getattr(review, "conditions", None) or getattr(review, "trail_condition", None)
    difficulty_rating = getattr(review, "difficulty_rating", None)
    if difficulty_rating is not None:
        try:
            difficulty_rating = int(difficulty_rating)
        except (TypeError, ValueError):
            difficulty_rating = None

    return {
        "id": review.id,
        "hike_id": review.hike_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "title": review.title or "Trail Review",
        "comment": review.comment or "",
        "difficulty_rating": difficulty_rating,
        "conditions": conditions,
        "trail_condition": conditions,
        "visited_date": _iso(getattr(review, "visited_date", None)),
        "helpful_count": getattr(review, "helpful_count", 0) or 0,
        "photos": _normalize_photos(getattr(review, "photos", None)),
        "created_at": _iso(review.created_at),
        "username": review.user.username if review.user else "Unknown",
        "user": {
            "id": review.user.id,
            "username": review.user.username,
            "profile_picture": review.user.profile_picture,
        } if review.user else None,
    }


def _session_to_dict(session: HikeSession) -> dict:
    status = getattr(session, "status", None) or "in_progress"
    created_at = session.ended_at or session.started_at
    return {
        "id": session.id,
        "hike_id": session.hike_id,
        "hike_name": session.hike.name if session.hike else None,
        "hike_location": session.hike.location if session.hike else None,
        "user_id": session.user_id,
        "username": session.user.username if session.user else "Unknown",
        "started_at": _iso(session.started_at),
        "ended_at": _iso(session.ended_at),
        "completed_at": _iso(session.ended_at),
        "created_at": _iso(created_at),
        "duration_hours": session.duration_hours or 0,
        "distance_covered_km": session.distance_covered_km or 0,
        "elevation_gain_m": session.elevation_gain_m or 0,
        "notes": session.notes,
        "route_data": session.route_data,
        "status": status,
    }


DEFAULT_ACHIEVEMENTS = [
    ("First Steps", "Complete your first hike", "🥾", "milestones", "complete_1_hike", 10),
    ("Trail Enthusiast", "Complete 5 hikes", "🏃", "milestones", "complete_5_hikes", 25),
    ("10K Walker", "Cover 10km total distance", "🚶", "distance", "distance_10km", 15),
    ("Marathon Hiker", "Cover 42km total distance", "🎯", "distance", "distance_42km", 40),
    ("Peak Seeker", "Gain 1000m total elevation", "🏔️", "elevation", "elevation_1000m", 50),
    ("Hard Core", "Complete 5 hard trails", "🪨", "difficulty", "hard_5_hikes", 80),
    ("Explorer", "Bookmark 10 trails to explore later", "🔖", "exploration", "bookmark_10_trails", 15),
    ("Critic's Choice", "Write 5 trail reviews", "✍️", "reviews", "write_5_reviews", 25),
    ("Social Starter", "Follow 3 other hikers", "👥", "social", "follow_3_users", 10),
]


def _ensure_default_achievements(db):
    if db.query(Achievement).count() > 0:
        return

    for name, description, icon, category, requirement, points in DEFAULT_ACHIEVEMENTS:
        db.add(
            Achievement(
                name=name,
                description=description,
                icon=icon,
                category=category,
                requirement=requirement,
                requirement_type=category,
                requirement_value=_achievement_target(requirement),
                points=points,
            )
        )
    db.flush()


def _achievement_target(requirement: str) -> int:
    if not requirement:
        return 1
    for part in requirement.split("_"):
        digits = "".join(ch for ch in part if ch.isdigit())
        if digits:
            return int(digits)
    return 1


def _achievement_current_value(requirement: str, stats: dict) -> float:
    if not requirement:
        return 0
    if requirement.startswith("complete_"):
        return stats["total_hikes"]
    if requirement.startswith("distance_"):
        return stats["total_distance_km"]
    if requirement.startswith("elevation_"):
        return stats["total_elevation_m"]
    if requirement.startswith("write_"):
        return stats["reviews_count"]
    if requirement.startswith("bookmark_"):
        return stats["bookmarks_count"]
    if requirement.startswith("follow_"):
        return stats["following_count"]
    if requirement.startswith("get_"):
        return stats["followers_count"]
    if requirement.startswith("hard_"):
        return stats["hard_hikes"]
    return 0


def _achievement_to_dict(achievement: Achievement, earned=None, stats=None) -> dict:
    requirement = getattr(achievement, "requirement", None) or getattr(achievement, "requirement_type", None)
    target = _achievement_target(requirement)
    current = _achievement_current_value(requirement, stats) if stats else 0
    completed = bool(getattr(earned, "completed", False)) or (bool(earned) and current >= target)
    progress = 100 if completed else min(int((current / target) * 100), 100) if target else 0

    return {
        "id": achievement.id,
        "name": achievement.name,
        "description": achievement.description,
        "icon": achievement.icon,
        "category": getattr(achievement, "category", None) or getattr(achievement, "requirement_type", None) or "milestones",
        "requirement": requirement,
        "requirement_type": getattr(achievement, "requirement_type", None),
        "requirement_value": getattr(achievement, "requirement_value", None),
        "points": achievement.points or 0,
        "earned": completed,
        "progress": getattr(earned, "progress", None) if earned and getattr(earned, "progress", None) else progress,
        "earned_at": _iso(getattr(earned, "earned_at", None)) if earned else None,
    }

# ============= HIKE SERVICES =============

def get_all_hikes(difficulty: str = None, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all hikes with optional filtering"""
    with get_db() as db:
        query = db.query(Hike)
        
        if difficulty:
            query = query.filter(Hike.difficulty == difficulty)
        
        hikes = query.offset(skip).limit(limit).all()
        return [_hike_to_dict(hike) for hike in hikes]

def get_hike(hike_id: int) -> Optional[dict]:
    """Get a single hike by ID"""
    with get_db() as db:
        hike = db.query(Hike).filter(Hike.id == hike_id).first()
        if not hike:
            return None
        return _hike_to_dict(hike)

def create_hike(hike_data: dict) -> dict:
    """Create a new hike"""
    with get_db() as db:
        new_hike = Hike(**hike_data)
        db.add(new_hike)
        db.flush()
        db.refresh(new_hike)
        return _hike_to_dict(new_hike)

# ============= REVIEW SERVICES =============

def get_reviews(hike_id: int = None, user_id: int = None) -> List[dict]:
    """Get reviews, optionally filtered by hike or user."""
    with get_db() as db:
        query = db.query(Review)
        if hike_id is not None:
            query = query.filter(Review.hike_id == hike_id)
        if user_id is not None:
            query = query.filter(Review.user_id == user_id)

        reviews = query.order_by(Review.created_at.desc()).all()
        return [_review_to_dict(review) for review in reviews]

def create_review(
    user_id: int,
    hike_id: int,
    rating: int,
    title: str = None,
    comment: str = None,
    difficulty_rating: int = None,
    conditions: str = None,
    visited_date=None,
    photos: List[str] = None,
) -> dict:
    """Create a new review"""
    with get_db() as db:
        existing = db.query(Review).filter(
            Review.user_id == user_id,
            Review.hike_id == hike_id,
        ).first()
        if existing:
            raise ValueError("You have already reviewed this trail")

        review = Review(
            user_id=user_id,
            hike_id=hike_id,
            rating=rating,
            title=title,
            comment=comment,
            difficulty_rating=difficulty_rating,
            trail_condition=conditions,
            conditions=conditions,
            visited_date=_as_datetime(visited_date),
            photos=photos or [],
        )
        db.add(review)
        db.flush()
        db.refresh(review)
        return _review_to_dict(review)

# ============= BOOKMARK SERVICES =============

def get_user_bookmarks(user_id: int) -> List[dict]:
    """Get all bookmarks for a user"""
    with get_db() as db:
        bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()

        return [{
            "id": b.id,
            "user_id": b.user_id,
            "hike_id": b.hike_id,
            "notes": b.notes,
            "hike": _hike_to_dict(b.hike),
            "created_at": _iso(b.created_at),
        } for b in bookmarks if b.hike]

def create_bookmark(user_id: int, hike_id: int, notes: str = None) -> dict:
    """Create a bookmark"""
    with get_db() as db:
        hike = db.query(Hike).filter(Hike.id == hike_id).first()
        if not hike:
            raise ValueError("Trail not found")

        # Check if already bookmarked
        existing = db.query(Bookmark).filter(
            Bookmark.user_id == user_id,
            Bookmark.hike_id == hike_id
        ).first()
        
        if existing:
            raise ValueError("Already bookmarked")
        
        bookmark = Bookmark(user_id=user_id, hike_id=hike_id, notes=notes)
        db.add(bookmark)
        db.flush()
        return {
            "id": bookmark.id,
            "user_id": bookmark.user_id,
            "hike_id": bookmark.hike_id,
            "notes": bookmark.notes,
            "hike": _hike_to_dict(hike),
            "created_at": _iso(bookmark.created_at),
        }

def delete_bookmark(user_id: int, hike_id: int = None) -> bool:
    """Delete a bookmark by user/trail pair or by bookmark id."""
    with get_db() as db:
        if hike_id is None:
            bookmark = db.query(Bookmark).filter(Bookmark.id == user_id).first()
        else:
            bookmark = db.query(Bookmark).filter(
                Bookmark.user_id == user_id,
                Bookmark.hike_id == hike_id
            ).first()
        
        if bookmark:
            db.delete(bookmark)
            return True
        return False

# ============= SESSION SERVICES =============

def get_user_sessions(user_id: int) -> List[dict]:
    """Get all hiking sessions for a user"""
    with get_db() as db:
        sessions = db.query(HikeSession).filter(HikeSession.user_id == user_id).all()
        return [_session_to_dict(session) for session in sessions]

def create_session(user_id: int, session_data=None, **kwargs) -> dict:
    """Create a new hiking session from either a data dict or legacy args."""
    with get_db() as db:
        payload = dict(session_data) if isinstance(session_data, dict) else {}
        if session_data is not None and not isinstance(session_data, dict):
            payload["hike_id"] = session_data
        payload.update(kwargs)

        if "distance_km" in payload and "distance_covered_km" not in payload:
            payload["distance_covered_km"] = payload.pop("distance_km")
        if "duration_minutes" in payload and "duration_hours" not in payload:
            minutes = payload.pop("duration_minutes") or 0
            payload["duration_hours"] = round(minutes / 60, 2)
        else:
            payload.pop("duration_minutes", None)

        if "ended_at" in payload:
            payload["ended_at"] = _as_datetime(payload["ended_at"])
        if payload.get("status") == "completed" and not payload.get("ended_at"):
            payload["ended_at"] = datetime.utcnow()

        session = HikeSession(user_id=user_id, **payload)
        db.add(session)
        db.flush()
        db.refresh(session)
        return _session_to_dict(session)

# ============= SOCIAL SERVICES =============

def get_followers(user_id: int) -> List[dict]:
    """Get all followers for a user"""
    with get_db() as db:
        follows = db.query(Follow).filter(Follow.following_id == user_id).all()

        return [{
            "id": f.id,
            "follower_user_id": f.follower_id,
            "following_user_id": f.following_id,
            "follower_username": f.follower.username if f.follower else "Unknown",
            "username": f.follower.username if f.follower else "Unknown",
            "profile_picture": f.follower.profile_picture if f.follower else None,
            "created_at": _iso(f.created_at),
        } for f in follows]

def get_following(user_id: int) -> List[dict]:
    """Get all users that a user is following"""
    with get_db() as db:
        follows = db.query(Follow).filter(Follow.follower_id == user_id).all()

        return [{
            "id": f.id,
            "follower_user_id": f.follower_id,
            "following_user_id": f.following_id,
            "following_username": f.following.username if f.following else "Unknown",
            "username": f.following.username if f.following else "Unknown",
            "profile_picture": f.following.profile_picture if f.following else None,
            "created_at": _iso(f.created_at),
        } for f in follows]

def follow_user(follower_id: int, following_id: int) -> dict:
    """Follow a user"""
    with get_db() as db:
        if follower_id == following_id:
            raise ValueError("You cannot follow yourself")

        if not db.query(User).filter(User.id == following_id).first():
            raise ValueError("User not found")

        # Check if already following
        existing = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()
        
        if existing:
            raise ValueError("Already following")
        
        follow = Follow(follower_id=follower_id, following_id=following_id)
        db.add(follow)
        db.flush()
        return {"id": follow.id, "follower_user_id": follower_id, "following_user_id": following_id}

def unfollow_user(follower_id: int, following_id: int = None) -> bool:
    """Unfollow a user by pair or remove a follow row by id."""
    with get_db() as db:
        if following_id is None:
            follow = db.query(Follow).filter(Follow.id == follower_id).first()
        else:
            follow = db.query(Follow).filter(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id
            ).first()
        
        if follow:
            db.delete(follow)
            return True
        return False

# ============= MESSAGE SERVICES =============

def get_user_conversations(user_id: int) -> List[dict]:
    """Get all conversations for a user"""
    with get_db() as db:
        participants = db.query(ConversationParticipant).filter(
            ConversationParticipant.user_id == user_id
        ).all()
        
        conversations = []
        for p in participants:
            conv = p.conversation
            
            # Get other participants
            other_users = [
                {
                    "id": op.user.id,
                    "username": op.user.username,
                    "profile_picture": op.user.profile_picture
                }
                for op in conv.participants if op.user_id != user_id
            ]
            
            # Get last message
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc()).first()
            
            conversations.append({
                "id": conv.id,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "participants": other_users,
                "last_message": {
                    "content": last_message.content,
                    "created_at": last_message.created_at.isoformat(),
                    "sender_id": last_message.sender_id
                } if last_message else None
            })
        
        return conversations

def get_conversation_messages(conversation_id: int, user_id: int) -> List[dict]:
    """Get all messages in a conversation"""
    with get_db() as db:
        # Verify user is participant
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id
        ).first()
        
        if not participant:
            raise ValueError("Not authorized to view this conversation")
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        return [{
            "id": m.id,
            "content": m.content,
            "sender_id": m.sender_id,
            "sender_username": m.sender.username,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in messages]

def send_message(sender_id: int, conversation_id: int, content: str) -> dict:
    """Send a message"""
    with get_db() as db:
        # Verify sender is participant
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == sender_id
        ).first()
        
        if not participant:
            raise ValueError("Not authorized to send message")
        
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content
        )
        db.add(message)
        db.flush()
        
        return {"id": message.id}

def create_conversation(user_ids: List[int]) -> dict:
    """Create a new conversation"""
    with get_db() as db:
        conversation = Conversation()
        db.add(conversation)
        db.flush()
        
        # Add participants
        for user_id in user_ids:
            participant = ConversationParticipant(
                conversation_id=conversation.id,
                user_id=user_id
            )
            db.add(participant)
        
        db.flush()
        return {"id": conversation.id}

# ============= USER SERVICES =============

def get_user_profile(user_id: int) -> Optional[dict]:
    """Get user profile with stats"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get stats
        session_count = db.query(func.count(HikeSession.id)).filter(HikeSession.user_id == user_id).scalar()
        follower_count = db.query(func.count(Follow.id)).filter(Follow.following_id == user_id).scalar()
        following_count = db.query(func.count(Follow.id)).filter(Follow.follower_id == user_id).scalar()
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "stats": {
                "total_hikes": session_count,
                "followers": follower_count,
                "following": following_count
            }
        }

def update_user_profile(user_id: int, updates: dict) -> dict:
    """Update user profile"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Update allowed fields
        for key, value in updates.items():
            if hasattr(user, key) and key not in ['id', 'username', 'hashed_password']:
                setattr(user, key, value)
        
        db.flush()
        return {"id": user.id, "username": user.username}

def get_user_stats(user_id: int) -> dict:
    """Get user statistics"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "total_hikes": 0,
                "total_distance": 0.0,
                "total_distance_km": 0.0,
                "total_elevation": 0.0,
                "total_elevation_m": 0.0,
                "total_duration": 0.0,
                "total_duration_hours": 0.0,
                "reviews_count": 0,
                "bookmarks_count": 0,
                "followers_count": 0,
                "following_count": 0,
                "achievements_earned": 0,
                "total_points": 0,
                "photos_count": 0,
                "helpful_received": 0,
            }

        sessions = db.query(HikeSession).filter(HikeSession.user_id == user_id).all()
        reviews_count = db.query(func.count(Review.id)).filter(Review.user_id == user_id).scalar()
        bookmarks_count = db.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user_id).scalar()
        followers_count = db.query(func.count(Follow.id)).filter(Follow.following_id == user_id).scalar()
        following_count = db.query(func.count(Follow.id)).filter(Follow.follower_id == user_id).scalar()
        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.completed == True
        ).all()

        total_distance = sum(s.distance_covered_km or 0 for s in sessions)
        total_elevation = sum(s.elevation_gain_m or 0 for s in sessions)
        total_duration = sum(s.duration_hours or 0 for s in sessions)
        total_points = sum(ua.achievement.points or 0 for ua in user_achievements if ua.achievement)
        photos_count = sum(len(_normalize_photos(r.photos)) for r in db.query(Review).filter(Review.user_id == user_id).all())
        helpful_received = sum((r.helpful_count or 0) for r in db.query(Review).filter(Review.user_id == user_id).all())
        hard_hikes = sum(
            1 for s in sessions
            if s.status == "completed" and s.hike and s.hike.difficulty == "Hard"
        )

        return {
            "total_hikes": len(sessions),
            "total_distance": round(total_distance, 2),
            "total_distance_km": round(total_distance, 2),
            "total_elevation": round(total_elevation, 2),
            "total_elevation_m": round(total_elevation, 2),
            "total_duration": round(total_duration, 2),
            "total_duration_hours": round(total_duration, 2),
            "reviews_count": reviews_count,
            "bookmarks_count": bookmarks_count,
            "followers_count": followers_count,
            "following_count": following_count,
            "achievements_earned": len(user_achievements),
            "total_points": total_points,
            "photos_count": photos_count,
            "helpful_received": helpful_received,
            "hard_hikes": hard_hikes,
        }

def search_users(query: str) -> List[dict]:
    """Search users by username or full name"""
    with get_db() as db:
        users = db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            )
        ).limit(20).all()
        
        return [{
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "profile_picture": u.profile_picture
        } for u in users]

def get_all_achievements() -> List[dict]:
    """Get all available achievements"""
    with get_db() as db:
        _ensure_default_achievements(db)
        achievements = db.query(Achievement).all()
        return [_achievement_to_dict(achievement) for achievement in achievements]

def get_user_achievements(user_id: int) -> List[dict]:
    """Get all achievements with the user's progress and earned state."""
    with get_db() as db:
        _ensure_default_achievements(db)
        sessions = db.query(HikeSession).filter(HikeSession.user_id == user_id).all()
        reviews = db.query(Review).filter(Review.user_id == user_id).all()
        stats = {
            "total_hikes": len([s for s in sessions if s.status == "completed"]),
            "total_distance_km": sum(s.distance_covered_km or 0 for s in sessions),
            "total_elevation_m": sum(s.elevation_gain_m or 0 for s in sessions),
            "reviews_count": len(reviews),
            "bookmarks_count": db.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user_id).scalar(),
            "following_count": db.query(func.count(Follow.id)).filter(Follow.follower_id == user_id).scalar(),
            "followers_count": db.query(func.count(Follow.id)).filter(Follow.following_id == user_id).scalar(),
            "hard_hikes": sum(
                1 for s in sessions
                if s.status == "completed" and s.hike and s.hike.difficulty == "Hard"
            ),
        }

        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        earned_by_id = {ua.achievement_id: ua for ua in user_achievements}

        # Mark newly completed achievements as earned.
        for achievement in db.query(Achievement).all():
            requirement = achievement.requirement or achievement.requirement_type
            target = _achievement_target(requirement)
            current = _achievement_current_value(requirement, stats)
            progress = 100 if current >= target else min(int((current / target) * 100), 100) if target else 0

            if achievement.id not in earned_by_id:
                if current < target:
                    continue
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress=progress,
                    completed=current >= target,
                )
                db.add(user_achievement)
                db.flush()
                earned_by_id[achievement.id] = user_achievement
                continue

            user_achievement = earned_by_id[achievement.id]
            user_achievement.progress = max(user_achievement.progress or 0, progress)
            if current >= target:
                user_achievement.completed = True

        achievements = db.query(Achievement).all()
        return [
            _achievement_to_dict(achievement, earned_by_id.get(achievement.id), stats)
            for achievement in achievements
        ]

# ============= ADMIN SERVICES =============

def get_all_users_admin(skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all users (admin only)"""
    with get_db() as db:
        users = db.query(User).offset(skip).limit(limit).all()
        return [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_admin": u.is_admin,
            "is_active": u.is_active,
            "two_factor_enabled": u.two_factor_enabled,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users]

def get_platform_stats() -> dict:
    """Get overall platform statistics (admin only)"""
    with get_db() as db:
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        total_hikes = db.query(func.count(Hike.id)).scalar()
        total_reviews = db.query(func.count(Review.id)).scalar()
        total_sessions = db.query(func.count(HikeSession.id)).scalar()
        total_bookmarks = db.query(func.count(Bookmark.id)).scalar()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_hikes": total_hikes,
            "total_reviews": total_reviews,
            "total_sessions": total_sessions,
            "total_bookmarks": total_bookmarks
        }

def toggle_user_status(user_id: int, is_active: bool) -> bool:
    """Activate/deactivate user (admin only)"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.is_active = is_active
        db.flush()
        return True

def toggle_admin_status(user_id: int, is_admin: bool) -> bool:
    """Grant/revoke admin privileges (admin only)"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.is_admin = is_admin
        db.flush()
        return True

def delete_user_admin(user_id: int) -> bool:
    """Delete user and all related data (admin only)"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.flush()
        return True

def delete_hike_admin(hike_id: int) -> bool:
    """Delete hike and all related data (admin only)"""
    with get_db() as db:
        hike = db.query(Hike).filter(Hike.id == hike_id).first()
        if not hike:
            return False
        db.delete(hike)
        db.flush()
        return True

def delete_review_admin(review_id: int) -> bool:
    """Delete review (admin only)"""
    with get_db() as db:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return False
        db.delete(review)
        db.flush()
        return True

def get_all_reviews_admin(skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all reviews with user info (admin only)"""
    with get_db() as db:
        reviews = db.query(Review).offset(skip).limit(limit).all()
        return [{
            "id": r.id,
            "hike_id": r.hike_id,
            "hike_name": r.hike.name if r.hike else None,
            "user_id": r.user_id,
            "username": r.user.username if r.user else None,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in reviews]

def get_recent_activity(limit: int = 50) -> List[dict]:
    """Get recent platform activity (admin only)"""
    with get_db() as db:
        # Get recent reviews
        recent_reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
        # Get recent sessions
        recent_sessions = db.query(HikeSession).order_by(HikeSession.started_at.desc()).limit(limit).all()
        
        activities = []
        
        for r in recent_reviews:
            activities.append({
                "type": "review",
                "user": r.user.username if r.user else "Unknown",
                "hike": r.hike.name if r.hike else "Unknown",
                "rating": r.rating,
                "timestamp": r.created_at.isoformat() if r.created_at else None
            })
        
        for s in recent_sessions:
            activities.append({
                "type": "session",
                "user": s.user.username if s.user else "Unknown",
                "hike": s.hike.name if s.hike else "Unknown",
                "duration": s.duration_hours * 60 if s.duration_hours else None,  # Convert to minutes
                "timestamp": s.started_at.isoformat() if s.started_at else None
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return activities[:limit]


def get_activity_feed(user_id: int, limit: int = 20) -> List[dict]:
    """Build an activity feed for the current user and followed hikers."""
    with get_db() as db:
        following_ids = [
            row[0] for row in db.query(Follow.following_id)
            .filter(Follow.follower_id == user_id)
            .all()
        ]
        visible_user_ids = set(following_ids + [user_id])

        activities = []

        sessions = db.query(HikeSession).filter(
            HikeSession.user_id.in_(visible_user_ids),
            HikeSession.status == "completed",
        ).all()
        for session in sessions:
            created_at = session.ended_at or session.started_at
            activities.append({
                "id": f"session-{session.id}",
                "activity_type": "completed_hike",
                "user_id": session.user_id,
                "username": session.user.username if session.user else "Unknown",
                "hike_id": session.hike_id,
                "hike_name": session.hike.name if session.hike else "Unknown",
                "hike_location": session.hike.location if session.hike else None,
                "description": f"completed {session.hike.name if session.hike else 'a hike'}",
                "created_at": _iso(created_at),
            })

        reviews = db.query(Review).filter(Review.user_id.in_(visible_user_ids)).all()
        for review in reviews:
            activities.append({
                "id": f"review-{review.id}",
                "activity_type": "review",
                "user_id": review.user_id,
                "username": review.user.username if review.user else "Unknown",
                "hike_id": review.hike_id,
                "hike_name": review.hike.name if review.hike else "Unknown",
                "hike_location": review.hike.location if review.hike else None,
                "description": f"reviewed {review.hike.name if review.hike else 'a trail'}",
                "created_at": _iso(review.created_at),
            })

        bookmarks = db.query(Bookmark).filter(Bookmark.user_id.in_(visible_user_ids)).all()
        for bookmark in bookmarks:
            activities.append({
                "id": f"bookmark-{bookmark.id}",
                "activity_type": "bookmark",
                "user_id": bookmark.user_id,
                "username": bookmark.user.username if bookmark.user else "Unknown",
                "hike_id": bookmark.hike_id,
                "hike_name": bookmark.hike.name if bookmark.hike else "Unknown",
                "hike_location": bookmark.hike.location if bookmark.hike else None,
                "description": f"saved {bookmark.hike.name if bookmark.hike else 'a trail'}",
                "created_at": _iso(bookmark.created_at),
            })

        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id.in_(visible_user_ids),
            UserAchievement.completed == True,
        ).all()
        for earned in user_achievements:
            activities.append({
                "id": f"achievement-{earned.id}",
                "activity_type": "achievement",
                "user_id": earned.user_id,
                "username": earned.user.username if earned.user else "Unknown",
                "hike_id": None,
                "hike_name": None,
                "hike_location": None,
                "description": f"earned {earned.achievement.name if earned.achievement else 'an achievement'}",
                "created_at": _iso(earned.earned_at),
            })

        activities.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return activities[:limit]

# ============= TRAIL COMMENTS SERVICES =============

def add_trail_comment(hike_id: int, user_id: int, comment: str, parent_id: int = None) -> dict:
    """Add a comment to a trail"""
    from models import TrailComment
    with get_db() as db:
        new_comment = TrailComment(
            hike_id=hike_id,
            user_id=user_id,
            comment=comment,
            parent_id=parent_id
        )
        db.add(new_comment)
        db.flush()
        return {"id": new_comment.id, "message": "Comment added successfully"}

def get_trail_comments(hike_id: int) -> List[dict]:
    """Get all comments for a trail"""
    from models import TrailComment
    with get_db() as db:
        comments = db.query(TrailComment).filter(
            TrailComment.hike_id == hike_id
        ).order_by(TrailComment.created_at.desc()).all()
        
        return [
            {
                "id": c.id,
                "hike_id": c.hike_id,
                "user_id": c.user_id,
                "username": c.user.username if c.user else "Unknown",
                "comment": c.comment,
                "parent_id": c.parent_id,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in comments
        ]

# ============= GOALS SERVICES =============

def create_goal(user_id: int, title: str, goal_type: str, target_value: float, deadline: datetime = None, description: str = None) -> dict:
    """Create a new goal"""
    from models import Goal
    with get_db() as db:
        parsed_deadline = _as_datetime(deadline)
        new_goal = Goal(
            user_id=user_id,
            title=title,
            goal_type=goal_type,
            target_value=target_value,
            deadline=parsed_deadline,
            description=description
        )
        db.add(new_goal)
        db.flush()
        return {"id": new_goal.id, "message": "Goal created successfully"}

def get_user_goals(user_id: int) -> List[dict]:
    """Get all goals for a user"""
    from models import Goal
    with get_db() as db:
        goals = db.query(Goal).filter(Goal.user_id == user_id).order_by(Goal.created_at.desc()).all()
        return [{
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "goal_type": g.goal_type,
            "target_value": g.target_value,
            "current_value": g.current_value,
            "progress": (g.current_value / g.target_value * 100) if g.target_value > 0 else 0,
            "deadline": g.deadline.isoformat() if g.deadline else None,
            "status": g.status,
            "completed_at": g.completed_at.isoformat() if g.completed_at else None,
            "created_at": g.created_at.isoformat() if g.created_at else None
        } for g in goals]

def update_goal_progress(goal_id: int, current_value: float) -> bool:
    """Update goal progress"""
    from models import Goal
    with get_db() as db:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return False
        goal.current_value = current_value
        if current_value >= goal.target_value:
            goal.status = "completed"
            goal.completed_at = goal.completed_at or datetime.utcnow()
        elif goal.status == "completed":
            goal.status = "active"
            goal.completed_at = None
        db.flush()
        return True

# ============= EMERGENCY CONTACTS SERVICES =============

def add_emergency_contact(user_id: int, name: str, phone: str, relation: str = None, is_primary: bool = False) -> dict:
    """Add emergency contact"""
    from models import EmergencyContact
    with get_db() as db:
        if is_primary:
            # Remove primary from other contacts
            db.query(EmergencyContact).filter(EmergencyContact.user_id == user_id).update({"is_primary": False})
        
        contact = EmergencyContact(
            user_id=user_id,
            name=name,
            phone=phone,
            relation=relation,
            is_primary=is_primary
        )
        db.add(contact)
        db.flush()
        return {"id": contact.id, "message": "Emergency contact added"}

def get_emergency_contacts(user_id: int) -> List[dict]:
    """Get all emergency contacts for a user"""
    from models import EmergencyContact
    with get_db() as db:
        contacts = db.query(EmergencyContact).filter(EmergencyContact.user_id == user_id).all()
        return [{
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "relation": c.relation,
            "is_primary": c.is_primary
        } for c in contacts]

def delete_emergency_contact(contact_id: int) -> bool:
    """Delete an emergency contact"""
    from models import EmergencyContact
    with get_db() as db:
        contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
        if not contact:
            return False
        db.delete(contact)
        db.flush()
        return True

# ============= TRAIL CONDITIONS SERVICES =============

def add_trail_condition(hike_id: int, user_id: int, condition: str, weather: str = None, notes: str = None) -> dict:
    """Report trail condition"""
    from models import TrailCondition
    with get_db() as db:
        report = TrailCondition(
            hike_id=hike_id,
            user_id=user_id,
            condition=condition,
            weather=weather,
            notes=notes
        )
        db.add(report)
        db.flush()
        return {"id": report.id, "message": "Trail condition reported"}

def get_trail_conditions(hike_id: int, limit: int = 10) -> List[dict]:
    """Get recent trail conditions"""
    from models import TrailCondition
    with get_db() as db:
        conditions = db.query(TrailCondition).filter(
            TrailCondition.hike_id == hike_id
        ).order_by(TrailCondition.created_at.desc()).limit(limit).all()
        return [{
            "id": c.id,
            "condition": c.condition,
            "weather": c.weather,
            "notes": c.notes,
            "username": c.user.username if c.user else "Unknown",
            "created_at": c.created_at.isoformat() if c.created_at else None
        } for c in conditions]

# ============= EQUIPMENT SERVICES =============

def add_equipment(hike_id: int, item_name: str, category: str, is_required: bool = False, notes: str = None) -> dict:
    """Add equipment recommendation for a trail"""
    from models import Equipment
    with get_db() as db:
        equipment = Equipment(
            hike_id=hike_id,
            item_name=item_name,
            category=category,
            is_required=is_required,
            notes=notes
        )
        db.add(equipment)
        db.flush()
        return {"id": equipment.id, "message": "Equipment added"}

def get_trail_equipment(hike_id: int) -> List[dict]:
    """Get equipment list for a trail"""
    from models import Equipment
    try:
        with get_db() as db:
            equipment = db.query(Equipment).filter(Equipment.hike_id == hike_id).all()
            return [{
                "id": e.id,
                "item_name": e.item_name,
                "category": e.category,
                "is_required": e.is_required,
                "notes": e.notes
            } for e in equipment]
    except Exception:
        # Return empty list if Equipment table doesn't exist yet
        return []

# ============= GEAR CATALOG SERVICES =============

def get_all_gear(category: str = None) -> List[dict]:
    """Get all gear items from catalog with optional category filter"""
    try:
        with get_db() as db:
            query = db.query(Equipment).filter(Equipment.hike_id.is_(None))
            
            if category:
                query = query.filter(Equipment.category == category)
            
            gear = query.order_by(Equipment.category, Equipment.item_name).all()
            
            return [{
                "id": g.id,
                "item_name": g.item_name,
                "category": g.category,
                "price": g.price,
                "vendor": g.vendor,
                "brand": g.brand,
                "is_required": g.is_required,
                "notes": g.notes,
                "image_url": g.image_url
            } for g in gear]
    except Exception:
        # Return empty list if Equipment table doesn't exist yet
        return []

def get_gear_by_id(gear_id: int) -> Optional[dict]:
    """Get a single gear item by ID"""
    try:
        with get_db() as db:
            gear = db.query(Equipment).filter(Equipment.id == gear_id).first()
            if not gear:
                return None
            
            return {
                "id": gear.id,
                "item_name": gear.item_name,
                "category": gear.category,
                "price": gear.price,
                "vendor": gear.vendor,
                "brand": gear.brand,
                "is_required": gear.is_required,
                "notes": gear.notes,
                "image_url": gear.image_url
            }
    except Exception:
        return None

def get_gear_categories() -> List[str]:
    """Get list of unique gear categories"""
    try:
        with get_db() as db:
            categories = db.query(Equipment.category).filter(
                Equipment.hike_id.is_(None)
            ).distinct().all()
            return [c[0] for c in categories if c[0]]
    except Exception:
        return []

# ============= PLANNED HIKE SERVICES =============

def create_planned_hike(user_id: int, hike_id: int, planned_date: datetime, 
                       transport_mode: str = "self_drive", notes: str = None,
                       meeting_point: str = None) -> dict:
    """Create a planned hike"""
    try:
        with get_db() as db:
            planned_hike = PlannedHike(
                user_id=user_id,
                hike_id=hike_id,
                planned_date=planned_date,
                transport_mode=transport_mode,
                notes=notes,
                meeting_point=meeting_point,
                status="planned",
                participants=[user_id]  # Creator is automatically a participant
            )
            db.add(planned_hike)
            db.flush()
            return {
                "id": planned_hike.id,
                "message": "Hike planned successfully"
            }
    except Exception as e:
        return {"error": "Unable to create planned hike. Database may need updating."}

def get_user_planned_hikes(user_id: int, status: str = None) -> List[dict]:
    """Get all planned hikes for a user"""
    try:
        with get_db() as db:
            query = db.query(PlannedHike).filter(PlannedHike.user_id == user_id)
            
            if status:
                query = query.filter(PlannedHike.status == status)
            
            planned_hikes = query.order_by(PlannedHike.planned_date).all()
            
            results = []
            for ph in planned_hikes:
                hike = db.query(Hike).filter(Hike.id == ph.hike_id).first()
                results.append({
                    "id": ph.id,
                    "hike_id": ph.hike_id,
                    "hike_name": hike.name if hike else "Unknown",
                    "hike_location": hike.location if hike else "Unknown",
                    "hike_latitude": hike.latitude if hike else None,
                    "hike_longitude": hike.longitude if hike else None,
                    "planned_date": ph.planned_date.isoformat(),
                    "status": ph.status,
                "transport_mode": ph.transport_mode,
                "meeting_point": ph.meeting_point,
                "notes": ph.notes,
                "participants": ph.participants,
                "driving_directions": ph.driving_directions
            })
        
            return results
    except Exception:
        return []

def update_planned_hike_status(planned_hike_id: int, status: str) -> dict:
    """Update status of a planned hike (planned, completed, cancelled)"""
    try:
        with get_db() as db:
            planned_hike = db.query(PlannedHike).filter(PlannedHike.id == planned_hike_id).first()
            if not planned_hike:
                return {"error": "Planned hike not found"}
            
            planned_hike.status = status
            planned_hike.updated_at = datetime.utcnow()
            db.flush()
            
            return {"message": f"Hike status updated to {status}"}
    except Exception:
        return {"error": "Unable to update hike status"}

def add_waypoint_to_planned_hike(planned_hike_id: int, waypoint: dict) -> dict:
    """Add a waypoint/pin to driving directions"""
    try:
        with get_db() as db:
            planned_hike = db.query(PlannedHike).filter(PlannedHike.id == planned_hike_id).first()
            if not planned_hike:
                return {"error": "Planned hike not found"}
            
            if planned_hike.driving_directions is None:
                planned_hike.driving_directions = []
            
            planned_hike.driving_directions.append(waypoint)
            planned_hike.updated_at = datetime.utcnow()
            db.flush()
            
            return {"message": "Waypoint added successfully"}
    except Exception:
        return {"error": "Unable to add waypoint"}

def delete_planned_hike(planned_hike_id: int) -> dict:
    """Delete a planned hike"""
    try:
        with get_db() as db:
            planned_hike = db.query(PlannedHike).filter(PlannedHike.id == planned_hike_id).first()
            if not planned_hike:
                return {"error": "Planned hike not found"}
            
            db.delete(planned_hike)
            db.flush()
            return {"message": "Planned hike deleted"}
    except Exception:
        return {"error": "Unable to delete planned hike"}


# Hike Registration Services
def register_for_hike(user_id: int, planned_hike_id: int, phone_number: str) -> dict:
    """Register a user for an upcoming hike"""
    try:
        from models import HikeRegistration, PlannedHike
        with get_db() as db:
            # Check if hike exists
            planned_hike = db.query(PlannedHike).filter(PlannedHike.id == planned_hike_id).first()
            if not planned_hike:
                return {"error": "Hike not found"}
            
            # Check if already registered
            existing = db.query(HikeRegistration).filter(
                HikeRegistration.planned_hike_id == planned_hike_id,
                HikeRegistration.user_id == user_id
            ).first()
            if existing:
                return {"error": "Already registered for this hike"}
            
            # Check capacity
            if planned_hike.max_participants:
                current_registrations = db.query(HikeRegistration).filter(
                    HikeRegistration.planned_hike_id == planned_hike_id,
                    HikeRegistration.status != "cancelled"
                ).count()
                if current_registrations >= planned_hike.max_participants:
                    return {"error": "Hike is full"}
            
            # Create registration
            registration = HikeRegistration(
                planned_hike_id=planned_hike_id,
                user_id=user_id,
                phone_number=phone_number,
                status="confirmed" if planned_hike.price == 0 else "pending",
                payment_status="paid" if planned_hike.price == 0 else "unpaid"
            )
            db.add(registration)
            db.flush()
            db.refresh(registration)
            
            return {
                "registration_id": registration.id,
                "status": registration.status,
                "payment_required": planned_hike.price > 0,
                "amount": planned_hike.price
            }
    except Exception as e:
        return {"error": f"Registration failed: {str(e)}"}


def get_user_registrations(user_id: int) -> list:
    """Get all hike registrations for a user"""
    try:
        from models import HikeRegistration, PlannedHike, Hike
        with get_db() as db:
            registrations = db.query(HikeRegistration).filter(
                HikeRegistration.user_id == user_id
            ).order_by(HikeRegistration.created_at.desc()).all()
            
            result = []
            for reg in registrations:
                planned_hike = db.query(PlannedHike).filter(PlannedHike.id == reg.planned_hike_id).first()
                if planned_hike:
                    hike = db.query(Hike).filter(Hike.id == planned_hike.hike_id).first()
                    result.append({
                        "registration_id": reg.id,
                        "hike_name": hike.name if hike else "Unknown",
                        "hike_location": hike.location if hike else "",
                        "planned_date": planned_hike.planned_date.isoformat(),
                        "status": reg.status,
                        "payment_status": reg.payment_status,
                        "price": planned_hike.price,
                        "created_at": reg.created_at.isoformat()
                    })
            
            return result
    except Exception:
        return []


def create_payment(registration_id: int, user_id: int, amount: float, phone_number: str) -> dict:
    """Create a payment record"""
    try:
        from models import Payment
        with get_db() as db:
            payment = Payment(
                registration_id=registration_id,
                user_id=user_id,
                amount=amount,
                phone_number=phone_number,
                status="pending"
            )
            db.add(payment)
            db.flush()
            db.refresh(payment)
            
            return {
                "payment_id": payment.id,
                "status": payment.status
            }
    except Exception as e:
        return {"error": f"Payment creation failed: {str(e)}"}


def update_payment_status(payment_id: int, status: str, transaction_id: str = None, 
                         checkout_request_id: str = None, merchant_request_id: str = None) -> dict:
    """Update payment status after M-Pesa response"""
    try:
        from models import Payment, HikeRegistration
        with get_db() as db:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                return {"error": "Payment not found"}
            
            payment.status = status
            if transaction_id:
                payment.transaction_id = transaction_id
            if checkout_request_id:
                payment.checkout_request_id = checkout_request_id
            if merchant_request_id:
                payment.merchant_request_id = merchant_request_id
            payment.updated_at = datetime.utcnow()
            
            # Update registration status if payment completed
            if status == "completed":
                registration = db.query(HikeRegistration).filter(
                    HikeRegistration.id == payment.registration_id
                ).first()
                if registration:
                    registration.payment_status = "paid"
                    registration.status = "confirmed"
            
            db.flush()
            return {"message": "Payment updated successfully"}
    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}


def get_hike_registrations(planned_hike_id: int) -> list:
    """Get all registrations for a specific hike (for organizers)"""
    try:
        from models import HikeRegistration, User
        with get_db() as db:
            registrations = db.query(HikeRegistration).filter(
                HikeRegistration.planned_hike_id == planned_hike_id
            ).all()
            
            result = []
            for reg in registrations:
                user = db.query(User).filter(User.id == reg.user_id).first()
                result.append({
                    "registration_id": reg.id,
                    "user_name": user.username if user else "Unknown",
                    "phone_number": reg.phone_number,
                    "status": reg.status,
                    "payment_status": reg.payment_status,
                    "created_at": reg.created_at.isoformat()
                })
            
            return result
    except Exception:
        return []
