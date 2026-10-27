"""
NAME: logging_config.py
PURPOSE: Configure terminal and rotating file logs.
DATE: 09-10-2026
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import BASE_DIR

# Store logs in a dedicated in the project root.
# Path() lets us build file paths cleanly across directories.
LOG_DIR = Path(BASE_DIR) / "logs"
# This is the main log file. Older logs will be rotated into backup files.
LOG_FILE = LOG_DIR / "lead-form-backend.log"

def configure_logging():
    # Create the logs directory if it does not exist.
    # parents=True creates missing parent directories too.
    # exist_ok=True prevents an error if the directory already exists.
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # The root logger is the top-level logger in Python's logging system.
    # The app.main logger can pass its messages up to this logger.
    root_logger = logging.getLogger()
    # Record INFO messages and anything more severe:
    # WARNING, ERROR and CRITICALA.
    root_logger.setLevel(logging.INFO)

    # Define the format shared by terminal and file log messages.
    # %(asctime)s = data and time
    # %(levelname)s = severity, such as INFO or ERROR
    # %(name)s = logger name, such as app.main
    # %(message)s = the message we supplied to logger.info(), etc.
    formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
            )

    # Resolve the log file to an absolute path for comparison.
    # This helps us check whether this handler is already installed.
    log_path = str(LOG_FILE.resolve())
    # Avoid attaching the same file handler more than once.
    # This matters if the logging setup function is called again.
    if not any(
            isinstance(handler, RotatingFileHandler)
            and handler.baseFilename == log_path
            for handler in root_logger.handlers
            ):
            # Write logs to a file and rotate it when it reaches about 1MB
            # maxBytes = max size of the current log file.
            # backupCount = number of older rotated files to retain
            # encoding="utf-8" supports a wide range of chars
            file_handler = RotatingFileHandler(
                    LOG_FILE,
                    maxBytes=1_000_000,
                    backupCount=5,
                    encoding="utf-8",
                    )
            # Apply the timestamp, severity, logger name and message format.
            file_handler.setFormatter(formatter)
            # Connect the file handler to the root logger.
            # Log messages can now be written to the file.
            root_logger.addHandler(file_handler)

    # Keep a console handler so application logs also appear in the terminal
    # Give it a name so we can check for it and avoid duplicates.
    if not any(
            handler.get_name() == "lead-form-console"
            for handler in root_logger.handlers
            ):
            console_handler = logging.StreamHandler()
            console_handler.set_name("lead-form-console")
            console_handler.setFormatter(formatter)
            # Connect the console handler to the root logger.
            root_logger.addHandler(console_handler)
