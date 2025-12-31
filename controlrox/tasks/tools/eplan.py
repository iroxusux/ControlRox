"""PLC Eplan Import Task
    """
import importlib
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.services import eplan


class EPlanImportTask(ControllerApplicationTask):
    """Controller Eplan Import task for the PLC Application.
    """

    def _import(self):
        if not self.controller:
            return
        importlib.reload(eplan)
        eplan.import_eplan(self.controller)

    def inject(self) -> None:
        return  # TODO: Disable for now
        tools_menu = self.application.menu.get_tools_menu()
        if not tools_menu:
            return

        tools_menu.add_item(label='EPlan Import', command=self._import)
