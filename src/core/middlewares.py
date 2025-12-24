import json
import re
from collections.abc import AsyncGenerator
from datetime import datetime
import traceback
from typing import Any

from fastapi import FastAPI
from fastapi.responses import Response, StreamingResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from core.dependency import AuthControl
from log import logger
from log.context import LogContext
from models.admin import AuditLog, User

from .bgtask import BgTasks


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Set more relaxed CSP policy for Swagger UI and ReDoc
        if request.url.path in ["/docs", "/redoc"]:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' data: https://cdn.jsdelivr.net https://unpkg.com; "
                "connect-src 'self'; "
                "worker-src 'self' blob:; "
                "child-src 'self' blob:"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            )

        # Only add HSTS header in HTTPS environment
        if request.url.scheme == "https":
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"

        return response


class SimpleBaseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def before_request(self, request: Request):
        return self.app

    async def after_request(self, request: Request):
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    async def before_request(self, request):
        await BgTasks.init_bg_tasks_obj()

    async def after_request(self, request):
        await BgTasks.execute_tasks()


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths
        self.audit_log_paths = ["/api/v1/auditlog/list"]
        self.max_body_size = 1024 * 1024  # 1MB response body size limit

    async def get_request_args(self, request: Request) -> dict:
        args = {}
        # Get query parameters
        for key, value in request.query_params.items():
            args[key] = value

        # Get request body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")

            # If it's a file upload request, skip request body parsing
            if "multipart/form-data" in content_type:
                return args

            try:
                body = await request.json()
                args.update(body)
            except json.JSONDecodeError:
                try:
                    body = await request.form()
                    args.update(body)
                except Exception:
                    pass

        return args

    async def get_response_body(self, request: Request, response: Response) -> Any:
        # For streaming responses, don't log response body
        if isinstance(response, StreamingResponse):
            return {"message": "[Streaming Response]"}

        # Check response type, skip if it's a streaming-related response type
        if hasattr(response, "body_iterator") and not hasattr(response, "body"):
            return {"message": "[Streaming Response]"}

        body = b""
        # Check Content-Length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return {
                "code": 0,
                "msg": "Response too large to log",
                "data": None,
            }

        try:
            if hasattr(response, "body"):
                body = response.body
            else:
                body_chunks = []
                async for chunk in response.body_iterator:
                    if not isinstance(chunk, bytes):
                        chunk = chunk.encode(response.charset)
                    body_chunks.append(chunk)

                response.body_iterator = self._async_iter(body_chunks)
                body = b"".join(body_chunks)
        except Exception:
            # If reading response body fails, return default value
            return {"message": "[Unable to read response body]"}

        if any(request.url.path.startswith(path) for path in self.audit_log_paths):
            try:
                data = self.lenient_json(body)
                # Only keep basic information, remove detailed response content
                if isinstance(data, dict):
                    data.pop("response_body", None)
                    if "data" in data and isinstance(data["data"], list):
                        for item in data["data"]:
                            item.pop("response_body", None)
                return data
            except Exception:
                return None

        return self.lenient_json(body)

    def lenient_json(self, v: Any) -> Any:
        if isinstance(v, str | bytes):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                pass
        return v

    async def _async_iter(self, items: list[bytes]) -> AsyncGenerator[bytes, None]:
        for item in items:
            yield item

    async def get_request_log(self, request: Request, response: Response) -> dict:
        """
        Get corresponding log record data based on request and response objects
        """
        data: dict = {
            "path": request.url.path,
            "status": response.status_code,
            "method": request.method,
        }
        # Route information
        app: FastAPI = request.app
        for route in app.routes:
            if (
                isinstance(route, APIRoute)
                and route.path_regex.match(request.url.path)
                and request.method in route.methods
            ):
                data["module"] = ",".join(route.tags)
                data["summary"] = route.summary
        # Get user information
        try:
            token = request.headers.get("token")
            user_obj = None
            if token:
                user_obj: User = await AuthControl.is_authed(token)
            data["user_id"] = user_obj.id if user_obj else 0
            data["username"] = user_obj.username if user_obj else ""
        except Exception:
            data["user_id"] = 0
            data["username"] = ""
        return data

    async def before_request(self, request: Request):
        request_args = await self.get_request_args(request)
        request.state.request_args = request_args

    async def after_request(
        self, request: Request, response: Response, process_time: int
    ):
        if request.method in self.methods:
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return
            data: dict = await self.get_request_log(request=request, response=response)
            data["response_time"] = process_time

            data["request_args"] = request.state.request_args
            data["response_body"] = await self.get_response_body(request, response)
            await AuditLog.create(**data)

        return response

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time: datetime = datetime.now()
        await self.before_request(request)
        response = await call_next(request)
        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)
        await self.after_request(request, response, process_time)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and log"""
        start_time = datetime.now()
        
        # Set request-level context information
        request_id = LogContext.set_request_id()
        LogContext.update_context(
            method=request.method,
            path=request.url.path,
            url=str(request.url),
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_type=request.headers.get("content-type"),
            content_length=request.headers.get("content-length"),
            start_time=start_time.isoformat(),
        )

        # Get logger with context
        context_logger = LogContext.get_logger()

        # Log request start
        context_logger.info(f"Request started: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            # Calculate processing time
            end_time = datetime.now()
            process_time = (end_time - start_time).total_seconds() * 1000
            
            # Update context information
            LogContext.update_context(
                status_code=response.status_code,
                process_time_ms=process_time,
                end_time=end_time.isoformat(),
                response_headers=dict(response.headers),
            )

            # Log request completion
            context_logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)"
            )

            return response

        except Exception as e:
            # Calculate processing time
            end_time = datetime.now()
            process_time = (end_time - start_time).total_seconds() * 1000
            
            # Update context information
            LogContext.update_context(
                exception_occurred=True,
                exception_type=type(e).__name__,
                exception_msg=str(e),
                process_time_ms=process_time,
                end_time=end_time.isoformat(),
                traceback=traceback.format_exc()
            )

            # Log detailed request exception information
            context_logger.error(
                f"Request processing exception: {request.method} {request.url.path} - {type(e).__name__}: {str(e)} ({process_time:.2f}ms)"
            )

            raise
        finally:
            # Clear request context
            LogContext.clear()
