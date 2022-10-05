# SPDX-FileCopyrightText: 2022 Mischback
# SPDX-License-Identifier: MIT
# SPDX-FileType: SOURCE

"""SMTP-related parts of the test suite.

These tests are meant to verify the SMTP-part of the mail setup.
"""

# Python imports
import logging
import smtplib
import time
from typing import Any, Optional, Union

# local imports
from ..common.log import add_level
from .exceptions import MailsrvTestException
from .fixture_mail import GENERIC_VALID_MAIL
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
        (default: Generic SMTP Suite).
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
        suite_name: str = "Generic SMTP Suite",
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

    def _sendmail_expect_queue(
        self,
        from_addr: str,
        to_addrs: Union[str, list[str]],
    ) -> None:
        """Send a mail and expect it to be queued.

        Parameters
        ----------
        from_addr: str

        to_addrs : str, list
            The recipient or list of recipients for the mail.

        Raises
        ------
        SmtpTestSuiteError
            Raised if the mail is rejected.
        """
        logger.debug("Sending mail to %r, expecting the mail to be queued", to_addrs)

        if not self._sendmail(from_addr, to_addrs, GENERIC_VALID_MAIL):
            raise self.SmtpTestSuiteError("Expected mail to be queued, got rejected")

    def _sendmail_expect_reject(
        self,
        from_addr: str,
        to_addrs: Union[str, list[str]],
    ) -> None:
        """Send a mail and expect it to be rejected.

        Parameters
        ----------
        to_addrs : str, list
            The recipient or list of recipients for the mail.

        Raises
        ------
        SmtpTestSuiteError
            Raised if the mail is accepted/queued.
        """
        logger.debug("Sending mail to %r, expecting the mail to be rejected", to_addrs)

        if self._sendmail(from_addr, to_addrs, GENERIC_VALID_MAIL):
            raise self.SmtpTestSuiteError("Expected mail to be queued, got rejected")

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
            raise self.SmtpOperationalError("SMTP exception")
        except ConnectionRefusedError:
            logger.critical("Target (%s) refused the connection", self.target_ip)
            raise self.SmtpOperationalError("Connection refused")
        except OSError:
            logger.critical("Target (%s) is not reachable", self.target_ip)
            raise self.SmtpOperationalError("Target not reachable")

        logger.summary("%s finished successfully", self.suite_name)  # type: ignore [attr-defined]
        return self._protocol


class OtherMtaTestSuite(SmtpGenericTestSuite):
    """Simulate another MTA that submits mails.

    The test suite acts like another Mail Transfer Agent (MTA), submitting
    mails for various recipients.

    While the actual test suite might seem to provide primarily tests for the
    MTA part of the setup, it might be used to prepare the testing of the
    Mail Delivery Agent (MDA) aswell. The class's ``run()`` method will return
    an instance of ``SmtpTestProtocol`` which might be used as input to tests
    of the MDA.

    Parameters
    ----------
    valid_recipients : list
        A ``list`` of ``str`` containing **valid** mail addresses. Mails to
        these addresses are expected to be accepted/queued.
    invalid_recipients : list
        A ``list`` of ``str`` containing **invalid** mail addresses. Mails to
        these addresses are expected to be rejected.
    from_address : str
        The address to be used as value to ``MAIL FROM:`` (default:
        sender@another-host.test).
    relay_recipient : str
        An address of another host, that the setup is not responsible for. This
        will be used to verify, that the SUT correctly rejects mails, if it is
        not responsible for a domain. There is no validation of the value
        (default: relay@another-host.test).
    """

    def __init__(
        self,
        *args: Any,
        valid_recipients: Optional[list[str]] = None,
        invalid_recipients: Optional[list[str]] = None,
        from_address: str = "sender@another-host.test",
        relay_recipient: str = "relay@another-host.test",
        suite_name: str = "Other MTA Test Suite",
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(  # type: ignore
            *args,
            suite_name=suite_name,
            **kwargs,  # type: ignore
        )

        if valid_recipients is None:
            # FIXME: Does this make sense? Is this an operational error?
            self._valid_recipients = []
        else:
            self._valid_recipients = valid_recipients

        if invalid_recipients is None:
            # FIXME: Does this make sense? Is this an operational error?
            self._invalid_recipients = []
        else:
            self._invalid_recipients = invalid_recipients

        self._from_address = from_address
        self._relay_recipient = relay_recipient

    def _run_tests(self) -> None:
        logger.info("Start sending of mails")

        # Send mails to all valid recipients
        for to_addr in self._valid_recipients:
            self._sendmail_expect_queue(self._from_address, to_addr)

        # Manually send a mail to multiple recipients:
        # Use the first to addresses in ``_valid_recipients``.
        self._sendmail_expect_queue(self._from_address, self._valid_recipients[:2])

        # Send mails to invalid recipients (expect REJECT)
        for to_addr in self._invalid_recipients:
            self._sendmail_expect_reject(self._from_address, to_addr)

        # Send mail to an external address (relaying; expect REJECT)
        self._sendmail_expect_reject(self._from_address, self._relay_recipient)

        logger.info("All mails sent; server reactions as expected")
        logger.verbose("Protocol: %s", self._protocol)  # type: ignore [attr-defined]
        logger.debug("Protocol: %r", self._protocol)


class OtherMtaTlsTestSuite(OtherMtaTestSuite):
    """Simulate another MTA that submits mails, using TLS.

    The only difference to ``OtherMtaTestSuite`` is the usage of the
    ``starttls()`` command before sending mails.
    """

    def __init__(
        self,
        *args: Any,
        suite_name: str = "Other MTA (TLS) Test Suite",
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(*args, suite_name=suite_name, **kwargs)  # type: ignore [arg-type]

    def _pre_run(self) -> None:
        logger.verbose("Sending command STARTTLS...")  # type: ignore [attr-defined]

        try:
            self.smtp.starttls()
        except (
            smtplib.SMTPNotSupportedError,
            RuntimeError,
            ValueError,
            smtplib.SMTPResponseException,
        ):
            logger.critical("Could not establish TLS connection using STARTTLS")
            raise self.SmtpOperationalError("TLS failure")
        logger.verbose("TLS encryption established")  # type: ignore [attr-defined]


class SubmissionTestSuite(SmtpGenericTestSuite):
    """Verify submission of mails from known users of the SUT.

    This test suite acts like a Mail User Agent (MUA), submitting mails for
    local and external recipients *coming from a local user*.

    The suite requires user credentials and a list of addresses to be used in
    the ``MAIL FROM`` command.

    The class's ``run()`` method will return an instance of
    ``SmtpTestProtocol`` which might e used as input to tests of the MDA.

    Parameters
    ----------
    username : str
        The username to be used for login.
    password : str
        The password, completing the login credentials.
    valid_from : list
        A ``list`` of ``str`` containing **valid** addresses to be used in the
        ``MAIL FROM`` command.
    invalid_from : str, optional
        An **invalid** address, meaning an address that can not be used in the
        ``MAIL FROM`` command (default: no_sending@sut-one.test).
    local_rcpt : str, optional
        A local address, meaning an address that is handled by the SUT
        (default: submission@sut-one.test).
    external_rcpt : str, optional
        An address on another MTA (default: submission@another-host.test).
    suite_name : str, optional
        The suites verbose name (default: Submission Test Suite).
    """

    def __init__(
        self,
        *args: Any,
        username: str,
        password: str,
        valid_from: Optional[list[str]] = None,
        invalid_from: str = "no_sending@sut-one.test",
        local_rcpt: str = "submission@sut-one.test",
        external_rcpt: str = "submission@another-host.test",
        suite_name: str = "Submission Test Suite",
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(  # type: ignore
            *args,
            target_port=587,
            suite_name=suite_name,
            **kwargs,  # type: ignore
        )

        self.username = username
        self.password = password
        self.invalid_from = invalid_from
        self.local_rcpt = local_rcpt
        self.external_rcpt = external_rcpt

        if valid_from is None:
            self.valid_from = []
        else:
            self.valid_from = valid_from

    def _pre_run(self) -> None:
        logger.verbose("Sending command STARTTLS...")  # type: ignore [attr-defined]

        try:
            self.smtp.starttls()
        except (
            smtplib.SMTPNotSupportedError,
            RuntimeError,
            ValueError,
            smtplib.SMTPResponseException,
        ):
            logger.critical("Could not establish TLS connection using STARTTLS")
            raise self.SmtpOperationalError("TLS failure")
        logger.verbose("TLS encryption established")  # type: ignore [attr-defined]

        try:
            self.smtp.login(self.username, self.password)
        except (
            smtplib.SMTPHeloError,
            smtplib.SMTPAuthenticationError,
            smtplib.SMTPNotSupportedError,
            smtplib.SMTPException,
        ):
            logger.critical("Could not login")
            raise self.SmtpOperationalError("Login error")
        logger.verbose("Login successful")  # type: ignore [attr-defined]

    def _run_tests(self) -> None:
        logger.verbose("Sending mails for account '%s'", self.username)  # type: ignore [attr-defined]
        for addr in self.valid_from:
            self._sendmail_expect_queue(from_addr=addr, to_addrs=self.local_rcpt)
            self._sendmail_expect_queue(from_addr=addr, to_addrs=self.external_rcpt)

        self._sendmail_expect_reject(
            from_addr=self.invalid_from, to_addrs=self.local_rcpt
        )
