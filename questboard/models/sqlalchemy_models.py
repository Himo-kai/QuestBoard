"""SQLAlchemy models for QuestBoard."""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from .base import db, BaseModel

# Define the association table in a way that prevents duplicate definitions
def get_user_quests_table(metadata):
    return Table(
        'user_quests',
        metadata,
        Column('user_id', String(64), ForeignKey('users.id'), primary_key=True),
        Column('quest_id', String(64), ForeignKey('quests.id'), primary_key=True),
        Column('created_at', DateTime, default=func.now()),
        extend_existing=True
    )

# Get the table using the function
user_quests = get_user_quests_table(db.metadata)

class Quest(BaseModel):
    """Quest model representing a task or challenge."""
    __tablename__ = 'quests'
    
    # Required fields
    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(String(512), nullable=False)
    posted_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Optional fields
    difficulty = Column(Float, default=5.0)
    reward = Column(String(255), default="Not specified")
    region = Column(String(100), default="Unknown")
    tags = Column(ARRAY(String), default=list)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(64), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    submitted_by = Column(String(64), nullable=True)
    
    # Relationships
    bookmarked_by = relationship(
        'User',
        secondary=user_quests,
        back_populates='bookmarks',
        lazy='dynamic'
    )
    
    # Class constants
    DIFFICULTY_LEVELS = {
        'Beginner': 3.0,
        'Intermediate': 6.0,
        'Advanced': 8.0,
        'Expert': 10.0
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'url': self.url,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'difficulty': self.difficulty,
            'reward': self.reward,
            'region': self.region,
            'tags': self.tags or [],
            'is_approved': self.is_approved,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'submitted_by': self.submitted_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update(self, **kwargs) -> None:
        """Update quest fields."""
        for key, value in kwargs.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> bool:
        """Add a tag to the quest if it doesn't already exist."""
        if not tag or not isinstance(tag, str):
            return False
            
        tag = tag.strip().lower()
        if not tag:
            return False
            
        if not self.tags:
            self.tags = []
            
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the quest."""
        if not self.tags or tag not in self.tags:
            return False
            
        self.tags.remove(tag)
        self.updated_at = datetime.now(timezone.utc)
        return True
    
    def get_difficulty_level(self) -> str:
        """Get a human-readable difficulty level."""
        if self.difficulty <= self.DIFFICULTY_LEVELS['Beginner']:
            return 'Beginner'
        elif self.difficulty <= self.DIFFICULTY_LEVELS['Intermediate']:
            return 'Intermediate'
        elif self.difficulty <= self.DIFFICULTY_LEVELS['Advanced']:
            return 'Advanced'
        return 'Expert'
    
    def is_expired(self, days: int = 30) -> bool:
        """Check if the quest is older than the specified number of days."""
        if not self.posted_date:
            return False
            
        now = datetime.now(timezone.utc)
        posted_date = self.posted_date.replace(tzinfo=timezone.utc) if self.posted_date.tzinfo is None else self.posted_date
        return (now - posted_date) > timedelta(days=days)
    
    def __repr__(self):
        return f'<Quest {self.id}: {self.title}>'
