"""Shared account, moderation and transactional notification persistence."""
import secrets
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, MetaData, String, Table, Text, and_, delete, or_, select, update
from .security import metadata

blocks = Table("user_blocks", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("blocked_id", Integer, primary_key=True))
reports = Table("community_reports", metadata,
    Column("id", Integer, primary_key=True), Column("user_id", Integer, nullable=False),
    Column("target_id", Integer), Column("category", String(40), nullable=False),
    Column("details", Text, nullable=False), Column("status", String(20), default="open", nullable=False),
    Column("resolution", Text), Column("created_at", DateTime, default=datetime.utcnow),
    Column("resolved_at", DateTime))
outbox = Table("notification_outbox", metadata,
    Column("key", String(120), primary_key=True), Column("user_id", Integer, nullable=False),
    Column("kind", String(40), nullable=False), Column("payload", JSON, nullable=False),
    Column("attempts", Integer, default=0, nullable=False),
    Column("available_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow), Column("sent_at", DateTime))


def insert_once(db, table, values):
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    insert = sqlite_insert if db.bind.dialect.name == "sqlite" else pg_insert
    db.execute(insert(table).values(**values).on_conflict_do_nothing())


def enqueue(db, key, user_id, kind, payload=None):
    insert_once(db, outbox, dict(key=key, user_id=user_id, kind=kind, payload=payload or {}))


def is_blocked(db, first, second):
    return db.execute(select(blocks.c.user_id).where(or_(
        and_(blocks.c.user_id == first, blocks.c.blocked_id == second),
        and_(blocks.c.user_id == second, blocks.c.blocked_id == first),
    ))).first() is not None


def set_block(db, user_id, target_id, enabled):
    if user_id == target_id:
        raise ValueError("You cannot block your own account.")
    if enabled:
        insert_once(db, blocks, {"user_id": user_id, "blocked_id": target_id})
    else:
        db.execute(delete(blocks).where(blocks.c.user_id == user_id, blocks.c.blocked_id == target_id))


def submit_report(db, user_id, category, details, target_id=None):
    if category not in {"support", "abuse", "privacy", "trail", "booking"}:
        raise ValueError("Choose a valid report category.")
    details = details.strip()
    if not 10 <= len(details) <= 4000:
        raise ValueError("Enter between 10 and 4,000 characters.")
    return db.execute(reports.insert().values(user_id=user_id, target_id=target_id,
        category=category, details=details).returning(reports.c.id)).scalar_one()


OWNED_TABLES = {
    "reviews": "user_id", "hike_sessions": "user_id", "bookmarks": "user_id",
    "user_achievements": "user_id", "messages": "sender_id", "trail_comments": "user_id",
    "goals": "user_id", "emergency_contacts": "user_id", "trail_conditions": "user_id",
    "planned_hikes": "user_id", "hike_registrations": "user_id", "payments": "user_id",
    "activities": "user_id", "strava_activities": "user_id", "community_reports": "user_id",
    "saved_hikes": "user_id",
}


def reflected_tables(db):
    tables = MetaData()
    tables.reflect(bind=db.connection())
    return tables.tables


def export_account(db, user):
    tables = reflected_tables(db)
    result = {"account": {key: getattr(user, key, None) for key in
        ("id", "username", "email", "full_name", "bio", "experience_level", "created_at")}}
    for name, owner in OWNED_TABLES.items():
        if name in tables and owner in tables[name].c:
            table = tables[name]
            result[name] = [dict(row) for row in db.execute(select(table).where(table.c[owner] == user.id)).mappings()]
    return result


def erase_account(db, user):
    """Remove personal content; retain anonymized booking ledger references."""
    tables = reflected_tables(db)
    planned = tables.get("planned_hikes")
    if planned is not None:
        active = db.execute(select(planned.c.id).where(planned.c.user_id == user.id,
            planned.c.status == "planned", planned.c.planned_date > datetime.utcnow())).first()
        if active:
            raise ValueError("Cancel or transfer your upcoming organized hikes before deleting your account.")
    for name in ("payments", "hike_registrations"):
        table = tables.get(name)
        if table is not None:
            db.execute(update(table).where(table.c.user_id == user.id).values(phone_number=""))
    registration = tables.get("hike_registrations")
    if registration is not None:
        db.execute(update(registration).where(registration.c.user_id == user.id).values(status="cancelled"))
    # Keep parent rows that other users may reference; remove their personal text.
    for name, owner, field in (("messages", "sender_id", "content"), ("trail_comments", "user_id", "comment")):
        table = tables.get(name)
        if table is not None and field in table.c:
            db.execute(update(table).where(table.c[owner] == user.id).values({field: "[deleted]"}))
    reviews_table = tables.get("reviews")
    if reviews_table is not None:
        own_reviews = select(reviews_table.c.id).where(reviews_table.c.user_id == user.id)
        for name in ("review_photos", "review_helpful"):
            table = tables.get(name)
            if table is not None:
                condition = table.c.review_id.in_(own_reviews)
                if "user_id" in table.c:
                    condition = or_(condition, table.c.user_id == user.id)
                db.execute(delete(table).where(condition))
    for name in ("session_tokens", "auth_action_tokens", "strava_activities", "strava_tokens", "reviews",
                 "bookmarks", "user_achievements", "hike_sessions", "goals", "emergency_contacts",
                 "trail_conditions", "activities", "saved_hikes", "conversation_participants", "notification_outbox"):
        table = tables.get(name)
        if table is not None and "user_id" in table.c:
            db.execute(delete(table).where(table.c.user_id == user.id))
    follow = tables.get("follows")
    if follow is not None:
        db.execute(delete(follow).where(or_(follow.c.follower_id == user.id, follow.c.following_id == user.id)))
    db.execute(delete(blocks).where(or_(blocks.c.user_id == user.id, blocks.c.blocked_id == user.id)))
    db.execute(update(reports).where(reports.c.user_id == user.id).values(details="[deleted]"))
    if planned is not None:
        db.execute(update(planned).where(planned.c.user_id == user.id).values(notes=None, meeting_point=None, driving_directions=None, participants=[]))
    suffix = secrets.token_hex(12)
    user.username, user.email = f"deleted_{suffix}", f"deleted_{suffix}@example.invalid"
    user.full_name, user.bio, user.profile_picture = "Deleted account", None, None
    user.hashed_password = "!deleted"
    user.is_active = user.is_admin = False
    user.password_changed_at = datetime.utcnow()
    user.two_factor_enabled = user.two_fa_enabled = False
    user.two_factor_secret = user.two_fa_secret = None
