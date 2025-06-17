# Import depdendencies
from mcp.server.fastmcp import FastMCP

# Server created
mcp = FastMCP("Utility Tools")

# Import all the tools (Must be specified after mcp instantiated.)
from tools import *

if __name__ == "__main__":
    mcp.run(transport="sse")