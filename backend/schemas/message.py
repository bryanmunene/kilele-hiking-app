from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    recipient_id: int
    content: str

class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    conversation_id: int
    sender_id: int
    sender_username: str
    content: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationParticipantResponse(BaseModel):
    """Schema for conversation participant"""
    user_id: int
    username: str
    profile_picture: Optional[str] = None
    last_read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: int
    participants: List[ConversationParticipantResponse]
    last_message: Optional[MessageResponse] = None
    unread_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    """Schema for detailed conversation with messages"""
    id: int
    participants: List[ConversationParticipantResponse]
    messages: List[MessageResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True
