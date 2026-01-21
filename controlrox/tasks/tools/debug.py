"""Debug task.
    """
from __future__ import annotations


from controlrox.models.tasks.task import ControllerApplicationTask


class DebugTask(ControllerApplicationTask):
    """Debug task for the application.
    """

    def debug(self, *_, **__) -> None:
        """Debug method."""
        print('this is a debug task')

    def inject(self) -> None:
        tools_menu = self.application.menu.get_tools_menu()
        if not tools_menu:
            return

        tools_menu.add_item(label='EPlan Import', command=self.debug)
