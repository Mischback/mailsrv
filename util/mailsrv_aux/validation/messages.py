"""Provide standard messages for the validation package."""

# Python imports
import logging
from typing import Optional, TypeVar

# local imports
from .exceptions import MailsrvValidationOperationalError

INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

__levels = [INFO, WARNING, ERROR]


class ValidationMessage:
    """Provide the actual feedback of the validation process."""

    def __init__(
        self, level: int, msg: str, id: str, hint: Optional[str] = None
    ) -> None:
        if level not in __levels:
            raise MailsrvValidationOperationalError("Invalid message level")

        self.level = level
        self.msg = msg
        self.id = id
        self.hint = hint

    def __str__(self) -> str:  # noqa: D105
        return "{id}: [{level}] - {message}".format(
            id=self.id, level=self.level, message=self.msg
        )

    def __repr__(self) -> str:  # noqa: D105
        return "<{classname}: level={level!r}, msg={message!r}, id={id!r}, hint={hint!r}>".format(
            classname=self.__class__.__name__,
            level=self.level,
            message=self.msg,
            id=self.id,
            hint=self.hint,
        )


class ValidationError(ValidationMessage):
    """Indicate an actual error in the configuration."""

    def __init__(self, msg: str, id: str, hint: Optional[str] = None) -> None:
        super().__init__(INFO, msg, id, hint=hint)


# Typing stuff
TValidationMessage = TypeVar("TValidationMessage", bound=ValidationMessage)
