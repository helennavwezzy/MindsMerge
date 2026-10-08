import contextlib
import json

import uvicorn
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from rich import print
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from libs import jwt_auth
from wforum.db import api

app = Server("wforum_mcp_server")


class ASGIAppEndpoint:
    """Allow Starlette Route to forward directly to an ASGI app."""

    def __init__(self, asgi_app):
        self._asgi_app = asgi_app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._asgi_app(scope, receive, send)


@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    return list(map(adk_to_mcp_tool_type, MCP_TOOLS.values()))


@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> mcp_types.CallToolResult | list[mcp_types.Content]:
    print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")

    tool = MCP_TOOLS.get(name)
    if tool is None:
        print(f"MCP Server: Tool '{name}' not found/exposed by this server.")
        error_text = json.dumps(
            {"error": f"Tool '{name}' not implemented by this server."}
        )
        return [mcp_types.TextContent(type="text", text=error_text)]

    try:
        adk_tool_response = await tool.run_async(
            args=arguments,
            tool_context=None,  # type: ignore
        )

        response_text = json.dumps(adk_tool_response, indent=2)
        return [mcp_types.TextContent(type="text", text=response_text)]

    except Exception as e:
        print(f"MCP Server: Error executing ADK tool '{name}': {e}")
        error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
        return [mcp_types.TextContent(type="text", text=error_text)]


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Check auth
        auth_header = request.headers.get("authorization")
        if auth_header:
            print("MCP Server: Authorization header found")
            try:
                username = jwt_auth.validate_auth_header(auth_header)
                print(f"MCP Server: Authenticated user '{username}'.")

                topics = api.topics.get_followed_topics(username)
                assert len(topics) == 1

                request.scope["headers"] = [
                    (b"x-username", username.encode("utf-8")),
                    (b"x-followed-topic", topics[0].name.encode("utf-8")),
                    *request.scope["headers"],
                ]
            except ValueError as err:
                return PlainTextResponse(str(err), status_code=401)

        return await call_next(request)


def run_mcp_server():
    session_manager = StreamableHTTPSessionManager(
        app=app, event_store=None, json_response=False, stateless=True
    )

    async def handle_http_request(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        """Manage session manager lifecycle."""
        async with session_manager.run():
            print("\n===================================")
            print("MCP Streamable HTTP server started!")
            print("Available tools:")
            for tool_name in MCP_TOOLS.keys():
                print(f"- {tool_name}")
            print("===================================\n")
            try:
                yield
            finally:
                print("MCP server shutting down...")

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/mcp", endpoint=ASGIAppEndpoint(handle_http_request)),
            Mount("/mcp/", app=handle_http_request),
        ],
        lifespan=lifespan,
    )

    starlette_app.add_middleware(ContextMiddleware)

    uvicorn.run(starlette_app, host="localhost", port=8080)


if __name__ == "__main__":
    from .mcp_tools import MCP_TOOLS

    run_mcp_server()
