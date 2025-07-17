# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Quest Fetcher Service

This module provides functionality to fetch quests/gigs from various sources.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime

# Initialize logger
from .logging_service import LoggingService
logger = LoggingService.get_logger(__name__)

def fetch_gigs():
    """Fetch gigs from various sources.
    
    This is a placeholder function that would normally fetch gigs from
    various sources like Craigslist, Reddit, etc.
    
    Returns:
        list: A list of fetched gigs
    """
    logger.info("Starting gig fetching process")
    
    # This is a placeholder implementation
    # In a real application, this would fetch gigs from various sources
    sample_gigs = [
        {
            'id': 'sample1',
            'title': 'Sample Gig 1',
            'source': 'test',
            'url': 'http://example.com/gig1',
            'posted_date': datetime.utcnow().isoformat(),
            'description': 'This is a sample gig',
            'location': 'Remote',
            'compensation': '$50-100',
            'tags': ['test', 'sample']
        },
        {
            'id': 'sample2',
            'title': 'Sample Gig 2',
            'source': 'test',
            'url': 'http://example.com/gig2',
            'posted_date': datetime.utcnow().isoformat(),
            'description': 'Another sample gig',
            'location': 'New York, NY',
            'compensation': '$100-200',
            'tags': ['test', 'sample']
        }
    ]
    
    logger.info(f"Fetched {len(sample_gigs)} gigs")
    return sample_gigs

# CLI command to manually trigger gig fetching
@click.command('fetch-gigs')
@with_appcontext
def fetch_gigs_command():
    """Fetch gigs from configured sources."""
    logger.info("Starting gig fetch from command line")
    try:
        gigs = fetch_gigs()
        click.echo(f"Successfully fetched {len(gigs)} gigs")
    except Exception as e:
        logger.error(f"Error fetching gigs: {e}")
        raise click.ClickException(f"Failed to fetch gigs: {e}")

def init_app(app):
    """Register CLI commands with the Flask application."""
    app.cli.add_command(fetch_gigs_command)
