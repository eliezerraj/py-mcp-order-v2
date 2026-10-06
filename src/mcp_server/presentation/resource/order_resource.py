import logging

from opentelemetry import trace

from src.mcp_server.domain.dto.apperrs import AppError
from src.mcp_server.domain.usecase.order_usecase import OrderUseCase
from src.mcp_server.config.settings import settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

def register_order_resource(mcp: "MCPServer", order_use_case: "OrderUseCase"):
    logger.info("Registering order resource SUCCESSFULLY.")
    
    @mcp.resource("mcp_info://")
    def mcp_info():
        """
        Provides general information about the mcp server.
        Use this tool when the user asks for server details or status.
        """
        logger.info("Fetching server information.")
        
        return {"status": settings.__dict__}
    
    @mcp.resource("order_service_info://")
    async def get_order_service_info():
        """
        Retrieves general order service information.
        Use this tool when the user wants to get an overview of the orders.
        """
        logger.info(f"Fetching order service info")
        
        with tracer.start_as_current_span("resource.get_order_service_info"):
            try:
                response = await order_use_case.get_order_service_info() 
            except AppError as e:
                return e.to_dict() 
            except Exception as e:
                logger.error(f"Error fetching order service info: {e}")
                response = {"message": str(e)}
        
        return response

    @mcp.resource("order://{order_number}")
    async def get_order(order_number):
        """
        Retrieves order information for a given order number.
        Use this tool when the user wants to get details about a specific order.
        """
        logger.info(f"Fetching order for order number: {order_number}")
        
        with tracer.start_as_current_span("resource.get_order"):
            try:
                response = await order_use_case.get_order(order_number) 
            except AppError as e:
                return e.to_dict() 
            except Exception as e:
                logger.error(f"Error fetching order for order number {order_number}: {e}")
                response = {"message": str(e)}
        
        return response

    @mcp.resource("time_series_order_items://{product}{?limit,offset}")
    async def get_time_series_order_items(product, limit=7, offset=0):
        """
        Retrieves time series order items for a given product SKU.
        Use this tool when the user wants to get time series data for a specific product.
        """
        logger.info(f"Fetching time series order items for product: {product}")
        
        with tracer.start_as_current_span("resource.get_time_series_order_items"):
            try:
                response = await order_use_case.get_time_series_order_items(product, limit=limit, offset=offset) 
            except AppError as e:
                return e.to_dict() 
            except Exception as e:
                logger.error(f"Error fetching time series order items for product {product}: {e}")
                response = {"message": str(e)}
        
        return response
        
    return get_order, get_order_service_info, get_time_series_order_items, mcp_info