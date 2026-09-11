import logging

from config.settings import settings

logger = logging.getLogger(__name__)

def register_info_tool(mcp: "MCPServer"):
    logger.info("Registering info tool SUCCESSFULLY.")

    @mcp.tool()
    def info_tool():
        """
        Provides general information about the server.
        Use this tool when the user asks for server details or status.
        """
        logger.info("Fetching server information.")
        
        return {"status": settings.__dict__}

    return info_tool