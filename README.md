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