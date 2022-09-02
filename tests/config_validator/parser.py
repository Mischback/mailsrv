"""Provide parsers for the different configuration files."""


class DovecotUserdbPasswdfileParser:
    """Parses *passwd*-file-based user databases."""

    def __init__(self, file_path):

        with open(file_path, "r") as f:
            self._raw_lines = [line.strip() for line in f.readlines()]

    def get_usernames(self):
        """Return the usernames.

        In a *passwd*-like file, the usernames are the very first column in
        every line.

        This seems like magic, but is in fact a very condensed version of
        "looking for the first occurrence of ``':'`` in a line, get the
        substring until that occurrence, repeat for every line".
        """
        return [line[: line.index(":")] for line in self._raw_lines]


class PostfixOnlyKeysParser:
    """Parses Postfix's virtual_mailbox files, provided as text files."""

    def __init__(self, file_path):
        with open(file_path, "r") as f:
            self._raw_lines = [line.strip() for line in f.readlines()]

    def get_keys(self):
        """Return the mailboxes."""
        return [line[: line.index(" ")] for line in self._raw_lines]
