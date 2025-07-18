"""
QuestBoard API package.

This package contains all API-related functionality including namespaces and routes.
"""
from flask_restx import Api

# Create the main API instance
api = Api(
    version='1.0',
    title='QuestBoard API',
    description='A RESTful API for the QuestBoard application',
    doc='/api/docs/'
)
