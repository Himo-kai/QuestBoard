"""
Association tables for many-to-many relationships.

This module defines all the association tables used in the application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint

from .base import db

# Association table for user-quest many-to-many relationship (bookmarks)
user_quests = db.Table(
    'user_quests',
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True, nullable=False),
    Column('quest_id', Integer, ForeignKey('quests.id'), primary_key=True, nullable=False),
    Column('bookmarked_at', DateTime, default=datetime.utcnow, nullable=False),
    UniqueConstraint('user_id', 'quest_id', name='uq_user_quest'),
    extend_existing=True
)

# Association table for quest-tag many-to-many relationship
quest_tags = db.Table(
    'quest_tags',
    Column('quest_id', Integer, ForeignKey('quests.id'), primary_key=True, nullable=False),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True, nullable=False),
    UniqueConstraint('quest_id', 'tag_id', name='uq_quest_tag'),
    extend_existing=True
)

__all__ = ['user_quests', 'quest_tags']
