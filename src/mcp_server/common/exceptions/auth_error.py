from src.mcp_server.common.exceptions.app_error import AppError

class InvalidAccessTokenError(AppError):
    pass

class AuthorizationDeniedError(AppError):
    pass