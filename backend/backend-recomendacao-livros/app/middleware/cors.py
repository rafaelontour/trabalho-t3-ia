import json
import logging
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("app_logger.cors")


class CORSErrorMiddleware:
    """ASGI middleware that guarantees CORS headers on every response,
    including 500 error responses that escape the Starlette CORSMiddleware."""

    def __init__(self, app: ASGIApp, allowed_origins: list[str]) -> None:
        self.app = app
        self.allowed_origins = set(allowed_origins)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_headers = dict(scope.get("headers", []))
        origin = request_headers.get(b"origin", b"").decode("utf-8")

        if origin not in self.allowed_origins:
            await self.app(scope, receive, send)
            return

        async def send_with_cors(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                header_names = {h[0].lower() for h in headers}

                if b"access-control-allow-origin" not in header_names:
                    headers.append(
                        (b"access-control-allow-origin", origin.encode())
                    )
                    headers.append(
                        (b"access-control-allow-credentials", b"true")
                    )
                    headers.append(
                        (b"access-control-expose-headers", b"*")
                    )
                    message["headers"] = headers

            await send(message)

        try:
            await self.app(scope, receive, send_with_cors)
        except Exception as exc:
            logger.exception(f"[CORSErrorMiddleware] Exceção capturada: {exc}")

            body = json.dumps({"detail": "Erro interno no servidor."}).encode()
            await send_with_cors({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send_with_cors({
                "type": "http.response.body",
                "body": body,
            })
