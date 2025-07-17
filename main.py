#!/usr/bin/env python3
"""
QuestBoard - Main entry point for the application.
"""
import argparse
import os
import sys
from typing import Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main() -> None:
    """Run the QuestBoard application."""
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Run the QuestBoard application')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the application on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the application to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    # Import here to avoid circular imports
    from questboard import create_app
    
    # Create and run the application
    app = create_app()
    
    # Run the application
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_reloader=args.reload
    )

if __name__ == '__main__':
    main()
