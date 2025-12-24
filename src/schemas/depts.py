from pydantic import BaseModel, Field


class BaseDept(BaseModel):
    name: str = Field(..., description="Department name", example="R&D Center")
    desc: str = Field("", description="Description", example="R&D Center")
    order: int = Field(0, description="Order")
    parent_id: int = Field(0, description="Parent department ID")


class DeptCreate(BaseDept):
    ...


class DeptUpdate(BaseDept):
    id: int

    def update_dict(self):
        return self.model_dump(exclude_unset=True, exclude={"id"})
