"""File service layer - unified file processing business logic"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from log import logger
from repositories.file_mapping import file_mapping_repository
from schemas.base import Success

# File security configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
UPLOADS_DIR = "uploads"

ALLOWED_EXTENSIONS: set[str] = {
    # Document types
    ".txt",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    # Image types
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".svg",
    # Audio/Video types
    ".mp3",
    ".wav",
    ".flac",
    ".aac",
    ".ogg",
    ".m4a",
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    # Other file types
    ".json",
    ".xml",
    ".csv",
    ".zip",
    ".rar",
    ".7z",
}

DANGEROUS_EXTENSIONS: set[str] = {
    ".exe",
    ".bat",
    ".cmd",
    ".com",
    ".pif",
    ".scr",
    ".vbs",
    ".js",
    ".jar",
    ".sh",
    ".ps1",
    ".php",
    ".asp",
    ".jsp",
    ".py",
    ".pl",
    ".rb",
}


class FileService:
    """File service class - specifically handles file upload and security validation logic"""

    def __init__(self):
        self.logger = logger
        # Ensure upload directory exists
        self.uploads_dir = Path(UPLOADS_DIR)
        self.uploads_dir.mkdir(exist_ok=True)

    async def upload_file(self, file: UploadFile, user_id: int) -> Success:
        """
        General file upload

        Args:
            file: Uploaded file
            user_id: Current user ID

        Returns:
            Success: Upload result response
        """
        try:
            # File security validation
            self._validate_file_security(file)

            # Generate safe filename
            safe_filename = self._generate_safe_filename(file.filename)

            # Read and validate file content
            content = await self._read_and_validate_file(file)

            # Generate file ID and save path
            file_id = str(uuid.uuid4())
            file_path = self.uploads_dir / f"{file_id}_{safe_filename}"

            # Save file to local
            with open(file_path, "wb") as f:
                f.write(content)

            self.logger.info(f"File saved: {file_path}")

            # Save file mapping information
            await self._save_file_mapping(
                {"file_id": file_id, "file_path": str(file_path)}, file, user_id
            )

            # Return file information
            response_data = {
                "file_id": file_id,
                "original_filename": file.filename,
                "file_type": self._determine_file_type(file.filename),
                "file_size": len(content),
                "file_path": str(file_path),
            }

            return Success(
                data=response_data,
                msg="File uploaded successfully",
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail="File upload failed") from e

    def _validate_file_security(self, file: UploadFile) -> None:
        """Validate file security"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")

        # Get file extension
        file_ext = Path(file.filename).suffix.lower()

        # Check dangerous file types
        if file_ext in DANGEROUS_EXTENSIONS:
            raise HTTPException(
                status_code=400, detail=f"File type not allowed for upload: {file_ext}"
            )

        # Check if it's in the allowed extensions list
        if file_ext and file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}, allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

    def _generate_safe_filename(self, original_filename: str) -> str:
        """Generate safe filename (prevent path traversal attacks)"""
        file_ext = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4().hex}{file_ext}"

    async def _read_and_validate_file(self, file: UploadFile) -> bytes:
        """Read and validate file content"""
        content = await file.read()

        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds limit {MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        return content

    async def _save_file_mapping(
        self,
        response_data: dict,
        file: UploadFile,
        user_id: int,
    ) -> None:
        """Save file mapping information"""
        try:
            # Get file ID from response
            file_id = response_data.get("file_id")
            if not file_id:
                self.logger.warning("Unable to get file ID from response")
                return

            # Determine file type
            file_type = self._determine_file_type(file.filename)

            # Get file size
            file_size = file.size if hasattr(file, "size") else None

            # Save file mapping
            await file_mapping_repository.create_file_mapping(
                file_id=file_id,
                original_name=file.filename,
                file_type=file_type,
                file_size=file_size,
                user_id=user_id,
                file_path=response_data.get("file_path"),  # Store local file path
            )

            self.logger.info(f"File mapping saved: {file_id} -> {file.filename}")

        except Exception as e:
            # File mapping save failure should not affect upload process
            self.logger.warning(f"Failed to save file mapping: {str(e)}")

    def _determine_file_type(self, filename: str) -> str:
        """Determine file type"""
        if not filename:
            return "unknown"

        file_ext = filename.lower().split(".")[-1] if "." in filename else ""

        # Image types
        image_exts = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]
        # Audio types
        audio_exts = ["mp3", "wav", "flac", "aac", "ogg", "m4a"]
        # Video types
        video_exts = ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"]

        if file_ext in image_exts:
            return "image"
        elif file_ext in audio_exts:
            return "audio"
        elif file_ext in video_exts:
            return "video"
        else:
            return "document"


# Global instance
file_service = FileService()
