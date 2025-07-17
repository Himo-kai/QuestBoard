import sqlite3
from pathlib import Path
import os

def run_migration():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'questboard.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create quests table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            link TEXT UNIQUE,
            reward TEXT,
            difficulty REAL DEFAULT 0,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gear_required TEXT,
            approved INTEGER DEFAULT NULL,
            region TEXT DEFAULT 'Unknown',
            submitted_by TEXT DEFAULT NULL
        )
    ''')
    
    # Add new columns if they don't exist
    cursor.execute('''
        PRAGMA table_info(quests)
    ''')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'approved' not in columns:
        cursor.execute('''
            ALTER TABLE quests 
            ADD COLUMN approved INTEGER DEFAULT NULL
        ''')
    
    if 'region' not in columns:
        cursor.execute('''
            ALTER TABLE quests 
            ADD COLUMN region TEXT DEFAULT 'Unknown'
        ''')
    
    if 'submitted_by' not in columns:
        cursor.execute('''
            ALTER TABLE quests 
            ADD COLUMN submitted_by TEXT DEFAULT NULL
        ''')
    
    # Create bookmarks table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE,
            UNIQUE(quest_id, user_id)
        )
    ''')
    
    # Create difficulty_curves table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS difficulty_curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            keyword TEXT,
            difficulty_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
    print("Database migration completed successfully!")
