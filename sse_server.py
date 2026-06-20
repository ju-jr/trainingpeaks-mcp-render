"""
SSE wrapper for TrainingPeaks MCP Server.
Allows the stdio-based tp-mcp to run as an HTTP/SSE server on Render.
Reads TP_AUTH_COOKIE from environment variable — tp_mcp uses it natively.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tp-mcp-sse")

# Validate TP_AUTH_COOKIE is set
if not os.environ.get("TP_AUTH_COOKIE"):
    logger.error("TP_AUTH_COOKIE environment variable is not set!")
    sys.exit(1)

logger.info("TP_AUTH_COOKIE found, starting server...")

# Import server (tp_mcp reads TP_AUTH_COOKIE natively via get_storage_backend)
from tp_mcp.server import server, _validate_auth_on_startup

# Create SSE transport
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    """Handle SSE connections from Claude.ai."""
    logger.info("New SSE connection from %s", request.client)
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options(),
        )


@asynccontextmanager
async def lifespan(app):
    await _validate_auth_on_startup()
    yield


app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info("Starting SSE server on port %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
