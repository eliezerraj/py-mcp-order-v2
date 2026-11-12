import logging
logger = logging.getLogger(__name__)

def register_prompt(mcp: "MCPServer") -> None:
    """ Register all MCP prompts. """

    register_order_prompt(mcp)
    
def register_order_prompt(mcp: "MCPServer") -> None:
    """ Register order-related MCP prompts. """

    @mcp.prompt()
    def order_retrieve(order_number: str) -> str:
        """ Start an order retrieval workflow for the given order ID. """

        if not order_number:
            raise ValueError("order_number is required")

        return (
            f"Retrieve order details for order ID: {order_number}\n\n"
            f"Show all details for the order {order_number}\n\n"
        )

    @mcp.prompt()
    def order_create(order_number: str, customer_id: str, order_date: str, sku: str, quantity: int ) -> str:
        """ Start an order creation workflow for the given order ID. """

        if not order_number:
            raise ValueError("order_number is required")
        if not customer_id:
            raise ValueError("customer_id is required")
        if not order_date:
            raise ValueError("order_date is required")
        if not sku:
            raise ValueError("sku is required")
        if not quantity:
            raise ValueError("quantity is required")

        return (
            f"Create a new order with order ID: {order_number} for customer ID: {customer_id} on order date: {order_date} with the following items: SKU: {sku}, Quantity: {quantity}\n\n"
            f"Include the following order with the following data {'order_number': '{order_number}', 'customer_id': '{customer_id}', 'order_date': '{order_date}'} items: SKU: {sku}, Quantity: {quantity}\n\n"
        )

    @mcp.prompt()
    def order_checkout(order_number: str, currency: str, amount: float, pan: str, holder_name: str) -> str:
        """ Start an order checkout workflow for the given order ID. """

        if not order_number:
            raise ValueError("order_number is required")
        if not currency:
            raise ValueError("currency is required")
        if not amount:
            raise ValueError("amount is required")
        if not pan:
            raise ValueError("pan is required")
        if not holder_name:
            raise ValueError("holder_name is required")

        return (
            f"Checkout order with order ID: {order_number} using currency: {currency} and amount: {amount} with PAN: {pan} and holder name: {holder_name}\n\n"
            f"Proceed to checkout for the order {order_number} with currency {currency} and amount {amount} with PAN: {pan} and holder name: {holder_name}\n\n"
        )
