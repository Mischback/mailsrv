"""Provide the actual check functions to validate the configuration."""

# Python imports
import logging
from typing import Optional, Tuple, Type, TypeVar  # noqa: F401

# local imports
from .messages import TValidationMessage, ValidationError  # noqa: F401

# Typing stuff

# FIXME: The arguments to the check functions may have different types, but
#        list[int] is not included.
#        As TypeVar requires more than one parameter, list[int] is added as a
#        placeholder and will be replaced.
TCheckArg = TypeVar("TCheckArg", list[str], list[int])


# get a module-level logger
logger = logging.getLogger(__name__)


def check_mailbox_has_account(
    postfix_mailboxes: TCheckArg, dovecot_accounts: TCheckArg
) -> list[TValidationMessage]:
    """Temporary fix."""
    logger.debug("check_mailbox_has_account()")

    findings: list[TValidationMessage] = list()

    for box in postfix_mailboxes:
        if box not in dovecot_accounts:
            logger.warning(box)
            findings.append(
                ValidationError(
                    "Mailbox {} has no matching account".format(box),
                    id="e001",
                    hint="Every Postfix *mailbox* requires a matching entry in Dovecot's *userdb*",
                )
            )

    return findings
