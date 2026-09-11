import logging

from src.mcp_server.domain.dto.context import SecurityContext
from src.mcp_server.domain.dto.order import OrderPayload
from src.mcp_server.domain.dto.checkout import CheckoutPayload
from src.mcp_server.domain.usecase.order_usecase import OrderUseCase

logger = logging.getLogger(__name__)
    
def register_order_tool(mcp: "MCPServer", order_use_case: OrderUseCase):
    logger.info("Registering order tool SUCCESSFULLY.")

    @mcp.tool()
    async def get_order_info():
        """
        Retrieves general order information.
        Use this tool when the user wants to get an overview of the orders.
        """
        logger.info(f"Fetching order info")
        
        try:
            response = await order_use_case.get_order_info() 
        except Exception as e:
            logger.error(f"Error fetching order info: {e}")
            response = {"message": str(e)}
        
        return response

    @mcp.tool()
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

    @mcp.tool()
    async def post_order(payload: OrderPayload):
        """
        Creates a new order with the given payload.
        Use this tool when the user wants to create a new order.
        
        The order must contain:
        - order_number: The unique identifier for the order.
        - customer_id: The identifier for the customer placing the order.
        - order_date: The date when the order was placed.
        - order_item: A list of items included in the order
            - product: The product details of the item.
                - sku: The unique identifier for the item.
            - quantity: The quantity of the item.
            - price: The price of the item.
        """
        logger.info(f"Creating order with payload: {payload}")
        
        try:
            response = await order_use_case.post_order(payload.model_dump()) 
        except Exception as e:
            logger.error(f"Error creating order with payload {payload}: {e}")
            response = {"message": str(e)}
        
        return response

    @mcp.tool()
    async def post_checkout(payload: CheckoutPayload):
        """
        Creates a new checkout with the given payload.
        Use this tool when the user wants to create a new checkout.
        
        The checkout must contain:
        - order: The order details for the checkout.
            - order_number: The unique identifier for the order.
        - payment: The payment details for the checkout.
            - type: The payment method used.
            - payment_detail: A list of payment details
                - currency: The ISO 4217 currency code.
                - amount: The payment amount.
                - credit_card: The credit card details if applicable.
        """
        logger.info(f"Creating checkout with payload: {payload}")
        
        try:
            response = await order_use_case.post_checkout(payload.model_dump()) 
        except Exception as e:
            logger.error(f"Error creating checkout with payload {payload}: {e}")
            response = {"message": str(e)}
        
        return response    
    return get_order_info, get_order, post_order, post_checkout