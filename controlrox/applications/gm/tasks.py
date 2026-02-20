"""GM Tasks
    """
import tkinter as tk
from pyrox.services import log
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
                    rung.set_comment(wrap_diagnostic_lines(rung.get_comment()))

        log(self).info('kDiag Wrapping Validation Complete')

    def inject(self) -> None:

        dropdown_menu = tk.Menu(
            master=self.tools_menu,
            name='gm_dkiag_wrapper',
            tearoff=0
        )
        self.tools_menu.add_cascade(label='GM Tools', menu=dropdown_menu)
        dropdown_menu.add_command(label='Validate kDiag Wrappings', command=self._work)
