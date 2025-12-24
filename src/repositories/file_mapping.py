"""File mapping repository - manages mapping relationships between file IDs and file information"""

from core.crud import CRUDBase
from models.admin import FileMapping


class FileMappingCreate:
    """File mapping creation model"""

    def __init__(
        self,
        file_id: str,
        original_name: str,
        file_type: str,
        file_size: int | None,
        user_id: int,
        agent_id: int | None = None,
    ):
        self.file_id = file_id
        self.original_name = original_name
        self.file_type = file_type
        self.file_size = file_size
        self.user_id = user_id
        self.agent_id = agent_id


class FileMappingUpdate:
    """File mapping update model"""

    pass


class FileMappingRepository(
    CRUDBase[FileMapping, FileMappingCreate, FileMappingUpdate]
):
    """File mapping repository"""

    async def create_file_mapping(
        self,
        file_id: str,
        original_name: str,
        file_type: str,
        file_size: int | None,
        user_id: int,
        file_path: str | None = None,
    ) -> FileMapping:
        """Create file mapping record"""
        return await FileMapping.create(
            file_id=file_id,
            original_filename=original_name,
            file_type=file_type,
            file_size=file_size,
            upload_user_id=user_id,
            file_path=file_path,
        )

    async def get_file_info_by_ids(self, file_ids: list[str]) -> list[FileMapping]:
        """Get file information by file ID list"""
        if not file_ids:
            return []

        return await FileMapping.filter(file_id__in=file_ids).all()

    async def get_file_mapping_by_file_id(self, file_id: str) -> dict | None:
        """Get file mapping information by file ID"""
        mapping = await FileMapping.filter(file_id=file_id).first()
        if mapping:
            return {
                "file_id": mapping.file_id,
                "original_filename": mapping.original_filename,
                "file_type": mapping.file_type,
                "file_size": mapping.file_size,
                "upload_user_id": mapping.upload_user_id,
                "file_path": mapping.file_path,
            }
        return None


# Global instance
file_mapping_repository = FileMappingRepository(FileMapping)
