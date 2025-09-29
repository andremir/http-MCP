"""Vercel serverless function with OAuth support for MCP"""
from http.server import BaseHTTPRequestHandler
import json
import secrets
from urllib.parse import parse_qs, urlparse

# Simple in-memory token store (in production, use a database)
# Vercel functions are stateless, so this is just for demonstration
VALID_TOKENS = {"demo-token-123": True}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle OAuth flow and authorization"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == "/api/oauth/authorize":
            # OAuth authorization endpoint
            redirect_uri = query_params.get("redirect_uri", [""])[0]
            state = query_params.get("state", [""])[0]

            # Generate a simple authorization code
            auth_code = "auth_" + secrets.token_urlsafe(16)

            # Redirect back to Claude with authorization code
            redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"

            self.send_response(302)
            self.send_header("Location", redirect_url)
            self.end_headers()

        elif path == "/api/oauth/token":
            # Token exchange endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Return a simple access token
            token_response = {
                "access_token": "demo-token-123",
                "token_type": "Bearer",
                "expires_in": 3600
            }
            self.wfile.write(json.dumps(token_response).encode())

        else:
            # Default response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "oauth": "enabled"}).encode())

    def do_POST(self):
        """Handle MCP requests with OAuth token validation"""
        content_length = int(self.headers.get('Content-Length', 0))

        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
        else:
            data = {}

        # Check for OAuth token in Authorization header
        auth_header = self.headers.get("Authorization", "")
        if auth_header and not auth_header.startswith("Bearer demo-token"):
            # If token is provided but invalid, reject
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid token"}).encode())
            return

        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")

        response_data = None

        # Handle OAuth token endpoint
        if self.path == "/api/oauth/token":
            code = data.get("code")
            grant_type = data.get("grant_type")

            response_data = {
                "access_token": "demo-token-123",
                "token_type": "Bearer",
                "expires_in": 3600
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            return

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
                        "name": "hello-mcp-oauth",
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()