# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""Provide file-system access abstraction."""

# Python imports
import logging

# local imports
from .exceptions import MailsrvIOException

# get a module-level logger
logger = logging.getLogger(__name__)


class GenericFileReader:
    """Read a plain-text config file and strip comment lines.

    The file is actually opened and parsed (at least the first pass of
    parsing) during object creation.

    Parameters
    ----------
    file_path : str
        The path to the file, either absolute or relative to the current
        working directory.

    Raises
    ------
    MailsrvIOException
        Any ``OSError`` will be catched and converted to an
        ``MailsrvIOException``.

    Notes
    -----
    The effective content of the file (as specified by ``file_path``) is
    available in ``self._raw_lines``. As the name indicates, the lines are
    stored in a ``list`` of ``str``.

    The assumed configuration files do in fact work *linewise*.
    """

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
            raise MailsrvIOException("Error while accessing '{}'".format(file_path))
