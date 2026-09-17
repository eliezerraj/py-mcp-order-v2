import logging

from src.mcp_server.domain.usecase.order_usecase import OrderUseCase

from src.mcp_server.config.settings import settings

logger = logging.getLogger(__name__)

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
        
        try:
            response = await order_use_case.get_order_service_info() 
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
        
        try:
            response = await order_use_case.get_order(order_number) 
        except Exception as e:
            logger.error(f"Error fetching order for order number {order_number}: {e}")
            response = {"message": str(e)}
        
        return response
    
    return get_order, get_order_service_info, mcp_info