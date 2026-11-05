from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    "mcp_http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "mcp_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

TOOL_CALLS = Counter(
    "mcp_tool_calls_total",
    "Total MCP tool calls",
    ["tool"],
)

TOOL_DURATION = Histogram(
    "mcp_tool_call_duration_seconds",
    "MCP tool execution duration",
    ["tool"],
)

TOOL_ERRORS = Counter(
    "mcp_tool_errors_total",
    "Total MCP tool errors",
    ["tool"],
)

ACTIVE_REQUESTS = Gauge(
    "mcp_active_requests",
    "Currently active MCP requests",
)