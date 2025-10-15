"""

File: custom_exceptions.py

Description: This module defines custom exception classes used throughout the Gameplay Database project.

Each custom exception inherits from Python's base `Exception` class and attaches a timestamp
indicating when the error was raised. These exceptions provide more meaningful context for
logging and debugging than standard exceptions.

Author: cobalt

"""

# --- Standard imports ---
from datetime import datetime

class DataNotFound(Exception):

    """

    Exception raised when a requested dataset or database entry cannot be found.

    This exception is typically raised by database query functions when no matching
    results are returned. It includes a timestamp to make logs more traceable.

    Parameters
    ----------
    message : str
        A descriptive message explaining what data was not found.

    Attributes
    ----------
    timestamp : datetime
        The exact time when the exception was raised, useful for logging and debugging.

    Example
    -------
    >>> raise DataNotFound("No creator found with username 'JohnDoe'")

    """

    def __init__(self, message):
        super().__init__(message)
        self.timestamp = datetime.now()

class MissingModPermissions(Exception):

    """

    Exception raised when a user attempts to perform a moderator-only action without permission.

    This is used to handle Discord interactions where a user is not listed in the
    moderation whitelist (see `check_mod()` in the utilities module).

    Parameters
    ----------
    message : str
        A message describing why the permission was denied.

    Attributes
    ----------
    timestamp : datetime
        The time at which the exception was raised.

    Example
    -------
    >>> raise MissingModPermissions("User tried to use a restricted mod command")

    """

    def __init__(self, message):
        super().__init__(message)
        self.timestamp = datetime.now()

class InvalidYouTubeURL(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.timestamp = datetime.now()