# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
QuestBoard routes package.

This package contains all the route blueprints for the QuestBoard application.
"""

# Import blueprints here to make them available when importing from routes
from .main import main_bp
from .admin import admin_bp
from .user import user_bp
from .api import api_bp

# List of all blueprints to be registered with the app
blueprints = [
    main_bp,
    admin_bp,
    user_bp,
    api_bp
]
