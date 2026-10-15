forbid(
    principal,
    action,
    resource
)
when {
    principal.client_id == "blocked-client"
};

// RESOURCE_CALL 

permit(
    principal,
    action == Action::"call_resource",
    resource == Resource::"get_order"
)
when {
    principal.scopes.contains("order:read")
};

permit(
    principal,
    action == Action::"call_resource",
    resource == Resource::"get_time_series_order_items"
)
when {
    principal.scopes.contains("order:history")
};

// TOOL_CALLS

permit(
    principal,
    action == Action::"call_tool",
    resource == Tool::"post_order"
)
when {
    principal.scopes.contains("order:create")
};

permit(
    principal,
    action == Action::"call_tool",
    resource == Tool::"post_checkout"
)
when {
    principal.scopes.contains("checkout:create")
};