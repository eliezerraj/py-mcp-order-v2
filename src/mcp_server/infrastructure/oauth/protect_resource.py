from src.mcp_server.config.settings import settings

PROTECT_RESOURCE_METADATA = {
    "resource": settings.MCP_PROTECTED_RESOURCE + "/mcp",
    "authorization_servers": [
        settings.AUTHORIZATION_SERVER
    ],
    "scopes_supported": [
        "resource:product",
        "tool:post_product",
        "tool:put_product",
        "tool:patch_product",
    ],
    "roles_supported": [
        "inventory-admin-role",
        "inventory-all-role",
        "inventory-resource-role",
        "inventory-tool-role"
    ],
    "bearer_methods_supported": [
        "header",
    ],
}