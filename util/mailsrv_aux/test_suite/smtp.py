"""SMTP-related parts of the test suite.

These tests are meant to verify the SMTP-part of the mail setup.
"""

# Python imports
import logging
import smtplib
import time
from typing import Union

# local imports
from ..common.logs import add_level
from .exceptions import MailsrvTestException
from .protocols import SmtpTestProtocol

# get a module-level logger
logger = logging.getLogger(__name__)

# add VERBOSE / SUMMARY log levels
add_level("VERBOSE", logging.INFO - 1)
add_level("SUMMARY", logging.INFO + 1)


class SmtpGenericTestSuite:
    """Provide the SMTP protocol abstraction for actual test suites.

    Parameters
    ----------
    target_ip : str, optional
        The IP to connect to (default: 127.0.0.1).
    target_port : int, optional
        The port to use for the connection (default: 25, from ``smtplib.SMTP_PORT``).
    suite_name : str, optional
        The name of the test suite. Should be set to distinguish several suites
        (default: Generic Suite).
    local_hostname : str, optional
        The hostname to use in SMTP HELO/EHLO (default: mail.another-host.test).
    mail_count_offset : int, optional
        Start counting the mails with this offset (default: 0).
    """

    class SmtpGenericException(MailsrvTestException):
        """Base class for all exceptions of SMTP test suites."""

    class SmtpOperationalError(SmtpGenericException):
        """Indicate operational errors, most likely while using ``smtplib``."""

    class SmtpTestSuiteError(SmtpGenericException):
        """Indicate an actual test failure."""

    def __init__(
        self,
        target_ip: str = "127.0.0.1",
        target_port: int = smtplib.SMTP_PORT,
        suite_name: str = "Generic Suite",
        local_hostname: str = "mail.another-host.test",
        mail_count_offset: int = 0,
    ) -> None:
        self.target_ip = target_ip
        self.target_port = target_port
        self.suite_name = suite_name
        self.local_hostname = local_hostname
        # ``__init__()``'s parameter is called ``_offset``, but this attribute
        # will only be incremented at the end of ``_sendmail()``, so in order
        # to let the numbering start with *1*, this has to be added here.
        self._mail_counter = mail_count_offset + 1
        self._protocol: SmtpTestProtocol = SmtpTestProtocol()

    def _pre_connect(self) -> None:
        pass

    def _pre_run(self) -> None:
        pass

    def _post_run(self) -> None:
        logger.debug("Protocol: %r", self._protocol)

    def _run_tests(self) -> None:
        raise NotImplementedError("Has to be implemented in real test suite")

    def _generate_subject(self) -> str:
        return "{} {}".format(self._mail_counter, hash(time.time()))

    def _increment_mail_counter(self) -> None:
        self._mail_counter += 1

    def _sendmail(
        self,
        from_addr: str,
        to_addrs: Union[str, list[str]],
        msg_template: str,
        mail_options: tuple = (),
        rcpt_options: tuple = (),
    ) -> bool:
        # Prepare the actual mail for sending:
        # 1) RCPT TO:
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
            header_to: str = to_addrs  # type: ignore [assignment]
        else:
            # to_addrs is already a list
            header_to = ", ".join(to_addrs)

        # 2) Generate the subject
        header_subject = self._generate_subject()

        # 3) Actualle generate the message from the template
        # TODO: Actually name the parameters in ``tests/test_suite/fixture_mail.py``
        msg = msg_template.format(
            mail_from=from_addr,
            rcpt_to=header_to,
            subject=header_subject,
        )

        logger.debug(
            "sendmail(): %s, %r, %s, %r, %r",
            from_addr,
            to_addrs,
            msg[:16],
            mail_options,
            rcpt_options,
        )

        self._increment_mail_counter()
        self._protocol.mail_sent(header_subject)

        try:
            # actually send the mail
            resp = self.smtp.sendmail(
                from_addr, to_addrs, msg, mail_options, rcpt_options
            )
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused):
            self._protocol.mail_rejected(header_subject)
            return False

        for addr in to_addrs:
            if addr not in resp:
                self._protocol.mail_accepted(addr, header_subject)

        return True

    def run(self) -> SmtpTestProtocol:
        """Run the test suite."""
        logger.summary("Running %s", self.suite_name)  # type: ignore [attr-defined]

        self._pre_connect()

        try:
            with smtplib.SMTP(
                host=self.target_ip,
                port=self.target_port,
                local_hostname=self.local_hostname,
            ) as self.smtp:
                logger.info("Connection to target (%s) established", self.target_ip)

                self._pre_run()
                self._run_tests()
                self._post_run()

                self.smtp.quit()
                logger.verbose("Connection to target (%s) terminated", self.target_ip)  # type: ignore [attr-defined]
        except smtplib.SMTPException as e:
            logger.critical("SMTP exception: '%s'", e)  # noqa: G200
            logger.exception(e)  # noqa: G200
            raise self.SmtpOperationalError("SMTP exception")
        except ConnectionRefusedError as e:
            logger.critical("Target (%s) refused the connection", self.target_ip)
            logger.exception(e)  # noqa: G200
            raise self.SmtpOperationalError("Connection refused")

        logger.summary("%s finished successfully", self.suite_name)  # type: ignore [attr-defined]
        return self._protocol
