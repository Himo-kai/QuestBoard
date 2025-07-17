# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest
import json
from datetime import datetime, timedelta, timezone
from questboard.models.quest import Quest

class TestQuestDatabase:
    def test_quest_crud(self, db, sample_quest):
        """Test CRUD operations for quests."""
        # Create
        assert db.cache_quest(sample_quest) is True
        
        # Read
        quest_data = db.get_quest(sample_quest['id'])
        assert quest_data is not None
        assert quest_data['title'] == sample_quest['title']
        assert quest_data['source'] == sample_quest['source']
        
        # Convert to Quest object
        quest = Quest.from_dict(quest_data)
        assert isinstance(quest, Quest)
        
        # Update
        updated_data = sample_quest.copy()
        updated_data['title'] = 'Updated Quest Title'
        assert db.cache_quest(updated_data) is True
        
        # Verify update
        updated_quest_data = db.get_quest(sample_quest['id'])
        assert updated_quest_data['title'] == 'Updated Quest Title'
    
    def test_get_quests(self, db, sample_quest):
        """Test retrieving multiple quests with filters."""
        # Add test quests
        quest1 = sample_quest.copy()
        quest1['id'] = 'test-quest-1'
        quest1['source'] = 'source1'
        quest1['is_approved'] = True
        
        quest2 = sample_quest.copy()
        quest2['id'] = 'test-quest-2'
        quest2['source'] = 'source2'
        quest2['is_approved'] = False
        
        db.cache_quest(quest1)
        db.cache_quest(quest2)
        
        # Test get all quests
        quests = db.get_quests()
        assert len(quests) >= 2
        
        # Test filter by source
        quests = db.get_quests(filters={'source': 'source1'})
        assert len(quests) == 1
        assert quests[0]['source'] == 'source1'
        
        # Test filter by approval status
        quests = db.get_quests(filters={'is_approved': True})
        assert all(q['is_approved'] for q in quests)
        
        # Test search
        quests = db.get_quests(filters={'search': 'test quest'})
        assert len(quests) > 0
        
        # Test pagination
        quests = db.get_quests(limit=1, offset=0)
        assert len(quests) == 1
        
        # Test ordering
        quests = db.get_quests()
        if len(quests) > 1:
            # Check that quests are ordered by posted_date desc by default
            dates = [q['posted_date'] for q in quests]
            assert dates == sorted(dates, reverse=True)
    
    def test_bookmarks(self, db, sample_quest):
        """Test bookmark operations."""
        # Add a quest
        assert db.cache_quest(sample_quest) is True
        
        # Test adding bookmark
        user_id = 'test-user-1'
        assert db.add_bookmark(user_id, sample_quest['id']) is True
        
        # Test getting bookmarks
        bookmarks = db.get_user_bookmarks(user_id)
        assert len(bookmarks) == 1
        assert bookmarks[0]['id'] == sample_quest['id']
        
        # Test duplicate bookmark
        assert db.add_bookmark(user_id, sample_quest['id']) is False
        
        # Test removing bookmark
        assert db.remove_bookmark(user_id, sample_quest['id']) is True
        
        # Verify removal
        assert len(db.get_user_bookmarks(user_id)) == 0
        
        # Test removing non-existent bookmark
        assert db.remove_bookmark(user_id, 'non-existent-id') is False
    
    def test_delete_old_quests(self, db, sample_quest):
        """Test cleanup of old quests."""
        # Add an old quest
        old_quest = sample_quest.copy()
        old_quest['id'] = 'old-quest-1'
        old_quest['posted_date'] = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
        assert db.cache_quest(old_quest) is True
        
        # Add a recent quest
        recent_quest = sample_quest.copy()
        recent_quest['id'] = 'recent-quest-1'
        recent_quest['posted_date'] = datetime.now(timezone.utc).isoformat()
        assert db.cache_quest(recent_quest) is True
        
        # Delete quests older than 30 days
        deleted_count = db.delete_old_quests(days_old=30)
        assert deleted_count >= 1
        
        # Verify old quest was deleted
        assert db.get_quest('old-quest-1') is None
        
        # Verify recent quest still exists
        assert db.get_quest('recent-quest-1') is not None
        
        # Test with custom days_old parameter
        old_quest = sample_quest.copy()
        old_quest['id'] = 'very-old-quest-1'
        old_quest['posted_date'] = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        db.cache_quest(old_quest)
        
        deleted_count = db.delete_old_quests(days_old=90)
        assert deleted_count >= 1
        assert db.get_quest('very-old-quest-1') is None
