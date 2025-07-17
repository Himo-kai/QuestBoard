# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, ClassVar

class LoggingService:
    """A service for managing application logging."""
    
    # Class variables
    _loggers: ClassVar[Dict[str, logging.Logger]] = {}
    _configured: ClassVar[bool] = False
    
    def __init__(self):
        """Initialize the LoggingService."""
        # Ensure class variables are initialized
        if not hasattr(self.__class__, '_loggers'):
            self.__class__._loggers = {}
        if not hasattr(self.__class__, '_configured'):
            self.__class__._configured = False
    
    @classmethod
    def configure(
        cls,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force_reconfigure: bool = False
    ) -> None:
        """Configure the root logger with the specified settings.
        
        Args:
            log_level: The minimum log level to capture (default: logging.INFO)
            log_file: Optional path to a log file (default: None)
            log_format: The log message format (default: '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            force_reconfigure: If True, reconfigure even if already configured (default: False)
        """
        # Ensure class variables are initialized
        if not hasattr(cls, '_loggers'):
            cls._loggers = {}
        if not hasattr(cls, '_configured'):
            cls._configured = False
            
        if cls._configured and not force_reconfigure:
            return
            
        # Get the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler if log file is specified
        if log_file:
            try:
                # Ensure directory exists
                log_path = Path(log_file).absolute()
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create file handler
                file_handler = logging.FileHandler(
                    str(log_path),
                    encoding='utf-8',
                    mode='a'  # Append mode
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                
                # Log successful file handler setup
                root_logger.info(f"Logging to file: {log_path}")
            except Exception as e:
                root_logger.error(f"Failed to configure file logging: {e}")
        
        # Update log level for existing loggers
        for logger in cls._loggers.values():
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)
        
        cls._configured = True
        root_logger.info(f"Logging service configured at level {logging.getLevelName(log_level)}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger with the specified name.
        
        Args:
            name: The name of the logger
            
        Returns:
            A configured logger instance
        """
        # Ensure class variables are initialized
        if not hasattr(cls, '_loggers'):
            cls._loggers = {}
            
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        return cls._loggers[name]
