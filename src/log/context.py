"""
Log context manager
Provides request tracking and user association functionality
"""

import uuid
import traceback
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Lazy import to avoid circular imports
# from log import logger

# Context variables
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")
request_context_var: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


class LogContext:
    """Log context manager"""

    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def set_request_id(request_id: str | None = None) -> str:
        """Set request ID"""
        if not request_id:
            request_id = LogContext.generate_request_id()
        request_id_var.set(request_id)
        return request_id

    @staticmethod
    def set_user_id(user_id: str | None) -> None:
        """Set user ID"""
        user_id_var.set(str(user_id) if user_id else "-")

    @staticmethod
    def get_request_id() -> str:
        """Get current request ID"""
        return request_id_var.get()

    @staticmethod
    def get_user_id() -> str:
        """Get current user ID"""
        return user_id_var.get()

    @staticmethod
    def set_context(key: str, value: Any) -> None:
        """Set context information"""
        context = request_context_var.get({})
        context[key] = value
        request_context_var.set(context)
    
    @staticmethod
    def get_context(key: str = None) -> Any:
        """Get context information"""
        context = request_context_var.get({})
        return context.get(key) if key else context
    
    @staticmethod
    def update_context(**kwargs) -> None:
        """Batch update context information"""
        context = request_context_var.get({})
        context.update(kwargs)
        request_context_var.set(context)
    
    @staticmethod
    def get_logger():
        """Get logger with context"""
        # Lazy import to avoid circular imports
        from log.log import logger

        # Get all context information
        context = request_context_var.get({})
        base_context = {
            "request_id": LogContext.get_request_id(),
            "user_id": LogContext.get_user_id(),
        }
        base_context.update(context)
        
        return logger.bind(**base_context)

    @staticmethod
    def clear():
        """Clear context"""
        request_id_var.set("-")
        user_id_var.set("-")
        request_context_var.set({})


class RequestLogContext:
    """Request-level log context manager"""

    def __init__(self, request_id: str | None = None, user_id: str | None = None):
        self.request_id = request_id
        self.user_id = user_id
        self.old_request_id = None
        self.old_user_id = None

    def __enter__(self):
        # Save old values
        self.old_request_id = LogContext.get_request_id()
        self.old_user_id = LogContext.get_user_id()

        # Set new values
        LogContext.set_request_id(self.request_id)
        LogContext.set_user_id(self.user_id)

        return LogContext.get_logger()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If there's an exception, log exception information
        if exc_type:
            logger = LogContext.get_logger()
            logger.error(
                f"Exception occurred in request context: {exc_type.__name__}: {exc_val}",
                extra={
                    "exception_type": exc_type.__name__,
                    "exception_msg": str(exc_val),
                    "traceback": traceback.format_exc()
                }
            )
        
        # Restore old values
        request_id_var.set(self.old_request_id)
        user_id_var.set(self.old_user_id)
        # Clear request-level context
        request_context_var.set({})


# Convenience functions
def get_context_logger():
    """Get logger with context"""
    return LogContext.get_logger()


def with_request_context(request_id: str | None = None, user_id: str | None = None):
    """Create request context manager"""
    return RequestLogContext(request_id, user_id)
