"""Domain-level exceptions.

The domain layer raises these; it has no HTTP awareness. Exception handlers
registered in main.py translate each to an HTTP status + JSON envelope. This is
the single place coupling business errors to status codes.
"""


class DomainError(Exception):
    """Base class for all expected, handleable domain errors."""
    code = "error"
    status_code = 400

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class ConflictError(DomainError):
    code = "conflict"
    status_code = 409


class AuthError(DomainError):
    code = "auth_error"
    status_code = 401


class PermissionError(DomainError):  # noqa: A001 - intentional domain name
    code = "forbidden"
    status_code = 403
