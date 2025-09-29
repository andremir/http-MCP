#!/usr/bin/env python3
"""FastMCP server for Claude Desktop (stdio transport)"""

from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("hello-mcp-server")

@mcp.tool()
def say_hello(message: str) -> str:
    """Say hello and get 4 as response"""
    if "hello" in message.lower():
        return "4"
    return f"You said: {message}"

def main():
    """Entry point for pipx"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()