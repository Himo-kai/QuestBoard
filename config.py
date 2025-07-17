# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'questboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # QuestBoard specific settings
    DEBUG = os.environ.get('FLASK_DEBUG', '0').lower() in ['1', 'true', 'yes']
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Craigslist settings
    CRAIGSLIST_BASE_URL = os.environ.get('CRAIGSLIST_BASE_URL', 'https://vancouver.craigslist.org')
    
    # Reddit settings
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT', 'QuestBoard/1.0')
    
    # WebDriver settings
    WEBDRIVER_PATH = os.environ.get('WEBDRIVER_PATH', '/usr/local/bin/chromedriver')
    
    # Application settings
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    LOG_LEVEL = 'WARNING'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
