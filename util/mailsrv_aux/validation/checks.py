"""Provide the actual check functions to validate the configuration."""

# Python imports
import logging

# local imports
from .messages import TValidationMessage, ValidationError  # noqa: F401

# get a module-level logger
logger = logging.getLogger(__name__)


def check_mailbox_has_account(
    postfix_mailboxes: list[str], dovecot_accounts: list[str]
) -> list[TValidationMessage]:
    """Temporary fix."""
    return []
