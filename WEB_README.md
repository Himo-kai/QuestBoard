# QuestBoard Web Application

This is the web interface for QuestBoard, a modern platform for discovering and managing freelance gigs and opportunities. This application provides a user-friendly interface to interact with the QuestBoard system.

## 🚀 Features

- **Modern Web Interface**: Responsive design that works on all devices
- **Real-time Updates**: See new quests as they're discovered
- **Interactive Difficulty Scoring**: Understand why quests are rated the way they are
- **Gear Suggestions**: Get personalized gear recommendations
- **User Accounts**: Save your preferences and bookmarks
- **Admin Dashboard**: Manage quests and users

## 🏗️ Project Structure

```
questboard/
├── app/                      # Main application package
│   ├── __init__.py           # Application factory
│   ├── routes/               # Route handlers
│   │   ├── __init__.py
│   │   ├── main.py           # Main routes
│   │   ├── admin.py          # Admin routes
│   │   └── user.py           # User routes
│   │
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── quest_fetcher.py  # Fetch quests from sources
│   │   ├── difficulty_engine.py  # Calculate difficulty scores
│   │   └── gear_suggester.py # Suggest gear for quests
│   │
│   ├── static/               # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/            # Jinja2 templates
│       ├── base.html
│       ├── questboard.html
│       └── ...
│
├── config.py                 # Configuration settings
├── run.py                    # Development server script
└── wsgi.py                   # Production WSGI entry point
```

## 🛠️ Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Copy `.env.example` to `.env` and update the values.

3. **Initialize the Database**
   ```bash
   flask init-db
   ```

## 🏃 Running the Application

### Development Mode
```bash
# Start the development server
python run.py --port 5002 --debug
```

### Production Mode
```bash
# Using Gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:application

# Using Docker
docker build -t questboard .
docker run -p 5000:5000 questboard
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Flask application module | `questboard` |
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Secret key for session management | Randomly generated |
| `DATABASE_URL` | Database connection URL | `sqlite:///questboard.db` |
| `REDDIT_CLIENT_ID` | Reddit API client ID | - |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | - |
| `CRAIGSLIST_BASE_URL` | Base URL for Craigslist | `https://vancouver.craigslist.org` |

## 📚 API Documentation

### Authentication

```http
POST /api/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword"
}
```

### Quests

- `GET /api/quests` - List all quests
- `GET /api/quests/<id>` - Get quest details
- `POST /api/quests` - Submit a new quest
- `PUT /api/quests/<id>` - Update a quest
- `DELETE /api/quests/<id>` - Delete a quest

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This web application is part of the QuestBoard ecosystem. For the command-line interface, see the main [QuestBoard](https://github.com/yourusername/questboard) repository.
