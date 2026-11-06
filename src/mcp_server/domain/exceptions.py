from src.mcp_server.domain.external.error_response import AppError

class InvalidAccessTokenError(AppError):
    pass

class AuthorizationDeniedError(AppError):
    pass

class MissingTokenError(AppError):
    pass

class ForbiddenError(AppError):
    pass