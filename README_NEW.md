# 🧭 QuestBoard

**QuestBoard** is a gamified job board that aggregates and curates gig listings—turning freelance hunting into an RPG-inspired experience. It pulls quests from various sources and provides a modern web interface with API access.

## 🚀 Features

- **Quest Management**: Browse, search, and filter quests
- **User Submissions**: Submit and manage your own quests
- **Bookmarking**: Save quests for later
- **API Access**: RESTful API with Swagger documentation
- **Monitoring**: Built-in metrics and monitoring with Prometheus and Grafana
- **Containerized**: Easy deployment with Docker

## 🛠 Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 14+ (for frontend development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/questboard.git
   cd questboard
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   flask init-db
   ```

6. **Run the development server**
   ```bash
   flask run
   ```

### Docker Deployment

1. **Build and start the application**
   ```bash
   docker-compose up --build
   ```

2. **Initialize the database**
   ```bash
   docker-compose exec web flask db upgrade
   docker-compose exec web flask init-db
   ```

## 🌐 Access Services

- **Web Application**: http://localhost:5000
- **API Documentation (Swagger UI)**: http://localhost:5000/api/docs
- **Grafana Dashboard**: http://localhost:3000
  - Username: admin
  - Password: admin
- **Prometheus**: http://localhost:9090

## 📚 API Documentation

The QuestBoard API is documented using OpenAPI (Swagger) and is available at `/api/docs` when the application is running.

### Available Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/quests` - List quests with pagination and filtering
- `GET /api/quests/<id>` - Get quest details
- `POST /api/quests` - Submit a new quest
- `POST /api/bookmarks` - Bookmark a quest
- `DELETE /api/bookmarks/<quest_id>` - Remove a bookmark

### Authentication

Most endpoints require authentication. Include a valid JWT token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

## 📊 Monitoring

The application includes built-in monitoring with Prometheus and Grafana:

- **Application Metrics**: Request rates, latencies, error rates
- **Database Performance**: Query times and counts
- **System Metrics**: CPU, memory, and disk usage (when running in Docker)

### Setting Up Grafana

1. Log in to Grafana at http://localhost:3000
2. Add Prometheus as a data source:
   - URL: http://prometheus:9090
   - Access: Server (default)
3. Import the QuestBoard dashboard from `/monitoring/grafana/questboard-dashboard.json`

## 🛠 Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses `black` for code formatting and `flake8` for linting:

```bash
black .
flake8
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
