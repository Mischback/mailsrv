"""Provide parsers for the different configuration files."""

# local imports
from .fs import GenericFileReader


class PasswdFileParser(GenericFileReader):
    """Parse ``passwd``-file-like configuration files."""

    def get_usernames(self) -> list[str]:
        """Return the usernames.

        In a *passwd*-like file, the usernames are the very first column in
        every line.
        """
        # The Pythonic-condensed version of "the very first occurence of ":"
        # in a line and get everything until that occurrence; repeat for
        # every line"
        return [line[: line.index(":")] for line in self._raw_lines]


class KeyParser(GenericFileReader):
    """Parse plain-text configuration files that only provide keys.

    The actual files do contain *keys* and another string, like
    ``KEY[BLANK]something``, where only the *keys* are relevant.
    """

    def get_values(self) -> list[str]:
        """Get the actual values."""
        return [line[: line.index(" ")] for line in self._raw_lines]


class KeyValueParser(GenericFileReader):
    """Parse plain-text configuration files that have keys and values.

    Everything until the first whitespace character is considered the *key*
    and everything after that whitespace the *value* or a list of *values*.

    ``KEY[BLANK]value_1 value_2``
    """

    def get_values(self) -> dict[str, list[str]]:
        """Return the actual key / value combinations as dictionary."""
        result = dict()
        for line in self._raw_lines:
            key = line[: line.index(" ")]
            value = line[line.index(" ") :].strip().split(" ")
            result[key] = value

        return result
