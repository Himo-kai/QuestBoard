# QuestBoard

A platform for managing and discovering quests with intelligent matching and scoring.

## 🚀 Features

- **Quest Management**: Create, read, update, and delete quests
- **Intelligent Matching**: NLP-powered quest recommendations
- **Scoring System**: Dynamic difficulty and relevance scoring
- **Bookmarking**: Save and organize favorite quests
- **RESTful API**: Fully documented API endpoints
- **Admin Dashboard**: Manage quests and users
- **Monitoring**: Real-time metrics and logging

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask, SQLAlchemy
- **Database**: PostgreSQL, Redis (caching)
- **ML/NLP**: scikit-learn, sentence-transformers
- **Monitoring**: Prometheus, Grafana
- **Frontend**: (To be implemented)
- **Deployment**: Docker, Docker Compose

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 16+ (for frontend, future)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/QuestBoard.git
   cd QuestBoard
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development dependencies
   ```

### Database Setup

1. **Configure Database**
   - Copy the example environment file and update the database credentials:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set your database connection string:
     ```
     DATABASE_URL=postgresql://username:password@localhost/questboard
     ```

2. **Initialize the Database**
   - For development (SQLite):
     ```bash
     export FLASK_APP=manage.py
     flask db upgrade
     ```
   - For production (PostgreSQL):
     ```bash
     export FLASK_APP=manage.py
     export DATABASE_URL=postgresql://username:password@localhost/questboard
     flask db upgrade
     ```

## 🔄 Database Migrations

QuestBoard uses Flask-Migrate with Alembic for database migrations. Here's how to work with migrations:

### Creating Migrations

When you make changes to your models, create a new migration:

```bash
export FLASK_APP=manage.py
flask db migrate -m "Description of changes"
```

### Applying Migrations

To apply pending migrations:

```bash
flask db upgrade
```

### Reverting Migrations

To revert the last migration:

```bash
flask db downgrade
```

### Migration Best Practices

1. Always create a new migration when you change your models
2. Test migrations in development before applying to production
3. Commit migration files to version control
4. Never manually edit migration files after they've been committed
5. Always back up your database before running migrations in production

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   # Development server
   flask run
   
   # Or with auto-reload
   FLASK_DEBUG=1 flask run
   ```

## 🧪 Development

### Project Structure

```
QuestBoard/
├── questboard/           # Main application package
│   ├── api/              # API routes and resources
│   ├── models/           # Database models
│   ├── services/         # Business logic and services
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # HTML templates
│   ├── __init__.py       # Application factory
│   └── config.py         # Configuration settings
├── tests/               # Test suite
├── migrations/          # Database migrations
├── monitoring/          # Monitoring configuration
├── .env.example         # Example environment variables
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage report
pytest --cov=questboard tests/
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with Black
black .

# Check for style issues
flake8

# Type checking
mypy .
```

## 📚 API Documentation

Once the development server is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:5000/api/docs`
- ReDoc: `http://localhost:5000/api/redoc`

## 🐳 Docker Deployment

Run the entire stack with Docker Compose:

```bash
docker-compose up --build
```

This will start:
- Web application
- PostgreSQL database
- Redis cache
- Prometheus (metrics)
- Grafana (visualization)

## 📊 Monitoring

Access monitoring dashboards:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/admin)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MPL 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [scikit-learn](https://scikit-learn.org/)
- And all other amazing open-source projects we depend on!
