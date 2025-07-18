import os
from dotenv import load_dotenv

load_dotenv()

def get_database_path(db_name):
    """Helper function to get the database path in the instance folder"""
    instance_path = os.path.join(os.getcwd(), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, f'{db_name}.db')
    print(f"Database path: {db_path}")  # Debug print
    return db_path

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{get_database_path("questboard")}'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{get_database_path("questboard_dev")}'
    
    def __init__(self):
        print(f"Development DB URI: {self.SQLALCHEMY_DATABASE_URI}")  # Debug print

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    def __init__(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError('DATABASE_URL environment variable must be set for production')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
