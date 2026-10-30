import logging

from src.mcp_server.presentation.prompt.templates.order_prompt_templates import (
    ORDER_OVERVIEW_PROMPT,
)

logger = logging.getLogger(__name__)

def register_prompt(mcp: "MCPServer") -> None:
    """
    Register all MCP prompts.
    """

    register_order_prompt(mcp)
    
def register_order_prompt(mcp: "MCPServer") -> None:
    """
    Register order-related MCP prompts.

    MCP prompts provide reusable interaction templates for
    order analysis and monitoring workflows.
    """

    @mcp.prompt()
    def order_overview() -> str:
        """
        Start an order overview and monitoring workflow.

        Use this prompt when the user wants to understand the
        current state of the orders and identify orders
        that may require attention.
        """

        logger.info("Order overview prompt requested")

        return ORDER_OVERVIEW_PROMPT
