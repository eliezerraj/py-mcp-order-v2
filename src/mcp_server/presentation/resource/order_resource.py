import logging
import time

from opentelemetry import trace

from src.mcp_server.common.exceptions.app_error import AppError
from src.mcp_server.infrastructure.auth.cedar_verifier import CedarVerifier
from src.mcp_server.domain.usecase.order_usecase import OrderUseCase
from src.mcp_server.infrastructure.telemetry.metric import (
    TOOL_CALLS,
    TOOL_DURATION, 
    TOOL_ERRORS, 
    ACTIVE_REQUESTS
)

from src.mcp_server.config.settings import settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class OrderResource:
    
    def __init__(self, mcp: "MCPServer", order_use_case: "OrderUseCase"):
        self.mcp = mcp
        self.order_use_case = order_use_case
        
        self.cedar_verifier = CedarVerifier()
        logger.info("OrderResource initialized SUCCESSFULLY.")

    def register_order_resource(self):
        logger.info("Registering order resource SUCCESSFULLY.")
        
        @self.mcp.resource("mcp_info://")
        def mcp_info():
            """
            Provides general information about the mcp server.
            Use this tool when the user asks for server details or status.
            """
            logger.info("Fetching server information.")
            
            return {"status": settings.__dict__}
        
        @self.mcp.resource("order_service_info://")
        async def get_order_service_info():
            """
            Retrieves general order service information.
            Use this tool when the user wants to get an overview of the orders.
            """
            logger.info(f"Fetching order service info")
            
            with tracer.start_as_current_span("resource.get_order_service_info") as span:
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
                
                try:
                    response = await self.order_use_case.get_order_service_info() 
                    TOOL_CALLS.labels(tool="order_service_info://").inc()
                except AppError as e:
                    return e.to_dict() 
                except Exception as e:
                    TOOL_ERRORS.labels(tool="order_service_info://").inc()
                    logger.error(f"Error fetching order service info: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="order_service_info://").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()

                return response

        @self.mcp.resource("order://{order_number}")
        async def get_order(order_number):
            """
            Retrieves order information for a given order number.
            Use this tool when the user wants to get details about a specific order.
            """
            logger.info(f"Fetching order for order number: {order_number}")
        
            with tracer.start_as_current_span("resource.get_order") as span:
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
            
                try:
                    
                    if settings.AUTHORIZATION_DRY_RUN:
                        logger.info("Authorization dry run enabled, skipping Cedar verification.")
                    else:
                        self.cedar_verifier.validate(
                            action="call_resource",
                            resource_type="Resource",
                            resource_id="get_order",
                            resource_attrs={"data": order_number},
                        )
                    
                    response = await self.order_use_case.get_order(order_number) 
                    TOOL_CALLS.labels(tool="order://{order_number}").inc()
                except AppError as e:
                    return e.to_dict() 
                except Exception as e:
                    TOOL_ERRORS.labels(tool="order://{order_number}").inc()
                    logger.error(f"Error fetching order for order number {order_number}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="order://{order_number}").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()
            
                return response

        @self.mcp.resource("time_series_order_items://{product}{?limit,offset}")
        async def get_time_series_order_items(product, limit=7, offset=0):
            """
            Retrieves time series order items for a given product SKU.
            Use this tool when the user wants to get time series data for a specific product.
            """
            logger.info(f"Fetching time series order items for product: {product}")

            with tracer.start_as_current_span("resource.get_time_series_order_items") as span:
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()

                try:
                    
                    if settings.AUTHORIZATION_DRY_RUN:
                        logger.info("Authorization dry run enabled, skipping Cedar verification.")
                    else:
                        self.cedar_verifier.validate(
                            action="call_resource",
                            resource_type="Resource",
                            resource_id="get_time_series_order_items",
                            resource_attrs={"data": product},
                        )
                        
                    response = await self.order_use_case.get_time_series_order_items(product, limit=limit, offset=offset) 
                    TOOL_CALLS.labels(tool="time_series_order_items://{product}{?limit,offset}").inc()
                except AppError as e:
                    return e.to_dict() 
                except Exception as e:
                    TOOL_ERRORS.labels(tool="time_series_order_items://{product}{?limit,offset}").inc()
                    logger.error(f"Error fetching time series order items for product {product}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="time_series_order_items://{product}{?limit,offset}").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()
            
                return response
