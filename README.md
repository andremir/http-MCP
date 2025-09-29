# Hello MCP Server

A simple MCP server that responds with "4" when you say "hello".

## Installation

### Option 1: Using uvx (Recommended)
```bash
# No installation needed, just add to Claude Desktop config
```

### Option 2: Using pipx
```bash
pipx install git+https://github.com/andrebacellardemiranda/http-MCP.git
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

### With uvx (Recommended - no installation):
```json
{
  "mcpServers": {
    "hello": {
      "command": "uvx",
      "args": ["hello-mcp-server@git+https://github.com/andrebacellardemiranda/http-MCP.git"]
    }
  }
}
```

### With pipx (after installation):
```json
{
  "mcpServers": {
    "hello": {
      "command": "hello-mcp-server"
    }
  }
}
```

## Usage

Once configured, restart Claude Desktop. You can then say "hello" and get "4" as response.

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python server_stdio.py
```