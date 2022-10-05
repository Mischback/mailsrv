# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""Test suite using POP3.

This suite has two important functions: They verify the POP3 functions of the
server **and** verify, that all mails got delivered as expected.
"""

# Python imports
import logging
import poplib
from typing import Any, Optional

# local imports
from ..common.log import add_level
from .exceptions import MailsrvTestException

# get a module-level logger
logger = logging.getLogger(__name__)

# add VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


class Pop3GenericTestSuite:
    """Provide the POP3 protocol abstraction for actual test suites.

    Parameters
    ----------
    target_ip : str, optional
        The IP to connect to (default: 127.0.0.1).
    target_port : int, optional
        The port to use for the connection (default: 110, from ``poplib.POP3_PORT``).
    suite_name : str, optional
        The name of the test suite. Should be set to distinguish several suites
        (default: Generic POP3 Suite).
    username : str
        The username to use during POP3's login. This is marked as *optional*
        for Python's typing, but a default value of ``None`` is provided which
        results in a ``Pop3OperationalError`` if not overwritten.
    password : str
        The password to use during POP3's login. This is marked as *optional*
        for Python's typing, but a default value of ``None`` is provided which
        results in a ``Pop3OperationalError`` if not overwritten.
    """

    class Pop3GenericException(MailsrvTestException):
        """Base class for all exceptions of POP3 test suites."""

    class Pop3OperationalError(Pop3GenericException):
        """Indicate operational errors, most likely while using ``poplib``."""

    class Pop3TestSuiteError(Pop3GenericException):
        """Indicate an actual test failure."""

    def __init__(
        self,
        target_ip: str = "127.0.0.1",
        target_port: int = poplib.POP3_PORT,
        suite_name: str = "Generic POP3 Suite",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.target_ip = target_ip
        self.target_port = target_port
        self.suite_name = suite_name

        if username is None:
            logger.critical("Missing parameter: 'username'")
            raise self.Pop3OperationalError("Missing parameter: 'username'")
        self.username = username

        if password is None:
            logger.critical("Missing parameter: 'password'")
            raise self.Pop3OperationalError("Missing parameter: 'password'")
        self.password = password

    def _connect(self) -> None:
        try:
            self.pop = poplib.POP3(self.target_ip, port=self.target_port)
        except ConnectionRefusedError:
            logger.critical("Target (%s) refused the connection", self.target_ip)
            raise self.Pop3OperationalError("Connection refused")

        logger.info("Connection to target (%s) established", self.target_ip)

    def _auth(self) -> None:
        try:
            self.pop.user(self.username)
            self.pop.pass_(self.password)
        except poplib.error_proto as e:
            logger.critical("Authentication failed: %s", e)  # noqa: G200
            raise self.Pop3OperationalError("Authentication failed")

    def _pre_connect(self) -> None:
        pass

    def _pre_run(self) -> None:
        pass

    def _post_run(self) -> None:
        pass

    def _disconnect(self) -> None:
        try:
            # Fetching the mails should have no side effects. In particular, no
            # mails should be deleted. So, ``rset()`` is called before quitting.
            self.pop.rset()
        except poplib.error_proto:
            # rset() will fail without successful login
            pass
        self.pop.quit()
        logger.verbose("Connection to target (%s) terminated", self.target_ip)  # type: ignore [attr-defined]

    def _run_tests(self) -> None:
        raise NotImplementedError("Has to be implemented in real test suite")

    def run(self) -> None:
        """Run the test suite."""
        logger.summary("Running %s", self.suite_name)  # type: ignore [attr-defined]
        self._pre_connect()
        self._connect()
        self._pre_run()
        try:
            self._run_tests()
            self._post_run()
        finally:
            self._disconnect()

        logger.summary("%s finished successfully", self.suite_name)  # type: ignore [attr-defined]


class NoNonSecureAuth(Pop3GenericTestSuite):
    """Verify that no unsecure login is possible."""

    def __init__(
        self,
        *args: Any,
        suite_name: str = "No non-secure auth Test Suite",
        username: str = "foo",
        password: str = "bar",
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(  # type: ignore
            *args,
            suite_name=suite_name,
            username=username,
            password=password,
            **kwargs,  # type: ignore [arg-type]
        )

    def _run_tests(self) -> None:
        try:
            self.pop.user(self.username)
        except poplib.error_proto:
            logger.info("Server rejected login as expected")
            return

        raise self.Pop3TestSuiteError("Server accepted login without secure connection")


class VerifyMailGotDelivered(Pop3GenericTestSuite):
    """Check the mailbox of a given user for expected mails.

    Parameters
    ----------
    expected_messages : list
        A ``list`` of ``str``, representing the subjects of the messages,
        expected to be present in the mailbox.

    Notes
    -----
    For a full list of parameters refer to ``Pop3GenericTestSuite``.
    """

    def __init__(
        self,
        *args: Any,
        suite_name: str = "Verify messages in Mailbox Test Suite",
        expected_messages: Optional[list[str]] = None,
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(  # type: ignore
            *args,
            suite_name=suite_name,
            **kwargs,  # type: ignore [arg-type]
        )

        if expected_messages is None:
            raise self.Pop3OperationalError("Missing parameter: 'expected_mails'")
        self.expected_messages = expected_messages

    def _pre_run(self) -> None:
        self.pop.stls()
        self._auth()

    def _get_message_subject(self, message: list[bytes]) -> str:
        # This is crazily kluged together...
        # It retrieves the actual subject by looking for the substring
        # ``"Subject: "`` in all *lines* of the message, then decodes the line
        # to UTF-8 / ASCII and removes the prefix.
        return [
            i.decode().removeprefix("Subject: ")
            for i in message
            if "Subject: " in i.decode()
        ][0]

    def _run_tests(self) -> None:
        # Get a list of all messages in the mailbox
        msg_list = self.pop.list()[1]

        # Loop all messages, find their *Subject* line and compare to the
        # provided list of expected messages (which is in fact a list of
        # subjects). The message is removed from the list of expected messages.
        for item in msg_list:
            msg_id = item.decode().split(" ")[0]
            # logger.debug("Processing message: %s", msg_id)

            msg = self.pop.retr(msg_id)[1]

            subject = self._get_message_subject(msg)
            # logger.debug("Subject of %s: %s", msg_id, subject)

            if subject in self.expected_messages:
                logger.debug("Found '%s' (message ID %s)", subject, msg_id)
                self.expected_messages.pop(self.expected_messages.index(subject))

        if self.expected_messages:
            logger.error(
                "Could not find expected message(s): %s", self.expected_messages
            )
            raise self.Pop3TestSuiteError(
                "At least one expected message could not be found"
            )

        logger.info("All expected messages found")
