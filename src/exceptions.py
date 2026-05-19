class AppError(Exception):
    """Base application error mapped to an HTTP response."""

    def __init__(self, message: str, *, code: int = 400, data: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data or {}


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", *, data: dict | None = None):
        super().__init__(message, code=404, data=data)


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", *, data: dict | None = None):
        super().__init__(message, code=400, data=data)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", *, data: dict | None = None):
        super().__init__(message, code=409, data=data)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", *, data: dict | None = None):
        super().__init__(message, code=401, data=data)
