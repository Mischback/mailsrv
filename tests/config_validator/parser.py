"""Provide parsers for the different configuration files."""

# Python imports
import logging

logger = logging.getLogger(__name__)


class ConfigValidatorOperationalError(Exception):
    """Indicate operational error."""


class GenericFileReader:
    """Reads a plain-text config file and strips comment lines."""

    def __init__(self, file_path):

        try:
            with open(file_path, "r") as f:
                self._raw_lines = [
                    line.strip() for line in f.readlines() if line[0] != "#"
                ]
        except OSError as e:
            logger.error("Error while accessing {}".format(file_path))
            logger.debug(e, exc_info=1)
            raise ConfigValidatorOperationalError(
                "Error while accessing {}".format(file_path)
            )


class DovecotUserdbPasswdfileParser(GenericFileReader):
    """Parse *passwd*-file-based user databases."""

    def get_usernames(self):
        """Return the usernames.

        In a *passwd*-like file, the usernames are the very first column in
        every line.

        This seems like magic, but is in fact a very condensed version of
        "looking for the first occurrence of ``':'`` in a line, get the
        substring until that occurrence, repeat for every line".
        """
        return [line[: line.index(":")] for line in self._raw_lines]


class PostfixOnlyKeysParser(GenericFileReader):
    """Parse Postfix's database files, that only depend on the keys."""

    def get_keys(self):
        """Return the left-hand side of the entries."""
        return [line[: line.index(" ")] for line in self._raw_lines]


class PostfixKeyValueParser(GenericFileReader):
    """Parse Postfix's database files, that actually have meaninful values."""

    def get_key_value(self):
        """Return the actual key / value combinations as dictionary."""
        result = dict()
        for line in self._raw_lines:
            key = line[: line.index(" ")]
            value = line[line.index(" ") :].strip().split(" ")
            result[key] = value

        return result
