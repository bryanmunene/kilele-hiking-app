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
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func, or_

# ============= HIKE SERVICES =============

def get_all_hikes(difficulty: str = None, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all hikes with optional filtering"""
    with get_db() as db:
        query = db.query(Hike)
        
        if difficulty:
            query = query.filter(Hike.difficulty == difficulty)
        
        hikes = query.offset(skip).limit(limit).all()
        
        return [{
            "id": h.id,
            "name": h.name,
            "location": h.location,
            "difficulty": h.difficulty,
            "distance_km": h.distance_km,
            "elevation_gain_m": h.elevation_gain_m,
            "estimated_duration_hours": h.estimated_duration_hours,
            "description": h.description,
            "trail_type": h.trail_type,
            "best_season": h.best_season,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "image_url": h.image_url,
            "created_at": h.created_at.isoformat() if h.created_at else None
        } for h in hikes]

def get_hike(hike_id: int) -> Optional[dict]:
    """Get a single hike by ID"""
    with get_db() as db:
        hike = db.query(Hike).filter(Hike.id == hike_id).first()
        if not hike:
            return None
        
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
            "image_url": hike.image_url
        }

def create_hike(hike_data: dict) -> dict:
    """Create a new hike"""
    with get_db() as db:
        new_hike = Hike(**hike_data)
        db.add(new_hike)
        db.flush()
        
        return {"id": new_hike.id, "name": new_hike.name}

# ============= REVIEW SERVICES =============

def get_reviews(hike_id: int) -> List[dict]:
    """Get all reviews for a hike"""
    with get_db() as db:
        reviews = db.query(Review).filter(Review.hike_id == hike_id).all()
        
        return [{
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment,
            "photos": r.photos,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "user": {
                "id": r.user.id,
                "username": r.user.username,
                "profile_picture": r.user.profile_picture
            }
        } for r in reviews]

def create_review(user_id: int, hike_id: int, rating: int, comment: str = None, photos: List[str] = None) -> dict:
    """Create a new review"""
    with get_db() as db:
        review = Review(
            user_id=user_id,
            hike_id=hike_id,
            rating=rating,
            comment=comment,
            photos=photos or []
        )
        db.add(review)
        db.flush()
        
        return {"id": review.id, "rating": rating}

# ============= BOOKMARK SERVICES =============

def get_user_bookmarks(user_id: int) -> List[dict]:
    """Get all bookmarks for a user"""
    with get_db() as db:
        bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
        
        return [{
            "id": b.id,
            "hike": {
                "id": b.hike.id,
                "name": b.hike.name,
                "location": b.hike.location,
                "difficulty": b.hike.difficulty,
                "distance_km": b.hike.distance_km,
                "image_url": b.hike.image_url
            },
            "created_at": b.created_at.isoformat() if b.created_at else None
        } for b in bookmarks]

def create_bookmark(user_id: int, hike_id: int) -> dict:
    """Create a bookmark"""
    with get_db() as db:
        # Check if already bookmarked
        existing = db.query(Bookmark).filter(
            Bookmark.user_id == user_id,
            Bookmark.hike_id == hike_id
        ).first()
        
        if existing:
            raise ValueError("Already bookmarked")
        
        bookmark = Bookmark(user_id=user_id, hike_id=hike_id)
        db.add(bookmark)
        db.flush()
        
        return {"id": bookmark.id}

def delete_bookmark(user_id: int, hike_id: int) -> bool:
    """Delete a bookmark"""
    with get_db() as db:
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
        
        return [{
            "id": s.id,
            "hike_id": s.hike_id,
            "hike_name": s.hike.name if s.hike else None,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "duration_hours": s.duration_hours,
            "distance_covered_km": s.distance_covered_km,
            "elevation_gain_m": s.elevation_gain_m,
            "notes": s.notes,
            "route_data": s.route_data,
            "status": s.status
        } for s in sessions]

def create_session(user_id: int, session_data: dict) -> dict:
    """Create a new hiking session"""
    with get_db() as db:
        session = HikeSession(user_id=user_id, **session_data)
        db.add(session)
        db.flush()
        
        return {"id": session.id}

# ============= SOCIAL SERVICES =============

def get_followers(user_id: int) -> List[dict]:
    """Get all followers for a user"""
    with get_db() as db:
        follows = db.query(Follow).filter(Follow.following_id == user_id).all()
        
        return [{
            "id": f.follower.id,
            "username": f.follower.username,
            "profile_picture": f.follower.profile_picture
        } for f in follows]

def get_following(user_id: int) -> List[dict]:
    """Get all users that a user is following"""
    with get_db() as db:
        follows = db.query(Follow).filter(Follow.follower_id == user_id).all()
        
        return [{
            "id": f.following.id,
            "username": f.following.username,
            "profile_picture": f.following.profile_picture
        } for f in follows]

def follow_user(follower_id: int, following_id: int) -> dict:
    """Follow a user"""
    with get_db() as db:
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
        
        return {"id": follow.id}

def unfollow_user(follower_id: int, following_id: int) -> bool:
    """Unfollow a user"""
    with get_db() as db:
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
                "total_elevation": 0.0,
                "total_duration": 0.0,
                "reviews_count": 0,
                "bookmarks_count": 0
            }
        
        sessions = db.query(HikeSession).filter(HikeSession.user_id == user_id).all()
        reviews_count = db.query(func.count(Review.id)).filter(Review.user_id == user_id).scalar()
        bookmarks_count = db.query(func.count(Bookmark.id)).filter(Bookmark.user_id == user_id).scalar()
        
        total_distance = sum(s.distance_km or 0 for s in sessions)
        total_elevation = sum(s.elevation_gain_m or 0 for s in sessions)
        total_duration = sum(s.duration_hours or 0 for s in sessions)
        
        return {
            "total_hikes": len(sessions),
            "total_distance": round(total_distance, 2),
            "total_elevation": round(total_elevation, 2),
            "total_duration": round(total_duration, 2),
            "reviews_count": reviews_count,
            "bookmarks_count": bookmarks_count
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
        achievements = db.query(Achievement).all()
        return [{
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
            "points": a.points,
            "requirement_type": a.requirement_type,
            "requirement_value": a.requirement_value
        } for a in achievements]

def get_user_achievements(user_id: int) -> List[dict]:
    """Get achievements earned by a user"""
    with get_db() as db:
        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        return [{
            "achievement_id": ua.achievement_id,
            "achievement_name": ua.achievement.name if ua.achievement else None,
            "achievement_description": ua.achievement.description if ua.achievement else None,
            "achievement_icon": ua.achievement.icon if ua.achievement else None,
            "achievement_points": ua.achievement.points if ua.achievement else 0,
            "earned_at": ua.earned_at.isoformat() if ua.earned_at else None
        } for ua in user_achievements]

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
            TrailComment.hike_id == hike_id,
            TrailComment.parent_id == None
        ).order_by(TrailComment.created_at.desc()).all()
        
        result = []
        for c in comments:
            replies = db.query(TrailComment).filter(TrailComment.parent_id == c.id).all()
            result.append({
                "id": c.id,
                "user_id": c.user_id,
                "username": c.user.username if c.user else "Unknown",
                "comment": c.comment,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "replies": [{
                    "id": r.id,
                    "user_id": r.user_id,
                    "username": r.user.username if r.user else "Unknown",
                    "comment": r.comment,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                } for r in replies]
            })
        return result

# ============= GOALS SERVICES =============

def create_goal(user_id: int, title: str, goal_type: str, target_value: float, deadline: datetime = None, description: str = None) -> dict:
    """Create a new goal"""
    from models import Goal
    with get_db() as db:
        new_goal = Goal(
            user_id=user_id,
            title=title,
            goal_type=goal_type,
            target_value=target_value,
            deadline=deadline,
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
    with get_db() as db:
        equipment = db.query(Equipment).filter(Equipment.hike_id == hike_id).all()
        return [{
            "id": e.id,
            "item_name": e.item_name,
            "category": e.category,
            "is_required": e.is_required,
            "notes": e.notes
        } for e in equipment]

# ============= GEAR CATALOG SERVICES =============

def get_all_gear(category: str = None) -> List[dict]:
    """Get all gear items from catalog with optional category filter"""
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

def get_gear_by_id(gear_id: int) -> Optional[dict]:
    """Get a single gear item by ID"""
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

def get_gear_categories() -> List[str]:
    """Get list of unique gear categories"""
    with get_db() as db:
        categories = db.query(Equipment.category).filter(
            Equipment.hike_id.is_(None)
        ).distinct().all()
        return [c[0] for c in categories if c[0]]

# ============= PLANNED HIKE SERVICES =============

def create_planned_hike(user_id: int, hike_id: int, planned_date: datetime, 
                       transport_mode: str = "self_drive", notes: str = None,
                       meeting_point: str = None) -> dict:
    """Create a planned hike"""
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

def get_user_planned_hikes(user_id: int, status: str = None) -> List[dict]:
    """Get all planned hikes for a user"""
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

def update_planned_hike_status(planned_hike_id: int, status: str) -> dict:
    """Update status of a planned hike (planned, completed, cancelled)"""
    with get_db() as db:
        planned_hike = db.query(PlannedHike).filter(PlannedHike.id == planned_hike_id).first()
        if not planned_hike:
            return {"error": "Planned hike not found"}
        
        planned_hike.status = status
        planned_hike.updated_at = datetime.utcnow()
        db.flush()
        
        return {"message": f"Hike status updated to {status}"}

def add_waypoint_to_planned_hike(planned_hike_id: int, waypoint: dict) -> dict:
    """Add a waypoint/pin to driving directions"""
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

def delete_planned_hike(planned_hike_id: int) -> dict:
    """Delete a planned hike"""
    with get_db() as db:
        planned_hike = db.query(PlannedHike).filter(PlannedHike.id == planned_hike_id).first()
        if not planned_hike:
            return {"error": "Planned hike not found"}
        
        db.delete(planned_hike)
        db.flush()
        return {"message": "Planned hike deleted"}

