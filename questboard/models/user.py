"""
User model for authentication and authorization.

This module defines the User model and related functionality for user management.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .base import db, BaseModel
from .associations import user_quests

if TYPE_CHECKING:
    from .quest import Quest

class User(BaseModel, UserMixin):
    """
    User model representing an application user.
    
    Handles user authentication, authorization, and relationships with quests.
    """
    __tablename__ = 'users'
    
    # Core user fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Status flags
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    last_login = db.Column(db.DateTime, nullable=True)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    created_quests = db.relationship(
        'Quest', 
        back_populates='creator',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    bookmarks = db.relationship(
        'Quest',
        secondary=user_quests,
        back_populates='bookmarked_by',
        lazy='dynamic',
        order_by='desc(user_quests.c.bookmarked_at)'
    )
    
    def __init__(self, username: str, email: str, password: Optional[str] = None, **kwargs):
        """
        Initialize a new user.
        
        Args:
            username: The user's username
            email: The user's email address (will be converted to lowercase)
            password: Optional plaintext password (will be hashed)
            **kwargs: Additional user attributes
        """
        self.username = username
        self.email = email.lower()
        if password:
            self.set_password(password)
            
        # Set any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def set_password(self, password):
        """Set password hash from plaintext password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Required by Flask-Login."""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Required by Flask-Login."""
        return True
    
    @property
    def is_anonymous(self):
        """Required by Flask-Login."""
        return False
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
