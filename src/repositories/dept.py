from tortoise.expressions import Q
from tortoise.transactions import atomic

from core.crud import CRUDBase
from log import logger
from models.admin import Dept, DeptClosure
from schemas.depts import DeptCreate, DeptUpdate


class DeptRepository(CRUDBase[Dept, DeptCreate, DeptUpdate]):
    def __init__(self):
        super().__init__(model=Dept)

    async def get_dept_tree(self, name):
        q = Q()
        # Get all departments that are not soft deleted
        q &= Q(is_deleted=False)
        if name:
            q &= Q(name__contains=name)
        all_depts = await self.model.filter(q).order_by("order")

        # Helper function to recursively build department tree
        def build_tree(parent_id):
            return [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "desc": dept.desc,
                    "order": dept.order,
                    "parent_id": dept.parent_id,
                    "children": build_tree(dept.id),  # Recursively build child departments
                }
                for dept in all_depts
                if dept.parent_id == parent_id
            ]

        # Build department tree starting from top-level departments (parent_id=0)
        dept_tree = build_tree(0)
        return dept_tree

    async def get_dept_info(self):
        pass

    async def update_dept_closure(self, obj: Dept):
        parent_depts = await DeptClosure.filter(descendant=obj.parent_id)
        for i in parent_depts:
            logger.debug(
                f"Processing dept closure: ancestor={i.ancestor}, descendant={i.descendant}"
            )
        dept_closure_objs: list[DeptClosure] = []
        # Insert parent relationships
        for item in parent_depts:
            dept_closure_objs.append(
                DeptClosure(
                    ancestor=item.ancestor,
                    descendant=obj.id,
                    level=item.level + 1,
                )
            )
        # Insert self relationship
        dept_closure_objs.append(
            DeptClosure(ancestor=obj.id, descendant=obj.id, level=0)
        )
        # Create relationships
        await DeptClosure.bulk_create(dept_closure_objs)

    @atomic()
    async def create_dept(self, obj_in: DeptCreate):
        # Create
        if obj_in.parent_id != 0:
            await self.get(id=obj_in.parent_id)
        new_obj = await self.create(obj_in=obj_in)
        await self.update_dept_closure(new_obj)

    @atomic()
    async def update_dept(self, obj_in: DeptUpdate):
        dept_obj = await self.get(id=obj_in.id)
        # Update department relationships
        if dept_obj.parent_id != obj_in.parent_id:
            await DeptClosure.filter(ancestor=dept_obj.id).delete()
            await DeptClosure.filter(descendant=dept_obj.id).delete()
            await self.update_dept_closure(dept_obj)
        # Update department information
        dept_obj.update_from_dict(obj_in.model_dump(exclude_unset=True))
        await dept_obj.save()

    @atomic()
    async def delete_dept(self, dept_id: int):
        # Delete department
        obj = await self.get(id=dept_id)
        obj.is_deleted = True
        await obj.save()
        # Delete relationships
        await DeptClosure.filter(descendant=dept_id).delete()


dept_repository = DeptRepository()
