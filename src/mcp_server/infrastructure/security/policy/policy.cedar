// RESOURCE_CALL 
permit(
    principal,
    action == Action::"call_resource",
    resource == Resource::"get_order"
)
when {
    principal.roles.contains("order-resource-role")
};

permit(
    principal,
    action == Action::"call_resource",
    resource == Resource::"get_order_service_info"
)
when {
    principal.roles.contains("order-resource-role")
};

permit(
    principal,
    action == Action::"call_resource",
    resource == Resource::"get_time_series_order_items"
)
when {
    principal.roles.contains("order-resource-role")
};

// TOOL_CALLS

permit(
    principal,
    action == Action::"call_tool",
    resource == Tool::"post_order"
)
when {
    principal.roles.contains("order-resource-role")
};

permit(
    principal,
    action == Action::"call_tool",
    resource == Tool::"post_checkout"
)
when {
    principal.roles.contains("order-resource-role")
};