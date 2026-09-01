from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    recipient_id: int
    content: str

class MessageResponse(BaseModel):
    """Schema for message response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_id: int
    sender_username: str
    content: str
    is_read: bool
    created_at: datetime
    
class ConversationParticipantResponse(BaseModel):
    """Schema for conversation participant"""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    profile_picture: Optional[str] = None
    last_read_at: Optional[datetime] = None
    
class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    participants: List[ConversationParticipantResponse]
    last_message: Optional[MessageResponse] = None
    unread_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
class ConversationDetailResponse(BaseModel):
    """Schema for detailed conversation with messages"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    participants: List[ConversationParticipantResponse]
    messages: List[MessageResponse]
    created_at: datetime
    
