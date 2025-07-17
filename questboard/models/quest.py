# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, ClassVar, TypeVar, Type
from dataclasses import dataclass, asdict, field, fields

T = TypeVar('T', bound='Quest')

@dataclass
class Quest:
    """A quest model representing a task or challenge."""
    
    # Required fields
    id: str
    title: str
    description: str
    source: str
    url: str
    posted_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional fields with defaults
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
            object.__setattr__(self, 'posted_date', self.posted_date.replace(tzinfo=timezone.utc))
            
        if hasattr(self, 'created_at') and self.created_at is not None and self.created_at.tzinfo is None:
            object.__setattr__(self, 'created_at', self.created_at.replace(tzinfo=timezone.utc))
            
        if hasattr(self, 'updated_at') and self.updated_at is not None and self.updated_at.tzinfo is None:
            object.__setattr__(self, 'updated_at', self.updated_at.replace(tzinfo=timezone.utc))
            
        if hasattr(self, 'approved_at') and self.approved_at is not None and self.approved_at.tzinfo is None:
            object.__setattr__(self, 'approved_at', self.approved_at.replace(tzinfo=timezone.utc))
    
    # Class constants
    DIFFICULTY_LEVELS: ClassVar[Dict[str, float]] = {
        'Beginner': 3.0,
        'Intermediate': 6.0,
        'Advanced': 8.0,
        'Expert': 10.0
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary.
        
        Returns:
            Dict containing quest data with ISO-formatted datetime strings.
        """
        result = {}
        
        # Get all field names from the dataclass
        for field in fields(self):
            value = getattr(self, field.name)
            
            # Convert datetime objects to ISO format strings
            if isinstance(value, datetime):
                result[field.name] = value.isoformat()
            # Handle other serialization if needed
            else:
                result[field.name] = value
        
        return result
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a Quest from a dictionary.
        
        Args:
            data: Dictionary containing quest data
            
        Returns:
            A new Quest instance
            
        Raises:
            ValueError: If required fields are missing
        """
        # Make a copy to avoid modifying the input
        data = data.copy()
        
        # Handle datetime conversions
        datetime_fields = ['posted_date', 'created_at', 'updated_at', 'approved_at']
        for field in datetime_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    try:
                        # Handle different datetime string formats
                        dt_str = data[field]
                        if dt_str.endswith('Z'):
                            dt_str = dt_str[:-1] + '+00:00'
                        data[field] = datetime.fromisoformat(dt_str).astimezone(timezone.utc)
                    except (ValueError, TypeError) as e:
                        raise ValueError(f"Invalid datetime format for field '{field}': {data[field]}") from e
        
        # Get field names from the dataclass
        field_names = {f.name for f in fields(cls)}
        
        # Filter out any extra fields that aren't in the dataclass
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        
        return cls(**filtered_data)
    
    def update(self, **kwargs) -> None:
        """Update quest fields.
        
        Args:
            **kwargs: Field names and values to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> bool:
        """Add a tag to the quest if it doesn't already exist.
        
        Args:
            tag: The tag to add
            
        Returns:
            bool: True if tag was added, False if it already existed
        """
        if not tag or not isinstance(tag, str):
            return False
            
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the quest.
        
        Args:
            tag: The tag to remove
            
        Returns:
            bool: True if tag was removed, False if it didn't exist
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def get_difficulty_level(self) -> str:
        """Get a human-readable difficulty level.
        
        Returns:
            str: One of 'Beginner', 'Intermediate', 'Advanced', or 'Expert'
        """
        if self.difficulty <= self.DIFFICULTY_LEVELS['Beginner']:
            return 'Beginner'
        elif self.difficulty <= self.DIFFICULTY_LEVELS['Intermediate']:
            return 'Intermediate'
        elif self.difficulty <= self.DIFFICULTY_LEVELS['Advanced']:
            return 'Advanced'
        return 'Expert'
    
    def is_expired(self, days: int = 30) -> bool:
        """Check if the quest is older than the specified number of days.
        
        Args:
            days: Number of days after which a quest is considered expired
            
        Returns:
            bool: True if the quest is older than the specified days
        """
        if not isinstance(self.posted_date, datetime):
            return False
            
        now = datetime.now(timezone.utc)
        if self.posted_date.tzinfo is None:
            posted_date = self.posted_date.replace(tzinfo=timezone.utc)
        else:
            posted_date = self.posted_date
            
        return (now - posted_date) > timedelta(days=days)
