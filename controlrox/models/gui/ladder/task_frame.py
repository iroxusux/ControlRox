"""Task frame for ladder logic editor.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from pyrox.services.logging import log
from pyrox.models.gui.frame import TaskFrame
from controlrox.interfaces import (
    IRoutine,
)
from controlrox.models.gui.ladder.canvas import LadderCanvas
from controlrox.models.gui.ladder.edit_mode import LadderEditorMode


class LadderEditorTaskFrame(TaskFrame):
    """Main task frame for the ladder logic editor."""

    def __init__(
        self,
        master,
        routine: Optional[IRoutine] = None,
        **kwargs
    ):
        name = f"Ladder Editor - {routine.name if routine else 'New Routine'}"
        super().__init__(
            master,
            name=name,
            **kwargs
        )

        self._routine = routine
        self._debug_mode = False
        self._setup_ui()

    @property
    def ladder_canvas(self) -> LadderCanvas:
        """Get the ladder canvas."""
        return self._ladder_canvas

    @property
    def status_label(self) -> tk.Label:
        """Get the status label."""
        return self._status_label

    def _setup_ui(
        self
    ):
        """Setup the ladder editor UI."""
        # Create toolbar
        self._create_toolbar()

        # Create main editor area with scrollbars
        self._create_editor_area()

        # Create status bar
        self._create_status_bar()

    def _create_toolbar(self):
        """Create the editor toolbar."""
        toolbar = tk.Frame(self.content_frame, height=40, relief='raised', bd=1)
        toolbar.pack(fill='x', side='top')

        # Mode buttons
        tk.Button(
            toolbar,
            text="Select",
            command=lambda: self._set_mode(LadderEditorMode.VIEW)
        ).pack(side='left', padx=2)

        tk.Button(
            toolbar,
            text="Contact",
            command=lambda: self._set_mode(LadderEditorMode.INSERT_CONTACT)
        ).pack(side='left', padx=2)

        tk.Button(
            toolbar,
            text="Coil",
            command=lambda: self._set_mode(LadderEditorMode.INSERT_COIL)
        ).pack(side='left', padx=2)

        tk.Button(
            toolbar,
            text="Block",
            command=lambda: self._set_mode(LadderEditorMode.INSERT_BLOCK)
        ).pack(side='left', padx=2)

        # Branch controls
        tk.Button(
            toolbar,
            text="Branch",
            command=lambda: self._set_mode(LadderEditorMode.INSERT_BRANCH)
        ).pack(side='left', padx=2)

        # Separator
        ttk.Separator(
            toolbar,
            orient='vertical'
        ).pack(side='left', fill='y', padx=5)

        # Rung operations
        tk.Button(
            toolbar,
            text="Add Rung",
            command=self._add_rung
        ).pack(side='left', padx=2)

        tk.Button(
            toolbar,
            text="Delete Rung",
            command=self._delete_current_rung
        ).pack(side='left', padx=2)

        # Separator
        ttk.Separator(
            toolbar,
            orient='vertical'
        ).pack(side='left', fill='y', padx=5)

        # File operations
        tk.Button(
            toolbar,
            text="Verify",
            command=self._verify_routine
        ).pack(side='left', padx=2)

        tk.Button(
            toolbar,
            text="Accept",
            command=self._accept_changes
        ).pack(side='left', padx=2)

    def _create_editor_area(self):
        """Create the main editor canvas with scrollbars."""
        editor_frame = tk.Frame(self.content_frame)
        editor_frame.pack(fill='both', expand=True)

        # Create canvas with scrollbars
        self._ladder_canvas = LadderCanvas(
            editor_frame,
            routine=self.routine
        )

        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(
            editor_frame,
            orient='vertical',
            command=self._ladder_canvas.yview
        )
        self._ladder_canvas.configure(yscrollcommand=v_scrollbar.set)

        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(
            editor_frame,
            orient='horizontal',
            command=self._ladder_canvas.xview
        )
        self._ladder_canvas.configure(xscrollcommand=h_scrollbar.set)

        # Grid layout
        self._ladder_canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

    def _create_status_bar(self):
        """Create the status bar."""
        self._status_bar = tk.Frame(self.content_frame, height=25, relief='sunken', bd=1)
        self._status_bar.pack(fill='x', side='bottom')

        self._status_label = tk.Label(self._status_bar, text="Ready", anchor='w')
        self._status_label.pack(side='left', padx=5)

        # Mode indicator
        self._mode_label = tk.Label(self._status_bar, text="Mode: View", anchor='e')
        self._mode_label.pack(side='right', padx=5)

    def _set_mode(self, mode: LadderEditorMode):
        """Set the editor mode."""
        self._ladder_canvas.mode = mode
        self._mode_label.config(text=f"Mode: {mode.value.title()}")
        self._status_label.config(text=f"Mode changed to {mode.value}")

    def _add_rung(self):
        """Add a new rung to the routine."""
        rung_number = self.ladder_canvas.add_rung()
        self.status_label.config(text=f"Added rung {rung_number}")

    def _delete_current_rung(self):
        """Delete the currently selected rung."""
        # This would need logic to determine which rung is selected
        self._status_label.config(text="Delete rung functionality not implemented")

    def _verify_routine(self):
        """Verify the routine for errors."""
        log(self).info('Not Yet Implemented...')

    def _accept_changes(self):
        """Accept changes and close editor."""
        if self._routine:
            # This would save changes back to the routine
            self._status_label.config(text="Changes accepted")
        self.destroy()

    def draw_routine(self):
        """Draw the current routine on the canvas."""
        self.ladder_canvas.draw_routine()

    @property
    def routine(self) -> IRoutine:
        """Get the current routine."""
        if not self._routine:
            raise ValueError("No routine is currently loaded.")
        return self._routine

    @routine.setter
    def routine(self, value: IRoutine):
        """Set the routine to edit."""
        if not value or not isinstance(value, IRoutine):
            raise ValueError("Invalid routine provided.")

        self._routine = value
        self._ladder_canvas.routine = value
        if value:
            self._name = f"Ladder Editor - {value.name}"
            self._status_label.config(text=f"Loaded routine: {value.name}")


if __name__ == "__main__":
    from controlrox.applications import App
    from controlrox.services import ControllerInstanceManager
    app = App()
    app.build()
    ctrl = ControllerInstanceManager.new_controller()
    routine = ctrl.create_routine(name="Test Routine")
    rung = ctrl.create_rung()
    routine.add_rung(rung)

    frame = LadderEditorTaskFrame(
        master=app.workspace.workspace_area.frame_root,
        routine=routine
    )

    app.workspace.add_workspace_task_frame(frame)
    frame.draw_routine()
    app.start()
