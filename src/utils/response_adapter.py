"""
Response adapter: Convert JSONResponse to dictionary format
Enables existing service layer code to be compatible with Pydantic response models
"""
from typing import Any
from schemas.base import Success, Fail, SuccessExtra


def adapt_response(response: Success | Fail | SuccessExtra) -> dict[str, Any]:
    """
    Convert JSONResponse object to dictionary format
    This function serves as a compatibility layer during transition, allowing existing service layer code to work with new Pydantic response models
    
    Args:
        response: Success, Fail, or SuccessExtra instance
        
    Returns:
        Dictionary containing response data
    """
    if hasattr(response, 'body'):
        # JSONResponse object, parse content from body
        import json
        return json.loads(response.body)
    else:
        # Directly return dictionary content
        return {
            "code": getattr(response, 'code', 200),
            "msg": getattr(response, 'msg', 'OK'),
            "data": getattr(response, 'data', None),
            "total": getattr(response, 'total', None),
            "page": getattr(response, 'page', None),
            "page_size": getattr(response, 'page_size', None),
        }