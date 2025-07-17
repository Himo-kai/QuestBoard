# 🧑‍💻 QuestBoard Developer Documentation

## 📚 Project Structure

```
QuestBoard/
├── app.py                 # Main application logic
├── database.py           # Database management and caching
├── errors.py            # Custom error handling
├── gear_keywords.py     # Gear detection and keyword management
├── reddit_source.py     # Reddit integration
├── utils.py             # Utility functions and helpers
├── tests/               # Unit tests
│   ├── test_database.py # Database tests
│   ├── test_gear.py    # Gear detection tests
│   └── test_reddit.py  # Reddit integration tests
├── docs/                # API documentation
│   ├── api.md          # API endpoints documentation
│   └── database.md     # Database schema documentation
└── requirements.txt     # Project dependencies
```

## 🛠️ Error Handling

### Custom Error Classes

QuestBoard uses a hierarchy of custom error classes:

```python
class QuestBoardError(Exception):
    """Base class for all QuestBoard errors."""
    def __init__(self, message, status_code=500, extra=None):
        super().__init__(message)
        self.status_code = status_code
        self.extra = extra or {}

# Derived error classes
- CacheError: Cache-related operations
- DatabaseError: Database operations
- APIError: External API calls
- ValidationError: Data validation
```

### Error Handling Pattern

```python
try:
    # Operation that might fail
except sqlite3.Error as e:
    raise DatabaseError(
        f"Failed to {operation}: {str(e)}",
        operation="operation_name",
        extra={"key": "value"}
    )
```

## 📊 Database Schema

### Tables

1. `quests`
   - Stores quest information and metadata
   - Fields:
     - `id`: Primary key
     - `quest_id`: Unique identifier
     - `title`: Quest title
     - `description`: Quest description
     - `link`: Source URL
     - `reward`: Compensation
     - `difficulty`: Estimated difficulty (1-5)
     - `source`: Source (Reddit/Craigslist)
     - `timestamp`: Creation timestamp
     - `score`: Reddit score (if applicable)
     - `author`: Reddit author (if applicable)
     - `gear_required`: Required gear
     - `created_at`: Record creation timestamp
     - `last_seen`: Last update timestamp

2. `bookmarks`
   - Tracks user-bookmarked quests
   - Fields:
     - `id`: Primary key
     - `quest_id`: Foreign key to quests
     - `title`: Quest title
     - `source`: Source
     - `timestamp`: Bookmark timestamp
     - `notes`: User notes

3. `difficulty_curves`
   - Stores historical difficulty ratings
   - Fields:
     - `id`: Primary key
     - `category`: Source category
     - `keyword`: Related keyword
     - `difficulty_score`: Score (1-5)
     - `created_at`: Timestamp

### Indexes

- `idx_quests_quest_id`: Quest ID lookup

## 🚀 Feature Roadmap

### ✅ Current Features
- Task aggregation from Reddit and Craigslist
- Difficulty scoring and gear detection
- Bookmarking system
- Basic caching and optimization
- Environment configuration wizard

### 📝 Planned Features

#### User Experience
- Multi-user support with authentication
- Personalized difficulty curves
- Advanced filtering and sorting
- Mobile-responsive design
- Dark/light theme support

#### Functionality
- User-specific bookmarks
- Task completion tracking
- Task categorization system
- Advanced search capabilities
- Task history and analytics
- Integration with more platforms

#### Technical
- Rate limiting for API calls
- Spam filtering and content moderation
- TF-IDF model persistence
- Real-time updates
- Performance optimizations

#### Future Improvements
- Machine learning for difficulty prediction
- Natural language processing for task analysis
- Integration with task management tools
- Social features and community building
- Mobile app development

### 🚨 Future Pain Points to Address

#### Scaling Bookmarks
- Implement user-specific bookmark tables
- Add user authentication system
- Consider multi-tenant architecture

#### TF-IDF Efficiency
- Persist TF-IDF models between runs
- Implement batch processing for large datasets
- Add model versioning and updates

#### Reddit API Limits
- Implement rate limiting middleware
- Add retry logic for API errors
- Cache API responses where possible

#### Spam Filtering
- Add profanity filter
- Implement scam detection
- Add content quality scoring
- Consider user reporting system
- `idx_quests_source`: Source-based queries
- `idx_quests_last_seen`: Time-based queries

## 🎯 API Endpoints

### Cache Management

- `GET /api/cache/stats`: Get cache statistics
- `POST /api/cache/optimize`: Optimize cache
- `GET /api/cache/history/<quest_id>`: Get quest history
- `GET /api/cache/similar/<quest_id>`: Get similar quests

### Bookmark Management

- `POST /api/bookmark/<quest_id>`: Toggle bookmark
- `GET /api/bookmarks`: Get all bookmarks

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_database.py

# Run with coverage
coverage run -m pytest tests/
coverage report
```

### Test Coverage

- Database operations: 100%
- Gear detection: 95%
- Reddit integration: 85%

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Update documentation
5. Submit a pull request

## 📜 Code Style

- Python: Black formatter
- Type hints: Required
- Logging: Use structured logging
- Error handling: Use custom error classes
- Documentation: Use docstrings for all public methods

## 📱 Environment Variables

```bash
# Reddit API credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=QuestBoard/1.0

# Database settings
DATABASE_PATH=questboard.db
```

## 📈 Performance Considerations

1. Use indexes for common queries
2. Implement caching for frequently accessed data
3. Use batch operations for bulk data
4. Clean up old data regularly
5. Monitor database size and performance
