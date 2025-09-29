"""Vercel serverless function with SSE support for MCP"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for SSE"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Send initial SSE connection
        self.wfile.write(b"data: connected\n\n")
        self.wfile.flush()

    def do_POST(self):
        """Handle POST requests for SSE transport"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")

        # Set SSE headers
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        response_data = None

        # Handle MCP methods
        if method == "initialize":
            response_data = {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "hello-mcp-sse",
                        "version": "1.0.0"
                    }
                },
                "id": request_id
            }

        elif method == "tools/list":
            response_data = {
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

                response_data = {
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

        elif method == "resources/list":
            response_data = {
                "jsonrpc": "2.0",
                "result": {
                    "resources": []
                },
                "id": request_id
            }

        elif method == "prompts/list":
            response_data = {
                "jsonrpc": "2.0",
                "result": {
                    "prompts": []
                },
                "id": request_id
            }

        if not response_data:
            response_data = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                },
                "id": request_id
            }

        # Send as SSE event
        event_data = f"data: {json.dumps(response_data)}\n\n"
        self.wfile.write(event_data.encode())
        self.wfile.flush()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()