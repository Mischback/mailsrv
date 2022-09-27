"""Provide parsers for the different configuration files."""

# Python imports
import collections
import logging
from typing import Any, Optional, Tuple

# local imports
from .exceptions import MailsrvParserException, MailsrvResolverException
from .fs import GenericFileReader

# get a module-level logger
logger = logging.getLogger(__name__)


class PasswdFileParser(GenericFileReader):
    """Parse ``passwd``-file-like configuration files."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(*args, **kwargs)  # type: ignore [arg-type]

        self._user_db = dict()
        for line in self._raw_lines:
            elems = line.split(":")

            self._user_db[elems[0]] = {
                "password": elems[1],
                "uid": elems[2],
                "gid": elems[3],
                "home": elems[5],
                "extra": elems[7],
            }

    def get_usernames(self) -> list[str]:
        """Return the usernames.

        In a *passwd*-like file, the usernames are the very first column in
        every line.

        Returns
        -------
        list
            A ``list`` of ``str``, representing the usernames in the
           *passwd-like* file.

        Notes
        -----
        The usernames are in fact the very first column in the file.
        """
        return list(self._user_db.keys())

    def get_password(self, username: str) -> str:
        """Return the password for a given user.

        Parameters
        ----------
        username : str
            Specify the user to get the password for.

        Returns
        -------
        str
            The password, provided as ``str``.
        """
        try:
            return self._user_db[username]["password"]
        except KeyError:
            logger.error("No entry for '%s' in userdb", username)
            raise MailsrvParserException("Missing entry in userdb")


class KeyParser(GenericFileReader):
    """Parse plain-text configuration files that only provide keys.

    The actual files do contain *keys* and another string, like
    ``KEY[BLANK]something``, where only the *keys* are relevant.
    """

    def get_values(self) -> list[str]:
        """Get the actual values.

        Returns
        -------
        list
            A ``list`` of ``str``, containing the *left-hand-side* of each
            line in the file.

        Notes
        -----
        The class is intended to discard the *right-hand-side* of the lines,
        so there are no other methods provided.

        If the *right-hand-side* should be considered, see ``KeyValueParser``.
        """
        return [line[: line.index(" ")] for line in self._raw_lines]


class KeyValueParser(GenericFileReader):
    """Parse plain-text configuration files that have keys and values.

    Everything until the first whitespace character is considered the *key*
    and everything after that whitespace the *value* or a list of *values*.

    ``KEY[BLANK]value_1 value_2``
    """

    def get_values(self) -> dict[str, list[str]]:
        """Return the actual key / value combinations as dictionary.

        Returns
        -------
        dict
            A ``dict``, using the *left-hand-side* as ``key`` and provide the
            *right-hand-side* as ``list`` of ``str``.
        """
        result = dict()
        for line in self._raw_lines:
            key = line[: line.index(" ")]
            value = line[line.index(" ") :].strip().split(" ")
            result[key] = value

        return result


class PostfixAliasResolver:
    """Resolve Postfix's virtual alias configuration.

    Parameters
    ----------
    postfix_mailboxes : ``list``
        A ``list`` of ``str`` containing the actual mailboxes.
    postfix_aliases : ``dict``
        A ``dict`` containing the acutal alias configuration.
    postfix_domains : ``list``
        A ``list`` of ``str`` containing the virtual domains.

    Notes
    -----
    The ``resolve()`` method has to be called explicitly.
    """

    class ResolverError(MailsrvResolverException):
        """Indicate a non-recoverable error during resolving."""

    def __init__(
        self,
        postfix_mailboxes: list[str],
        postfix_aliases: dict[str, list[str]],
        postfix_domains: list[str],
    ) -> None:

        self.ref_mailboxes = postfix_mailboxes
        self.ref_domains = postfix_domains

        self._work_aliases = postfix_aliases

        self.resolved: dict[str, list[str]] = dict()
        self.external: dict[str, set[str]] = collections.defaultdict(set)
        self.unresolved: dict[str, set[str]] = collections.defaultdict(set)

        self._resolve_external = 0
        self._resolve_failed = 0

    def resolve(
        self,
    ) -> Tuple[
        dict[str, list[str]],
        Optional[dict[str, set[str]]],
        Optional[dict[str, set[str]]],
    ]:
        """Resolve the alias configuration and return the result.

        Returns
        -------
        dict
            The ``dict`` contains the aliases (as keys) with lists of ``str``
            for its targets. These *targets* do not longer contain any other
            aliases.
        dict, Optional
            The ``dict`` contains aliases that could not be resolved.
        dict, Optional
            The ``dict`` contains aliases that resolve to external addresses.
        """
        ret_failed = None
        ret_external = None

        self.resolved = self._resolve()

        if self._resolve_external > 0:
            ret_external = self.external

        if self._resolve_failed > 0:
            ret_failed = self.unresolved

        return self.resolved, ret_failed, ret_external

    def _resolve(self) -> dict[str, list[str]]:
        """Resolve all aliases.

        Basically just loop through all configured aliases.

        Returns
        -------
        dict
            The ``dict`` contains the aliases (as keys) with lists of ``str``
            for its targets. These *targets* do not longer contain any other
            aliases.
        """
        for alias in self._work_aliases:
            logger.debug("[processing] %s: %r", alias, self._work_aliases[alias])
            self._work_aliases[alias] = self._resolve_alias(
                alias, self._work_aliases[alias]
            )

        return self._work_aliases

    def _resolve_alias(self, alias: str, targets: list[str]) -> list[str]:
        """Resolve a single alias.

        This method performs the actual resolving of a single line in the
        alias configuration. It does work recursively, if required. The method
        identifies *internal mailboxes* and *external addresses* and does
        provide them in the results.

        *Unresolvable* aliases are tracked aswell.

        Parameters
        ----------
        alias : str
            The actual alias address.
        targets: list
            A ``list`` of ``str``, representing the target addresses.

        Returns
        -------
        list
            A ``list`` of ``str``, containing only *resolved* targets. This
            means either internal *mailboxes* or *external addresses*. The
            list does not contain any other *aliases*.

        Raises
        ------
        self.ResolverError
            If an alias is included in its own list of targets, this is an
            unresolvable cirle and indicated by this error.

        Notes
        -----
        Beside the actual return value, the function adds *external addresses*
        to ``self.external`` and *unresolvable aliases* to ``self.unresolved``.
        These are returned by ``resolve()``, if not empty.
        """
        result: list[str] = list()

        for target in targets:
            logger.debug("[checking] %s", target)

            if target == alias:
                raise self.ResolverError(
                    "Alias '{}' included in targets; unresolvable".format(alias)
                )

            if target in self.ref_mailboxes:
                logger.debug("[ok] '%s' is a valid mailbox", target)
                result.append(target)
                continue

            if target[target.index("@") + 1 :] not in self.ref_domains:
                logger.debug("[ok'ish] '%s' is an external address", target)
                self.external[alias].add(target)
                self._resolve_external += 1
                result.append(target)
                continue

            # at this point ``target`` is another alias
            try:
                result = result + self._resolve_alias(
                    target, self._work_aliases[target]
                )
            except KeyError:
                self.unresolved[alias].add(target)
                self._resolve_failed += 1
                logger.debug("[warning] '%s' is not resolvable", target)

        return result
