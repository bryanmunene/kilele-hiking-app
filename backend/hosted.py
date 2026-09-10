"""One public service for the API and Streamlit, including its WebSocket connection."""
import os
from contextlib import asynccontextmanager
import httpx
from fastapi import Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi_proxy_lib.core.http import ReverseHttpProxy
from fastapi_proxy_lib.core.websocket import ReverseWebSocketProxy
from main import app, lifespan as api_lifespan, health_check

upstream = f"http://127.0.0.1:{int(os.getenv('STREAMLIT_PORT', '8501'))}/"
http_proxy = ReverseHttpProxy(base_url=upstream)
ws_proxy = ReverseWebSocketProxy(base_url=upstream.replace("http:", "ws:"), max_message_size_bytes=16 * 1024 * 1024)


@asynccontextmanager
async def lifespan(application):
    async with api_lifespan(application):
        try:
            yield
        finally:
            await http_proxy.aclose()
            await ws_proxy.aclose()


app.router.lifespan_context = lifespan
# Streamlit owns the root and /static assets in this deployment mode.
app.router.routes = [route for route in app.router.routes if getattr(route, "path", None) not in {"/", "/static"}]


@app.get("/_ready")
async def ready():
    database = health_check()
    if isinstance(database, JSONResponse):
        return database
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(upstream + "_stcore/health")
        if response.status_code == 200 and response.text.strip() == "ok":
            return {"status": "healthy", "database": "connected", "website": "ready"}
    except httpx.HTTPError:
        pass
    return JSONResponse({"status": "starting", "website": "unavailable"}, status_code=503)


@app.api_route("/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], include_in_schema=False)
async def website(request: Request, path: str):
    return await http_proxy.proxy(request=request, path=path)


@app.websocket("/{path:path}")
async def website_socket(websocket: WebSocket, path: str):
    return await ws_proxy.proxy(websocket=websocket, path=path)
