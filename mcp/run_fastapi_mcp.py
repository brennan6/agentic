from fastapi import FastAPI # Import your existing app, if defined elsewhere
from fastapi_mcp import FastApiMCP

# Your FastAPI app
app = FastAPI()

# Create and mount the MCP server directly to your FastAPI app
mcp = FastApiMCP(app)
mcp.mount()