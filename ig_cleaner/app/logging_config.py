import logging
import structlog
import sys
from .config import LOG_LEVEL, LOG_DIR
import os

def setup_logging():
    """
    Configures structured logging for the entire application.
    """
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(message)s",
        stream=sys.stdout,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name, account_username=None):
    """

    Gets a logger, and if an account username is provided,
    configures a file handler to log to a specific file for that account.
    """
    logger = structlog.get_logger(name)

    if account_username:
        log_path = os.path.join(LOG_DIR, account_username)
        os.makedirs(log_path, exist_ok=True)

        file_handler = logging.FileHandler(os.path.join(log_path, "activity.log"))
        # Using a JSON formatter for file logs
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        # To avoid duplicate logs, we get the underlying standard logger and add the handler
        std_logger = logging.getLogger(name)
        std_logger.addHandler(file_handler)

    return logger

# Example usage
if __name__ == "__main__":
    setup_logging()
    log = get_logger("test_logger", account_username="test_account")
    log.info("This is an info message.", user="test")
    log.warning("This is a warning.")

    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("An error occurred.")
