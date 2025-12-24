import json
from datetime import datetime

from fastapi import APIRouter, Query
from tortoise.expressions import Q

from models.admin import AuditLog
from schemas import SuccessExtra
from schemas.response import AuditLogListResponse

router = APIRouter()


@router.get("/list", summary="Get audit log list", response_model=AuditLogListResponse)
async def get_audit_log_list(
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Items per page"),
    username: str = Query("", description="Operator name"),
    module: str = Query("", description="Function module"),
    method: str = Query("", description="Request method"),
    summary: str = Query("", description="Interface description"),
    status: int = Query(None, description="Status code"),
    start_time: datetime = Query("", description="Start time"),
    end_time: datetime = Query("", description="End time"),
):
    q = Q()
    if username:
        q &= Q(username__icontains=username)
    if module:
        q &= Q(module__icontains=module)
    if method:
        q &= Q(method__icontains=method)
    if summary:
        q &= Q(summary__icontains=summary)
    if status:
        q &= Q(status=status)
    if start_time and end_time:
        q &= Q(created_at__range=[start_time, end_time])
    elif start_time:
        q &= Q(created_at__gte=start_time)
    elif end_time:
        q &= Q(created_at__lte=end_time)

    audit_log_objs = (
        await AuditLog.filter(q)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by("-created_at")
    )
    total = await AuditLog.filter(q).count()
    data = [await audit_log.to_dict() for audit_log in audit_log_objs]
    result = SuccessExtra(data=data, total=total, page=page, page_size=page_size)
    return json.loads(result.body)
