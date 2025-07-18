"""
Quest and Tag models for the QuestBoard application.

This module defines the Quest and Tag models along with their relationships.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, TYPE_CHECKING, TypeVar, Union
from sqlalchemy.orm import Query

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from .base import db, BaseModel
from .associations import quest_tags
from .tag import Tag

if TYPE_CHECKING:
    from .user import User

# Type variable for generic class methods
T = TypeVar('T', bound='Quest')

class Quest(BaseModel):
    """
    Quest model representing a task or challenge in the system.
    
    Quests can be created by users, tagged for categorization, and bookmarked
    for easy reference. They support various difficulty levels and rewards.
    """
    __tablename__ = 'quests'
    
    # Core fields
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True, index=True)
    url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    
    # Status and metadata
    difficulty = db.Column(db.Float, default=5.0, nullable=False, index=True)
    reward = db.Column(db.String(200), default="Not specified", nullable=False)
    region = db.Column(db.String(100), default="Unknown", nullable=False, index=True)
    is_approved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    posted_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    creator_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True, index=True)
    approved_by_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Many-to-many relationships
    tags = db.relationship(
        'Tag',
        secondary=quest_tags,
        lazy='subquery',
        back_populates='quests',
        cascade='save-update, merge, refresh-expire, expunge'
    )
    
    # Backrefs (defined in User model)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_quests")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    bookmarked_by = relationship(
        'User',
        secondary='user_quests',
        back_populates='bookmarks',
        lazy='dynamic',
        order_by='desc(user_quests.c.bookmarked_at)'
    )
    
    # Difficulty level mappings
    DIFFICULTY_LEVELS = {
        'beginner': 3.0,
        'intermediate': 6.0,
        'advanced': 8.0,
        'expert': 10.0
    }
    
    def __init__(self, **kwargs):
        """
        Initialize a new quest.
        
        Args:
            **kwargs: Quest attributes
        """
        super().__init__(**kwargs)
        # Ensure URL is normalized
        if hasattr(self, 'url'):
            self.url = self.url.strip()
    
    def to_dict(self, include_relationships: bool = True) -> Dict[str, Any]:
        """
        Convert quest object to dictionary.
        
        Args:
            include_relationships: Whether to include related objects
            
        Returns:
            Dictionary representation of the quest with ISO-formatted datetime strings
        """
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'url': self.url,
            'difficulty': self.difficulty,
            'difficulty_level': self.get_difficulty_level(),
            'reward': self.reward,
            'region': self.region,
            'is_approved': self.is_approved,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relationships:
            data.update({
                'creator': self.creator.to_dict() if self.creator else None,
                'approved_by': self.approved_by.to_dict() if self.approved_by else None,
                'tags': [tag.to_dict() for tag in self.tags],
                'bookmark_count': self.bookmarked_by.count() if hasattr(self, 'bookmarked_by') else 0
            })
            
        return data
    
    def approve(self, user_id: int) -> None:
        """
        Approve this quest.
        
        Args:
            user_id: ID of the user approving the quest
        """
        self.is_approved = True
        self.approved_by_id = user_id
        self.approved_at = datetime.utcnow()
        self.save()
    
    def get_difficulty_level(self) -> str:
        """
        Get the human-readable difficulty level.
        
        Returns:
            str: The difficulty level (e.g., 'Beginner', 'Intermediate')
        """
        if self.difficulty < 4.0:
            return 'Beginner'
        elif self.difficulty < 7.0:
            return 'Intermediate'
        elif self.difficulty < 9.0:
            return 'Advanced'
        return 'Expert'
    
    def is_expired(self, days: int = 30) -> bool:
        """
        Check if the quest is older than the specified number of days.
        
        Args:
            days: Number of days after which a quest is considered expired
            
        Returns:
            bool: True if the quest is older than the specified days
        """
        if not self.posted_date:
            return False
        return (datetime.utcnow() - self.posted_date).days > days
    
    def add_tag(self, tag: Union['Tag', str]) -> None:
        """
        Add a tag to this quest.
        
        Args:
            tag: Tag object or tag name to add
        """
        if isinstance(tag, str):
            tag = Tag.get_or_create(tag)
            
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()
    
    def remove_tag(self, tag: Union['Tag', str]) -> None:
        """
        Remove a tag from this quest.
        
        Args:
            tag: Tag object or tag name to remove
        """
        if isinstance(tag, str):
            tag = Tag.get_by_name(tag)
            
        if tag and tag in self.tags:
            self.tags.remove(tag)
            self.save()
    
    @classmethod
    def get_by_difficulty(cls, level: str) -> 'Query[Quest]':
        """
        Get quests by difficulty level.
        
        Args:
            level: Difficulty level ('beginner', 'intermediate', 'advanced', 'expert')
            
        Returns:
            Query: SQLAlchemy query for quests with the specified difficulty
        """
        level = level.lower()
        if level not in cls.DIFFICULTY_LEVELS:
            level = 'intermediate'
            
        target_difficulty = cls.DIFFICULTY_LEVELS[level]
        return cls.query.filter(
            (cls.difficulty >= target_difficulty - 1.5) & 
            (cls.difficulty <= target_difficulty + 1.5)
        )


# Tag model is now in tag.py


# Maintain the original Quest dataclass for backward compatibility
@dataclass
class QuestDataclass:
    """Legacy dataclass for Quest model."""
    id: str
    title: str
    description: str
    source: str
    url: str
    posted_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    difficulty: float = 5.0
    reward: str = "Not specified"
    region: str = "Unknown"
    tags: List[str] = field(default_factory=list)
    is_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    submitted_by: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default=None)
    
    def __post_init__(self):
        """Initialize the quest after __init__ is called."""
        # Set updated_at to created_at if not set
        if not hasattr(self, 'updated_at') or self.updated_at is None:
            object.__setattr__(self, 'updated_at', self.created_at)
            
        # Ensure tags is a list
        if not hasattr(self, 'tags') or self.tags is None:
            object.__setattr__(self, 'tags', [])
            
        # Ensure datetime objects are timezone-aware
        if hasattr(self, 'posted_date') and self.posted_date is not None and self.posted_date.tzinfo is None:
            posted_date = self.posted_date
            
        return (datetime.now(timezone.utc) - posted_date).days > days

# Add any model-level functions or utilities here
