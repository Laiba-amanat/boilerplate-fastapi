import logging
import os
import sys
import json
from datetime import date, datetime
from typing import Any, Dict, Set

from loguru import logger as loguru_logger

from settings import settings


LOGGING_RESERVED_FIELDS: Set[str] = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


class InterceptHandler(logging.Handler):
    """Forward standard logging logs to loguru."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - direct call
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in LOGGING_RESERVED_FIELDS
        }

        loguru_logger.bind(**extra).opt(
            depth=depth, exception=record.exc_info
        ).log(level, record.getMessage())


class LoggingConfig:
    """Unified logging configuration management"""

    def __init__(self) -> None:
        self.debug = settings.DEBUG
        self.level = "DEBUG" if self.debug else "INFO"
        self.log_dir = settings.LOGS_ROOT if hasattr(settings, "LOGS_ROOT") else "logs"
        self.service_name = getattr(settings, "PROJECT_NAME", "application")
        self.environment = getattr(settings, "APP_ENV", "development")
        self.ensure_log_dir()

    def ensure_log_dir(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    @staticmethod
    def _json_default(value: Any) -> Any:
        """Default JSON serialization handling logic"""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, (set, tuple)):
            return list(value)
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

    def _build_log_entry(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized log structure"""
        extra: Dict[str, Any] = dict(record.get("extra", {}))
        # Avoid recursive references
        extra.pop("serialized", None)

        log_entry: Dict[str, Any] = {
            "timestamp": record["time"].astimezone().isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "logger": record["name"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
            "process": record["process"].id,
            "thread": record["thread"].id,
            "service": self.service_name,
            "environment": self.environment,
        }

        # Support context passthrough, compatible with request_id / user_id and other fields
        context = extra.pop("context", None)
        if isinstance(context, dict):
            extra.update(context)

        log_entry.update(extra)

        if record.get("exception"):
            exception = record["exception"]
            log_entry["exception"] = {
                "type": exception.type.__name__ if exception.type else None,
                "value": str(exception.value),
                "traceback": exception.traceback,
            }

        return log_entry

    def _serialize_record(self, record: Dict[str, Any]) -> str:
        """Serialize log record to JSON string"""
        log_entry = self._build_log_entry(record)
        return json.dumps(
            log_entry,
            ensure_ascii=False,
            default=self._json_default,
            sort_keys=self.debug,
            separators=(",", ":") if not self.debug else (",", ": "),
        )

    def _patch_record(self, record: Dict[str, Any]) -> None:
        """Attach serialized content to each log record"""
        record.setdefault("extra", {})
        record["extra"]["serialized"] = self._serialize_record(record)

    def setup_logger(self):
        """Configure log output"""
        # Clear default handlers
        loguru_logger.remove()

        # Intercept standard logging, unify output format
        intercept_handler = InterceptHandler()
        logging.basicConfig(handlers=[intercept_handler], level=0, force=True)

        for logger_name in (
            "uvicorn",
            "uvicorn.error",
            "uvicorn.access",
            "fastapi",
        ):
            standard_logger = logging.getLogger(logger_name)
            standard_logger.handlers = [intercept_handler]
            standard_logger.propagate = False

        # Enable unified patcher to ensure all log output is JSON structure
        loguru_logger.configure(patcher=self._patch_record)

        # Console output (JSON stream)
        loguru_logger.add(
            sink=sys.stdout,
            level=self.level,
            format="{extra[serialized]}",
            colorize=False,
            backtrace=True,
            diagnose=self.debug,
            enqueue=True,
        )

        # File output - all level logs
        loguru_logger.add(
            sink=f"{self.log_dir}/backend_{{time:YYYY-MM-DD}}.log",
            level="DEBUG",
            format="{extra[serialized]}",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=self.debug,
            enqueue=True,
        )

        # Error logs separate file
        loguru_logger.add(
            sink=f"{self.log_dir}/backend_error_{{time:YYYY-MM-DD}}.log",
            level="ERROR",
            format="{extra[serialized]}",
            rotation="50 MB",
            retention="90 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=self.debug,
            enqueue=True,
        )

        # Critical error logs (CRITICAL level)
        loguru_logger.add(
            sink=f"{self.log_dir}/backend_critical_{{time:YYYY-MM-DD}}.log",
            level="CRITICAL",
            format="{extra[serialized]}",
            rotation="10 MB",
            retention="180 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=self.debug,
            enqueue=True,
        )

        # Add default context for all logs
        # Note: rebinding here will create a new logger instance

        # Log logging system startup
        loguru_logger.bind(event="logger_startup").info("Logging system started")

        return loguru_logger


# Global logging configuration instance
logging_config = LoggingConfig()
logger = logging_config.setup_logger()
