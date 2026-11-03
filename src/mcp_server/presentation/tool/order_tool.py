import logging
import time

from opentelemetry import trace

from src.mcp_server.config.settings import settings
from src.mcp_server.domain.dto.context import SecurityContext
from src.mcp_server.domain.dto.order import OrderPayload, OrderResponse, CheckoutPayload, CheckoutResponse
from src.mcp_server.domain.usecase.order_usecase import OrderUseCase

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

class OrderTool:
    def __init__(self, mcp: "MCPServer", order_use_case: OrderUseCase):
        self.mcp = mcp
        self.order_use_case = order_use_case
        logger.info("OrderTool initialized SUCCESSFULLY.")
        
    def register_order_tool(self):
        logger.info("Registering order tool SUCCESSFULLY.")

        #---------------------------------
        # post_order
        #---------------------------------    
        @self.mcp.tool()
        async def post_order(payload: OrderPayload) -> OrderResponse | dict:
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
                    
            with tracer.start_as_current_span("tool.post_order") as span:  
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
                                    
                try:
                    response = await self.order_use_case.post_order(payload.model_dump(exclude_none=True)) 
                    TOOL_CALLS.labels(tool="post_order").inc()
                    
                    order_data = (
                        response.get("order")
                        if isinstance(response, dict) and "order" in response
                        else response
                    )
                    
                    order_response = OrderResponse(
                        id=order_data.get("id") if isinstance(order_data, dict) else None,
                        order_number=order_data.get("order_number") if isinstance(order_data, dict) else None,
                        transaction_id=order_data.get("transaction_id") if isinstance(order_data, dict) else None,
                        order_date=order_data.get("order_date") if isinstance(order_data, dict) else None,
                        status=order_data.get("status") if isinstance(order_data, dict) else None,
                        customer_id=order_data.get("customer_id") if isinstance(order_data, dict) else None,
                        currency=order_data.get("currency") if isinstance(order_data, dict) else None,
                        amount=order_data.get("amount") if isinstance(order_data, dict) else None,
                        order_item=order_data.get("order_item") if isinstance(order_data, dict) else None,
                    )
                    
                except Exception as e:
                    TOOL_ERRORS.labels(tool="post_order").inc()
                    logger.error(f"Error creating order with payload {payload}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="post_order").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()

                return {
                    "response": response.get("response") if isinstance(response, dict) else None,
                    "order": order_response.model_dump(exclude_none=True),
                }
            
        #---------------------------------
        # post_checkout
        #---------------------------------    
        @self.mcp.tool()
        async def post_checkout(payload: CheckoutPayload):
            """
            Creates a new checkout with the given payload. Use this tool when the user wants to create a new checkout.
            
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

            with tracer.start_as_current_span("tool.post_checkout") as span:
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
                
                try:
                    response = await self.order_use_case.post_checkout(payload.model_dump(exclude_none=True)) 
                    TOOL_CALLS.labels(tool="post_checkout").inc()
                
                    checkout_data = (
                        response.get("checkout")
                        if isinstance(response, dict) and "checkout" in response
                        else response
                    )
                           
                    checkoutResponse = CheckoutResponse(
                        order=checkout_data.get("order") if isinstance(checkout_data, dict) else None,
                        payment=checkout_data.get("payment") if isinstance(checkout_data, dict) else None,
                    )
                except Exception as e:
                    TOOL_ERRORS.labels(tool="post_checkout").inc()
                    logger.error(f"Error creating checkout with payload {payload}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="post_checkout").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()
            
                return {
                    "response": response.get("response") if isinstance(response, dict) else None,
                    "order": checkoutResponse.model_dump(exclude_none=True),
                }
        