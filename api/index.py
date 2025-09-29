"""Vercel serverless function for MCP server"""
import json

def handler(request, response):
    """Handle HTTP requests"""
    body = request.body

    if request.method == 'GET':
        response.status_code = 200
        return {"status": "ok", "server": "hello-mcp-server"}

    if request.method != 'POST':
        response.status_code = 405
        return {"error": "Method not allowed"}

    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        response.status_code = 400
        return {"error": "Invalid JSON"}

    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id")

    # Handle MCP methods
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "hello-mcp-server",
                    "version": "1.0.0"
                }
            },
            "id": request_id
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "say_hello",
                        "description": "Say hello and get 7 as response",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "The message to send"
                                }
                            },
                            "required": ["message"]
                        }
                    }
                ]
            },
            "id": request_id
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "say_hello":
            message = args.get("message", "")
            if "hello" in message.lower():
                result_text = "7"
            else:
                result_text = f"You said: {message}"

            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                },
                "id": request_id
            }

    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found"
        },
        "id": request_id
    }