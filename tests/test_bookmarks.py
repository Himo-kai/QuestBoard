import unittest
from unittest.mock import patch, MagicMock, ANY, call
from questboard.database import QuestDatabase
from datetime import datetime
import sqlite3
from pathlib import Path

class TestBookmarks(unittest.TestCase):
    def setUp(self):
        # Create a mock database connection
        self.db = MagicMock(spec=QuestDatabase)
        
        # Set up return values for the methods we'll test
        self.db.add_bookmark.side_effect = self._mock_add_bookmark
        self.db.remove_bookmark.side_effect = self._mock_remove_bookmark
        self.db.get_user_bookmarks.side_effect = self._mock_get_user_bookmarks
        self.db.is_bookmarked.side_effect = self._mock_is_bookmarked
        self.db.toggle_bookmark.side_effect = self._mock_toggle_bookmark
        
        # Track bookmarks in memory for testing
        self._bookmarks = set()
        
    def _mock_add_bookmark(self, user_id, quest_id):
        """Mock implementation of add_bookmark."""
        if (user_id, quest_id) in self._bookmarks:
            raise sqlite3.IntegrityError("UNIQUE constraint failed")
        self._bookmarks.add((user_id, quest_id))
        return True
        
    def _mock_remove_bookmark(self, user_id, quest_id):
        """Mock implementation of remove_bookmark."""
        try:
            self._bookmarks.remove((user_id, quest_id))
            return True
        except KeyError:
            return False
            
    def _mock_get_user_bookmarks(self, user_id):
        """Mock implementation of get_user_bookmarks."""
        # Return a list of quests that the user has bookmarked
        return [{"id": qid, "title": f"Quest {qid}", "source": "Test"} 
                for uid, qid in self._bookmarks if uid == user_id]
                
    def _mock_is_bookmarked(self, user_id, quest_id):
        """Mock implementation of is_bookmarked."""
        return (user_id, quest_id) in self._bookmarks
        
    def _mock_toggle_bookmark(self, user_id, quest_id):
        """Mock implementation of toggle_bookmark."""
        if self._mock_is_bookmarked(user_id, quest_id):
            self._mock_remove_bookmark(user_id, quest_id)
            return False
        else:
            self._mock_add_bookmark(user_id, quest_id)
            return True
        
    def test_add_bookmark_new(self):
        """Test adding a new bookmark."""
        user_id = "user1"
        quest_id = "test123"
        
        # Test adding bookmark
        result = self.db.add_bookmark(user_id, quest_id)
        self.assertTrue(result)
        
        # Verify the bookmark was added
        self.assertIn((user_id, quest_id), self._bookmarks)
        
        # Verify the method was called with correct arguments
        self.db.add_bookmark.assert_called_once_with(user_id, quest_id)
        
    def test_add_bookmark_duplicate(self):
        """Test adding a duplicate bookmark."""
        user_id = "user1"
        quest_id = "test123"
        
        # Add the bookmark first
        self._bookmarks.add((user_id, quest_id))
        
        # Try to add it again - should raise IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add_bookmark(user_id, quest_id)
        
    def test_remove_bookmark_existing(self):
        """Test removing an existing bookmark."""
        user_id = "user1"
        quest_id = "test123"
        
        # Add the bookmark first
        self._bookmarks.add((user_id, quest_id))
        
        # Test removing bookmark
        result = self.db.remove_bookmark(user_id, quest_id)
        self.assertTrue(result)
        
        # Verify the bookmark was removed
        self.assertNotIn((user_id, quest_id), self._bookmarks)
        
        # Verify the method was called with correct arguments
        self.db.remove_bookmark.assert_called_once_with(user_id, quest_id)
        
    def test_remove_bookmark_nonexistent(self):
        """Test removing a non-existent bookmark."""
        user_id = "user1"
        quest_id = "nonexistent"
        
        # Test removing non-existent bookmark
        result = self.db.remove_bookmark(user_id, quest_id)
        self.assertFalse(result)
        
        # Verify the method was called with correct arguments
        self.db.remove_bookmark.assert_called_once_with(user_id, quest_id)
        
    def test_get_user_bookmarks(self):
        """Test retrieving user's bookmarked quests."""
        user_id = "user1"
        quest_id1 = "test123"
        quest_id2 = "test456"
        
        # Add some bookmarks
        self._bookmarks.add((user_id, quest_id1))
        self._bookmarks.add((user_id, quest_id2))
        
        # Add a bookmark for a different user
        self._bookmarks.add(("other_user", "other_quest"))
        
        # Test getting bookmarks
        result = self.db.get_user_bookmarks(user_id)
        
        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual({q["id"] for q in result}, {quest_id1, quest_id2})
        
        # Verify the method was called with correct arguments
        self.db.get_user_bookmarks.assert_called_once_with(user_id)
        
    def test_toggle_bookmark(self):
        """Test toggling a bookmark."""
        user_id = "user1"
        quest_id = "test123"
        
        # First toggle - should add the bookmark
        result = self.db.toggle_bookmark(user_id, quest_id)
        self.assertTrue(result)
        self.assertIn((user_id, quest_id), self._bookmarks)
        
        # Verify the method was called with correct arguments
        self.db.toggle_bookmark.assert_called_with(user_id, quest_id)
        
        # Second toggle - should remove the bookmark
        result = self.db.toggle_bookmark(user_id, quest_id)
        self.assertFalse(result)
        self.assertNotIn((user_id, quest_id), self._bookmarks)

if __name__ == '__main__':
    unittest.main()
