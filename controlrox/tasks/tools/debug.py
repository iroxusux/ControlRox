"""Debug task.
    """
from __future__ import annotations


from pyrox.models import ApplicationTask


class DebugTask(ApplicationTask):
    """Debug task for the application.
    """

    def debug(self, *_, **__) -> None:
        """Debug method."""
        pass

    def inject(self) -> None:
        pass
