from starlette.background import BackgroundTasks

from .ctx import CTX_BG_TASKS


class BgTasks:
    """Unified background task management"""

    @classmethod
    async def init_bg_tasks_obj(cls):
        """Instantiate background tasks and set to context"""
        bg_tasks = BackgroundTasks()
        CTX_BG_TASKS.set(bg_tasks)

    @classmethod
    async def get_bg_tasks_obj(cls):
        """Get background task instance from context"""
        return CTX_BG_TASKS.get()

    @classmethod
    async def add_task(cls, func, *args, **kwargs):
        """Add background task"""
        bg_tasks = await cls.get_bg_tasks_obj()
        bg_tasks.add_task(func, *args, **kwargs)

    @classmethod
    async def execute_tasks(cls):
        """Execute background tasks, usually executed after request result is returned"""
        bg_tasks = await cls.get_bg_tasks_obj()
        if bg_tasks.tasks:
            await bg_tasks()
