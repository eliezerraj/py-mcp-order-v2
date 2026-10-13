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
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

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
        span_name = f"middleware:{request.url.path}"
        with tracer.start_as_current_span(span_name) as span:
            logger.info(f"Processing RequestContextMiddleware request: {request}")
            
            # Step 1: Generate or retrieve request ID for tracing
            request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
            auth_header = request.headers.get("Authorization")
            
            # Step 2: Propagate request ID in span and baggage
            span = trace.get_current_span()
            set_baggage("http.request.id", request_id)
            span.set_attribute("http.request.id", request_id)
            
            # Step 3: Extract and verify the authorization token from the header
            auth_header = request.headers.get("Authorization")
            auth_token = None
            if auth_header and auth_header.startswith("Bearer "):
                auth_token = auth_header.split(" ", 1)[1]
            
            logger.info(f"Processing request with auth_token present: {auth_token}")
            
            # Step 4: Verify token and create SecurityContext with ALL verified data at once
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
                    logger.error(f"Invalid access token error: {e.message}")
                    span.set_attribute("error.type", e.error_type)
                    span.set_attribute("http.status_code", e.status_code or 401)
                    
                    # Return 401 Unauthorized response using exception's to_dict()
                    error_response = e.to_dict()
                    
                    return JSONResponse(
                        status_code=e.status_code or 401,
                        content=error_response,
                        headers={"x-request-id": request_id}
                    )
                except Exception as e:
                    logger.error(f"Unexpected error during token verification: {str(e)}")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("http.status_code", 401)
                    
                    # Return 401 Unauthorized response for unexpected errors
                    error_response = e.to_dict()
  
                    return JSONResponse(
                        status_code=401,
                        content=error_response,
                        headers={"x-request-id": request_id}
                    )
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