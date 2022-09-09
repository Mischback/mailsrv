"""Provide validation-specific exceptions."""

# local imports
from ..common.exceptions import MailsrvBaseException


class MailsrvValidationException(MailsrvBaseException):
    """Base class for all validation-related exception."""


class MailsrvValidationOperationalError(MailsrvValidationException):
    """Indicate non-recoverable operational errors."""
