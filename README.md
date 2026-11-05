# py-mcp-order-v2
py-mcp-order-v2

### create venv
```sh
# run only if the env not exists
python3 -m venv .venv
```
### activate
```sh
# env installed 2 folder above
source ../../.venv/bin/activate
```
### install dependecies
```sh
pip install -e .
```
### run
```sh
python -m app.main
```

## run mcp inspector
```sh
# Session 1
npx @modelcontextprotocol/inspector

# Sesssion 2 (venv activated)
python -m app.main

# Setup Transport Type: streamable http
http://localhost:5000/mcp
```

## MCP transport security

Configure allowed hosts and origins using comma-separated environment variables:

```sh
export ENABLE_DNS_REBINDING_PROTECTION=True
export ALLOWED_HOSTS="localhost:*,127.0.0.1:*,py-mcp-order-v2:*,py-mcp-order-v2.architecture.xpto.io"
export ALLOWED_ORIGINS="http://localhost:*,http://127.0.0.1:*,http://py-mcp-order-v2:*,https://py-mcp-order-v2.architecture.xpto.io"
```

Whitespace around entries and empty entries are ignored. When unset, the lists
default to the local hosts and origins shown in the Makefile. Explicitly empty
values produce empty lists.

These lists apply only when `ENABLE_DNS_REBINDING_PROTECTION=True` (default:
`False`). MCP supports exact matches and wildcard ports (`:*`), not a standalone
`*` wildcard. Kubernetes values are configured in
[`configmap.yaml`](assets/kubernetes/aws/configmap.yaml); restart the deployment
after updating its environment variables.