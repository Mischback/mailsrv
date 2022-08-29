"""Test cases for POP3.

These tests are meant to test the pop3 functions of a server.
"""
# Python imports
import logging
import poplib

# app imports
from test_suite.exceptions import (
    MailsrvTestSuiteConfigurationException,
    MailsrvTestSuiteException,
)

# get a module-level logger
logger = logging.getLogger(__name__)


class Pop3TestCase:
    """Test the POP3 setup of a mail server.

    Basically verify that no login is possible without TLS and then check
    the number of mails in the mailbox. This should match the provided
    value of ``exptected_messages``.
    """

    class Pop3TestOperationalError(MailsrvTestSuiteException):
        """Raised for operational errors."""

    class Pop3TestError(MailsrvTestSuiteException):
        """Raised if a test fails."""

    def __init__(
        self, username=None, password=None, target_host=None, expected_messages=None
    ):
        if username is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'username'"
            )
        self.username = username
        logger.debug("username: {}".format(self.username))

        if password is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'password'"
            )
        self.password = password
        logger.debug("password: {}".format(self.password))

        if target_host is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'target_host'"
            )
        self.target_host = target_host
        logger.debug("target_host: {}".format(self.target_host))

        if expected_messages is None:
            raise MailsrvTestSuiteConfigurationException(
                "Missing parameter: 'expected_messages'"
            )
        self.expected_messages = expected_messages
        logger.debug("expected_messages: {}".format(self.expected_messages))

    def _connect(self):
        try:
            self.pop = poplib.POP3(self.target_host)
        except ConnectionRefusedError as e:
            logger.error("target ({}) refused the connection.".format(self.target_host))
            logger.debug(e, exc_info=1)
            raise self.Pop3TestOperationalError("Target refused the connection")

    def _auth(self):
        try:
            self.pop.user(self.username)
            self.pop.pass_(self.password)
        except poplib.error_proto as e:
            logger.error("Authentication failed: {}".format(e))
            raise self.Pop3TestOperationalError("Authentication failed")

    def _pre_auth(self):
        try:
            self.pop.user(self.username)
        except poplib.error_proto:
            logger.debug(
                "Test 01: [SUCCESS] Server disallows non-encrypted authentication!"
            )
            self.pop.stls()

    def _run(self):
        """Run the tests."""
        self._connect()

        self._pre_auth()

        try:
            self._auth()
            num_messages = len(self.pop.list()[1])
            logger.debug("Found messages: {}".format(num_messages))
        except poplib.error_proto as e:
            logger.error(e)

        if self.expected_messages != num_messages:
            raise self.Pop3TestError(
                "Expected number of messages not found (expected: {}, found: {})!".format(
                    self.expected_messages, num_messages
                )
            )
        logger.debug(
            "Test 02: [SUCCESS] Expected number of messages match retrieved messages"
        )

    def run(self):
        """Wrap around ``_run()``."""
        logger.info("Running POP3 tests...")
        self._run()
        logger.info("POP3 tests finished successfully...")


class Pop3sTestCase(Pop3TestCase):
    """Use the secure version of POP3."""

    def _pre_auth(self):
        pass

    def _connect(self):
        try:
            self.pop = poplib.POP3_SSL(self.target_host)
        except ConnectionRefusedError as e:
            logger.error("target ({}) refused the connection.".format(self.target_host))
            logger.debug(e, exc_info=1)
            raise self.Pop3TestOperationalError("Target refused the connection")

    def run(self):
        """Wrap around ``_run()``."""
        logger.info("Running POP3S tests...")
        self._run()
        logger.info("POP3S tests finished successfully...")
