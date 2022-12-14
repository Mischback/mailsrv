# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""Provide test suite-specific exceptions."""

# local imports
from ..common.exceptions import MailsrvBaseException


class MailsrvTestException(MailsrvBaseException):
    """Base class for all test suite-related exceptions."""
