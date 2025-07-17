# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sqlite3
from pathlib import Path
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
from errors import DatabaseError

logger = logging.getLogger(__name__)

class QuestDatabase:
    """
    Database manager for QuestBoard quests and related data.
    
    This class handles all database operations including:
    - Quest caching and retrieval
    - Bookmark management
    - Difficulty curve tracking
    - Cache optimization
    """

    def __init__(self, db_path: str = "questboard.db"):
        """
        Initialize the database connection.
        
        Creates the database file if it doesn't exist and ensures
        all required tables are created.
        """
        try:
            self.db_path = os.path.join(os.path.dirname(__file__), db_path)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.create_tables()
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to initialize database connection: {str(e)}",
                operation="init",
                extra={"db_path": self.db_path}
            )

    def create_tables(self):
        """
        Create all necessary database tables.
        
        Tables created:
        - quests: Stores quest information and metadata
        - bookmarks: Tracks user-bookmarked quests
        - difficulty_curves: Stores historical difficulty ratings
        
        Raises:
            DatabaseError: If table creation fails
        """
        try:
            with self.conn:
                # Drop existing tables if they exist
                self.conn.execute('DROP TABLE IF EXISTS bookmarks')
                self.conn.execute('DROP TABLE IF EXISTS difficulty_curves')
                self.conn.execute('DROP TABLE IF EXISTS quests')
                
                # Create quests table first (without foreign key constraints)
                self.conn.execute('''
                    CREATE TABLE quests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        quest_id TEXT UNIQUE,
                        title TEXT,
                        description TEXT,
                        link TEXT UNIQUE,
                        reward TEXT,
                        difficulty INTEGER,
                        source TEXT,
                        timestamp DATETIME,
                        score INTEGER,
                        author TEXT,
                        gear_required TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create bookmarks table with foreign key constraint
                self.conn.execute('''
                    CREATE TABLE bookmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        quest_id TEXT,
                        title TEXT,
                        source TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (quest_id) REFERENCES quests(quest_id) ON DELETE CASCADE
                    )
                ''')
                
                # Create difficulty_curves table
                self.conn.execute('''
                    CREATE TABLE difficulty_curves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT,
                        keyword TEXT,
                        difficulty_score INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes after tables are created
                self.conn.execute('CREATE INDEX idx_quests_quest_id ON quests (quest_id)')
                self.conn.execute('CREATE INDEX idx_quests_source ON quests (source)')
                self.conn.execute('CREATE INDEX idx_quests_difficulty ON quests (difficulty)')
                self.conn.execute('CREATE INDEX idx_quests_created_at ON quests (created_at)')
                self.conn.execute('CREATE INDEX idx_bookmarks_quest_id ON bookmarks (quest_id)')
                self.conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_quests_last_seen ON quests (last_seen)
                ''')
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to create tables: {str(e)}",
                operation="create_tables"
            )

    def bookmark_quest(self, quest_id: str, title: str, source: str, notes: str = ""):
        """
        Bookmark a quest for the user.
        
        Args:
            quest_id (str): Unique identifier for the quest
            title (str): Title of the quest
            source (str): Source of the quest (Reddit/Craigslist)
            notes (str): Optional notes for the bookmark
            
        Raises:
            DatabaseError: If bookmarking fails
        """
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT OR REPLACE INTO bookmarks (quest_id, title, source, notes)
                    VALUES (?, ?, ?, ?)
                ''', (quest_id, title, source, notes))
        except sqlite3.IntegrityError:
            logger.info(f"Quest {quest_id} is already bookmarked")
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to bookmark quest: {str(e)}",
                operation="bookmark",
                extra={"quest_id": quest_id}
            )

    def get_bookmarked_quests(self):
        """
        Retrieve all bookmarked quests.
        
        Returns:
            List[Tuple]: List of bookmarked quests
        """
        """Retrieve all bookmarked quests."""
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    SELECT quest_id, title, source, timestamp, notes
                    FROM bookmarks
                    ORDER BY timestamp DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching bookmarks: {e}")
            return []

    def remove_bookmark(self, quest_id: str):
        """Remove a quest from bookmarks."""
        try:
            with self.conn:
                self.conn.execute('''
                    DELETE FROM bookmarks WHERE quest_id = ?
                ''', (quest_id,))
            return True
        except sqlite3.Error as e:
            logger.error(f"Error removing bookmark: {e}")
            return False

    def update_bookmark_notes(self, quest_id: str, notes: str):
        """Update notes for a bookmarked quest."""
        try:
            with self.conn:
                self.conn.execute('''
                    UPDATE bookmarks SET notes = ? WHERE quest_id = ?
                ''', (notes, quest_id))
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating bookmark notes: {e}")
            return False

    def add_difficulty_curve(self, category: str, keyword: str, difficulty_score: int):
        """Add or update a difficulty curve entry with caching."""
        try:
            with self.conn:
                # Check if curve already exists
                cursor = self.conn.execute('''
                    SELECT id, difficulty_score FROM difficulty_curves 
                    WHERE category = ? AND keyword = ?
                ''', (category, keyword))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing curve if score changed
                    if existing[1] != difficulty_score:
                        self.conn.execute('''
                            UPDATE difficulty_curves 
                            SET difficulty_score = ?, created_at = CURRENT_TIMESTAMP
                            WHERE category = ? AND keyword = ?
                        ''', (difficulty_score, category, keyword))
                        return True
                    return False
                else:
                    # Insert new curve
                    self.conn.execute('''
                        INSERT INTO difficulty_curves (category, keyword, difficulty_score)
                        VALUES (?, ?, ?)
                    ''', (category, keyword, difficulty_score))
                    return True
        except sqlite3.Error as e:
            logger.error(f"Error adding/updating difficulty curve: {e}")
            raise

    def get_difficulty_curves(self, category: str = None):
        """Retrieve difficulty curves."""
        try:
            query = "SELECT category, keyword, difficulty_score, created_at FROM difficulty_curves"
            params = ()
            if category:
                query += " WHERE category = ?"
                params = (category,)
            query += " ORDER BY created_at DESC"
            
            with self.conn:
                cursor = self.conn.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching difficulty curves: {e}")
            return []

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

def get_database():
    """
    Get a singleton instance of the database.
    
    Returns:
        QuestDatabase: Singleton instance of the database
    """
    if not hasattr(get_database, "instance"):
        get_database.instance = QuestDatabase()
    return get_database.instance

# Add cache-related functions
def cache_quest(quest: dict) -> Dict[str, any]:
    """Cache a quest in the database and return quest statistics."""
    try:
        db = get_database()
        with db.conn:
            # Check if quest already exists
            cursor = db.conn.execute('''
                SELECT id FROM quests 
                WHERE link = ?
            ''', (quest.get('link', ''),))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing quest
                db.conn.execute('''
                    UPDATE quests 
                    SET title = ?, description = ?, reward = ?, 
                        difficulty = ?, source = ?, last_seen = CURRENT_TIMESTAMP,
                        gear_required = ?
                    WHERE id = ?
                ''', (
                    quest.get('title', ''),
                    quest.get('description', ''),
                    quest.get('reward', ''),
                    quest.get('difficulty', 0),
                    quest.get('source', ''),
                    quest.get('gear_required', ''),
                    existing[0]
                ))
            else:
                # Insert new quest
                db.conn.execute('''
                    INSERT INTO quests 
                    (
                        title, 
                        description, 
                        link, 
                        reward, 
                        difficulty, 
                        source, 
                        created_at, 
                        last_seen, 
                        gear_required
                    )
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                ''', (
                    quest.get('title', ''),
                    quest.get('description', ''),
                    quest.get('link', ''),
                    quest.get('reward', ''),
                    quest.get('difficulty', 0),
                    quest.get('source', ''),
                    quest.get('gear_required', '')
                ))
            
            # Remove old quests older than 30 days
            cutoff = datetime.now() - timedelta(days=30)
            if 'source' in quest:
                db.conn.execute('''
                    DELETE FROM quests 
                    WHERE last_seen < ?
                    AND source = ?
                ''', (cutoff, quest['source']))
            else:
                db.conn.execute('''
                    DELETE FROM quests 
                    WHERE last_seen < ?
                ''', (cutoff,))
            
            # Get quest statistics
            stats = {}
            
            # Total quests
            cursor = db.conn.execute('SELECT COUNT(*) FROM quests')
            stats['total_quests'] = cursor.fetchone()[0]
            
            # Quests by source
            cursor = db.conn.execute('''
                SELECT source, COUNT(*) 
                FROM quests 
                GROUP BY source
            ''')
            stats['quests_by_source'] = dict(cursor.fetchall())
            
            # Average difficulty
            cursor = db.conn.execute('SELECT AVG(difficulty) FROM quests')
            stats['avg_difficulty'] = cursor.fetchone()[0]
            
            # Oldest and newest quests
            cursor = db.conn.execute('''
                SELECT 
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM quests
            ''')
            oldest, newest = cursor.fetchone()
            stats['oldest_quest'] = oldest
            stats['newest_quest'] = newest
            
            # Quests with no gear requirements
            cursor = db.conn.execute('''
                SELECT COUNT(*) 
                FROM quests 
                WHERE gear_required = 'TBD' OR gear_required = ''
            ''')
            stats['quests_no_gear'] = cursor.fetchone()[0]
            
            return stats
    except sqlite3.Error as e:
        logger.error(f"Error caching quest: {e}")
        raise DatabaseError(
            f"Failed to cache quest: {str(e)}",
            operation="cache_quest"
        )

def get_pending_quests():
    """Retrieve all quests pending approval."""
    try:
        db = get_database()
        cursor = db.conn.execute('''
            SELECT * FROM quests 
            WHERE approved IS NULL
            ORDER BY created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error getting pending quests: {e}")
        raise DatabaseError(
            f"Failed to get pending quests: {str(e)}",
            operation="get_pending_quests"
        )

def approve_quest(quest_id: str):
    """Approve a quest submission."""
    try:
        db = get_database()
        with db.conn:
            db.conn.execute('''
                UPDATE quests 
                SET approved = 1 
                WHERE id = ?
            ''', (quest_id,))
    except sqlite3.Error as e:
        logger.error(f"Error approving quest {quest_id}: {e}")
        raise DatabaseError(
            f"Failed to approve quest: {str(e)}",
            operation="approve_quest"
        )

def reject_quest(quest_id: str):
    """Reject a quest submission."""
    try:
        db = get_database()
        with db.conn:
            db.conn.execute('''
                UPDATE quests 
                SET approved = 0 
                WHERE id = ?
            ''', (quest_id,))
    except sqlite3.Error as e:
        logger.error(f"Error rejecting quest {quest_id}: {e}")
        raise DatabaseError(
            f"Failed to reject quest: {str(e)}",
            operation="reject_quest"
        )

def get_user_stats(user_id: str) -> dict:
    """Get statistics for a specific user."""
    try:
        db = get_database()
        cursor = db.conn.execute('''
            SELECT 
                COUNT(*) as total_submitted,
                AVG(difficulty) as avg_difficulty
            FROM quests
            WHERE submitted_by = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if not result or result[0] is None:
            return {
                'total_submitted': 0,
                'avg_difficulty': 0,
                'rank': 'Novice',
                'quests_approved': 0,
                'quests_rejected': 0
            }
            
        total, avg_diff = result
        
        # Get approval stats
        cursor = db.conn.execute('''
            SELECT 
                SUM(CASE WHEN approved = 1 THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN approved = 0 THEN 1 ELSE 0 END) as rejected
            FROM quests
            WHERE submitted_by = ?
        ''', (user_id,))
        
        approved, rejected = cursor.fetchone() or (0, 0)
        
        return {
            'total_submitted': total or 0,
            'avg_difficulty': round(avg_diff or 0, 2),
            'rank': get_rank_from_difficulty(avg_diff or 0),
            'quests_approved': approved or 0,
            'quests_rejected': rejected or 0
        }
        
    except sqlite3.Error as e:
        logger.error(f"Error getting user stats for {user_id}: {e}")
        raise DatabaseError(
            f"Failed to get user stats: {str(e)}",
            operation="get_user_stats"
        )

def get_rank_from_difficulty(avg_difficulty: float) -> str:
    """Determine user rank based on average quest difficulty."""
    if avg_difficulty >= 8:
        return "Warlord"
    elif avg_difficulty >= 5:
        return "Knight"
    elif avg_difficulty >= 2:
        return "Adventurer"
    return "Squire"

def get_quests_by_region(region: str) -> list:
    """Get all quests for a specific region."""
    try:
        db = get_database()
        cursor = db.conn.execute('''
            SELECT * FROM quests 
            WHERE region = ? AND (approved = 1 OR approved IS NULL)
            ORDER BY created_at DESC
        ''', (region,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error getting quests for region {region}: {e}")
        raise DatabaseError(
            f"Failed to get quests by region: {str(e)}",
            operation="get_quests_by_region"
        )

def get_recent_activity(days: int = 1):
    """Get recent quest activity."""
    try:
        db = get_database()
        cutoff = datetime.now() - timedelta(days=days)
        with db.conn:
            cursor = db.conn.execute('''
                SELECT 
                    source,
                    COUNT(*) as count,
                    AVG(difficulty) as avg_difficulty,
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM quests
                WHERE created_at >= ?
                GROUP BY source
            ''', (cutoff,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to get recent activity: {str(e)}",
            operation="get_recent_activity"
        )

def optimize_cache():
    """Optimize the cache by:
    1. Removing duplicates with same title and description
    2. Updating difficulty scores based on recent data
    3. Cleaning up old difficulty curves
    """
    try:
        db = get_database()
        with db.conn:
            # Remove exact duplicates
            db.conn.execute('''
                DELETE FROM quests
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM quests
                    GROUP BY title, description
                )
            ''')
            
            # Update difficulty scores based on recent data
            db.conn.execute('''
                UPDATE quests
                SET difficulty = (
                    SELECT AVG(difficulty) as avg_diff
                    FROM quests t2
                    WHERE t2.source = quests.source
                    AND t2.created_at >= datetime('now', '-7 days')
                )
                WHERE difficulty IS NULL OR difficulty = 0
            ''')
            
            # Clean up old difficulty curves
            db.conn.execute('''
                DELETE FROM difficulty_curves
                WHERE created_at < datetime('now', '-30 days')
            ''')
            
            # Vacuum the database
            db.conn.execute('VACUUM')
            
        return True
    except sqlite3.Error as e:
        logger.error(f"Error optimizing cache: {e}")
        return False

def get_quest_history(quest_id: str, days: int = 30):
    """Get the history of a specific quest."""
    try:
        db = get_database()
        cutoff = datetime.now() - timedelta(days=days)
        with db.conn:
            cursor = db.conn.execute('''
                SELECT 
                    created_at,
                    difficulty,
                    score,
                    gear_required
                FROM quests
                WHERE quest_id = ? AND created_at >= ?
                ORDER BY created_at DESC
            ''', (quest_id, cutoff))
            return cursor.fetchall()
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to get quest history: {str(e)}",
            operation="get_quest_history"
        )

def get_similar_quests(quest_id: str, limit: int = 5):
    """Get quests similar to the given quest."""
    try:
        db = get_database()
        with db.conn:
            # Get the target quest's data
            cursor = db.conn.execute('''
                SELECT title, description, source, difficulty
                FROM quests
                WHERE quest_id = ?
            ''', (quest_id,))
            target = cursor.fetchone()
            
            if not target:
                return []
                
            # Get similar quests based on source and difficulty
            cursor = db.conn.execute('''
                SELECT 
                    quest_id,
                    title,
                    description,
                    source,
                    difficulty,
                    ABS(? - difficulty) as diff
                FROM quests
                WHERE quest_id != ?
                AND source = ?
                ORDER BY diff ASC, created_at DESC
                LIMIT ?
            ''', (target[3], quest_id, target[2], limit))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error getting similar quests: {e}")
        return []
