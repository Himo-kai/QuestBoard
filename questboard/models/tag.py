"""
Tag model for categorizing quests.

This module defines the Tag model and related functionality.
"""
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import db, BaseModel
from .associations import quest_tags

if TYPE_CHECKING:
    from .quest import Quest

class Tag(BaseModel):
    """
    Tag model for categorizing quests.
    
    Tags are used to categorize and filter quests. Each tag can be associated
    with multiple quests, and each quest can have multiple tags.
    """
    __tablename__ = 'tags'
    
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    quests = relationship(
        'Quest',
        secondary=quest_tags,
        back_populates='tags',
        lazy='dynamic'
    )
    
    def __init__(self, name: str, **kwargs):
        """
        Initialize a new tag.
        
        Args:
            name: The name of the tag (will be converted to lowercase)
            **kwargs: Additional attributes
        """
        super().__init__(**kwargs)
        self.name = name.lower().strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tag object to dictionary.
        
        Returns:
            Dictionary representation of the tag
        """
        return {
            'id': self.id,
            'name': self.name,
            'quest_count': self.quests.count() if hasattr(self, 'quests') else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_or_create(cls, name: str) -> 'Tag':
        """
        Get an existing tag or create a new one.
        
        Args:
            name: The name of the tag to get or create
            
        Returns:
            Tag: The existing or newly created tag
        """
        name = name.lower().strip()
        tag = cls.query.filter_by(name=name).first()
        if not tag:
            tag = cls(name=name)
            db.session.add(tag)
            db.session.commit()
        return tag
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Tag']:
        """
        Get a tag by name (case-insensitive).
        
        Args:
            name: The name of the tag to find
            
        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        return cls.query.filter_by(name=name.lower().strip()).first()
    
    def __repr__(self) -> str:
        return f'<Tag {self.name}>'
