"""
Centralized logging configuration for RainingKeys.

Provides a configured logger instance for use throughout the application.
"""
import logging
import os
import sys
from PySide6.QtCore import QObject, Signal


class LogEmitter(QObject):
    """Qt signal emitter for log messages to be displayed in UI.

    This class is provided for future integration with a UI log viewer.
    It can be used to display log messages in real-time in the application's GUI.
    """
    log_message = Signal(str, str)  # level, message


def setup_logging(debug_mode: bool = False, log_file: str = "rainingkeys.log") -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        debug_mode: If True, sets level to DEBUG. Otherwise INFO.
        log_file: Path to log file for persistent logging.

    Returns:
        Configured root logger instance.
    """
    logger = logging.getLogger("RainingKeys")

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Set log level based on debug mode
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logger.setLevel(log_level)

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler for persistent logs
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except (OSError, IOError) as e:
                logger.warning(f"Could not create log directory {log_dir}: {e}")
                # Continue without file logging

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except (IOError, OSError, PermissionError) as e:
        logger.warning(f"Could not create log file {log_file}: {e}")
        logger.warning("File logging disabled. Only console logging available.")

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__). If None, returns root logger.

    Returns:
        Logger instance for the specified module or root logger.
    """
    if name:
        return logging.getLogger(f"RainingKeys.{name}")
    return logging.getLogger("RainingKeys")
