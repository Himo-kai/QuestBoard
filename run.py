#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
QuestBoard - Main entry point for development server.

This script provides a development server with hot-reload functionality.
For production deployment, use a proper WSGI server with wsgi.py.
"""
import os
import sys
import argparse
import logging
from questboard import create_app
from config import DevelopmentConfig

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the QuestBoard application')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the application on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--fetch-only', action='store_true', 
                       help='Only fetch quests without starting the web server')
    return parser.parse_args()

def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('questboard.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create the application instance
        app = create_app(DevelopmentConfig)
        
        # Handle fetch-only mode
        if args.fetch_only:
            logger.info("Running in fetch-only mode...")
            with app.app_context():
                from services.quest_fetcher import fetch_gigs
                from database import get_database
                
                quests = fetch_gigs()
                db = get_database()
                
                for quest in quests:
                    db.cache_quest(quest)
                
                logger.info(f"Fetched and cached {len(quests)} quests")
            return 0
        
        # Run the development server
        logger.info(f"Starting QuestBoard on port {args.port} (Debug: {args.debug})")
        app.run(
            host='0.0.0.0',
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug,
            use_debugger=args.debug
        )
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
