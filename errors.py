# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from typing import Dict, Any
from http import HTTPStatus

class QuestBoardError(Exception):
    """Base class for all QuestBoard errors."""
    def __init__(self, message: str, status_code: int = 500, extra: Dict[str, Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.extra = extra or {}

class CacheError(QuestBoardError):
    """Error related to cache operations."""
    def __init__(self, message: str, operation: str, extra: Dict[str, Any] = None):
        super().__init__(message, status_code=500, extra={"operation": operation, **(extra or {})})

class DatabaseError(QuestBoardError):
    """Error related to database operations."""
    def __init__(self, message: str, operation: str, extra: Dict[str, Any] = None):
        super().__init__(message, status_code=500, extra={"operation": operation, **(extra or {})})

class APIError(QuestBoardError):
    """Error related to external API calls."""
    def __init__(self, message: str, service: str, status_code: int = 500, extra: Dict[str, Any] = None):
        super().__init__(message, status_code=status_code, extra={"service": service, **(extra or {})})

class ValidationError(QuestBoardError):
    """Error related to data validation."""
    def __init__(self, message: str, field: str, extra: Dict[str, Any] = None):
        super().__init__(message, status_code=400, extra={"field": field, **(extra or {})})

def handle_error(error: Exception):
    """Handle errors and return appropriate HTTP response."""
    logger = logging.getLogger(__name__)
    
    if isinstance(error, QuestBoardError):
        logger.error(f"{error.__class__.__name__}: {str(error)}", extra=error.extra)
        return {
            "error": str(error),
            "type": error.__class__.__name__,
            **error.extra
        }, error.status_code
    
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "type": "InternalServerError"
    }, HTTPStatus.INTERNAL_SERVER_ERROR
