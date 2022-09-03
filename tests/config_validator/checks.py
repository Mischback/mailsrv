"""Provide the actual validation logic."""

# Python imports
import logging

logger = logging.getLogger(__name__)


class ConfigValidatorWarning(Exception):
    """Indicate some configuration that might result in problems."""


class ConfigValidatorError(Exception):
    """Indicate some configuration that makes the service unusable."""


def mailbox_has_account(postfix_mailboxes, dovecot_usernames):
    """All mailboxes must have an associated Dovecot user.

    Mailboxes without a corresponding entry in Dovecot's ``userdb`` can not
    be accessed, even the mails can not be delivered.
    """
    logger.debug("Check: mailbox_has_account()")
    not_found = set()
    for box in postfix_mailboxes:
        if box not in dovecot_usernames:
            not_found.add(box)

    if not_found:
        raise ConfigValidatorError("{} not found in Dovecot's userdb".format(not_found))

    logger.verbose("[OK] All mailboxes have a corresponding Dovecot user")


def address_matches_domains(postfix_addresses, postfix_domains):
    """All addresses' domain parts must have an entry in the virtual domains."""
    logger.debug("Check: address_matches_domains()")

    logger.debug(postfix_addresses)
    logger.debug(postfix_domains)
    for address in postfix_addresses:
        if address[address.index("@") + 1 :] not in postfix_domains:
            raise ConfigValidatorError(
                "{} not found in Postfix's virtual domains".format(address)
            )

    logger.verbose("[OK] All addresses have a corresponding (virtual) domain")
