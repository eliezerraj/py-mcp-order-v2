# Define environment variables

export VERSION=0.1
export ACCOUNT=local:localhost
export APP_NAME=py-mcp-order-v2
export HOST=127.0.0.1
export PORT=7501
export SESSION_TIMEOUT=700

export ORDER_URL=http://localhost:7001

export METRICS_HOST=0.0.0.0
export METRICS_PORT=8501

export AUTHORIZATION_DRY_RUN=False
export AUTHORIZATION_JWKS_URL=http://localhost:7100/v1/.well-known/jwks.json
export AUTHORIZATION_ISSUER=go-authorizer-v2
export AUTHORIZATION_AUDIENCE=go-ecommerce

export MCP_PROTECTED_RESOURCE=http://localhost:7501
export AUTHORIZATION_SERVER=http://localhost:7100

export LOG_LEVEL=INFO
export OTEL_EXPORTER_OTLP_ENDPOINT=localhost:4317
export OTEL_STDOUT_LOG_GROUP=False
export LOG_GROUP=/mnt/c/Eliezer/log/py-mcp-order-v2.log

# Default target
all: env activate run

# Show environment variables
env:
	@echo "Current Environment Variables:"
	@echo "VERSION=$(VERSION)"
	@echo "APP_NAME=$(APP_NAME)"
	@echo "HOST=$(HOST)"
	@echo "PORT=$(PORT)"
	@echo "SESSION_TIMEOUT=$(SESSION_TIMEOUT)"
	@echo "ORDER_URL=$(ORDER_URL)"
	@echo "METRICS_HOST=$(METRICS_HOST)"
	@echo "METRICS_PORT=$(METRICS_PORT)"
	@echo "AUTHORIZATION_DRY_RUN=$(AUTHORIZATION_DRY_RUN)"
	@echo "AUTHORIZATION_JWKS_URL=$(AUTHORIZATION_JWKS_URL)"
	@echo "AUTHORIZATION_ISSUER=$(AUTHORIZATION_ISSUER)"
	@echo "AUTHORIZATION_AUDIENCE=$(AUTHORIZATION_AUDIENCE)"
	@echo "LOG_GROUP=$(LOG_GROUP)"
	@echo "LOG_LEVEL=$(LOG_LEVEL)"	
	@echo "OTEL_EXPORTER_OTLP_ENDPOINT=$(OTEL_EXPORTER_OTLP_ENDPOINT)"
	@echo "OTEL_STDOUT_LOG_GROUP=$(OTEL_STDOUT_LOG_GROUP)"
activate:
	@echo "Activate venv..."
	@bash -c "source ../../.venv/bin/activate"

# Run the Python application
run:
	@echo "Running application with environment variables..."
	@bash -c "source ../../.venv/bin/activate && python -m src.mcp_server.main"
    
.PHONY: all env activate run