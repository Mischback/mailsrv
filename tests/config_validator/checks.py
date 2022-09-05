"""Provide the actual validation logic."""

# Python imports
import collections
import copy
import logging

logger = logging.getLogger(__name__)


class ConfigValidatorWarning(Exception):
    """Indicate some configuration that might result in problems."""

    def __init__(self, *args, more_context=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.more_context = more_context


class ConfigValidatorError(Exception):
    """Indicate some configuration that makes the service unusable."""

    def __init__(self, *args, more_context=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.more_context = more_context


class PostfixAliasResolver:
    """Provide alias resolving as an actual check.

    The implementation will fail, if there are actually malformed aliases.

    It will raise warnings about unresolvable and external alias targets.
    """

    class CouldNotResolve(Exception):
        """Internal Exception to indicate, that resolving is stopped."""

    def __init__(self, postfix_aliases, postfix_mailboxes, postfix_domains):
        self.src_aliases = postfix_aliases
        self.ref_mailboxes = postfix_mailboxes
        self.ref_domains = postfix_domains

        logger.debug(self.src_aliases)
        logger.debug(self.ref_mailboxes)
        logger.debug(self.ref_domains)

        self._work_aliases = copy.deepcopy(self.src_aliases)
        self.resolved = dict()
        self.external = collections.defaultdict(set)
        self.unresolved = collections.defaultdict(set)
        self._iteration = 0
        self._resolve_external = 0
        self._resolve_failed = 0

    def resolve(self):
        """Resolve the alias configuration.

        The method returns the resolved configuration, mapping all aliases to
        a local mailbox or an external address.
        *Unresolvable* aliases are still provided, with an empty target list.

        The method returns the status of resolving by including instances of
        ``ConfigValidatorWarning`` for unresolvable and external addresses.
        """
        self.resolved = self._resolve()

        if self._resolve_external > 0:
            # TODO: provide the list of external addresses as context to the exception object
            ret_external = ConfigValidatorWarning(
                "External addresses detected!", more_context=self.external
            )
        else:
            ret_external = None

        if self._resolve_failed > 0:
            # TODO: provide the list of failed resolves as context to the exception object
            ret_failed = ConfigValidatorWarning(
                "Resolve failed!", more_context=self.unresolved
            )
        else:
            ret_failed = None

        return ret_failed, ret_external, self.resolved

    def _resolve(self):

        for alias in self._work_aliases:
            logger.debug("[PROCESSING] {}: {}".format(alias, self._work_aliases[alias]))
            self._work_aliases[alias] = self._resolve_alias(
                alias, self._work_aliases[alias]
            )

        return self._work_aliases

    def _resolve_alias(self, alias, targets):
        result = list()

        for target in targets:
            logger.debug("[CHECKING] {}".format(target))
            if target == alias:
                raise ConfigValidatorError(
                    "Alias included in targets; unresolvable cirle"
                )

            if target in self.ref_mailboxes:
                logger.debug("[OK] {} is a valid mailbox!".format(target))
                result.append(target)
                continue

            if target[target.index("@") + 1 :] not in self.ref_domains:
                logger.debug("[OK'ish] {} is an external address!".format(target))
                self.external[alias].add(target)
                self._resolve_external += 1
                result.append(target)
                continue

            # at this point, ``target`` is another alias
            try:
                result = result + self._resolve_alias(
                    target, self._work_aliases[target]
                )
            except KeyError:
                self.unresolved[alias].add(target)
                self._resolve_failed += 1
                logger.warning("WARNING: {} is not resolvable!".format(target))

        return result


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
    """Alias targets *should not* be external addresses.

    This function is made obsolete by ``resolve_alias_configuration()``, but
    kept for reference or when actual parsing of the alias configuration is
    not desired.
    """
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


def resolve_alias_configuration(postfix_aliases, postfix_mailboxes, postfix_domains):
    """Check and resolve the alias configuration.

    Raise an error, if an alias can not be resolved, raise a warning if there
    are external addresses detected.

    Makes ``external_alias_targets()`` obsolete.
    """
    logger.debug("Check: resolve_alias_configuration()")

    resolver = PostfixAliasResolver(postfix_aliases, postfix_mailboxes, postfix_domains)

    tmp_fail, tmp_ext, resolve = resolver.resolve()

    if tmp_fail is not None:
        logger.info("Some aliases could not be resolved!")
        logger.info(dict(tmp_fail.more_context))
        raise ConfigValidatorError(tmp_fail)

    if tmp_ext is not None:
        logger.info("Some aliases resolved to external addresses!")
        logger.verbose(
            "This might pose a severe rist to make the server be considered a spam relay."
        )
        logger.info(dict(tmp_fail.more_context))
        raise ConfigValidatorWarning(tmp_ext)

    logger.verbose("[OK] Alias configuration valid!")
    return resolve


def address_can_send(postfix_addresses, postfix_senders):
    """Addresses *should* be included in Postfix's sender login map."""
    logger.debug("Check: address_can_send()")

    sender_lhs = list(postfix_senders.keys())
    na_addresses = list()

    for address in postfix_addresses:
        if address not in sender_lhs:
            logger.debug("{} not in sender map".format(address))
            na_addresses.append(address)

    if na_addresses:
        raise ConfigValidatorWarning("Not all addresses can send emails!")

    logger.verbose("[OK] All addresses can send mails")
