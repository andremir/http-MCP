"""Vercel serverless function for MCP SSE server"""
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json
import asyncio
from typing import AsyncGenerator

app = FastAPI()

def say_hello(message: str) -> str:
    """Say hello and get 7 as response"""
    if "hello" in message.lower():
        return "7"
    return f"You said: {message}"

async def event_stream() -> AsyncGenerator[str, None]:
    """Generate SSE events"""
    # Send initial connection event
    yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"

    # Keep connection alive
    while True:
        await asyncio.sleep(30)
        yield f"data: {json.dumps({'type': 'ping'})}\n\n"

@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "server": "hello-mcp-server"}

@app.post("/")
async def handle_mcp(request: Request):
    """Handle MCP requests"""
    body = await request.json()

    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    if method == "initialize":
        return JSONResponse({
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
        })

    elif method == "tools/list":
        return JSONResponse({
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
        })

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "say_hello":
            result = say_hello(args.get("message", ""))
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                },
                "id": request_id
            })

    return JSONResponse({
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found"
        },
        "id": request_id
    })

@app.get("/sse")
async def sse_endpoint():
    """SSE endpoint for server-sent events"""
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )