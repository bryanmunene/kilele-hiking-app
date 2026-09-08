"""Booking tables shared with the Streamlit service's database schema."""
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from database import Base
from models.equipment import PlannedHike


class HikeRegistration(Base):
    __tablename__ = "hike_registrations"
    id = Column(Integer, primary_key=True)
    planned_hike_id = Column(Integer, ForeignKey("planned_hikes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")
    payment_status = Column(String, default="unpaid")
    phone_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    registration_id = Column(Integer, ForeignKey("hike_registrations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    phone_number = Column(String, nullable=False)
    transaction_id = Column(String)
    checkout_request_id = Column(String)
    merchant_request_id = Column(String)
    status = Column(String, default="pending")
    environment = Column(String, default="sandbox")
    payment_method = Column(String, default="mpesa")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
