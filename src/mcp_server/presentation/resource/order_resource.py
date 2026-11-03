import logging
import time

from opentelemetry import trace

from src.mcp_server.config.settings import settings
from src.mcp_server.common.exceptions.app_error import AppError
from src.mcp_server.domain.usecase.order_usecase import OrderUseCase
from src.mcp_server.domain.dto.order import OrderResponse, TimeSeriesResponse
from src.mcp_server.infrastructure.telemetry.metric import (
    TOOL_CALLS,
    TOOL_DURATION, 
    TOOL_ERRORS, 
    ACTIVE_REQUESTS
)

#---------------------------------
# Configure logging
#---------------------------------
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class OrderResource:
    
    def __init__(self, mcp: "MCPServer", order_use_case: "OrderUseCase"):
        self.mcp = mcp
        self.order_use_case = order_use_case
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

                except Exception as e:
                    TOOL_ERRORS.labels(tool="order_service_info://").inc()
                    logger.error(f"Error fetching order service info: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="order_service_info://").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()

                return response

        #---------------------------------
        # get_order
        #---------------------------------    
        @self.mcp.resource("order://{order_number}")
        async def get_order(order_number) -> OrderResponse | dict:
            """
            Retrieves order information for a given order number.
            Use this tool when the user wants to get details about a specific order.
            """
            logger.info(f"Fetching order for order number: {order_number}")
        
            with tracer.start_as_current_span("resource.get_order") as span:
                
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
            
                try:
                    response = await self.order_use_case.get_order(order_number) 
                    TOOL_CALLS.labels(tool="order://{order_number}").inc()
                    
                    order_data = (
                        response.get("order")
                        if isinstance(response, dict) and "order" in response
                        else response
                    )
                    
                    order_response = OrderResponse(
                        id=order_data.get("id") if isinstance(order_data, dict) else None,
                        order_number=order_number,
                        transaction_id=order_data.get("transaction_id") if isinstance(order_data, dict) else None,
                        order_date=order_data.get("order_date") if isinstance(order_data, dict) else None,
                        status=order_data.get("status") if isinstance(order_data, dict) else None,
                        customer_id=order_data.get("customer_id") if isinstance(order_data, dict) else None,
                        currency=order_data.get("currency") if isinstance(order_data, dict) else None,
                        amount=order_data.get("amount") if isinstance(order_data, dict) else None,
                        order_item=order_data.get("order_item") if isinstance(order_data, dict) else None,
                        payment_details=order_data.get("payment_details") if isinstance(order_data, dict) else None
                    )
                    
                except Exception as e:
                    TOOL_ERRORS.labels(tool="order://{order_number}").inc()
                    logger.error(f"Error fetching order for order number {order_number}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="order://{order_number}").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()
            
                return {
                    "response": response.get("response") if isinstance(response, dict) else None,
                    "order": order_response.model_dump(exclude_none=True),
                }

        #---------------------------------
        # get_time_series_order_items
        #---------------------------------
        @self.mcp.resource("time_series_order_items://{product}{?limit,offset}")
        async def get_time_series_order_items(product, limit=7, offset=0) -> TimeSeriesResponse | dict:
            """
            Retrieves time series order items for a given product SKU.
            Use this tool when the user wants to get time series data for a specific product.
            """
            logger.info(f"Fetching time series order items for product: {product}")

            with tracer.start_as_current_span("resource.get_time_series_order_items") as span:
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()

                try:
                    response = await self.order_use_case.get_time_series_order_items(product, limit=limit, offset=offset) 
                    TOOL_CALLS.labels(tool="time_series_order_items://{product}{?limit,offset}").inc()
                    
                    time_series_data = (
                        response.get("time_series_order_items")
                        if isinstance(response, dict) and "time_series_order_items" in response
                        else response
                    )
                    
                    timeSeriesResponse = TimeSeriesResponse(
                        product=time_series_data.get("product") if isinstance(time_series_data, dict) else None,
                        time_series_data=time_series_data.get("time_series_data") if isinstance(time_series_data, dict) else None,
                    )
                                        
                except Exception as e:
                    TOOL_ERRORS.labels(tool="time_series_order_items://{product}{?limit,offset}").inc()
                    logger.error(f"Error fetching time series order items for product {product}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="time_series_order_items://{product}{?limit,offset}").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()
            
                return {
                    "response": response.get("response") if isinstance(response, dict) else None,
                    "time_series_order_items": timeSeriesResponse.model_dump(exclude_none=True) if 'timeSeriesResponse' in locals() else None,
                }
