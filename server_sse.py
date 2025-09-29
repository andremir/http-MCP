#!/usr/bin/env python3
"""FastMCP server with SSE transport for claude.ai"""

from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("hello-mcp-server")

@mcp.tool()
def say_hello(message: str) -> str:
    """Say hello and get 4 as response"""
    if "hello" in message.lower():
        return "4"
    return f"You said: {message}"

if __name__ == "__main__":
    # Run with SSE transport for web compatibility
    # This needs to be deployed to a public URL
    mcp.run(transport="sse", host="0.0.0.0", port=8000)