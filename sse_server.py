"""
SSE wrapper for TrainingPeaks MCP Server.
Allows the stdio-based tp-mcp to run as an HTTP/SSE server on Render.
Reads TP_COOKIE from environment variable and injects into tp_mcp credential store.
"""

import os
import sys
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

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


def inject_cookie_from_env():
    """
    Reads TP_COOKIE env var and writes it to the credential file
    that tp_mcp.auth.get_credential() expects (~/.tp-mcp/credentials.json).
    """
    cookie = os.environ.get("TP_COOKIE")
    if not cookie:
        logger.warning("TP_COOKIE environment variable not set!")
        return False

    cred_dir = Path.home() / ".tp-mcp"
    cred_dir.mkdir(parents=True, exist_ok=True)
    cred_file = cred_dir / "credentials.json"

    cred_data = {"cookie": cookie}
    cred_file.write_text(json.dumps(cred_data))
    logger.info("Cookie injected from TP_COOKIE env var into %s", cred_file)
    return True


# Inject cookie BEFORE importing tp_mcp so it's available at startup
inject_cookie_from_env()

# Now import the server (it will find the credential file)
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
    """Validate auth on startup."""
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
