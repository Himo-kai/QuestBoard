import os
import sqlite3
import json
import logging
import contextlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class QuestDatabase:
    """Database handler for QuestBoard application."""
    
    def __init__(self, db_path: str = None):
        """Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        logger.info("Initializing QuestDatabase")
        if db_path is None:
            # Default to a database in the instance folder
            db_dir = Path('instance')
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / 'questboard.db')
            
        self.db_path = db_path
        logger.info(f"Using database at: {self.db_path}")
        self._init_db()
    
    def _get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @contextlib.contextmanager
    def _get_cursor(self):
        """Context manager for database operations."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    def _init_db(self):
        """Initialize the database schema."""
        logger.info("Initializing database schema")
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            logger.debug("Database connection established")
            
            # Create quests table
            logger.debug("Creating quests table if not exists")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quests (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    source TEXT NOT NULL,
                    url TEXT UNIQUE,
                    posted_date TIMESTAMP,
                    difficulty FLOAT DEFAULT 5.0,
                    reward TEXT,
                    region TEXT,
                    tags TEXT,  -- JSON array of tags
                    is_approved BOOLEAN DEFAULT 0,
                    approved_by TEXT,
                    approved_at TIMESTAMP,
                    submitted_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create bookmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    user_id TEXT NOT NULL,
                    quest_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, quest_id),
                    FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
                )
            ''')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Commit the changes
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def create_tables(self):
        """Create all database tables if they don't exist."""
        self._init_db()
    
    def add_quest(self, quest_data: Dict, retry_count: int = 0) -> Optional[Dict]:
        """Add a new quest to the database.
        
        Args:
            quest_data: Dictionary containing quest data
            retry_count: Internal counter to prevent infinite recursion
            
        Returns:
            Optional[Dict]: The created quest data or None on failure
        """
        if retry_count > 3:  # Prevent infinite recursion
            print("Max retries reached for add_quest")
            return None
            
        # Make a copy to avoid modifying the input
        quest_data = quest_data.copy()
        
        # Generate a new ID if not provided
        if 'id' not in quest_data:
            from uuid import uuid4
            quest_data['id'] = str(uuid4())
        
        # Set default values
        quest_data.setdefault('title', 'Untitled Quest')
        quest_data.setdefault('description', '')
        quest_data.setdefault('source', 'unknown')
        quest_data.setdefault('url', f"http://example.com/quest/{quest_data['id']}")
        quest_data.setdefault('is_approved', 0)  # Use 0/1 for SQLite boolean
        quest_data.setdefault('difficulty', 5.0)
        quest_data.setdefault('reward', '')
        quest_data.setdefault('region', '')
        quest_data.setdefault('tags', [])
        quest_data.setdefault('submitted_by', 'anonymous')
        
        # Handle posted_date
        if 'posted_date' not in quest_data:
            quest_data['posted_date'] = datetime.utcnow().isoformat()
        
        # Convert tags to JSON string if it's a list
        if isinstance(quest_data['tags'], (list, tuple)):
            quest_data['tags'] = json.dumps(quest_data['tags'])
        
        # Set timestamps
        now = datetime.utcnow().isoformat()
        quest_data['created_at'] = now
        quest_data['updated_at'] = now
        
        # Ensure all string fields are properly encoded
        for key, value in quest_data.items():
            if isinstance(value, str):
                quest_data[key] = value.encode('utf-8', 'ignore').decode('utf-8')
            elif isinstance(value, bool):
                # Convert boolean to int for SQLite
                quest_data[key] = int(value)
        
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Prepare the SQL query
            columns = ', '.join(f'"{k}"' for k in quest_data.keys())
            placeholders = ', '.join(['?'] * len(quest_data))
            query = f'INSERT INTO quests ({columns}) VALUES ({placeholders})'
            
            # Execute the query
            cursor.execute(query, list(quest_data.values()))
            conn.commit()
            
            # Return the inserted quest
            return self.get_quest(quest_data['id'])
            
        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
                
            error_msg = str(e).lower()
            
            # Handle URL conflict by appending a unique identifier
            if 'unique constraint failed: quests.url' in error_msg:
                if 'url' in quest_data:
                    from uuid import uuid4
                    base_url = quest_data['url'].split('-')[0]  # Get the base URL before any existing suffix
                    quest_data['url'] = f"{base_url}-{uuid4().hex[:8]}"
                    return self.add_quest(quest_data, retry_count + 1)
            
            # Handle missing table by initializing database and retrying once
            elif 'no such table' in error_msg and retry_count == 0:
                self._init_db()
                return self.add_quest(quest_data, retry_count + 1)
                
            print(f"Integrity error in add_quest: {e}")
            return None
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error in add_quest: {e}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def cache_quest(self, quest_data: Dict[str, Any]) -> bool:
        """Cache a quest in the database.
        
        Args:
            quest_data: Dictionary containing quest data
            
        Returns:
            bool: True if quest was inserted or updated, False otherwise
        """
        required_fields = {'id', 'title', 'source'}
        if not all(field in quest_data for field in required_fields):
            raise ValueError(f"Missing required fields. Required: {required_fields}")
        
        # Prepare data for insertion
        quest_id = quest_data['id']
        title = quest_data['title']
        description = quest_data.get('description', '')
        source = quest_data['source']
        url = quest_data.get('url', '')
        
        # Handle posted_date
        posted_date = quest_data.get('posted_date')
        if isinstance(posted_date, str):
            # Parse ISO format string to datetime
            posted_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
        elif posted_date is None:
            posted_date = datetime.utcnow()
            
        # Handle tags
        tags = quest_data.get('tags', [])
        if isinstance(tags, (list, tuple)):
            tags = json.dumps(tags)
            
        # Prepare data for upsert
        data = {
            'id': quest_id,
            'title': title,
            'description': description,
            'source': source,
            'url': url,
            'posted_date': posted_date.isoformat(),
            'difficulty': quest_data.get('difficulty', 5.0),
            'reward': quest_data.get('reward', ''),
            'region': quest_data.get('region', ''),
            'tags': tags,
            'is_approved': int(quest_data.get('is_approved', False)),
            'submitted_by': quest_data.get('submitted_by'),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Build query for upsert
        columns = ', '.join(data.keys())
        placeholders = ':' + ', :'.join(data.keys())
        updates = ', '.join(f"{k} = :{k}" for k in data.keys() if k != 'id')
        
        query = f"""
        INSERT INTO quests ({columns})
        VALUES ({placeholders})
        ON CONFLICT(id) DO UPDATE SET {updates}
        """
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(query, data)
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_quest(self, quest_id: str) -> Optional[Dict]:
        """Get a quest by ID."""
        if not isinstance(quest_id, str):
            quest_id = str(quest_id)
            
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quests WHERE id = ?', (quest_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Error in get_quest: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def get_quests(self, page: int = 1, per_page: int = 10, filters: Dict = None) -> Dict:
        """Retrieve quests with pagination and optional filtering.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            filters: Dictionary of filter criteria
            
        Returns:
            Dictionary containing quests and pagination info
        """
        offset = (page - 1) * per_page
        
        # Base query for counting total records
        count_query = "SELECT COUNT(*) as total FROM quests WHERE 1=1"
        query = "SELECT * FROM quests WHERE 1=1"
        params = []
        
        if filters:
            if 'is_approved' in filters:
                query += " AND is_approved = ?"
                count_query += " AND is_approved = ?"
                params.append(int(filters['is_approved']))
                
            if 'source' in filters:
                query += " AND source = ?"
                count_query += " AND source = ?"
                params.append(filters['source'])
                
            if 'region' in filters:
                query += " AND region = ?"
                count_query += " AND region = ?"
                params.append(filters['region'])
                
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query += " AND (title LIKE ? OR description LIKE ?)"
                count_query += " AND (title LIKE ? OR description LIKE ?)"
                params.extend([search_term, search_term])
        
        # Add ordering and pagination to the main query
        query += " ORDER BY posted_date DESC LIMIT ? OFFSET ?"
        
        with self._get_cursor() as cursor:
            # Get total count
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Get paginated results
            cursor.execute(query, params + [per_page, offset])
            quests = [dict(row) for row in cursor.fetchall()]
            
            return {
                'quests': quests,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
    
    def delete_old_quests(self, days_old: int = 30) -> int:
        """Delete quests older than the specified number of days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        with self._get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM quests WHERE posted_date < ?",
                (cutoff_date.isoformat(),)
            )
            return cursor.rowcount
    
    def add_bookmark(self, user_id: str, quest_id: str) -> bool:
        """Add a quest to user's bookmarks."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO bookmarks (user_id, quest_id) VALUES (?, ?)",
                    (user_id, quest_id)
                )
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    def remove_bookmark(self, user_id: str, quest_id: str) -> bool:
        """Remove a quest from user's bookmarks.
        
        Args:
            user_id: The ID of the user
            quest_id: The ID of the quest to remove from bookmarks
            
        Returns:
            bool: True if the bookmark was removed, False if it didn't exist
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM bookmarks WHERE user_id = ? AND quest_id = ?",
                    (user_id, quest_id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            if "no such table" in str(e).lower():
                # Handle case where bookmarks table doesn't exist yet
                self._init_db()
                return False
            print(f"Database error in remove_bookmark: {e}")
            raise
    
    def get_user_bookmarks(self, user_id: str) -> List[Dict]:
        """Get all bookmarks for a user."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT q.* FROM quests q
                JOIN bookmarks b ON q.id = b.quest_id
                WHERE b.user_id = ?
                ORDER BY b.created_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
            
    def is_bookmarked(self, user_id: str, quest_id: str) -> bool:
        """Check if a quest is bookmarked by a user.
        
        Args:
            user_id: The ID of the user
            quest_id: The ID of the quest
            
        Returns:
            bool: True if the quest is bookmarked by the user, False otherwise
        """
        with self._get_cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM bookmarks WHERE user_id = ? AND quest_id = ?",
                (user_id, quest_id)
            )
            return cursor.fetchone() is not None
    
    def toggle_bookmark(self, user_id: str, quest_id: str) -> bool:
        """Toggle a bookmark for a quest.
        
        Args:
            user_id: The ID of the user
            quest_id: The ID of the quest to toggle
            
        Returns:
            bool: True if the quest is now bookmarked, False if it was unbookmarked
            
        Raises:
            ValueError: If the quest doesn't exist
        """
        try:
            # First verify the quest exists
            quest = self.get_quest(quest_id)
            if not quest:
                raise ValueError(f"Quest with ID {quest_id} not found")
                
            # Check if the bookmark already exists
            is_bookmarked = self.is_bookmarked(user_id, quest_id)
            
            if is_bookmarked:
                # Remove the bookmark
                self.remove_bookmark(user_id, quest_id)
                return False
            else:
                # Add the bookmark
                with self._get_cursor() as cursor:
                    try:
                        cursor.execute(
                            "INSERT INTO bookmarks (user_id, quest_id) VALUES (?, ?)",
                            (user_id, quest_id)
                        )
                        return True
                    except sqlite3.IntegrityError as ie:
                        # Handle race condition where another process added the bookmark
                        if "UNIQUE constraint failed" in str(ie):
                            return True
                        raise
                        
        except sqlite3.Error as e:
            if "no such table" in str(e).lower():
                # Handle case where bookmarks table doesn't exist yet
                self._init_db()
                # Retry the operation
                return self.toggle_bookmark(user_id, quest_id)
            print(f"Database error in toggle_bookmark: {e}")
            raise


# Singleton instance
_db_instance = None

def init_app(app):
    """Initialize the database for the Flask app."""
    global _db_instance
    if _db_instance is None:
        db_path = app.config.get('DATABASE')
        _db_instance = QuestDatabase(db_path)
    return _db_instance

def get_database() -> QuestDatabase:
    """Get the database instance."""
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_app() first.")
    return _db_instance
