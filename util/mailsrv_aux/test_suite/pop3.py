"""Test suite using POP3.

This suite has two important functions: They verify the POP3 functions of the
server **and** verify, that all mails got delivered as expected.
"""

# Python imports
import logging
import poplib
from typing import Any, Optional

# local imports
from .exceptions import MailsrvTestException

# get a module-level logger
logger = logging.getLogger(__name__)


class PopGenericTestSuite:
    """Provide the POP3 protocol abstraction for actual test suites.

    Parameters
    ----------
    target_ip : str, optional
        The IP to connect to (default: 127.0.0.1).
    target_port : int, optional
        The port to use for the connection (default: 110, from ``poplib.POP3_PORT``).
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
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.target_ip = target_ip
        self.target_port = target_port

        if username is None:
            raise self.Pop3OperationalError("Missing parameter: 'username'")
        self.username = username

        if password is None:
            raise self.Pop3OperationalError("Missing parameter: 'password'")
        self.password = password

    def _connect(self) -> None:
        try:
            self.pop = poplib.POP3(self.target_ip, port=self.target_port)
        except ConnectionRefusedError:
            logger.critical("Target (%s) refused the connection", self.target_ip)
            raise self.Pop3OperationalError("Connection refused")

    def _auth(self) -> None:
        try:
            self.pop.user(self.username)
            self.pop.pass_(self.password)
        except poplib.error_proto as e:
            logger.error("Authentication failed: %s", e)  # noqa: G200
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
            pass
        self.pop.quit()

    def _run_tests(self) -> None:
        raise NotImplementedError("Has to be implemented in real test suite")

    def run(self) -> None:
        """Run the test suite."""
        self._pre_connect()
        self._connect()
        self._pre_run()
        self._run_tests()
        self._post_run()
        self._disconnect()


class NoNonSecureAuth(PopGenericTestSuite):
    """Verify that no unsecure login is possible."""

    def __init__(
        self,
        *args: Any,
        username: str = "foo",
        password: str = "bar",
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(*args, username=username, password=password, **kwargs)  # type: ignore

    def _run_tests(self) -> None:
        try:
            self.pop.user(self.username)
        except poplib.error_proto:
            logger.info("Server rejected login as expected")
            return

        raise self.Pop3TestSuiteError("Server accepted login without secure connection")


class VerifyMailGotDelivered(PopGenericTestSuite):
    """Check the mailbox of a given user for expected mails."""

    def __init__(
        self,
        *args: Any,
        expected_mails: Optional[list[str]] = None,
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(*args, **kwargs)  # type: ignore [arg-type]

        if expected_mails is None:
            raise self.Pop3OperationalError("Missing parameter: 'expected_mails'")
        self.expected_mails = expected_mails

    def _pre_run(self) -> None:
        self.pop.stls()
        self._auth()

    def _run_tests(self) -> None:
        logger.info("starting tests...")
