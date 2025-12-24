import json
import traceback
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from log import logger
from settings.config import settings


class SettingNotFound(Exception):
    pass


async def DoesNotExistHandle(req: Request, exc: DoesNotExist) -> JSONResponse:
    # Log detailed error information
    error_details = {
        "method": req.method,
        "url": str(req.url),
        "path": req.url.path,
        "query_params": dict(req.query_params),
        "client_ip": req.client.host if req.client else None,
        "user_agent": req.headers.get("user-agent"),
        "exception_type": type(exc).__name__,
        "exception_msg": str(exc),
        "traceback": traceback.format_exc()
    }
    
    # Build detailed error information
    error_message = f"DoesNotExist exception: {req.method} {req.url.path} - {exc}\n"
    error_message += f"Exception Type: {type(exc).__name__}\n"
    error_message += f"Exception Message: {str(exc)}\n"
    error_message += f"\nStack Trace:\n{error_details.get('traceback', 'No traceback available')}\n"
    error_message += f"\nRequest Context:\n"
    for key, value in error_details.items():
        if key != 'traceback':
            if isinstance(value, dict):
                error_message += f"  {key}: {json.dumps(value, indent=2, ensure_ascii=False)}\n"
            else:
                error_message += f"  {key}: {value}\n"
    error_message += "=" * 80
    
    logger.error(error_message)
    
    # Determine error message detail level based on environment
    if settings.DEBUG:
        msg = f"Object not found: {exc}, query_params: {req.query_params}"
    else:
        msg = "Requested resource does not exist"

    content = dict(code=404, msg=msg)
    return JSONResponse(content=content, status_code=404)


async def HttpExcHandle(request: Request, exc: HTTPException):
    # Log HTTP exception details
    error_details = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "status_code": exc.status_code,
        "exception_type": type(exc).__name__,
        "exception_msg": str(exc.detail),
        "traceback": traceback.format_exc()
    }
    
    # Determine log level based on status code
    if exc.status_code >= 500:
        logger.bind(**error_details).error(
            f"HTTP {exc.status_code} exception: {request.method} {request.url.path} - {exc.detail}"
        )
    elif exc.status_code >= 400:
        logger.bind(**error_details).warning(
            f"HTTP {exc.status_code} exception: {request.method} {request.url.path} - {exc.detail}"
        )
    
    if exc.status_code == 401 and exc.headers and "WWW-Authenticate" in exc.headers:
        return Response(status_code=exc.status_code, headers=exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
    )


async def IntegrityHandle(request: Request, exc: IntegrityError):
    # Log data integrity error details
    error_details = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "exception_type": type(exc).__name__,
        "exception_msg": str(exc),
        "traceback": traceback.format_exc()
    }
    
    logger.bind(**error_details).error(
        f"Data integrity error: {request.method} {request.url.path} - {exc}"
    )
    
    # Determine error message detail level based on environment
    if settings.DEBUG:
        msg = f"IntegrityError: {exc}"
    else:
        msg = "Data integrity error, please check input data"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=500)


async def RequestValidationHandle(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Log request validation error details
    error_details = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "exception_type": type(exc).__name__,
        "exception_msg": str(exc),
        "validation_errors": exc.errors(),
        "traceback": traceback.format_exc()
    }
    
    logger.bind(**error_details).warning(
        f"Request parameter validation failed: {request.method} {request.url.path} - {len(exc.errors())} errors"
    )
    
    # Determine error message detail level based on environment
    if settings.DEBUG:
        msg = f"RequestValidationError: {exc.errors()}"
    else:
        msg = "Request parameter validation failed, please check input format"

    content = dict(code=422, msg=msg)
    return JSONResponse(content=content, status_code=422)


async def ResponseValidationHandle(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    # Log response validation error details
    error_details = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "exception_type": type(exc).__name__,
        "exception_msg": str(exc),
        "validation_errors": exc.errors(),
        "traceback": traceback.format_exc()
    }
    
    logger.bind(**error_details).error(
        f"Response format validation error: {request.method} {request.url.path} - {len(exc.errors())} errors"
    )
    
    # Determine error message detail level based on environment
    if settings.DEBUG:
        msg = f"ResponseValidationError: {exc.errors()}"
    else:
        msg = "Server response format error"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=500)


async def UnhandledExceptionHandle(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions"""
    # Log detailed information about unhandled exception
    error_details = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "exception_type": type(exc).__name__,
        "exception_msg": str(exc),
        "exception_module": getattr(exc, "__module__", "unknown"),
        "traceback": traceback.format_exc()
    }
    
    # Try to get request body information (if possible)
    try:
        if hasattr(request, "_body"):
            error_details["request_body_size"] = len(request._body) if request._body else 0
    except Exception:
        pass
    
    logger.bind(**error_details).critical(
        f"Unhandled exception: {request.method} {request.url.path} - {type(exc).__name__}: {exc}"
    )
    
    # Determine error message detail level based on environment
    if settings.DEBUG:
        msg = f"Unhandled exception: {type(exc).__name__}: {exc}"
    else:
        msg = "Internal server error, please try again later"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=500)
