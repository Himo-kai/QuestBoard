# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
WSGI entry point for production deployments.

This module provides a production WSGI interface to the application.
"""
import os
import logging
from questboard import create_app
from config import ProductionConfig

# Configure logging before creating the app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Create the application instance with production config
    application = create_app(ProductionConfig)
    logger.info("Application initialized successfully")
    
except Exception as e:
    logger.critical(f"Failed to initialize the application: {e}", exc_info=True)
    raise

# For development use with: python wsgi.py
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    application.run(host='0.0.0.0', port=port, debug=False)
