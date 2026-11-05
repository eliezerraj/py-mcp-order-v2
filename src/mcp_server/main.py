import logging
import uvicorn

from prometheus_client import start_http_server

from mcp_server.transport.http.app import create_app
from mcp_server.config.settings import settings

logger = logging.getLogger(__name__)

# Create FastAPI application instance with Prometheus middleware
app = create_app()

# Server entrypoint execution handler
def run():
    logger.info(f"Starting METRICS SERVER: {settings.METRICS_HOST}:{settings.METRICS_PORT}")
    start_http_server(port=int(settings.METRICS_PORT), 
                      addr=settings.METRICS_HOST
    )
    
    logger.info(f"Starting SERVER: {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        app,
        host=settings.HOST,
        port=int(settings.PORT),
        log_level=settings.LOG_LEVEL.lower(),
    )

if __name__ == "__main__":
    run()