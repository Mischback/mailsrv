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
                "{} without corresponding entry in Postfix's virtual domains".format(
                    address
                )
            )

    logger.verbose("[OK] All addresses have a corresponding (virtual) domain")


def external_alias_targets(postfix_aliases, postfix_domains):
    """Alias targets *should not* be external addresses."""
    # This check might be run WITHOUT actually resolving the alias file!

    logger.debug("Check: external_alias_targets()")

    postfix_alias_targets = [
        item for sublist in postfix_aliases.values() for item in sublist
    ]
    logger.debug("Alias targets: {}".format(postfix_alias_targets))

    for target in postfix_alias_targets:
        if target[target.index("@") + 1 :] not in postfix_domains:
            logger.verbose("{} is an external address!".format(target))
            logger.verbose(
                "This might pose a severe risk to make the server be considered a spam relay."
            )
            raise ConfigValidatorWarning("{} is an external address".format(target))

    logger.verbose("[OK] No alias pointing to an external domain")
