"""Provide a package-specific extension of Python's ``logging`` module."""

# Python imports
import logging
from typing import Any, Optional

# get a module-level logger
logger = logging.getLogger(__name__)


LOGGING_DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "console_output": {
            "format": "[%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "console_output",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "SUMMARY",
            "propagate": True,
        },
        "mailsrv_aux": {
            "propagate": True,
        },
    },
}


def add_level(level_name: str, level_number: int) -> None:
    """Add a new logging level to Python's ``logging`` module."""
    # Make the additions as compatible as possible with the original module
    # code.
    # Actual "level names" are upper-case, "method names" are lower-case.
    _level_name = level_name.upper()
    _method_name = level_name.lower()

    # Lock Python's logging module while we're messing with its internal
    # functions
    logging._acquireLock()  # type: ignore [attr-defined]

    try:
        # If ``level_name`` is already taken, don't take further actions.
        if hasattr(logging, _level_name):
            raise AttributeError("{} already defined".format(_level_name))
        if hasattr(logging, _method_name):
            raise AttributeError("{} already defined".format(_method_name))
        if hasattr(logging.getLoggerClass(), _method_name):
            raise AttributeError(
                "{} already defined in logger class".format(_method_name)
            )

        # Provide our specific logging method implementation
        # Basically this is a generic version of the pre-defined methods in
        # Python's logging module, see ``logging.Logger.debug()``.
        def generic_log_class(
            self: Any, msg: str, *args: Optional[Any], **kwargs: Optional[Any]
        ) -> None:
            """Specific log method to be added to the LoggerClass."""
            if self.isEnabledFor(level_number):
                self._log(level_number, msg, args, **kwargs)

        def generic_log_module(
            msg: str, *args: Optional[Any], **kwargs: Optional[Any]
        ) -> None:
            """Specific log method to be added to the ``logging`` module."""
            logging.log(level_number, msg, *args, **kwargs)  # type: ignore [arg-type]

        # Actually add the custom level to the ``logging`` module and its
        # LoggerClass.
        logging.addLevelName(level_number, _level_name)
        setattr(logging, _level_name, level_number)
        setattr(logging.getLoggerClass(), _method_name, generic_log_class)
        setattr(logging, _method_name, generic_log_module)
    except AttributeError:
        logger.debug("Name '%s' already defined!", level_name)
    finally:
        # Release the lock to Python's logging module
        logging._releaseLock()  # type: ignore [attr-defined]
