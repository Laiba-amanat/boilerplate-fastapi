"""
Debug helper utility
Used to add detailed debugging information in business code
"""
import inspect
import json
import traceback
from functools import wraps
from typing import Any, Dict, Optional, Callable
from datetime import datetime

from log.context import LogContext


class DebugHelper:
    """Debug helper class"""
    
    @staticmethod
    def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None, result: Any = None, error: Exception = None):
        """Log function call details"""
        logger = LogContext.get_logger()
        
        call_info = {
            "function_name": func_name,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()) if kwargs else [],
            "has_result": result is not None,
            "has_error": error is not None,
            "call_time": datetime.now().isoformat(),
        }
        
        # Log parameters (avoid logging sensitive information)
        safe_args = []
        for i, arg in enumerate(args):
            if isinstance(arg, (str, int, float, bool)):
                if len(str(arg)) < 100:  # Avoid logging overly long strings
                    safe_args.append(str(arg))
                else:
                    safe_args.append(f"<Long string: {len(str(arg))} characters>")
            else:
                safe_args.append(f"<{type(arg).__name__} object>")
        
        call_info["safe_args"] = safe_args
        
        if error:
            call_info["error_type"] = type(error).__name__
            call_info["error_msg"] = str(error)
            call_info["traceback"] = traceback.format_exc()
            logger.error(f"Function call exception: {func_name}", extra=call_info)
        else:
            logger.debug(f"Function call: {func_name}", extra=call_info)
    
    @staticmethod
    def log_database_query(query_type: str, table: str, conditions: dict = None, result_count: int = None, duration_ms: float = None, error: Exception = None):
        """Log database query details"""
        logger = LogContext.get_logger()
        
        query_info = {
            "query_type": query_type,
            "table": table,
            "conditions": conditions or {},
            "result_count": result_count,
            "duration_ms": duration_ms,
            "query_time": datetime.now().isoformat(),
        }
        
        if error:
            query_info["error_type"] = type(error).__name__
            query_info["error_msg"] = str(error)
            query_info["traceback"] = traceback.format_exc()
            logger.error(f"Database query exception: {query_type} {table}", extra=query_info)
        else:
            logger.debug(f"Database query: {query_type} {table}", extra=query_info)
    
    @staticmethod
    def log_business_logic(operation: str, data: dict = None, result: Any = None, error: Exception = None):
        """Log business logic execution details"""
        logger = LogContext.get_logger()
        
        logic_info = {
            "operation": operation,
            "input_data": data or {},
            "has_result": result is not None,
            "operation_time": datetime.now().isoformat(),
        }
        
        if error:
            logic_info["error_type"] = type(error).__name__
            logic_info["error_msg"] = str(error)
            logic_info["traceback"] = traceback.format_exc()
            logger.error(f"Business logic exception: {operation}", extra=logic_info)
        else:
            logger.debug(f"Business logic execution: {operation}", extra=logic_info)
    
    @staticmethod
    def log_external_call(service: str, endpoint: str, method: str = "GET", request_data: dict = None, response_data: dict = None, duration_ms: float = None, error: Exception = None):
        """Log external service call details"""
        logger = LogContext.get_logger()
        
        call_info = {
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "request_data": request_data or {},
            "has_response": response_data is not None,
            "duration_ms": duration_ms,
            "call_time": datetime.now().isoformat(),
        }
        
        if error:
            call_info["error_type"] = type(error).__name__
            call_info["error_msg"] = str(error)
            call_info["traceback"] = traceback.format_exc()
            logger.error(f"External service call exception: {service} {endpoint}", extra=call_info)
        else:
            logger.debug(f"External service call: {service} {endpoint}", extra=call_info)


def debug_trace(include_args: bool = False, include_result: bool = False):
    """Function call tracing decorator"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"
            start_time = datetime.now()
            
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log successful call
                call_args = args if include_args else ()
                call_result = result if include_result else None
                
                DebugHelper.log_function_call(
                    func_name=func_name,
                    args=call_args,
                    kwargs=kwargs,
                    result=call_result
                )
                
                LogContext.update_context(
                    last_function_call=func_name,
                    last_function_duration_ms=duration,
                    last_function_success=True
                )
                
                return result
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log exception call
                call_args = args if include_args else ()
                
                DebugHelper.log_function_call(
                    func_name=func_name,
                    args=call_args,
                    kwargs=kwargs,
                    error=e
                )
                
                LogContext.update_context(
                    last_function_call=func_name,
                    last_function_duration_ms=duration,
                    last_function_success=False,
                    last_function_error=str(e)
                )
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log successful call
                call_args = args if include_args else ()
                call_result = result if include_result else None
                
                DebugHelper.log_function_call(
                    func_name=func_name,
                    args=call_args,
                    kwargs=kwargs,
                    result=call_result
                )
                
                LogContext.update_context(
                    last_function_call=func_name,
                    last_function_duration_ms=duration,
                    last_function_success=True
                )
                
                return result
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log exception call
                call_args = args if include_args else ()
                
                DebugHelper.log_function_call(
                    func_name=func_name,
                    args=call_args,
                    kwargs=kwargs,
                    error=e
                )
                
                LogContext.update_context(
                    last_function_call=func_name,
                    last_function_duration_ms=duration,
                    last_function_success=False,
                    last_function_error=str(e)
                )
                
                raise
        
        # Check if it's an async function
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Convenience functions
def log_debug(message: str, **extra):
    """Log debug information"""
    logger = LogContext.get_logger()
    logger.debug(message, extra=extra)


def log_info(message: str, **extra):
    """Log information"""
    logger = LogContext.get_logger()
    logger.info(message, extra=extra)


def log_warning(message: str, **extra):
    """Log warning"""
    logger = LogContext.get_logger()
    logger.warning(message, extra=extra)


def log_error(message: str, error: Exception = None, **extra):
    """Log error"""
    logger = LogContext.get_logger()
    
    if error:
        # Build detailed error information
        error_info = f"{message}\n"
        error_info += f"Exception Type: {type(error).__name__}\n"
        error_info += f"Exception Message: {str(error)}\n"
        error_info += f"\nStack Trace:\n{traceback.format_exc()}\n"
        
        # Add context information
        if extra:
            error_info += f"\nContext Info:\n"
            for key, value in extra.items():
                if isinstance(value, dict):
                    error_info += f"  {key}: {json.dumps(value, indent=2, ensure_ascii=False)}\n"
                else:
                    error_info += f"  {key}: {value}\n"
        
        error_info += "=" * 80
        
        # Log detailed information
        logger.error(error_info)
    else:
        logger.bind(**extra).error(message)


def log_critical(message: str, error: Exception = None, **extra):
    """Log critical error"""
    logger = LogContext.get_logger()
    
    if error:
        # Build detailed critical error information
        error_info = f"{message}\n"
        error_info += f"CRITICAL Exception Type: {type(error).__name__}\n"
        error_info += f"CRITICAL Exception Message: {str(error)}\n"
        error_info += f"\nCRITICAL Stack Trace:\n{traceback.format_exc()}\n"
        
        # Add context information
        if extra:
            error_info += f"\nContext Info:\n"
            for key, value in extra.items():
                if isinstance(value, dict):
                    error_info += f"  {key}: {json.dumps(value, indent=2, ensure_ascii=False)}\n"
                else:
                    error_info += f"  {key}: {value}\n"
        
        error_info += "=" * 80
        
        # Log critical error information
        logger.critical(error_info)
    else:
        logger.bind(**extra).critical(message)