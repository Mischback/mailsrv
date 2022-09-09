"""Provide file-system access abstraction."""

# Python imports
import logging

# local imports
from .exceptions import MailsrvIOException

# get a module-level logger
logger = logging.getLogger(__name__)


class GenericFileReader:
    """Read a plain-text config file and strip comment lines."""

    def __init__(self, file_path: str) -> None:
        try:
            with open(file_path, "r") as f:
                self._raw_lines = [
                    line.strip()
                    for line in f.readlines()
                    if line.strip() and line[0] != "#"
                ]
        except OSError as e:
            logger.error("Error while acessing '%s'", file_path)
            logger.debug(e, exc_info=True)  # noqa: G200
            raise MailsrvIOException("Error while accessing {}".format(file_path))
