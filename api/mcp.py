"""Vercel serverless function for MCP server"""
from http.server import BaseHTTPRequestHandler
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP method constants
METHOD_INITIALIZE = "initialize"
METHOD_INITIALIZED = "initialized"
METHOD_PING = "ping"
METHOD_TOOLS_LIST = "tools/list"
METHOD_TOOLS_CALL = "tools/call"
METHOD_RESOURCES_LIST = "resources/list"
METHOD_PROMPTS_LIST = "prompts/list"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "server": "hello-mcp-server"}).encode())

    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, -32700, "Empty request body")
                return

            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                self._send_error(400, -32700, "Parse error: Invalid JSON")
                return

            # Validate JSON-RPC structure
            if not isinstance(data, dict):
                self._send_error(400, -32600, "Invalid Request: Must be an object")
                return

            method = data.get("method")
            if not method:
                self._send_error(400, -32600, "Invalid Request: Missing method field")
                return

            params = data.get("params", {})
            request_id = data.get("id")

            logger.info(f"Processing method: {method}, id: {request_id}")

            response_data = None

            # Handle MCP methods
            if method == METHOD_INITIALIZE:
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

            elif method == METHOD_INITIALIZED:
                # Notification - no response needed
                logger.info("Client initialized")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                return

            elif method == METHOD_PING:
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {},
                    "id": request_id
                }

            elif method == METHOD_TOOLS_LIST:
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": [
                            {
                                "name": "say_hello",
                                "description": "Say hello and get 4 as response",
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

            elif method == METHOD_TOOLS_CALL:
                tool_name = params.get("name")
                if not tool_name:
                    self._send_error(400, -32602, "Invalid params: Missing tool name", request_id)
                    return

                args = params.get("arguments")
                if args is None:
                    self._send_error(400, -32602, "Invalid params: Missing arguments", request_id)
                    return

                if not isinstance(args, dict):
                    self._send_error(400, -32602, "Invalid params: Arguments must be an object", request_id)
                    return

                if tool_name == "say_hello":
                    message = args.get("message")
                    if not message:
                        self._send_error(400, -32602, "Invalid params: Missing required argument 'message'", request_id)
                        return

                    if not isinstance(message, str):
                        self._send_error(400, -32602, "Invalid params: 'message' must be a string", request_id)
                        return

                    if "hello" in message.lower():
                        result_text = "4"
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
                else:
                    self._send_error(400, -32602, f"Unknown tool: {tool_name}", request_id)
                    return

            elif method == METHOD_RESOURCES_LIST:
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {
                        "resources": []
                    },
                    "id": request_id
                }

            elif method == METHOD_PROMPTS_LIST:
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {
                        "prompts": []
                    },
                    "id": request_id
                }

            else:
                self._send_error(404, -32601, f"Method not found: {method}", request_id)
                return

            # Send successful response
            self._send_response(response_data)

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self._send_error(500, -32603, f"Internal error: {str(e)}", request_id if 'request_id' in locals() else None)

    def _send_response(self, data):
        """Send a successful JSON-RPC response"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            logger.error(f"Error sending response: {e}")

    def _send_error(self, http_status, error_code, message, request_id=None):
        """Send a JSON-RPC error response"""
        try:
            error_data = {
                "jsonrpc": "2.0",
                "error": {
                    "code": error_code,
                    "message": message
                },
                "id": request_id
            }
            self.send_response(http_status)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(error_data).encode())
            logger.warning(f"Error response: {error_code} - {message}")
        except Exception as e:
            logger.error(f"Error sending error response: {e}")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()