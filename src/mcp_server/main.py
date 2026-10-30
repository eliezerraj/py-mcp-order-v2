import sys
import logging
import httpx
import uvicorn

from threading import Thread

from contextlib import asynccontextmanager
from opentelemetry import trace

from prometheus_client import make_asgi_app

from src.mcp_server.infrastructure.adapter.http import HttpAdapter
from src.mcp_server.presentation.resource.order_resource import OrderResource
from src.mcp_server.presentation.tool.order_tool import OrderTool

from src.mcp_server.infrastructure.middleware.middleware import RequestContextMiddleware
from src.mcp_server.infrastructure.middleware.middleware_metric import PrometheusMiddleware
from src.mcp_server.infrastructure.middleware.middleware_cedar_auth import CedarAuthorizationMiddleware
from src.mcp_server.infrastructure.telemetry.tracer import setup_tracer

from src.mcp_server.domain.usecase.order_usecase import OrderUseCase

from src.mcp_server.config.logger import setup_logger
from src.mcp_server.config.settings import settings

from mcp.server.transport_security import TransportSecuritySettings
from mcp.server.mcpserver import MCPServer

from src.mcp_server.presentation.prompt.order_prompt import (
    register_prompt as register_order_prompt,
)

from src.mcp_server.infrastructure.oauth.protect_resource import PROTECT_RESOURCE_METADATA

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

setup_logger(settings.LOG_LEVEL, 
             settings.APP_NAME, 
             settings.OTEL_STDOUT_LOG_GROUP, 
             settings.LOG_GROUP)

logger = logging.getLogger(__name__)
    
# Setup OpenTelemetry tracer
setup_tracer(settings.APP_NAME, 
             settings.OTEL_EXPORTER_OTLP_ENDPOINT)

tracer = trace.get_tracer(__name__)
  
# -------------------------------------------------------------------
# MCP lifespan
# -------------------------------------------------------------------       
@asynccontextmanager
async def server_lifespan(app):
    logger.info("Initializing Enterprise MCP Server resources SUCCESSFULLY...")
    
    try:
        # Initialize HTTP client for inventory service
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.SESSION_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        ) as http_client:
        
            # Initialize inventory adapter with the inventory service URL
            http_adapter = HttpAdapter(settings.ORDER_URL)
            
            # Initialize order use case
            order_usecase = OrderUseCase(http_adapter)
            
            # Register order tool with the MCP server
            order_tool = OrderTool(mcp, order_usecase)
            order_tool.register_order_tool()

            # Register order prompts
            register_order_prompt(mcp)

            # Register resource
            order_resource = OrderResource(mcp, order_usecase)
            order_resource.register_order_resource()
        
        yield
    
    finally:
        logger.info("Server shutting down SUCCESSFULLY.")

# -------------------------------------------------------------------
# Transport security
# -------------------------------------------------------------------
transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "localhost:*",
        "127.0.0.1:*",
        "py-mcp-order-v2:*",
    ],
    allowed_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://py-mcp-order-v2:*",
    ],
)

# -------------------------------------------------------------------
# OAuth Protected Resource Metadata
# -------------------------------------------------------------------
async def oauth_protected_resource_metadata(request: Request) -> JSONResponse:
    logger.info("Handling /.well-known/oauth-protected-resource request")
    return JSONResponse(
        content=PROTECT_RESOURCE_METADATA,
        headers={
            "Cache-Control": "public, max-age=300",
        },
    )
    
#---------------------------------
# setup MCP server
#---------------------------------
mcp = MCPServer(name=settings.APP_NAME,
                lifespan=server_lifespan,
                debug=True,
)

# Add middleware to the MCP server application (ASGI compatible)
mcp_app = mcp.streamable_http_app(transport_security=transport_security)
mcp_app.add_middleware(RequestContextMiddleware)
#mcp_app.add_middleware(CedarAuthorizationMiddleware)
mcp_app.add_middleware(PrometheusMiddleware)

# ---------------------------------
# OAuth application lifespan
# ---------------------------------
@asynccontextmanager
async def application_lifespan(app: Starlette):
    async with mcp.session_manager.run():
        yield

# Define routes
routes = [
    Route(
        "/.well-known/oauth-protected-resource",
        endpoint=oauth_protected_resource_metadata,
        methods=["GET"],
        name="oauth-protected-resource-metadata",
    ),
    Mount(
        "/",
        app=mcp_app,
        name="mcp",
    ),
]

app = Starlette(
    routes=routes,
    lifespan=application_lifespan,
)

# Log registered routes
print("Registered routes:")
for route in app.routes:
    print(f"  - {route.path if hasattr(route, 'path') else route}")
    
# ---------------------------------
# Prometheus server
# ---------------------------------
metrics_app = make_asgi_app()

def run_metrics_server():
    logger.info(f"PROMETHEUS SERVER: "f"{settings.METRICS_HOST}:{settings.METRICS_PORT}")

    uvicorn.run(
        metrics_app,
        host=settings.METRICS_HOST,
        port=int(settings.METRICS_PORT),
        log_level=settings.LOG_LEVEL.lower(),
    )

# ---------------------------------
# Server entrypoint function
# ---------------------------------
def run():
    """Server entrypoint execution handler."""
    try:
        
        # Start Prometheus server
        metrics_thread = Thread(
            target=run_metrics_server,
            name="prometheus-server",
            daemon=True,
        )

        metrics_thread.start()
        
        # Start MCP server
        logger.info(f"SERVER: {settings.HOST}:{settings.PORT}")
        
        uvicorn.run(app, 
                    host=settings.HOST, 
                    port=int(settings.PORT),
                    log_level=settings.LOG_LEVEL.lower(),
                    )
    except Exception as e:
        logger.error(f"Server encountered an error: {e}")
        sys.exit(1)
    finally:
        logger.info("Server stopped SUCCESSFULLY.")

# Run the server if this script is executed directly
if __name__ == "__main__":
    run()