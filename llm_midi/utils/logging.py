"""Logging utilities for the llm_midi application."""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        # Get the base formatted message
        message = super().format(record)

        # Add colors if outputting to terminal
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            return f"{color}{message}{reset}"

        return message


def setup_logging(
    level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    console_output: bool = True,
    file_level: Optional[Union[str, int]] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        level: Console logging level (default: INFO)
        log_file: Path to log file (optional)
        console_output: Whether to output to console (default: True)
        file_level: File logging level (defaults to same as console level)
        format_string: Custom format string (optional)
    """
    # Convert string levels to constants
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    if file_level is None:
        file_level = level
    elif isinstance(file_level, str):
        file_level = getattr(logging, file_level.upper())

    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set root logger level to the most permissive level needed
    root_logger.setLevel(min(level, file_level) if log_file and file_level is not None else level)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Use colored formatter for console
        console_formatter = ColoredFormatter(format_string)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        if file_level is not None:
            file_handler.setLevel(file_level)

        # Use standard formatter for file (no colors)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def setup_app_logging(
    debug: bool = False,
    log_dir: Optional[Union[str, Path]] = None,
    quiet: bool = False
) -> None:
    """
    Set up application-specific logging configuration.

    Args:
        debug: Enable debug-level logging
        log_dir: Directory for log files (optional)
        quiet: Suppress console output except errors
    """
    # Determine console level
    if quiet:
        console_level = logging.ERROR
    elif debug:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO

    # Set up log file path if log_dir is provided
    log_file = None
    if log_dir:
        log_dir = Path(log_dir)
        log_file = log_dir / "llm_midi.log"

    # File logging should capture everything if enabled
    file_level = logging.DEBUG if log_file else None

    setup_logging(
        level=console_level,
        log_file=log_file,
        console_output=not quiet or console_level <= logging.ERROR,
        file_level=file_level
    )

    # Suppress noisy third-party loggers unless in debug mode
    if not debug:
        # Reduce anthropic client verbosity
        logging.getLogger("anthropic").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

        # Reduce urllib3 verbosity
        logging.getLogger("urllib3").setLevel(logging.WARNING)


class LoggingContext:
    """Context manager for temporary logging configuration."""

    def __init__(
        self,
        level: Union[str, int],
        logger_name: Optional[str] = None
    ):
        """
        Initialize logging context.

        Args:
            level: Temporary logging level
            logger_name: Specific logger to modify (defaults to root)
        """
        self.level = level
        self.logger_name = logger_name
        self.original_level = None

        if isinstance(level, str):
            self.level = getattr(logging, level.upper())

    def __enter__(self):
        """Enter the logging context."""
        logger = logging.getLogger(self.logger_name)
        self.original_level = logger.level
        logger.setLevel(self.level)
        return logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the logging context."""
        logger = logging.getLogger(self.logger_name)
        if self.original_level is not None:
            logger.setLevel(self.original_level)


# Convenience context managers
def debug_logging(logger_name: Optional[str] = None):
    """Context manager for temporary debug logging."""
    return LoggingContext(logging.DEBUG, logger_name)


def quiet_logging(logger_name: Optional[str] = None):
    """Context manager for temporary quiet logging."""
    return LoggingContext(logging.ERROR, logger_name)


# Module-level logger for this package
logger = get_logger(__name__)
