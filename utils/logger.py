"""Logging utility module."""
import logging
import os
from datetime import datetime


class Log:
    """Logger class for the automation framework."""

    _logger = None

    @classmethod
    def _get_logger(cls):
        """Get or create logger instance."""
        if cls._logger is None:
            cls._logger = logging.getLogger("RaapidAutomation")
            cls._logger.setLevel(logging.INFO)

            # Create logs directory if it doesn't exist
            if not os.path.exists("logs"):
                os.makedirs("logs")

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # File handler
            log_file = f"logs/test_execution.log"
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s [%(threadName)s] %(levelname)-5s %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # Add handlers
            cls._logger.addHandler(console_handler)
            cls._logger.addHandler(file_handler)

        return cls._logger

    @classmethod
    def info(cls, message: str):
        """Log info message."""
        cls._get_logger().info(message)

    @classmethod
    def error(cls, message: str):
        """Log error message."""
        cls._get_logger().error(message)

    @classmethod
    def warn(cls, message: str):
        """Log warning message."""
        cls._get_logger().warning(message)

    @classmethod
    def debug(cls, message: str):
        """Log debug message."""
        cls._get_logger().debug(message)

