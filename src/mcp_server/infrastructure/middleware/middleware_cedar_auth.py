import logging
import json
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.mcp_server.infrastructure.auth.cedar_verifier import CedarVerifier
from src.mcp_server.common.exceptions.auth_error import ForbiddenError
from src.mcp_server.config.settings import settings
from src.mcp_server.infrastructure.context.request_context import get_security_context

#---------------------------------
# Configure logging
#---------------------------------
logger = logging.getLogger(__name__)

CEDAR_AUTH_EXCLUDED_PATHS = ["/metrics", "/health", "/.well-known/oauth-protected-resource"]

class CedarAuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce Cedar authorization policies at the HTTP layer.
    Intercepts MCP resource calls and validates them before MCP processing.
    """

    def __init__(self, app):
        super().__init__(app)
        self.cedar_verifier = CedarVerifier()
        logger.info("Initializing CedarAuthorizationMiddleware SUCCESSFULLY")

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        logger.info("Dispatching CedarAuthorizationMiddleware for request path: %s %s", request.method , request.url.path)
        print("---------------------------1------------------------")
        # Skip authorization for excluded paths
        if request.url.path in CEDAR_AUTH_EXCLUDED_PATHS:
            return await call_next(request)
        
        # Skip if dry-run mode is enabled
        if settings.AUTHORIZATION_DRY_RUN:
            logger.info("Cedar authorization dry run enabled, skipping authorization")
            return await call_next(request)
        
        # Only validate POST requests (MCP uses POST for JSON-RPC calls)
        if request.method != "POST":
            return await call_next(request)
        
        print("---------------------------2------------------------")
        try:
            # Read the request body
            body = await request.body()
            
            # Skip if body is empty
            if not body:
                return await call_next(request)
            
            # Parse JSON-RPC request
            try:
                payload = json.loads(body.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON, pass through
                return await call_next(request)
            
            # Check if this is a resource call (method = "resources/read")
            print("---------------------------3------------------------")
            print(f"payload.get: {payload.get('method')}")
            
            if payload.get("method") == "resources/read":
                resource_uri = payload.get("params", {}).get("uri", "")
                
                logger.info(f"Intercepting resource call: {resource_uri}")
                
                # Map resource URI to Cedar authorization action
                resource_id, resource_attrs = self._parse_resource_uri(resource_uri)
                
                print("---------------------------4------------------------")
                try:
                    # Perform Cedar authorization check
                    self.cedar_verifier.validate(
                        action="call_resource",
                        resource_type="Resource",
                        resource_id=resource_id,
                        resource_attrs=resource_attrs,
                    )
                    logger.info(f"Cedar authorization passed for resource: {resource_id}")
                    
                except ForbiddenError as e:
                    logger.warning(f"Cedar authorization denied for resource {resource_id}: {e}")
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": "FORBIDDEN",
                            "error_type": "ForbiddenError",
                            "message": f"Authorization denied: {str(e)}",
                        },
                        headers={"x-request-id": request.headers.get("x-request-id", "")}
                    )

            print("---------------------------5 end------------------------")            
            # Create a new receive callable that returns the stored body
            async def receive():
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False,
                }
            
            # Replace request's receive method
            request._receive = receive
            
        except Exception as e:
            logger.error(f"Error in CedarAuthorizationMiddleware: {e}")
            # Let other errors pass through; don't block on middleware errors
        
        # Call the next middleware/handler
        response = await call_next(request)
        
        # Capture and log response payload for error status codes
        if response.status_code >= 400:
            try:
                # Read response body
                body_bytes = b""
                async for chunk in response.body_iterator:
                    body_bytes += chunk
                
                # Try to parse as JSON for logging
                try:
                    response_payload = json.loads(body_bytes.decode())
                    logger.warning(
                        f"Upstream error {response.status_code}: {json.dumps(response_payload, indent=2)}"
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.warning(
                        f"Upstream error {response.status_code}: {body_bytes.decode(errors='ignore')}"
                    )
                
                # Re-wrap the response with the body we just read
                response = Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            except Exception as e:
                logger.error(f"Error capturing response payload: {e}")
        
        return response
    
    def _parse_resource_uri(self, uri: str) -> tuple:
        """
        Parse resource URI and extract resource_id and attributes.
        Examples:
        - "order://123" -> ("get_order", {"data": "123"})
        - "time_series_order_items://SKU001?limit=7&offset=0" -> ("get_time_series_order_items", {"data": "SKU001", "limit": "7", "offset": "0"})
        """
        
        if uri.startswith("order://"):
            order_number = uri.replace("order://", "")
            return "get_order", {"data": order_number}
        
        elif uri.startswith("time_series_order_items://"):
            path_part = uri.replace("time_series_order_items://", "")
            # Handle query string
            if "?" in path_part:
                product, query = path_part.split("?", 1)
                attrs = {"data": product}
                # Parse query params
                for param in query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        attrs[key] = value
                return "get_time_series_order_items", attrs
            else:
                return "get_time_series_order_items", {"data": path_part}
        
        elif uri.startswith("order_service_info://"):
            return "get_order_service_info", {}
        
        elif uri.startswith("mcp_info://"):
            return "mcp_info", {}
        
        else:
            # Default fallback
            return uri, {}
