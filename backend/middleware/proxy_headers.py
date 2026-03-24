from starlette.types import ASGIApp, Receive, Scope, Send


class DisableProxyBufferingMiddleware:
    """
    Middleware that adds headers to disable proxy buffering for streaming responses.
    This is critical for Hostinger/OpenResty to prevent 'TypeError: network error' 
    during long-running research tasks.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                # Check if it's a streaming response
                content_type = headers.get(b"content-type", b"").decode()
                if "text/event-stream" in content_type:
                    # Inject headers to disable buffering
                    # Note: OpenResty/Nginx respects X-Accel-Buffering
                    new_headers = list(message.get("headers", []))
                    new_headers.append((b"X-Accel-Buffering", b"no"))
                    new_headers.append((b"Cache-Control", b"no-cache"))
                    message["headers"] = new_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
