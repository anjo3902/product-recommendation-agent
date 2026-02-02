# src/routes/conversations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from src.database.connection import get_db
from src.database.models import ConversationHistory, User
from src.utils.middleware import get_current_user, get_optional_user

router = APIRouter(prefix="/conversations", tags=["conversations"])

# ============================================================================
# Pydantic Models
# ============================================================================

class ConversationCreate(BaseModel):
    session_id: Optional[str] = None
    user_message: str
    agent_response: str
    context_data: Optional[dict] = None
    products_mentioned: Optional[List[int]] = None
    intent: Optional[str] = None
    sentiment: Optional[str] = "neutral"

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    session_id: Optional[str]
    user_message: str
    agent_response: str
    context_data: Optional[dict]
    products_mentioned: Optional[List[int]]
    intent: Optional[str]
    sentiment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationSummary(BaseModel):
    total_conversations: int
    recent_intents: List[str]
    common_topics: List[str]
    sentiment_distribution: dict

# ============================================================================
# Conversation History Endpoints
# ============================================================================

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a conversation between user and agent.
    
    This builds agent memory for context-aware recommendations.
    """
    # Convert lists/dicts to JSON strings for storage
    context_json = json.dumps(conversation.context_data) if conversation.context_data else None
    products_json = json.dumps(conversation.products_mentioned) if conversation.products_mentioned else None
    
    conv = ConversationHistory(
        user_id=current_user.id,
        session_id=conversation.session_id,
        user_message=conversation.user_message,
        agent_response=conversation.agent_response,
        context_data=context_json,
        products_mentioned=products_json,
        intent=conversation.intent,
        sentiment=conversation.sentiment
    )
    
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    # Parse JSON back for response
    response = ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        session_id=conv.session_id,
        user_message=conv.user_message,
        agent_response=conv.agent_response,
        context_data=json.loads(conv.context_data) if conv.context_data else None,
        products_mentioned=json.loads(conv.products_mentioned) if conv.products_mentioned else None,
        intent=conv.intent,
        sentiment=conv.sentiment,
        created_at=conv.created_at
    )
    
    return response

@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    session_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for the current user.
    
    - **session_id**: Filter by session (optional)
    - **skip**: Pagination offset
    - **limit**: Maximum results
    """
    query = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == current_user.id
    )
    
    if session_id:
        query = query.filter(ConversationHistory.session_id == session_id)
    
    conversations = query.order_by(
        desc(ConversationHistory.created_at)
    ).offset(skip).limit(limit).all()
    
    # Parse JSON fields
    result = []
    for conv in conversations:
        result.append(ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            session_id=conv.session_id,
            user_message=conv.user_message,
            agent_response=conv.agent_response,
            context_data=json.loads(conv.context_data) if conv.context_data else None,
            products_mentioned=json.loads(conv.products_mentioned) if conv.products_mentioned else None,
            intent=conv.intent,
            sentiment=conv.sentiment,
            created_at=conv.created_at
        ))
    
    return result

@router.get("/sessions")
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique session IDs for the current user."""
    sessions = db.query(ConversationHistory.session_id).filter(
        ConversationHistory.user_id == current_user.id,
        ConversationHistory.session_id.isnot(None)
    ).distinct().all()
    
    return {"sessions": [s[0] for s in sessions if s[0]]}

@router.get("/summary", response_model=ConversationSummary)
async def get_conversation_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics of user's conversation history."""
    
    conversations = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == current_user.id
    ).all()
    
    total = len(conversations)
    
    # Extract intents
    intents = [c.intent for c in conversations if c.intent]
    recent_intents = list(dict.fromkeys(intents[:10]))  # Unique, preserve order
    
    # Extract common topics from messages
    all_messages = ' '.join([c.user_message for c in conversations])
    # Simple topic extraction (in production, use NLP)
    common_words = ['laptop', 'phone', 'camera', 'headphone', 'watch', 'tablet']
    common_topics = [word for word in common_words if word.lower() in all_messages.lower()]
    
    # Sentiment distribution
    sentiments = [c.sentiment for c in conversations if c.sentiment]
    sentiment_dist = {
        'positive': sentiments.count('positive'),
        'neutral': sentiments.count('neutral'),
        'negative': sentiments.count('negative')
    }
    
    return ConversationSummary(
        total_conversations=total,
        recent_intents=recent_intents,
        common_topics=common_topics[:5],
        sentiment_distribution=sentiment_dist
    )

@router.get("/context")
async def get_conversation_context(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent conversation context for agent memory.
    
    This helps the agent understand previous interactions.
    """
    recent_convs = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == current_user.id
    ).order_by(
        desc(ConversationHistory.created_at)
    ).limit(limit).all()
    
    context = []
    for conv in reversed(recent_convs):  # Chronological order
        context.append({
            "user": conv.user_message,
            "agent": conv.agent_response,
            "intent": conv.intent,
            "products": json.loads(conv.products_mentioned) if conv.products_mentioned else [],
            "timestamp": conv.created_at.isoformat()
        })
    
    return {"context": context}

@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all conversations in a specific session."""
    db.query(ConversationHistory).filter(
        ConversationHistory.user_id == current_user.id,
        ConversationHistory.session_id == session_id
    ).delete()
    
    db.commit()
    return None

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_conversation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear all conversation history for the current user."""
    db.query(ConversationHistory).filter(
        ConversationHistory.user_id == current_user.id
    ).delete()
    
    db.commit()
    return None
