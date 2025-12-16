"""GM Tasks
    """
from pyrox.services import log
from pyrox.services.gui import GuiManager
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.services import (
    ControllerInstanceManager,
)


class KDiagWrapperTask(ControllerApplicationTask):
    """General Motors kDiag Message Wrapper Task.
    Go through all kDiags in the controller and validate they are wrapped with '<' and '>' characters.
    """

    def _work(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return

        from controlrox.applications.gm import GmController
        if not isinstance(ctrl, GmController):
            return

        log(self).info('Validating kDiag Wrappings')
        from controlrox.applications.gm.diagnostic_wrapper import wrap_diagnostic_lines
        for prog in ctrl.programs:
            for rout in prog.routines:
                for rung in rout.rungs:
                    rung.set_rung_comment(wrap_diagnostic_lines(rung.get_rung_comment()))

        log(self).info('kDiag Wrapping Validation Complete')

    def inject(self) -> None:
        tools_menu = self.application.menu.get_tools_menu()
        if not tools_menu:
            raise RuntimeError('Tools menu not found!')

        backend = GuiManager.get_backend()
        if not backend:
            raise RuntimeError('GUI backend not found!')

        dropdown_menu = backend.create_gui_menu(
            master=tools_menu.menu,
            name='gm_dkiag_wrapper',
            tearoff=0
        )
        tools_menu.add_submenu(label='GM Tools', submenu=dropdown_menu)

        dropdown_menu.add_item(label='Validate kDiag Wrappings', command=self._work)
