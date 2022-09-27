"""Provide data classes."""

from __future__ import annotations

# Python imports
from collections import defaultdict
from functools import total_ordering
from typing import Any, Optional


@total_ordering
class SmtpTestProtocol:
    """Data class to store the results of a SMTP-related test suite."""

    def __init__(
        self,
        sent: Optional[list[str]] = None,
        rejected: Optional[list[str]] = None,
        accepted: Optional[dict[str, list[str]]] = None,
    ) -> None:
        if sent is None:
            self._sent: list[str] = []
        else:
            self._sent = sent

        if rejected is None:
            self._rejected: list[str] = []
        else:
            self._rejected = rejected

        if accepted is None:
            self._accepted: dict[str, list[str]] = defaultdict(list)
        else:
            self._accepted = accepted

    def get_mail_count(self) -> int:
        """Return the number of sent mails during a run."""
        return len(self._sent)

    def mail_accepted(self, recipient: str, subject: str) -> None:
        """Add the subject of a mail to the dict of accepted mails."""
        self._accepted[recipient].append(subject)

    def mail_rejected(self, subject: str) -> None:
        """Add the subject of a mail to the list of rejected mails."""
        self._rejected.append(subject)

    def mail_sent(self, subject: str) -> None:
        """Add the subject of a mail to the list of sent mails."""
        self._sent.append(subject)

    def __add__(self, other: Any) -> SmtpTestProtocol:
        """**Add** is implemented as *merging* two instances."""
        if not isinstance(other, SmtpTestProtocol):
            return NotImplemented

        # FIXME: What if ``other`` contains keys that are not present in self?
        return SmtpTestProtocol(
            sent=self._sent + other._sent,
            rejected=self._rejected + other._rejected,
            accepted=defaultdict(
                list,
                {k: self._accepted[k] + other._accepted[k] for k in self._accepted},
            ),
        )

    def __bool__(self) -> bool:  # noqa: D105
        return self.get_mail_count() > 0

    def __eq__(self, other: Any) -> bool:  # noqa: D105
        # see https://stackoverflow.com/a/2909119
        # see https://stackoverflow.com/a/8796908
        # see https://stackoverflow.com/a/44575926
        if isinstance(other, SmtpTestProtocol):
            return self.__key() == other.__key()
        return NotImplemented

    def __hash__(self) -> int:  # noqa: D105
        # see https://stackoverflow.com/a/2909119
        return hash(self.__key)

    def __lt__(self, other: Any) -> bool:  # noqa: D105
        # see https://stackoverflow.com/a/44575926
        return NotImplemented

    def __repr__(self) -> str:  # noqa: D105
        return "<{classname}: sent={sent!r}, rejected={rejected!r}, accepted={accepted!r}>".format(
            classname=self.__class__.__name__,
            sent=self._sent,
            rejected=self._rejected,
            accepted=self._accepted,
        )

    def __str__(self) -> str:  # noqa: D105
        return "Mails sent: {} ({} rejected)".format(
            len(self._sent), len(self._rejected)
        )

    def __key(self) -> tuple:
        # see https://stackoverflow.com/a/2909119
        return (self._sent, self._rejected, self._accepted)
