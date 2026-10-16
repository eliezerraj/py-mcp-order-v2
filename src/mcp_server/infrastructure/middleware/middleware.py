import logging
import uuid

from opentelemetry import trace
from opentelemetry.baggage import set_baggage
            
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.mcp_server.config.settings import settings
from src.mcp_server.domain.dto.context import SecurityContext
from src.mcp_server.config.logger import REQUEST_ID_CTX
from src.mcp_server.infrastructure.context.request_context import (
    set_security_context,
    reset_security_context,
)

from src.mcp_server.infrastructure.auth.token_verifier import JwtTokenVerifier

from src.mcp_server.common.exceptions.auth_error import (
    InvalidAccessTokenError,
    MissingTokenError,
)

#---------------------------------
# Configure logging
#---------------------------------
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

TRACING_EXCLUDED_PATHS = ["/metrics", "/health"]
AUTHORIZATION_EXCLUDED_PATHS = ["/metrics", "/health", "/info"]

#---------------------------------
# Exception handler utility
#---------------------------------
def handle_auth_exception(exception: Exception, span, request_id: str, log_level: str = "warning") -> JSONResponse:
    """
    Unified exception handler for authentication errors.
    
    Args:
        exception: The exception to handle (custom or generic)
        span: OpenTelemetry span for setting attributes
        request_id: Request ID for correlation
        log_level: Log level to use ("warning" or "error")
    
    Returns:
        JSONResponse with appropriate error response and status code
    """
    # Determine status code and error response
    status_code = 401
    if hasattr(exception, 'status_code') and exception.status_code:
        status_code = exception.status_code
    
    # Get error message based on exception type
    if hasattr(exception, 'message'):
        log_msg = f"{type(exception).__name__}: {exception.message}"
        error_response = exception.to_dict() if hasattr(exception, 'to_dict') else {"error": exception.message}
    else:
        log_msg = f"Unexpected error during token verification: {str(exception)}"
        error_response = {"error": "Unexpected error", "message": str(exception)}
    
    # Log the error
    if log_level == "error":
        logger.error(log_msg)
    else:
        logger.warning(log_msg)
    
    # Set span attributes
    span.set_attribute("error.type", type(exception).__name__)
    span.set_attribute("http.status_code", status_code)
    
    return JSONResponse(
        status_code=status_code,
        content=error_response,
        headers={"x-request-id": request_id}
    )
    
class RequestContextMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        self._token_verifier = JwtTokenVerifier(
            issuer=settings.AUTHORIZATION_ISSUER,
            audience=settings.AUTHORIZATION_AUDIENCE,
            jwks_url=settings.AUTHORIZATION_JWKS_URL,
        )

        logger.info("Initializing RequestContextMiddleware SUCCESSFULLY")

    async def dispatch(self, request: Request, call_next):
        
        # Step 1: Generate or retrieve request ID for tracing
        request_id = request.headers.get("x-request-id", str(uuid.uuid4())) 
        REQUEST_ID_CTX.set(request_id)
        
        # Step 2: Skip auth for excluded paths    
        if request.url.path in TRACING_EXCLUDED_PATHS:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        
        span_name = f"middleware:{request.url.path}"
        with tracer.start_as_current_span(span_name) as span:
            logger.info(f"Processing RequestContextMiddleware request: {request}")
                 
            # Step 3: Propagate request ID in span and baggage
            span = trace.get_current_span()
            set_baggage("http.request.id", request_id)
            span.set_attribute("http.request.id", request_id)

            # Step 4: Skip auth for excluded paths
            if request.url.path in AUTHORIZATION_EXCLUDED_PATHS:
                response = await call_next(request)
                response.headers["x-request-id"] = request_id
                return response
                        
            # Step 5: Extract and verify the authorization token from the header
            auth_header = request.headers.get("Authorization")
            auth_token = None
            if auth_header and auth_header.startswith("Bearer "):
                auth_token = auth_header.split(" ", 1)[1]
            
            logger.info(f"Processing request with auth_token present: {auth_token}")
            
            # Step 6: Verify token and create SecurityContext with ALL verified data at once
            sec_context = None
            if not settings.AUTHORIZATION_DRY_RUN:
                logger.info("Performing token verification")
                try:
                    verified_identity = await self._token_verifier.verify_token(auth_token)
                    
                    logger.info(f"Token verified successfully for subject={verified_identity.subject}")
                    
                    # Create SecurityContext with all verified data (immutable)
                    sec_context = SecurityContext(
                        x_request_id=request_id,
                        auth_token=auth_token,
                        subject=verified_identity.subject,
                        roles=verified_identity.roles,
                        scopes=verified_identity.scopes,
                        claims=verified_identity.claims,
                    )
                    
                except InvalidAccessTokenError as e:
                    return handle_auth_exception(e, span, request_id, log_level="warning")
                except MissingTokenError as e:
                    return handle_auth_exception(e, span, request_id, log_level="warning")
                except Exception as e:
                    return handle_auth_exception(e, span, request_id, log_level="error")
            else:
                logger.info("Authentication dry run enabled, skipping token verification")
                # Create basic SecurityContext for dry run
                sec_context = SecurityContext(
                    x_request_id=request_id,
                    auth_token=auth_token,
                )
            
            # Step 6: Set security context for this request
            token = set_security_context(sec_context)
            
            try:
                # Step 7: Process request with security context
                response = await call_next(request)
                response.headers["x-request-id"] = request_id
                return response
            finally:
                # Step 8: Always reset context
                reset_security_context(token)