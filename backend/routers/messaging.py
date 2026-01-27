from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List
from datetime import datetime

from database import get_db
from models.user import User
from models.message import Message, Conversation, ConversationParticipant
from schemas.message import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationParticipantResponse
)
from routers.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/messages", tags=["messaging"])

def get_or_create_conversation(db: Session, user1_id: int, user2_id: int) -> Conversation:
    """Get existing conversation between two users or create a new one"""
    # Find existing conversation
    conversation = db.query(Conversation).join(
        ConversationParticipant, Conversation.id == ConversationParticipant.conversation_id
    ).filter(
        ConversationParticipant.user_id.in_([user1_id, user2_id])
    ).group_by(
        Conversation.id
    ).having(
        func.count(ConversationParticipant.user_id) == 2
    ).first()
    
    if conversation:
        # Verify both users are in this conversation
        participant_ids = [p.user_id for p in conversation.participants]
        if user1_id in participant_ids and user2_id in participant_ids:
            return conversation
    
    # Create new conversation
    new_conversation = Conversation()
    db.add(new_conversation)
    db.flush()
    
    # Add participants
    participant1 = ConversationParticipant(conversation_id=new_conversation.id, user_id=user1_id)
    participant2 = ConversationParticipant(conversation_id=new_conversation.id, user_id=user2_id)
    db.add(participant1)
    db.add(participant2)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    # Get all conversation IDs where user is a participant
    user_conversations = db.query(Conversation).join(
        ConversationParticipant
    ).filter(
        ConversationParticipant.user_id == current_user.id
    ).order_by(
        Conversation.updated_at.desc()
    ).all()
    
    result = []
    for conv in user_conversations:
        # Get participants info
        participants = []
        for participant in conv.participants:
            if participant.user_id != current_user.id:  # Don't include current user
                participants.append(ConversationParticipantResponse(
                    user_id=participant.user.id,
                    username=participant.user.username,
                    profile_picture=participant.user.profile_picture,
                    last_read_at=participant.last_read_at
                ))
        
        # Get last message
        last_message = None
        if conv.messages:
            last_msg = conv.messages[-1]
            last_message = MessageResponse(
                id=last_msg.id,
                conversation_id=last_msg.conversation_id,
                sender_id=last_msg.sender_id,
                sender_username=last_msg.sender.username,
                content=last_msg.content,
                is_read=last_msg.is_read,
                created_at=last_msg.created_at
            )
        
        # Count unread messages
        unread_count = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        ).count()
        
        result.append(ConversationResponse(
            id=conv.id,
            participants=participants,
            last_message=last_message,
            unread_count=unread_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))
    
    return result

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify user is a participant
    is_participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == current_user.id
    ).first()
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="You are not a participant in this conversation")
    
    # Mark messages as read
    db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    
    # Update last_read_at
    is_participant.last_read_at = datetime.utcnow()
    db.commit()
    
    # Get participants
    participants = []
    for participant in conversation.participants:
        participants.append(ConversationParticipantResponse(
            user_id=participant.user.id,
            username=participant.user.username,
            profile_picture=participant.user.profile_picture,
            last_read_at=participant.last_read_at
        ))
    
    # Get messages
    messages = []
    for msg in conversation.messages:
        messages.append(MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            sender_username=msg.sender.username,
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at
        ))
    
    return ConversationDetailResponse(
        id=conversation.id,
        participants=participants,
        messages=messages,
        created_at=conversation.created_at
    )

@router.post("/send", response_model=MessageResponse)
def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message to another user"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Can't message yourself
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    # Get or create conversation
    conversation = get_or_create_conversation(db, current_user.id, recipient.id)
    
    # Create message
    new_message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        content=message_data.content,
        is_read=False
    )
    db.add(new_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(new_message)
    
    return MessageResponse(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        sender_id=new_message.sender_id,
        sender_username=current_user.username,
        content=new_message.content,
        is_read=new_message.is_read,
        created_at=new_message.created_at
    )

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation (only removes it for the current user)"""
    # Verify user is a participant
    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Remove user from conversation
    db.delete(participant)
    
    # If no participants left, delete the conversation
    remaining_participants = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id
    ).count()
    
    if remaining_participants == 0:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
    
    db.commit()
    
    return {"message": "Conversation deleted successfully"}

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get total count of unread messages"""
    # Get all conversation IDs where user is a participant
    conversation_ids = db.query(ConversationParticipant.conversation_id).filter(
        ConversationParticipant.user_id == current_user.id
    ).all()
    conversation_ids = [c[0] for c in conversation_ids]
    
    # Count unread messages in those conversations
    unread_count = db.query(Message).filter(
        Message.conversation_id.in_(conversation_ids),
        Message.sender_id != current_user.id,
        Message.is_read == False
    ).count()
    
    return {"unread_count": unread_count}
