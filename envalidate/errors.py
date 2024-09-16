"""Custom exceptions related to environment parsing and validation.
"""


class MissingEnvironmentError(Exception):
    """Exception raised when a required environment varialbe was not able to be resolved."""
