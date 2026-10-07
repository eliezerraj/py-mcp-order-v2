import sys
import logging
import httpx
import uvicorn

from threading import Thread

from contextlib import asynccontextmanager
from opentelemetry import trace

from prometheus_client import make_asgi_app

from src.mcp_server.infrastructure.adapter.http import HttpAdapter
from src.mcp_server.infrastructure.middleware.middleware import RequestContextMiddleware
from src.mcp_server.infrastructure.middleware.middleware_metric import PrometheusMiddleware
from src.mcp_server.infrastructure.telemetry.tracer import setup_tracer

from src.mcp_server.domain.usecase.order_usecase import OrderUseCase
from src.mcp_server.presentation.tool.order_tool import register_order_tool
from src.mcp_server.config.logger import setup_logger
from src.mcp_server.config.settings import settings

from mcp.server.mcpserver import MCPServer

from src.mcp_server.presentation.prompt.order_prompt import (
    register_prompt as register_order_prompt,
)

from src.mcp_server.presentation.resource.order_resource import register_order_resource

setup_logger(settings.LOG_LEVEL, 
             settings.APP_NAME, 
             settings.OTEL_STDOUT_LOG_GROUP, 
             settings.LOG_GROUP)

logger = logging.getLogger(__name__)
    
# Setup OpenTelemetry tracer
setup_tracer(settings.APP_NAME, 
             settings.OTEL_EXPORTER_OTLP_ENDPOINT)
tracer = trace.get_tracer(__name__)
    
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
            register_order_tool(mcp, order_usecase)

            # Register order prompts
            register_order_prompt(mcp)

            # Register resource
            register_order_resource(mcp, order_usecase)
        
        yield
    finally:
        logger.info("Server shutting down SUCCESSFULLY.")

#---------------------------------
# setup MCP server
#---------------------------------
mcp = MCPServer(name=settings.APP_NAME,
                lifespan=server_lifespan,
                debug=True,
)

# Add middleware to the MCP server application (ASGI compatible)
mcp_app = mcp.streamable_http_app()
mcp_app.add_middleware(RequestContextMiddleware)
mcp_app.add_middleware(PrometheusMiddleware)

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
        log_level=settings.LOG_LEVEL,
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
        
        uvicorn.run(mcp_app, 
                    host=settings.HOST, 
                    port=int(settings.PORT))
        
    except Exception as e:
        logger.error(f"Server encountered an error: {e}")
        sys.exit(1)
    finally:
        logger.info("Server stopped SUCCESSFULLY.")

# Run the server if this script is executed directly
if __name__ == "__main__":
    run()