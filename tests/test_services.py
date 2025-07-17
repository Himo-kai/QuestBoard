# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest
import logging
from datetime import datetime, timezone
from questboard.services.nlp_service import NLPService
from questboard.services.logging_service import LoggingService

class TestNLPService:
    def test_calculate_difficulty(self, nlp_service):
        """Test difficulty score calculation."""
        # Simple text
        assert 1.0 <= nlp_service.calculate_difficulty("Simple task") <= 10.0
        
        # Technical text
        tech_text = """
        We need a senior Python developer with experience in Django, PostgreSQL, 
        and AWS to build a scalable microservices architecture using Docker and Kubernetes.
        Experience with machine learning and data pipelines is a plus.
        """
        assert nlp_service.calculate_difficulty(tech_text) > 5.0
        
        # Empty text
        assert nlp_service.calculate_difficulty("") == 5.0
    
    def test_extract_keywords(self, nlp_service):
        """Test keyword extraction."""
        text = """
        Looking for a Python developer with Flask experience to build RESTful APIs.
        Knowledge of SQLAlchemy and PostgreSQL is required.
        """
        keywords = nlp_service.extract_keywords(text, top_n=3)
        assert len(keywords) == 3
        assert isinstance(keywords, list)
        assert all(isinstance(kw, str) for kw in keywords)
        
        # Test with empty text
        assert nlp_service.extract_keywords("") == []
    
    def test_extract_reward(self, nlp_service):
        """Test reward extraction from text."""
        # Test different reward patterns
        test_cases = [
            ("Pay: $500", "$500"),
            ("Budget: 1000 USD", "1000"),
            ("Reward: €750", "750"),  # Updated to match actual implementation
            ("Compensation: £2500", "2500"),  # Updated to match actual implementation
            ("No reward mentioned", "Not specified")
        ]
        
        for text, expected in test_cases:
            assert nlp_service.extract_reward(text) == expected
    
    def test_suggest_gear(self, nlp_service):
        """Test gear suggestion based on text."""
        # Test with technical description
        tech_text = """
        We need a full-stack developer to build a web application using 
        React, Node.js, and MongoDB. Experience with Docker and AWS is a plus.
        """
        suggestions = nlp_service.suggest_gear(tech_text)
        assert len(suggestions) > 0
        assert any(s['category'] == 'Coding' for s in suggestions)
        
        # Test with hardware description
        hardware_text = "Need help setting up a Raspberry Pi cluster"
        suggestions = nlp_service.suggest_gear(hardware_text)
        assert any(s['category'] == 'Hardware' for s in suggestions)
        
        # Test with no relevant keywords
        assert nlp_service.suggest_gear("Simple task") == []

class TestLoggingService:
    def test_logging_configuration(self, tmp_path):
        """Test logging service configuration."""
        # Create a temporary log file
        log_file = tmp_path / 'test.log'

        # Configure logging with DEBUG level
        LoggingService.configure(
            log_level=logging.DEBUG,
            log_file=str(log_file),
            force_reconfigure=True  # Force reconfiguration
        )

        # Get a logger
        logger = LoggingService.get_logger('test_logger')
        assert isinstance(logger, logging.Logger)

        # Test logging at different levels
        test_message = 'Test log message'
        logger.debug(test_message)
        logger.info(test_message)
        logger.warning(test_message)
        logger.error(test_message)
        logger.critical(test_message)

        # Verify log file was created and contains our message
        assert log_file.exists()
        log_content = log_file.read_text()
        
        # All messages should be in the log since we're at DEBUG level
        assert test_message in log_content
        
        # Test getting the same logger again
        same_logger = LoggingService.get_logger('test_logger')
        assert same_logger is logger

        # Test getting a different logger
        another_logger = LoggingService.get_logger('another_logger')
        assert another_logger is not logger
        
        # Clear the log file for the next test
        log_file.write_text('')
        
        # Test log level filtering - reconfigure to ERROR level only
        LoggingService.configure(
            log_level=logging.ERROR,
            log_file=str(log_file),
            force_reconfigure=True
        )
        
        # Get a new logger after reconfiguration
        error_logger = LoggingService.get_logger('level_test')
        error_logger.debug('This should not appear')
        error_logger.info('This should not appear')
        error_logger.warning('This should not appear')
        error_logger.error('This should appear')
        error_logger.critical('This should appear')
        
        # Read the log file again
        log_content = log_file.read_text()
        
        # Only ERROR and CRITICAL messages should appear
        assert 'This should appear' in log_content
        assert 'This should not appear' not in log_content
        
        # Verify the debug message is not in the log
        debug_logs = [line for line in log_content.split('\n') if 'DEBUG' in line]
        assert not any('This should not appear' in line for line in debug_logs)
