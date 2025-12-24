from fastapi import APIRouter

from .auditlog import router

auditlog_router = APIRouter()
auditlog_router.include_router(router, tags=["Audit Log Module"])

__all__ = ["auditlog_router"]
