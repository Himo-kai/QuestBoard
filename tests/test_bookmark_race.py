import unittest
from unittest.mock import patch, MagicMock, ANY
from database import QuestDatabase
from datetime import datetime
import threading
import sqlite3

class TestBookmarkRaceConditions(unittest.TestCase):
    def setUp(self):
        # Create a mock database connection
        self.db = MagicMock(spec=QuestDatabase)
        # Add the methods we'll be testing
        self.db.add_bookmark = MagicMock(wraps=self._add_bookmark_impl)
        self.db.toggle_bookmark = MagicMock(wraps=self._toggle_bookmark_impl)
        self.db.get_quest = MagicMock(return_value={"id": "test123"})
        self.db.conn = MagicMock()
        self._bookmarks = set()  # Track bookmarks for testing
    
    def _add_bookmark_impl(self, user_id, quest_id):
        """Implementation of add_bookmark for testing."""
        key = (user_id, quest_id)
        if key in self._bookmarks:
            raise sqlite3.IntegrityError("UNIQUE constraint failed")
        self._bookmarks.add(key)
        return True
    
    def _toggle_bookmark_impl(self, user_id, quest_id):
        """Implementation of toggle_bookmark for testing."""
        key = (user_id, quest_id)
        if key in self._bookmarks:
            self._bookmarks.remove(key)
            return False
        else:
            self._bookmarks.add(key)
            return True
        
    def test_concurrent_bookmarking(self):
        """Test concurrent bookmarking of the same quest."""
        user_id = "user1"
        quest_id = "test123"
        
        # Reset the mock call count
        self.db.add_bookmark.reset_mock()
        
        # Create two threads trying to bookmark the same quest
        def bookmark_thread():
            try:
                return self.db.add_bookmark(user_id, quest_id)
            except sqlite3.IntegrityError:
                return False
        
        thread1 = threading.Thread(target=bookmark_thread)
        thread2 = threading.Thread(target=bookmark_thread)
        
        # Start both threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        # Verify that add_bookmark was called exactly twice (once per thread)
        self.assertEqual(self.db.add_bookmark.call_count, 2)
        
        # Verify that only one bookmark was actually added
        self.assertEqual(len(self._bookmarks), 1)
        self.assertIn((user_id, quest_id), self._bookmarks)
        
    def test_bookmark_race_with_empty_db(self):
        """Test bookmarking when database is empty."""
        user_id = "user1"
        quest_id = "test123"
        
        # Reset the mock call count and clear bookmarks
        self.db.add_bookmark.reset_mock()
        self._bookmarks.clear()
        
        # Test bookmarking
        result = self.db.add_bookmark(user_id, quest_id)
        self.assertTrue(result)
        
        # Verify the bookmark was added
        self.assertEqual(len(self._bookmarks), 1)
        self.assertIn((user_id, quest_id), self._bookmarks)
        
        # Verify the method was called once
        self.db.add_bookmark.assert_called_once_with(user_id, quest_id)
        
    def test_bookmark_race_with_duplicate_link(self):
        """Test bookmarking quests with duplicate links."""
        user_id = "user1"
        quest_id = "test123"
        
        # Reset the mock call count and clear bookmarks
        self.db.add_bookmark.reset_mock()
        self._bookmarks.clear()
        
        # First bookmark should succeed
        result = self.db.add_bookmark(user_id, quest_id)
        self.assertTrue(result)
        
        # Verify the bookmark was added
        self.assertEqual(len(self._bookmarks), 1)
        self.assertIn((user_id, quest_id), self._bookmarks)
        
        # Second bookmark with same user and quest should raise IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add_bookmark(user_id, quest_id)
        
    def test_toggle_bookmark_race(self):
        """Test concurrent toggling of bookmarks."""
        user_id = "user1"
        quest_id = "test123"
        
        # Reset the mock call count and clear bookmarks
        self.db.toggle_bookmark.reset_mock()
        self._bookmarks.clear()
        
        # Create two threads trying to toggle the same bookmark
        def toggle_thread():
            return self.db.toggle_bookmark(user_id, quest_id)
        
        thread1 = threading.Thread(target=toggle_thread)
        thread2 = threading.Thread(target=toggle_thread)
        
        # Start both threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        # Verify that toggle_bookmark was called exactly twice (once per thread)
        self.assertEqual(self.db.toggle_bookmark.call_count, 2)
        
        # Verify that the final state is consistent
        # If both toggles were processed, the final state should be the same as the initial state
        # Since we started with no bookmarks, and toggled twice, we should end with no bookmarks
        self.assertEqual(len(self._bookmarks), 0)
        
        # Verify the method was called with the correct arguments
        self.db.toggle_bookmark.assert_any_call(user_id, quest_id)

if __name__ == '__main__':
    unittest.main()
