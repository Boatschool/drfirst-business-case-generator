"""
Logging test utilities for verifying enhanced diagnostic logging.
Provides helpers to assert that specific log messages are emitted during tests.
"""

import re
import logging
from typing import List, Optional, Pattern
from _pytest.logging import LogCaptureFixture


def assert_log_contains(caplog: LogCaptureFixture, level: str, message_pattern: str, logger_name: Optional[str] = None) -> bool:
    """
    Assert that a log message matching the pattern exists at the specified level.
    
    Args:
        caplog: pytest caplog fixture
        level: Log level (e.g., 'INFO', 'ERROR', 'DEBUG')
        message_pattern: String pattern to match in log message (supports regex)
        logger_name: Optional specific logger name to check
        
    Returns:
        bool: True if matching log message found
        
    Raises:
        AssertionError: If no matching log message is found
    """
    level_num = getattr(logging, level.upper())
    pattern = re.compile(message_pattern)
    
    matching_records = []
    for record in caplog.records:
        # Check level
        if record.levelno != level_num:
            continue
            
        # Check logger name if specified
        if logger_name and record.name != logger_name:
            continue
            
        # Check message pattern
        if pattern.search(record.getMessage()):
            matching_records.append(record)
    
    if not matching_records:
        # Create helpful error message
        all_messages = [f"{record.levelname}: {record.getMessage()}" for record in caplog.records]
        error_msg = (
            f"No log message found matching pattern '{message_pattern}' at level '{level}'"
        )
        if logger_name:
            error_msg += f" from logger '{logger_name}'"
        error_msg += f"\nActual log messages:\n" + "\n".join(all_messages)
        raise AssertionError(error_msg)
    
    return True


def assert_log_sequence(caplog: LogCaptureFixture, expected_patterns: List[str], level: str = "INFO") -> bool:
    """
    Assert that log messages appear in a specific sequence.
    
    Args:
        caplog: pytest caplog fixture
        expected_patterns: List of regex patterns that should appear in order
        level: Log level to check
        
    Returns:
        bool: True if sequence is found
        
    Raises:
        AssertionError: If sequence is not found
    """
    level_num = getattr(logging, level.upper())
    messages = [record.getMessage() for record in caplog.records if record.levelno == level_num]
    
    pattern_index = 0
    for message in messages:
        if pattern_index < len(expected_patterns):
            pattern = re.compile(expected_patterns[pattern_index])
            if pattern.search(message):
                pattern_index += 1
    
    if pattern_index != len(expected_patterns):
        missing_patterns = expected_patterns[pattern_index:]
        raise AssertionError(
            f"Log sequence incomplete. Missing patterns: {missing_patterns}\n"
            f"Actual messages: {messages}"
        )
    
    return True


def assert_log_count(caplog: LogCaptureFixture, level: str, expected_count: int, logger_name: Optional[str] = None) -> bool:
    """
    Assert that a specific number of log messages exist at the given level.
    
    Args:
        caplog: pytest caplog fixture
        level: Log level to check
        expected_count: Expected number of log messages
        logger_name: Optional specific logger name to check
        
    Returns:
        bool: True if count matches
        
    Raises:
        AssertionError: If count doesn't match
    """
    level_num = getattr(logging, level.upper())
    
    matching_count = 0
    for record in caplog.records:
        if record.levelno == level_num:
            if logger_name is None or record.name == logger_name:
                matching_count += 1
    
    if matching_count != expected_count:
        raise AssertionError(
            f"Expected {expected_count} log messages at level '{level}', "
            f"but found {matching_count}"
        )
    
    return True


def get_log_messages(caplog: LogCaptureFixture, level: str, logger_name: Optional[str] = None) -> List[str]:
    """
    Get all log messages at the specified level.
    
    Args:
        caplog: pytest caplog fixture
        level: Log level to filter by
        logger_name: Optional specific logger name to filter by
        
    Returns:
        List[str]: List of log messages
    """
    level_num = getattr(logging, level.upper())
    
    messages = []
    for record in caplog.records:
        if record.levelno == level_num:
            if logger_name is None or record.name == logger_name:
                messages.append(record.getMessage())
    
    return messages


def assert_workflow_logging_sequence(caplog: LogCaptureFixture, case_id: str, workflow_type: str) -> bool:
    """
    Assert that a complete workflow logging sequence is present.
    
    Args:
        caplog: pytest caplog fixture
        case_id: The case ID that should appear in logs
        workflow_type: Type of workflow (e.g., 'approval', 'rejection')
        
    Returns:
        bool: True if complete sequence found
    """
    if workflow_type == "approval":
        expected_patterns = [
            f"System design approval initiated for case {case_id}",
            f"Status check for case {case_id}:",
            f"Status transition: .* -> .* for case {case_id}",
            f"Calling orchestrator\\.handle_system_design_approval\\(\\) for case {case_id}"
        ]
    elif workflow_type == "rejection":
        expected_patterns = [
            f"System design rejection initiated for case {case_id}",
            f"Status check for case {case_id}:",
            f"Status transition: .* -> .* for case {case_id}"
        ]
    else:
        raise ValueError(f"Unknown workflow_type: {workflow_type}")
    
    return assert_log_sequence(caplog, expected_patterns)


class LogLevelContext:
    """Context manager to temporarily change log level for testing."""
    
    def __init__(self, logger_name: str, level: str):
        self.logger_name = logger_name
        self.new_level = getattr(logging, level.upper())
        self.old_level = None
        
    def __enter__(self):
        logger = logging.getLogger(self.logger_name)
        self.old_level = logger.level
        logger.setLevel(self.new_level)
        return logger
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.old_level) 