"""Provide the actual check functions to validate the configuration."""

# Python imports
import logging
from typing import TypeVar

# local imports
from .messages import TValidationMessage, ValidationError

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
    """All Postfix mailboxes **must have** a matching entry in Dovecot's user database.

    Parameters
    ----------
    postfix_mailboxes : list
        A ``list`` of ``str``, representing the actual mailboxes of Postfix.
    dovecot_accounts : list
        A ``list`` of ``str``, representing the available user accounts for
        Dovecot.

    Returns
    -------
    list
        A list of ``ValidationError`` instances. One instance per missing
        mailbox.

    Notes
    -----
    This documentation mentions the actual expected input parameter types and
    output types, while the source code uses a slight abstraction while working
    with ``mypy`` for static type checking.
    """
    logger.debug("check_mailbox_has_account()")

    findings: list[TValidationMessage] = list()

    for box in postfix_mailboxes:
        if box not in dovecot_accounts:
            logger.debug("Mailbox '%s' not in dovecot_accounts", box)
            findings.append(
                ValidationError(
                    "Mailbox {} has no matching account".format(box),
                    id="e001",
                    hint="Every Postfix *mailbox* requires a matching entry in Dovecot's *userdb*",
                )
            )

    return findings
