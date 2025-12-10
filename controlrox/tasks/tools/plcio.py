"""PLC Inspection Application
    """
import importlib
from controlrox.applications import plcio
from controlrox.models.tasks.task import ControllerApplicationTask


class PlcIoTask(ControllerApplicationTask):
    """Controller verification task for the PLC verification Application.
    """

    def run(self) -> None:
        mgr = getattr(self, 'manager', None)
        if mgr:
            del self.manager
        importlib.reload(plcio)
        self.manager = plcio.PlcIoApplicationManager(self.application)

    def inject(self) -> None:
        tools_menu = self.application.menu.get_tools_menu()
        if not tools_menu:
            raise RuntimeError('Tools menu not found')

        tools_menu.add_item(
            label='PLC I/O',
            command=self.run
        )
