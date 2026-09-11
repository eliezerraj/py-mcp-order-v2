import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.mcp_server.domain.dto.context import SecurityContext
from config.logger import REQUEST_ID_CTX
from src.mcp_server.infrastructure.context.request_context import (
    set_security_context,
    reset_security_context,
)

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("Initializing Middleware SUCCESSFULLY")

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Processing request: {request}")
        
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        auth_header = request.headers.get("Authorization")
        
        auth_token = None
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ", 1)[1]
        
        logger.info(f"Setting Request ID {request_id} and auth_token in context: {auth_token}")
        
        REQUEST_ID_CTX.set(request_id)
        
        sec_context = SecurityContext(
            x_request_id=request_id,
            auth_token=auth_token,
        )
        
        set_security_context(sec_context)
        
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            
            return response
        finally:
            reset_security_context(set_security_context(sec_context))
