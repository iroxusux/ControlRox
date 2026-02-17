""" view tasks
    """
from __future__ import annotations

from pyrox.interfaces import IGuiBackend
from pyrox.services.logging import log
from pyrox.services.gui import GuiManager
from controlrox.models.tasks.task import ControllerApplicationTask


class ViewTask(ControllerApplicationTask):

    def _open_dir(self, dir_location: str):
        """Open a directory in the file explorer."""

        if not dir_location:
            log(self).warning('No directory selected...')
            return

        log(self).info('Opening directory -> %s', dir_location)
        try:
            import os
            os.startfile(dir_location)
        except Exception as e:
            log(self).error(f'Failed to open directory: {e}')

    def inject(self) -> None:
        dropdown_menu = self.gui.unsafe_get_backend().create_gui_menu(
            master=self.view_menu.menu,
            name='application_directories',
            tearoff=0
        )

        self.view_menu.add_submenu(
            submenu=dropdown_menu,
            label='Application Directories',
        )

        for dir_name in self.application.directory.all_directories():
            dropdown_menu.add_item(
                label=dir_name,
                command=lambda d=dir_name: self._open_dir(
                    self.application.directory.all_directories()[d]
                )
            )

        self.view_menu.add_separator()
        self.view_menu.add_item(
            label='Toggle Organizer',
            command=self.application.workspace.toggle_sidebar,
            accelerator='Ctrl+B',
            underline=0
        )
