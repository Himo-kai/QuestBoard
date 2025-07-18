# Flask environment variables
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database configuration
DATABASE_URL=sqlite:///instance/questboard.db

# Secret key for session management
SECRET_KEY=dev-key-change-in-production

# Email configuration
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_DEBUG=True
MAIL_USERNAME=None
MAIL_PASSWORD=None
MAIL_DEFAULT_SENDER=no-reply@questboard.local

# Frontend URL for email templates
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:////home/himokai/Downloads/QuestBoard/instance/questboard.db
