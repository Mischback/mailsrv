"""Provide the actual validation logic."""

# Python imports
import copy
import logging

logger = logging.getLogger(__name__)


class ConfigValidatorWarning(Exception):
    """Indicate some configuration that might result in problems."""


class ConfigValidatorError(Exception):
    """Indicate some configuration that makes the service unusable."""


class PostfixAliasResolver:  # noqa: D101
    def __init__(self, postfix_aliases, postfix_mailboxes):
        self.src_aliases = postfix_aliases
        self.src_mailboxes = postfix_mailboxes

        logger.debug(self.src_aliases)
        logger.debug(self.src_mailboxes)

        self._work_aliases = copy.deepcopy(self.src_aliases)
        self.result = dict()
        self._iteration = 0

    def resolve(self, max_iterations=5):  # noqa: D102
        self._iteration = self._iteration + 1
        logger.debug("max_iterations = {}".format(max_iterations))
        logger.debug("this iteration = {}".format(self._iteration))

        tmp_aliases = copy.deepcopy(self._work_aliases)
        for alias in tmp_aliases:
            logger.debug("{}: {}".format(alias, tmp_aliases[alias]))

            targets_are_mailboxes = True
            for target in tmp_aliases[alias]:
                logger.debug("Checking alias target '{}'".format(target))
                if target not in self.src_mailboxes:
                    logger.debug("{} not a mailbox".format(target))
                    targets_are_mailboxes = False
                if target in self.result.keys():
                    logger.debug("{} present in result!".format(target))
                    logger.debug("BEFORE resolving: {}".format(tmp_aliases[alias]))
                    tmp_aliases[alias].remove(target)
                    tmp_aliases[alias] = tmp_aliases[alias] + self.result[target]
                    logger.debug("AFTER resolving: {}".format(tmp_aliases[alias]))
                    self._work_aliases[alias] = tmp_aliases[alias]

            if targets_are_mailboxes:
                self.result[alias] = tmp_aliases[alias]
                del self._work_aliases[alias]

        if self._work_aliases:
            if self._iteration == max_iterations:
                logger.error("Unresolved aliases: {}".format(self._work_aliases))
                logger.verbose("Resolved aliases: {}".format(self.result))
                raise Exception("Could not complete resolving of aliases")

            self.resolve(max_iterations=max_iterations)


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
