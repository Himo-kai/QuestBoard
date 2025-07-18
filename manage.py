#!/usr/bin/env python
"""
Command-line utility for administrative tasks.
"""
import os
import sys
import click
from flask_migrate import Migrate, upgrade, migrate as migrate_db, init, stamp
from questboard import create_app, db
from questboard.models.user import User
from questboard.models.quest import Quest, Tag

# Create the Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'development')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """
    Automatically import these objects in the Flask shell.
    """
    return {
        'db': db,
        'User': User,
        'Quest': Quest,
        'Tag': Tag
    }

def register_commands(app):
    """Register custom CLI commands."""
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        with app.app_context():
            # Create all database tables
            db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                click.echo("Created admin user with email 'admin@example.com' and password 'admin123'")
            
            click.echo("Database initialized successfully!")
    
    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('password')
    def create_admin(email, password):
        """Create an admin user."""
        with app.app_context():
            admin = User.query.filter_by(email=email).first()
            if admin:
                click.echo(f"User with email {email} already exists.")
                return
            
            admin = User(
                username=email.split('@')[0],
                email=email,
                is_admin=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.echo(f"Created admin user with email {email}")

# Register commands with the application
register_commands(app)

if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
