"""Ladder logic application module.
"""
from __future__ import annotations
from typing import Optional
from ..models.gui import ladder
from controlrox.interfaces import IController, IRoutine
from controlrox.models.tasks.task import ControllerApplicationTask


class LadderEditorApplicationTask(ControllerApplicationTask):
    """Ladder editor application task.
    """

    def __init__(self, application):
        super().__init__(application)
        self._task_frame: Optional[ladder.LadderEditorTaskFrame] = None

    def run(
        self,
        routine: Optional[IRoutine] = None,
        controller: Optional[IController] = None
    ) -> None:
        """Run the ladder editor task.
        """
        frame = self.application.workspace.workspace_area.frame
        if not frame:
            raise RuntimeError("Workspace frame is not available.")

        if not self._task_frame:
            self._task_frame = ladder.LadderEditorTaskFrame(
                master=frame.root,
                controller=controller or self.application.controller,
                routine=routine
            )
        self.application.workspace.add_workspace_task_frame(self._task_frame)
