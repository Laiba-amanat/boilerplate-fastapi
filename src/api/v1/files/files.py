import json

from fastapi import APIRouter, File, UploadFile

from core.dependency import DependAuth
from models.admin import User
from schemas.response import ResponseBase
from services.file_service import file_service

router = APIRouter()


@router.post(
    "/upload",
    summary="Upload file",
    response_model=ResponseBase[dict],
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    current_user: User = DependAuth,
):
    """
    General file upload

    Args:
        file: File to upload

    Returns:
        Upload success response containing file information
    """
    result = await file_service.upload_file(file, current_user.id)
    return json.loads(result.body)
