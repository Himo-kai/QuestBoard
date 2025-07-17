# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest
from datetime import datetime, timedelta, timezone
from questboard.models.quest import Quest
import json

class TestQuestModel:
    def test_quest_creation(self):
        """Test creating a new quest instance."""
        now = datetime.now(timezone.utc)
        quest = Quest(
            id="test-1",
            title="Test Quest",
            description="A test quest description",
            source="test",
            url="http://example.com/quest/1",
            posted_date=now,
            difficulty=5.0,
            reward="$100",
            region="test-region"
        )
        
        assert quest.id == "test-1"
        assert quest.title == "Test Quest"
        assert quest.description == "A test quest description"
        assert quest.source == "test"
        assert quest.url == "http://example.com/quest/1"
        assert quest.difficulty == 5.0
        assert quest.reward == "$100"
        assert quest.region == "test-region"
        assert quest.is_approved is False
        assert quest.posted_date == now
        assert quest.created_at is not None
        assert quest.updated_at is not None
        assert quest.tags == []
        assert quest.approved_by is None
        assert quest.approved_at is None
        assert quest.submitted_by is None
    
    def test_quest_to_dict(self):
        """Test converting quest to dictionary."""
        now = datetime.now(timezone.utc)
        quest = Quest(
            id="test-1",
            title="Test Quest",
            description="Test description",
            source="test",
            url="http://example.com",
            posted_date=now
        )
        
        quest_dict = quest.to_dict()
        
        assert quest_dict["id"] == "test-1"
        assert quest_dict["title"] == "Test Quest"
        assert "created_at" in quest_dict
        assert "updated_at" in quest_dict
    
    def test_quest_from_dict(self):
        """Test creating quest from dictionary."""
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        
        quest_data = {
            "id": "test-1",
            "title": "Test Quest",
            "description": "Test description",
            "source": "test",
            "url": "http://example.com",
            "posted_date": now_iso,
            "created_at": now_iso,
            "updated_at": now_iso,
            "tags": ["test", "pytest"],
            "difficulty": 5.0,
            "reward": "100 gold",
            "region": "Test Region"
        }
        
        quest = Quest.from_dict(quest_data)
        assert quest.id == "test-1"
        assert quest.title == "Test Quest"
        assert quest.description == "Test description"
        assert quest.source == "test"
        assert quest.url == "http://example.com"
        assert "test" in quest.tags
        assert "pytest" in quest.tags
        assert quest.difficulty == 5.0
        assert quest.reward == "100 gold"
        assert quest.region == "Test Region"
        assert quest.posted_date.tzinfo is not None
        assert quest.created_at.tzinfo is not None
        assert quest.updated_at.tzinfo is not None
        
        # Test with timezone offset
        offset_time = (now - timedelta(hours=5)).isoformat()
        quest_data["posted_date"] = offset_time
        quest = Quest.from_dict(quest_data)
        assert quest.posted_date.tzinfo is not None
        
        # Test with Z timezone
        z_time = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        quest_data["posted_date"] = z_time
        quest = Quest.from_dict(quest_data)
        assert quest.posted_date.tzinfo is not None
        
        # Test with missing optional fields
        minimal_data = {
            "id": "min-1",
            "title": "Minimal Quest",
            "description": "Minimal description",
            "source": "test",
            "url": "http://example.com/min"
        }
        quest = Quest.from_dict(minimal_data)
        assert quest.id == "min-1"
        assert quest.title == "Minimal Quest"
        assert quest.difficulty == 5.0  # Default value
        assert quest.region == "Unknown"  # Default value
        assert quest.tags == []  # Default empty list
    
    def test_quest_update(self):
        """Test updating quest fields."""
        quest = Quest(
            id="test-1",
            title="Old Title",
            description="Old Description",
            source="test",
            url="http://example.com",
            posted_date=datetime.now(timezone.utc)
        )
        
        original_updated = quest.updated_at
        quest.update(
            title="New Title",
            description="New Description"
        )
        
        assert quest.title == "New Title"
        assert quest.description == "New Description"
        assert quest.updated_at > original_updated
    
    def test_quest_tags(self):
        """Test adding and removing tags."""
        quest = Quest(
            id="test-1",
            title="Test Quest",
            description="Test description",
            source="test",
            url="http://example.com",
            posted_date=datetime.now(timezone.utc),
            tags=[]
        )
        
        # Add tags
        assert quest.add_tag("test") is True
        assert quest.add_tag("pytest") is True
        assert "test" in quest.tags
        assert "pytest" in quest.tags
        
        # Test duplicate tag
        assert quest.add_tag("test") is False  # Already exists
        assert len([t for t in quest.tags if t == "test"]) == 1
        
        # Test adding invalid tags
        assert quest.add_tag("") is False  # Empty string
        assert quest.add_tag(" ") is False  # Whitespace only
        assert quest.add_tag(None) is False  # None
        
        # Remove tag
        assert quest.remove_tag("test") is True
        assert "test" not in quest.tags
        
        # Remove non-existent tag
        assert quest.remove_tag("nonexistent") is False
        
        # Test with tags from initialization
        quest = Quest(
            id="test-2",
            title="Test Quest with Tags",
            description="Test",
            source="test",
            url="http://example.com",
            tags=["initial", "tags"]
        )
        assert "initial" in quest.tags
        assert "tags" in quest.tags
    
    def test_difficulty_level(self):
        """Test difficulty level classification."""
        quest = Quest(
            id="test-1",
            title="Test Quest",
            description="Test",
            source="test",
            url="http://example.com"
        )
        
        # Test each difficulty level
        test_cases = [
            (0.0, "Beginner"),
            (2.5, "Beginner"),
            (3.0, "Beginner"),  # Edge case
            (3.1, "Intermediate"),
            (6.0, "Intermediate"),  # Edge case
            (6.1, "Advanced"),
            (8.0, "Advanced"),  # Edge case
            (8.1, "Expert"),
            (10.0, "Expert"),  # Max difficulty
            (15.0, "Expert")   # Above max
        ]
        
        for difficulty, expected_level in test_cases:
            quest.difficulty = difficulty
            assert quest.get_difficulty_level() == expected_level, f"Failed for difficulty {difficulty}"
    
    def test_is_expired(self):
        """Test quest expiration check."""
        # Create a quest from 31 days ago
        old_date = datetime.now(timezone.utc) - timedelta(days=31)
        quest = Quest(
            id="test-1",
            title="Old Quest",
            description="Old quest",
            source="test",
            url="http://example.com",
            posted_date=old_date
        )
        
        assert quest.is_expired(days=30) is True
        assert quest.is_expired(days=60) is False
