"""Vercel serverless function for MCP server"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "server": "hello-mcp-server"}).encode())

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")

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
                        "name": "hello-mcp-server",
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

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()