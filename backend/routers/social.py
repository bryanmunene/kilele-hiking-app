from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
import shutil
from pathlib import Path
import uuid

from database import get_db
from models.user import User
from models.hike import Hike
from models.review import Review, ReviewPhoto, ReviewHelpful
from models.bookmark import Bookmark
from models.follow import Follow
from models.achievement import Achievement, UserAchievement
from models.activity import Activity
from models.hike_session import HikeSession
from schemas.social import (
    ReviewCreate, ReviewResponse, BookmarkCreate, BookmarkResponse,
    FollowCreate, FollowResponse, AchievementResponse, ActivityResponse,
    UserStatistics
)
from auth import get_current_active_user

router = APIRouter()

# ==================== REVIEWS ====================

@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new review for a hike"""
    # Check if hike exists
    hike = db.query(Hike).filter(Hike.id == review.hike_id).first()
    if not hike:
        raise HTTPException(status_code=404, detail="Hike not found")
    
    # Check if user already reviewed this hike
    existing = db.query(Review).filter(
        Review.hike_id == review.hike_id,
        Review.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this hike")
    
    # Create review
    db_review = Review(
        **review.dict(),
        user_id=current_user.id
    )
    db.add(db_review)
    
    # Create activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="review",
        hike_id=review.hike_id,
        description=f"Reviewed {hike.name} - {review.rating}★"
    )
    db.add(activity)
    
    db.commit()
    db.refresh(db_review)
    
    response = ReviewResponse.from_orm(db_review)
    response.username = current_user.username
    response.user_profile_picture = current_user.profile_picture
    return response

@router.get("/reviews/hike/{hike_id}", response_model=List[ReviewResponse])
def get_hike_reviews(
    hike_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific hike"""
    reviews = db.query(Review).filter(Review.hike_id == hike_id)\
        .order_by(desc(Review.created_at))\
        .offset(skip).limit(limit).all()
    
    result = []
    for review in reviews:
        response = ReviewResponse.from_orm(review)
        response.username = review.user.username
        response.user_profile_picture = review.user.profile_picture
        result.append(response)
    
    return result

@router.post("/reviews/{review_id}/helpful")
def mark_review_helpful(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a review as helpful"""
    # Check if already marked
    existing = db.query(ReviewHelpful).filter(
        ReviewHelpful.review_id == review_id,
        ReviewHelpful.user_id == current_user.id
    ).first()
    
    if existing:
        # Unlike
        db.delete(existing)
        db.query(Review).filter(Review.id == review_id).update(
            {Review.helpful_count: Review.helpful_count - 1}
        )
    else:
        # Like
        helpful = ReviewHelpful(review_id=review_id, user_id=current_user.id)
        db.add(helpful)
        db.query(Review).filter(Review.id == review_id).update(
            {Review.helpful_count: Review.helpful_count + 1}
        )
    
    db.commit()
    return {"message": "Updated"}

@router.post("/reviews/{review_id}/photos")
async def upload_review_photo(
    review_id: int,
    file: UploadFile = File(...),
    caption: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload photo for a review"""
    # Verify review belongs to user
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save file
    file_extension = Path(file.filename).suffix
    unique_filename = f"review_{review_id}_{uuid.uuid4()}{file_extension}"
    file_path = Path("static/review_photos") / unique_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create photo record
    photo = ReviewPhoto(
        review_id=review_id,
        photo_url=f"/static/review_photos/{unique_filename}",
        caption=caption
    )
    db.add(photo)
    db.commit()
    
    return {"message": "Photo uploaded", "photo_url": photo.photo_url}

# ==================== BOOKMARKS ====================

@router.post("/bookmarks", response_model=BookmarkResponse, status_code=201)
def create_bookmark(
    bookmark: BookmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bookmark a hike"""
    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.hike_id == bookmark.hike_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already bookmarked")
    
    db_bookmark = Bookmark(**bookmark.dict(), user_id=current_user.id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    
    response = BookmarkResponse.from_orm(db_bookmark)
    hike = db.query(Hike).filter(Hike.id == bookmark.hike_id).first()
    if hike:
        response.hike_name = hike.name
        response.hike_location = hike.location
        response.hike_image = hike.image_url
    
    return response

@router.get("/bookmarks", response_model=List[BookmarkResponse])
def get_my_bookmarks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's bookmarked hikes"""
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    
    result = []
    for bookmark in bookmarks:
        response = BookmarkResponse.from_orm(bookmark)
        hike = db.query(Hike).filter(Hike.id == bookmark.hike_id).first()
        if hike:
            response.hike_name = hike.name
            response.hike_location = hike.location
            response.hike_image = hike.image_url
        result.append(response)
    
    return result

@router.delete("/bookmarks/{hike_id}")
def delete_bookmark(
    hike_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove bookmark"""
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.hike_id == hike_id
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()
    return {"message": "Bookmark removed"}

# ==================== FOLLOWING ====================

@router.post("/follow", response_model=FollowResponse, status_code=201)
def follow_user(
    follow: FollowCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if follow.following_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following
    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == follow.following_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already following")
    
    db_follow = Follow(follower_id=current_user.id, following_id=follow.following_id)
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    
    response = FollowResponse.from_orm(db_follow)
    user = db.query(User).filter(User.id == follow.following_id).first()
    if user:
        response.username = user.username
        response.profile_picture = user.profile_picture
    
    return response

@router.delete("/follow/{user_id}")
def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()
    if not follow:
        raise HTTPException(status_code=404, detail="Not following")
    
    db.delete(follow)
    db.commit()
    return {"message": "Unfollowed"}

@router.get("/followers", response_model=List[FollowResponse])
def get_followers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of followers"""
    follows = db.query(Follow).filter(Follow.following_id == current_user.id).all()
    
    result = []
    for follow in follows:
        response = FollowResponse.from_orm(follow)
        user = db.query(User).filter(User.id == follow.follower_id).first()
        if user:
            response.username = user.username
            response.profile_picture = user.profile_picture
        result.append(response)
    
    return result

@router.get("/following", response_model=List[FollowResponse])
def get_following(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of users I'm following"""
    follows = db.query(Follow).filter(Follow.follower_id == current_user.id).all()
    
    result = []
    for follow in follows:
        response = FollowResponse.from_orm(follow)
        user = db.query(User).filter(User.id == follow.following_id).first()
        if user:
            response.username = user.username
            response.profile_picture = user.profile_picture
        result.append(response)
    
    return result

# ==================== ACTIVITY FEED ====================

@router.get("/feed", response_model=List[ActivityResponse])
def get_activity_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get activity feed from followed users"""
    # Get list of followed users
    following_ids = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).all()
    following_ids = [f[0] for f in following_ids]
    following_ids.append(current_user.id)  # Include own activities
    
    # Get activities
    activities = db.query(Activity).filter(
        Activity.user_id.in_(following_ids)
    ).order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for activity in activities:
        response = ActivityResponse.from_orm(activity)
        response.username = activity.user.username
        response.user_profile_picture = activity.user.profile_picture
        if activity.hike_id:
            hike = db.query(Hike).filter(Hike.id == activity.hike_id).first()
            if hike:
                response.hike_name = hike.name
        result.append(response)
    
    return result

# ==================== ACHIEVEMENTS ====================

@router.get("/achievements", response_model=List[AchievementResponse])
def get_my_achievements(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's achievements"""
    all_achievements = db.query(Achievement).all()
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id
    ).all()
    
    user_ach_dict = {ua.achievement_id: ua for ua in user_achievements}
    
    result = []
    for ach in all_achievements:
        response = AchievementResponse.from_orm(ach)
        if ach.id in user_ach_dict:
            ua = user_ach_dict[ach.id]
            response.earned = ua.completed
            response.progress = ua.progress
            response.earned_at = ua.earned_at
        result.append(response)
    
    return result

# ==================== STATISTICS ====================

@router.get("/statistics", response_model=UserStatistics)
def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    # Count completed hikes
    completed_sessions = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id,
        HikeSession.status == "completed"
    ).all()
    
    total_hikes = len(completed_sessions)
    total_distance = sum(s.distance_km or 0 for s in completed_sessions)
    total_elevation = sum(s.elevation_gain_m or 0 for s in completed_sessions)
    total_duration = sum(s.duration_hours or 0 for s in completed_sessions)
    
    # Review stats
    reviews = db.query(Review).filter(Review.user_id == current_user.id).all()
    total_reviews = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0
    
    # Achievement stats
    achievements_earned = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.completed == True
    ).count()
    
    # Social stats
    followers_count = db.query(Follow).filter(Follow.following_id == current_user.id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == current_user.id).count()
    bookmarks_count = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).count()
    
    return UserStatistics(
        total_hikes=total_hikes,
        total_distance_km=round(total_distance, 2),
        total_elevation_m=round(total_elevation, 0),
        total_duration_hours=round(total_duration, 2),
        total_reviews=total_reviews,
        average_rating_given=round(avg_rating, 2),
        achievements_earned=achievements_earned,
        followers_count=followers_count,
        following_count=following_count,
        bookmarks_count=bookmarks_count
    )
