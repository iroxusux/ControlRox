""" file tasks
"""
from typing import Optional
from pyrox.services import GuiManager, log, get_open_file, get_save_file
from controlrox.models import ControllerApplicationTask


class FileTask(ControllerApplicationTask):

    def _prompt_for_controller_closing(self) -> bool:
        # Prompt if a controller is already loaded
        if self.application.controller is not None:
            backend = GuiManager.get_backend()
            if not backend:
                raise RuntimeError('No GUI backend available for prompting user.')

            return backend.prompt_user_yes_no(
                "Open New File",
                "A controller is currently loaded. Do you want to continue and open a new file?"
            )
        return True

    def _on_file_close(self):
        """Close the current controller instance."""
        if not self.application.controller:
            log(self).warning('No controller loaded, cannot close...')
            return
        if not self._prompt_for_controller_closing():
            return
        self.application.set_controller(None)
        log(self).info('Controller instance closed successfully.')

    def _on_file_new(self):
        """Create a new controller instance."""
        if self.application.controller is not None:
            if not self._prompt_for_controller_closing():
                return
        raise NotImplementedError('New controller creation not implemented yet.')

    def _on_file_open(
        self,
        file_location: Optional[str] = None
    ) -> None:
        if not self._prompt_for_controller_closing():
            return

        if not file_location:
            file_location = get_open_file([("L5X XML Files", ".L5X")])

        if not file_location:
            log(self).warning('No file selected...')
            return

        self.application.load_controller(file_location)

    def _on_file_save(
        self,
        file_location: Optional[str] = None,
        save_as: bool = False
    ) -> None:
        if not self.application.controller:
            log(self).warning('No controller loaded, cannot save...')
            return

        file_location = file_location or self.application.controller.get_file_location()

        if save_as is True:
            file_location = None

        if not file_location:
            file_location = get_save_file([("L5X XML Files", ".L5X")])

        if not file_location:
            return log(self).warning('No save location selected...')

        self.application.save_controller(file_location=file_location)

    def inject(self) -> None:
        self.file_menu.add_separator()
        self.file_menu.add_item(
            label='New Controller',
            command=self._on_file_new,
            accelerator='Ctrl+N',
            underline=0,
            binding_info=('<Control-n>', lambda e: self._on_file_new())
        )
        self.file_menu.add_separator()
        self.file_menu.add_item(
            label='Open Controller',
            command=self._on_file_open,
            accelerator='Ctrl+O',
            underline=0,
            binding_info=('<Control-o>', lambda e: self._on_file_open())
        )
        self.file_menu.add_item(
            label='Save Controller',
            command=self._on_file_save,
            accelerator='Ctrl+S',
            underline=0,
            binding_info=('<Control-s>', lambda e: self._on_file_save())
        )
        self.file_menu.add_item(
            label='Save Controller As...',
            command=lambda: self._on_file_save(save_as=True),
            accelerator='Ctrl+Shift+S',
            underline=0,
            binding_info=('<Control-Shift-s>', lambda e: self._on_file_save(save_as=True))
        )
        self.file_menu.add_separator()
        self.file_menu.add_item(
            index=6,
            label='Close Controller',
            command=self._on_file_close,
            accelerator='Ctrl+W',
            underline=0,
            binding_info=('<Control-w>', lambda e: self._on_file_close())
        )
