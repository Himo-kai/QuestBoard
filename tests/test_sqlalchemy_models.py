"""Tests for SQLAlchemy models."""
import pytest
from datetime import datetime, timezone, timedelta
from questboard.models import User, SQLAlchemyQuest, db

class TestSQLAlchemyModels:
    """Test cases for SQLAlchemy models."""
    
    def test_user_creation(self, db):
        """Test creating a new user."""
        user = User(
            id="test-user-1",
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Verify the user was saved
        assert user.id == "test-user-1"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpassword")
        assert not user.is_admin
        assert user.is_active
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_quest_creation(self, db):
        """Test creating a new quest."""
        now = datetime.now(timezone.utc)
        quest = SQLAlchemyQuest(
            id="test-quest-1",
            title="Test Quest",
            description="A test quest description",
            source="test",
            url="http://example.com/quest/1",
            posted_date=now,
            difficulty=5.0,
            reward="$100",
            region="test-region",
            is_approved=True
        )
        
        db.session.add(quest)
        db.session.commit()
        
        # Verify the quest was saved
        assert quest.id == "test-quest-1"
        assert quest.title == "Test Quest"
        assert quest.description == "A test quest description"
        assert quest.source == "test"
        assert quest.url == "http://example.com/quest/1"
        assert quest.difficulty == 5.0
        assert quest.reward == "$100"
        assert quest.region == "test-region"
        assert quest.is_approved is True
        assert quest.posted_date == now
        assert quest.created_at is not None
        assert quest.updated_at is not None
    
    def test_quest_tags(self, db):
        """Test adding and removing tags from a quest."""
        quest = SQLAlchemyQuest(
            id="test-quest-tags",
            title="Quest with Tags",
            description="A quest for testing tags",
            source="test",
            url="http://example.com/quest/tags"
        )
        
        # Add tags
        assert quest.add_tag("python") is True
        assert quest.add_tag("flask") is True
        assert quest.add_tag("python") is False  # Duplicate
        
        db.session.add(quest)
        db.session.commit()
        
        # Verify tags were saved
        assert len(quest.tags) == 2
        assert "python" in quest.tags
        assert "flask" in quest.tags
        
        # Remove a tag
        assert quest.remove_tag("python") is True
        assert quest.remove_tag("nonexistent") is False
        
        db.session.commit()
        
        # Verify tag was removed
        assert len(quest.tags) == 1
        assert "python" not in quest.tags
        assert "flask" in quest.tags
    
    def test_user_quest_relationship(self, db):
        """Test the many-to-many relationship between users and quests."""
        # Create a user
        user = User(
            id="test-user-rel",
            username="testuser_rel",
            email="test_rel@example.com",
            password="testpassword"
        )
        
        # Create a quest
        quest = SQLAlchemyQuest(
            id="test-quest-rel",
            title="Quest for Relationship Test",
            description="Testing user-quest relationship",
            source="test",
            url="http://example.com/quest/rel"
        )
        
        # Add quest to user's bookmarks
        user.bookmarks.append(quest)
        
        db.session.add_all([user, quest])
        db.session.commit()
        
        # Verify the relationship
        assert len(user.bookmarks) == 1
        assert user.bookmarks[0].id == "test-quest-rel"
        assert len(quest.bookmarked_by) == 1
        assert quest.bookmarked_by[0].id == "test-user-rel"
    
    def test_quest_difficulty_level(self):
        """Test the difficulty level calculation."""
        quest = SQLAlchemyQuest(
            id="test-diff-level",
            title="Difficulty Test",
            description="Testing difficulty levels",
            source="test",
            url="http://example.com/difficulty"
        )
        
        # Test different difficulty levels
        quest.difficulty = 2.0
        assert quest.get_difficulty_level() == "Beginner"
        
        quest.difficulty = 5.0
        assert quest.get_difficulty_level() == "Intermediate"
        
        quest.difficulty = 7.5
        assert quest.get_difficulty_level() == "Advanced"
        
        quest.difficulty = 9.5
        assert quest.get_difficulty_level() == "Expert"
    
    def test_quest_expiration(self):
        """Test the quest expiration check."""
        quest = SQLAlchemyQuest(
            id="test-expiry",
            title="Expiry Test",
            description="Testing quest expiration",
            source="test",
            url="http://example.com/expiry"
        )
        
        # Set posted date to 31 days ago
        quest.posted_date = datetime.now(timezone.utc) - timedelta(days=31)
        
        # Should be expired with default 30-day threshold
        assert quest.is_expired() is True
        
        # Should not be expired with 60-day threshold
        assert quest.is_expired(days=60) is False
