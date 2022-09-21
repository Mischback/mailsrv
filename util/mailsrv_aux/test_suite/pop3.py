"""Test suite using POP3.

This suite has two important functions: They verify the POP3 functions of the
server **and** verify, that all mails got delivered as expected.
"""

# Python imports
import logging
import poplib
from typing import Optional

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
