import logging
import time

from starlette.requests import Request

from src.mcp_server.infrastructure.telemetry.metric import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
)

logger = logging.getLogger(__name__)

class PrometheusMiddleware:

    def __init__(self, app):
        self.app = app
        logger.info("Initializing PrometheusMiddleware SUCCESSFULLY")

    async def __call__(self, scope, receive, send):

        # Only instrument HTTP requests
        if scope["type"] != "http":
            await self.app(scope,receive,send,)
            return

        request = Request(scope, receive,)

        start_time = time.perf_counter()

        # Default status in case the application
        # fails before sending a response.
        status_code = 500

        async def send_wrapper(message):

            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]

            await send(message)

        try:

            await self.app(scope,receive,send_wrapper,)

        except Exception:
            # Keep the original exception behavior.
            raise
        finally:
            duration = (time.perf_counter() - start_time)

            method = request.method
            path = request.url.path

            REQUEST_COUNT.labels(
                method=method,
                path=path,
                status=str(status_code),
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                path=path,
            ).observe(duration)