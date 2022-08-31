"""Provide a package-specific extension of Python's ``logging`` module."""

# Python imports
import logging
import warnings


def add_level(level_name, level_number):
    """Add a new logging level to Python's ``logging`` module."""
    # Make the additions as compatible as possible with the original module
    # code.
    # Actual "level names" are upper-case, "method names" are lower-case.
    _level_name = level_name.upper()
    _method_name = level_name.lower()

    # Lock Python's logging module while we're messing with its internal
    # functions
    logging._acquireLock()

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
        def generic_log_class(self, msg, *args, **kwargs):
            """Specific log method to be added to the LoggerClass."""
            if self.isEnabledFor(level_number):
                self._log(level_number, msg, args, **kwargs)

        def generic_log_module(msg, *args, **kwargs):
            """Specific log method to be added to the ``logging`` module."""
            logging.log(level_number, msg, *args, **kwargs)

        # Actually add the custom level to the ``logging`` module and its
        # LoggerClass.
        logging.addLevelName(level_number, _level_name)
        setattr(logging, _level_name, level_number)
        setattr(logging.getLoggerClass(), _method_name, generic_log_class)
        setattr(logging, _method_name, generic_log_module)
    except AttributeError:
        warnings.warn("Name {} already defined!".format(level_name))
    finally:
        # Release the lock to Python's logging module
        logging._releaseLock()
