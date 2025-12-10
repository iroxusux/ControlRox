"""PLC Inspection Application
    """
from pyrox.services.gui import GuiManager
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.services import (
    ControllerInstanceManager,
    create_checklist_from_template,
    inject_emulation_routine,
    remove_emulation_routine
)


class ControllerGenerateTask(ControllerApplicationTask):
    """Controller generation task for the PLC Application.
    """

    def _gen_checklist(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return
        create_checklist_from_template(ctrl)

    def _inject(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return
        inject_emulation_routine(ctrl)

    def _remove(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return
        remove_emulation_routine(ctrl)

    def inject(self) -> None:
        tools_menu = self.application.menu.get_tools_menu()
        if not tools_menu:
            raise RuntimeError('Tools menu not found!')

        backend = GuiManager.get_backend()
        if not backend:
            raise RuntimeError('GUI backend not found!')

        dropdown_menu = backend.create_gui_menu(
            master=tools_menu.menu,
            name='logic_generation',
            tearoff=0
        )
        tools_menu.add_submenu(label='Logic Generation', submenu=dropdown_menu)

        dropdown_menu.add_item(label='Inject Emulation Routine', command=self._inject)
        dropdown_menu.add_item(label='Remove Emulation Routine', command=self._remove)
        dropdown_menu.add_separator()
        dropdown_menu.add_item(label='Generate Checklist', command=self._gen_checklist)
