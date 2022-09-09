"""Provide the actual check functions to validate the configuration."""

# Python imports
import logging
from typing import TypeVar

# local imports
from .messages import TValidationMessage, ValidationError, ValidationWarning

# Typing stuff

# FIXME: The arguments to the check functions may have different types, but
#        list[int] is not included.
#        As TypeVar requires more than one parameter, list[int] is added as a
#        placeholder and will be replaced.
TCheckArg = TypeVar("TCheckArg", list[str], list[str])


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


def check_addresses_match_domains(
    postfix_addresses: TCheckArg, postfix_domains: TCheckArg
) -> list[TValidationMessage]:
    """All Postfix addresses **must have** a matching entry in Postfix's virtual domains.

    Parameters
    ----------
    postfix_addresses : list
        A ``list`` of ``str``, representing all addresses of the Postfix
        server.
    postfix_domains : list
        A ``list`` of ``str``, representing all virtual domains.

    Returns
    -------
    list
        A list of ``ValidationError`` instances.

    Notes
    -----
    This documentation mentions the actual expected input parameter types and
    output types, while the source code uses a slight abstraction while working
    with ``mypy`` for static type checking.
    """
    logger.debug("check_addresses_match_domains()")

    findings: list[TValidationMessage] = list()

    for address in postfix_addresses:
        if address[address.index("@") + 1 :] not in postfix_domains:
            logger.debug("Address '%s' not in postfix_domains", address)
            findings.append(
                ValidationError(
                    "Address {} not in virtual domains".format(address),
                    id="e002",
                    hint="The domain parts of the addresses require a matching entry in Postfix's virtual domains",
                )
            )

    return findings


def check_address_can_send(
    postfix_addresses: TCheckArg, postfix_senders: TCheckArg
) -> list[TValidationMessage]:
    """fooo."""
    logger.debug("check_address_can_send()")

    findings: list[TValidationMessage] = list()

    for address in postfix_addresses:
        if address not in postfix_senders:
            logger.debug("Address '%s' can not send", address)
            findings.append(
                ValidationWarning(
                    "Address {} not in sender_login_map".format(address),
                    id="w003",
                )
            )

    return findings
