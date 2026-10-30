from contextvars import ContextVar

from src.mcp_server.domain.dto.context import SecurityContext

SECURITY_CONTEXT_CTX: ContextVar[SecurityContext | None] = ContextVar(
    "security_context",
    default=None,
)

def set_security_context(context: SecurityContext):
    return SECURITY_CONTEXT_CTX.set(context)

def get_security_context() -> SecurityContext | None:
    return SECURITY_CONTEXT_CTX.get()

def reset_security_context(token):
    SECURITY_CONTEXT_CTX.reset(token)