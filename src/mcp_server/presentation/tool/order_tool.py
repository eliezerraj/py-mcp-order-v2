import logging
import time

from src.mcp_server.infrastructure.auth.cedar_verifier import CedarVerifier

from opentelemetry import trace

from src.mcp_server.infrastructure.telemetry.metric import TOOL_CALLS, TOOL_DURATION, TOOL_ERRORS, ACTIVE_REQUESTS
from src.mcp_server.config.settings import settings
from src.mcp_server.domain.dto.context import SecurityContext
from src.mcp_server.domain.dto.order import OrderPayload
from src.mcp_server.domain.dto.checkout import CheckoutPayload
from src.mcp_server.domain.usecase.order_usecase import OrderUseCase

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class OrderTool:
    def __init__(self, mcp: "MCPServer", order_use_case: OrderUseCase):
        self.mcp = mcp
        self.order_use_case = order_use_case
        
        self.cedar_verifier = CedarVerifier()
        logger.info("OrderTool initialized SUCCESSFULLY.")
        
    def register_order_tool(self):
        logger.info("Registering order tool SUCCESSFULLY.")

        @self.mcp.tool()
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
                    
            with tracer.start_as_current_span("tool.post_order"):
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
                
                try:
                    
                    if settings.AUTHORIZATION_DRY_RUN:
                        logger.info("Authorization dry run enabled, skipping Cedar verification.")
                    else:
                        self.cedar_verifier.validate(
                            action="call_tool",
                            resource_type="Tool",
                            resource_id="post_order",
                            resource_attrs={"data": payload.model_dump()},
                        )
                    
                    response = await self.order_use_case.post_order(payload.model_dump()) 
                    TOOL_CALLS.labels(tool="post_order").inc()
                except Exception as e:
                    TOOL_ERRORS.labels(tool="post_order").inc()
                    logger.error(f"Error creating order with payload {payload}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="post_order").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()

                return response

        @self.mcp.tool()
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

            with tracer.start_as_current_span("tool.post_checkout"):
                ACTIVE_REQUESTS.inc()
                start_time = time.perf_counter()
                
                try:
                    
                    if settings.AUTHORIZATION_DRY_RUN:
                        logger.info("Authorization dry run enabled, skipping Cedar verification.")
                    else:
                        self.cedar_verifier.validate(
                            action="call_tool",
                            resource_type="Tool",
                            resource_id="post_checkout",
                            resource_attrs={"data": payload.model_dump()},
                        )
                      
                    response = await self.order_use_case.post_checkout(payload.model_dump()) 
                    TOOL_CALLS.labels(tool="post_checkout").inc()
                except Exception as e:
                    TOOL_ERRORS.labels(tool="post_checkout").inc()
                    logger.error(f"Error creating checkout with payload {payload}: {e}")
                    response = {"message": str(e)}
                finally:
                    TOOL_DURATION.labels(tool="post_checkout").observe(time.perf_counter() - start_time)
                    ACTIVE_REQUESTS.dec()
            
                return response
        