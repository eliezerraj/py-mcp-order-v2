# Define environment variables

export VERSION=0.1
export ACCOUNT=local:localhost
export APP_NAME=py-mcp-order-v2
export HOST=127.0.0.1
export PORT=7501
export SESSION_TIMEOUT=700

export ORDER_URL=http://localhost:7001

export LOG_LEVEL=INFO
export OTEL_EXPORTER_OTLP_ENDPOINT=localhost:4317
export OTEL_STDOUT_LOG_GROUP=True
export LOG_GROUP=/mnt/c/Eliezer/log/py-mcp-order-v2.log
export MCP_VALIDATE_CONTEXT=false

# Default target
all: env activate run

# Show environment variables
env:
	@echo "Current Environment Variables:"
	@echo "VERSION=$(VERSION)"
	@echo "APP_NAME=$(APP_NAME)"
	@echo "LOG_LEVEL=$(LOG_LEVEL)"
	@echo "ORDER_URL=$(ORDER_URL)"
activate:
	@echo "Activate venv..."
	@bash -c "source ../../.venv/bin/activate"

# Run the Python application
run:
	@echo "Running application with environment variables..."
	@bash -c "source ../../.venv/bin/activate && python -m src.mcp_server.main"
    
.PHONY: all env activate run