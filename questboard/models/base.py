"""
Base models and database setup for QuestBoard.

This module contains the base model class and database initialization.
"""
from datetime import datetime
from typing import Dict, Any, Type, TypeVar

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

# Import the shared SQLAlchemy instance
from . import db

class BaseModel(db.Model):
    """
    Base model class that includes common fields and methods.
    
    All models should inherit from this class to get common functionality.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self) -> None:
        """Save the current instance to the database."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self) -> None:
        """Delete the current instance from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs) -> 'BaseModel':
        """
        Update the current instance with the provided attributes.
        
        Args:
            **kwargs: Attributes to update
            
        Returns:
            The updated model instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        self.save()
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    @classmethod
    def get_by_id(cls, id: int) -> 'BaseModel':
        """
        Get a model instance by its ID.
        
        Args:
            id: The ID of the model to retrieve
            
        Returns:
            The model instance or None if not found
        """
        return cls.query.get(id)
