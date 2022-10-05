# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""Provide exceptions.

This module includes the specific exceptions for the ``common`` sub- package
and general exceptions for the ``mailsrv_aux`` package.
"""


class MailsrvBaseException(Exception):
    """Base exception for the overall package."""


class MailsrvIOException(MailsrvBaseException):
    """Indicate I/O-related errors."""


class MailsrvParserException(MailsrvBaseException):
    """Indicate an error during parsing."""


class MailsrvResolverException(MailsrvBaseException):
    """Base class for exceptions in ``PostfixAliasResolver``."""
