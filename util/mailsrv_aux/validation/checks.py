"""Provide the actual check functions to validate the configuration."""

# Python imports
import logging

# local imports
from ..common.log import add_level
from ..common.parser import PasswdFileParser, PostfixAliasResolver
from .messages import ValidationError, ValidationMessage, ValidationWarning

# get a module-level logger
logger = logging.getLogger(__name__)

# add the VERBOSE log level
add_level("VERBOSE", logging.INFO - 1)


def check_mailbox_has_account(
    postfix_mailboxes: list[str], dovecot_accounts: list[str]
) -> list[ValidationMessage]:
    """All Postfix mailboxes **must have** a matching entry in Dovecot's user database.

    Parameters
    ----------
    postfix_mailboxes : list
        A ``list`` of ``str``, representing the actual mailboxes of Postfix.
    dovecot_accounts : list
        A ``list`` of ``str``, representing the available user accounts for
        Dovecot.

    Returns
    -------
    list
        A list of ``ValidationError`` instances. One instance per missing
        mailbox.
    """
    logger.debug("check_mailbox_has_account()")
    logger.verbose("Check: Postfix's virtual mailboxes must have a Dovecot account")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    for box in postfix_mailboxes:
        if box not in dovecot_accounts:
            logger.debug("Mailbox '%s' not in dovecot_accounts", box)
            findings.append(
                ValidationError(
                    "Mailbox '{}' has no matching account".format(box),
                    id="e001",
                    hint="Every Postfix *mailbox* requires a matching entry in Dovecot's *userdb*",
                )
            )

    return findings


def check_addresses_match_domains(
    postfix_addresses: list[str], postfix_domains: list[str]
) -> list[ValidationMessage]:
    """All Postfix addresses **must have** a matching entry in Postfix's virtual domains.

    Parameters
    ----------
    postfix_addresses : list
        A ``list`` of ``str``, representing all addresses of the Postfix
        server.
    postfix_domains : list
        A ``list`` of ``str``, representing all virtual domains.

    Returns
    -------
    list
        A list of ``ValidationError`` instances.
    """
    logger.debug("check_addresses_match_domains()")
    logger.verbose("Check: Postfix's addresses must have a matchin virtual domain")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    for address in postfix_addresses:
        if address[address.index("@") + 1 :] not in postfix_domains:
            logger.debug("Address '%s' not in postfix_domains", address)
            findings.append(
                ValidationError(
                    "Address '{}' not in virtual domains".format(address),
                    id="e002",
                    hint="The domain parts of the addresses require a matching entry in Postfix's virtual domains",
                )
            )

    return findings


def check_address_can_send(
    postfix_addresses: list[str], postfix_senders: dict[str, list[str]]
) -> list[ValidationMessage]:
    """Check if addresses are included in the senders map.

    Parameters
    ----------
    postfix_addresses : list
        A ``list`` of ``str``, representing all addresses of the Postfix
        server.
    postfix_senders : dict
        A ``dict``, representing the sender to login mapping.

    Returns
    -------
    list
        A list of ``ValidationWarning`` instances.
    """
    logger.debug("check_address_can_send()")
    logger.verbose("Check: Can the addresses send?")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    senders_lhs = list(postfix_senders.keys())

    for address in postfix_addresses:
        if address not in senders_lhs:
            logger.debug("Address '%s' can not send", address)
            findings.append(
                ValidationWarning(
                    "Address '{}' not in sender_login_map".format(address),
                    id="w003",
                )
            )

    return findings


def check_sender_has_login(
    postfix_senders: dict[str, list[str]], dovecot_accounts: list[str]
) -> list[ValidationMessage]:
    """All senders **must have** a matching entry in Dovecot's user database.

    Parameters
    ----------
    postfix_senders : dict
        A ``dict``, representing the sender to login mapping.
    dovecot_accounts : list
        A ``list`` of ``str``, representing the available user accounts for
        Dovecot.

    Returns
    -------
    list
        A list of ``ValidationError`` instances. One instance per missing
        account.
    """
    logger.debug("check_sender_has_login()")
    logger.verbose("Check: Can the sender login?")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    # Crazy kluge: All values in ``postfix_senders`` (which are ``lists``)
    # combined into one ``set``
    senders_rhs = {item for sublist in postfix_senders.values() for item in sublist}

    for sender in senders_rhs:
        if sender not in dovecot_accounts:
            logger.debug("Sender '%s' not in dovecot_accounts", sender)
            findings.append(
                ValidationError(
                    "Sender '{}' has no matching account".format(sender),
                    id="e004",
                    hint="Every Postfix *sender* requires a matching entry in Dovecot's *userdb*",
                )
            )

    return findings


def check_account_has_function(
    postfix_mailboxes: list[str],
    postfix_senders: dict[str, list[str]],
    dovecot_accounts: list[str],
) -> list[ValidationMessage]:
    """All Dovecot accounts *should have* some sort of function.

    A *function* might be either an associated Postfix mailbox or the usage
    as a sender login.

    Parameters
    ----------
    postfix_mailboxes : list
        A ``list`` of ``str``, representing the actual mailboxes of Postfix.
    postfix_senders : dict
        A ``dict``, representing the sender to login mapping.
    dovecot_accounts : list
        A ``list`` of ``str``, representing the available user accounts for
        Dovecot.

    Returns
    -------
    list
        A list of ``ValidationWarning`` instances.
    """
    logger.debug("check_account_has_function()")
    logger.verbose("Check: Dovecot's accounts should have a function")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    # Crazy kluge: All values in ``postfix_senders`` (which are ``lists``)
    # combined into one ``set``
    senders_rhs = {item for sublist in postfix_senders.values() for item in sublist}

    for account in dovecot_accounts:
        if account in postfix_mailboxes:
            continue

        if account in senders_rhs:
            continue

        logger.debug("Account '%s' has neither mailbox nor is a sender", account)
        findings.append(
            ValidationWarning(
                "Account '{}' has neither mailbox nor is a sender".format(account),
                id="w005",
            )
        )

    return findings


def check_domain_has_admin_addresses(
    postfix_domains: list[str], postfix_addresses: list[str]
) -> list[ValidationMessage]:
    """All virtual domains should have postmaster and abuse addresses.

    Parameters
    ----------
    postfix_domains : list
        A ``list`` of ``str``, representing the virtual domains.
    postfix_addresses : list
        A ``list`` of ``str``, representing all addresses.

    Returns
    -------
    list
        A list of ``ValidationWarning`` instances.
    """
    logger.debug("check_domain_has_admin_addresses()")
    logger.verbose("Check: All domains should have postmaster and abuse addresses")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    for domain in postfix_domains:
        if "postmaster@{}".format(domain) in postfix_addresses:
            continue

        if "abuse@{}".format(domain) in postfix_addresses:
            continue

        logger.debug("Domain '%s' is missing admin addresses", domain)
        findings.append(
            ValidationWarning(
                "Domain '{}' is missing admin addresses".format(domain),
                id="w006",
                hint="The domain should have 'postmaster@' and 'abuse@' addresses",
            )
        )

    return findings


def check_resolve_alias_configuration(
    postfix_mailboxes: list[str],
    postfix_aliases: dict[str, list[str]],
    postfix_domains: list[str],
) -> list[ValidationMessage]:
    """All aliases **must** resolve to a mailbox or external address.

    Resolving to an external address will be handled by a warning, see the
    provided hint.

    Parameters
    ----------
    postfix_mailboxes : list
        A ``list`` of ``str``, representing the virtual mailboxes.
    postfix_aliases : dict
        A ``dict`` containing the acutal alias configuration.
    postfix_domains : list
        A ``list`` of ``str``, representing the virtual domains.

    Returns
    -------
    list
        A list of ``ValidationWarning`` and/or ``ValidationError`` instances.

    Notes
    -----
    Uses ``PostfixAliasResolver`` internally.
    """
    logger.debug("check_resolve_alias_configuration()")
    logger.verbose("Check: Resolve the alias configuration")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    resolver = PostfixAliasResolver(postfix_mailboxes, postfix_aliases, postfix_domains)

    resolve, tmp_fail, tmp_external = resolver.resolve()

    if tmp_fail is not None:
        for alias in tmp_fail:
            logger.debug("Alias '%s' could not be resolved", alias)
            findings.append(
                ValidationError(
                    "Alias '{}' could not be resolved. Target was: {}".format(
                        alias, tmp_fail[alias]
                    ),
                    id="e007",
                    hint="Target is neither a mailbox nor an external address.",
                )
            )

    if tmp_external is not None:
        for alias in tmp_external:
            logger.debug("Alias '%s' resolves to external address", alias)
            findings.append(
                ValidationWarning(
                    "Alias '{}' resolves to external addresses: {}".format(
                        alias, tmp_external[alias]
                    ),
                    id="w008",
                    hint="Mails to this alias are forwarded to an external address."
                    " This poses a severe risk to the mail setup, as spam might"
                    " be forwarded and this server will be considered a spam"
                    " relay. Other problems regarding SPF and DMARC may arise.",
                )
            )

    return findings


def check_no_plaintext_passwords(
    userdb: PasswdFileParser,
) -> list[ValidationMessage]:
    """Dovecot's userdatabase **must not** contain plain test passwords.

    Parameters
    ----------
    userdb : ``PasswdFileParser``
        The internal representation of Dovecot's userdb.

    Returns
    -------
    list
        A list of ``ValidationError`` instances.
    """
    logger.debug("check_no_plaintext_passwords()")
    logger.verbose("Check: Dovecot's userdb must not contain plain text passwords")  # type: ignore [attr-defined]

    findings: list[ValidationMessage] = []

    for entry in userdb.get_usernames():
        if userdb.get_password(entry).startswith("{plain}"):
            logger.debug("Entry '%s' has a plain text password", entry)
            findings.append(
                ValidationError(
                    "Account '{}' has a plain text password".format(entry),
                    id="e009",
                    hint="Provide a hashed password",
                )
            )

    return findings
