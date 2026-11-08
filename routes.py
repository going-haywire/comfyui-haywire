# SPDX-License-Identifier: GPL-3.0-or-later
"""HTTP routes of the workflow exchange, under /api/haywire."""

from __future__ import annotations

from aiohttp import web
from server import PromptServer

from .exchange import PROTOCOL, PUBLISHED, Exchange

VERSION = "0.1.0"
exchange = Exchange()


async def _send(pairs):
    server = PromptServer.instance
    for sid, message in pairs:
        await server.send_json(PUBLISHED, message, sid)


async def _body(request: web.Request, *keys: str) -> dict | web.Response:
    try:
        body = await request.json()
    except ValueError:
        return web.json_response({"error": "body must be JSON"}, status=400)
    missing = [k for k in keys if k not in body]
    if missing:
        return web.json_response({"error": f"missing: {', '.join(missing)}"}, status=400)
    return body


def register() -> None:
    routes = PromptServer.instance.routes

    @routes.get("/api/haywire/version")
    async def version(request: web.Request) -> web.Response:
        return web.json_response({"protocol": PROTOCOL, "version": VERSION})

    @routes.get("/api/haywire/workflows")
    async def workflows(request: web.Request) -> web.Response:
        return web.json_response(exchange.listing())

    @routes.post("/api/haywire/workflow/publish")
    async def publish(request: web.Request) -> web.Response:
        body = await _body(request, "client_id", "name", "workflow")
        if isinstance(body, web.Response):
            return body
        try:
            pairs = exchange.publish(str(body["client_id"]), str(body["name"]), body["workflow"])
        except ValueError as exc:
            return web.json_response({"error": str(exc)}, status=400)
        await _send(pairs)
        return web.json_response({"status": "success"})

    @routes.post("/api/haywire/workflow/subscribe")
    async def subscribe(request: web.Request) -> web.Response:
        body = await _body(request, "client_id")
        if isinstance(body, web.Response):
            return body
        await _send(exchange.subscribe(str(body["client_id"])))
        return web.json_response({"status": "success"})

    @routes.post("/api/haywire/workflow/unsubscribe")
    async def unsubscribe(request: web.Request) -> web.Response:
        body = await _body(request, "client_id")
        if isinstance(body, web.Response):
            return body
        exchange.unsubscribe(str(body["client_id"]))
        return web.json_response({"status": "success"})

    @routes.post("/api/haywire/workflow/withdraw")
    async def withdraw(request: web.Request) -> web.Response:
        body = await _body(request, "client_id")
        if isinstance(body, web.Response):
            return body
        exchange.withdraw(str(body["client_id"]))
        return web.json_response({"status": "success"})
