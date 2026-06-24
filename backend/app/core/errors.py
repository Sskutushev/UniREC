class AppError(Exception):
    def __init__(self, message: str, *, error_code: str) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class NotFoundError(AppError):
    pass


class ValidationAppError(AppError):
    pass


class ProviderError(AppError):
    pass


class CacheError(AppError):
    pass
