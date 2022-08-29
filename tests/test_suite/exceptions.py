"""App-specific exceptions."""


class MailsrvTestSuiteException(Exception):
    """Base class for all app-specific exceptions.

    These exceptions are used to give feedback to the main application in
    case of operational failures during the test execution and in case of
    actually failed tests.
    """

    pass
