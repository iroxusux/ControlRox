from __future__ import annotations
import os
from typing import Optional, Union
from pathlib import Path

from pyrox.models import Application, ApplicationTaskFactory
from pyrox.services.env import get_env, set_env, EnvManager
from pyrox.services.logging import log
from controlrox.interfaces import IControllerApplication, IController
from controlrox.models import (
    HasController,
)
from controlrox.services.plc import (
    ControllerInstanceManager
)


ENV_LAST_OPEN_L5X = 'PLC_LAST_OPEN_L5X'


class ControllerApplication(
    Application,
    HasController,
    IControllerApplication,
):

    def build(self):
        super().build()

        # Load Application Tasks
        ApplicationTaskFactory.build_tasks(self)

        # Load last opened controller
        self.load_last_opened_controller()

    def invalidate(self) -> None:
        if self.controller:
            self.controller.invalidate()

    def load_controller(
        self,
        file_location: Union[Path, str]
    ) -> None:
        """Load a controller from a specified .L5X file location.
        Args:
            file_location (str): The file location of the .L5X file to load.
        """
        try:
            self.set_app_state_busy()

            self.set_controller(
                ControllerInstanceManager.load_controller_from_file_location(
                    file_location=file_location,
                ))

        finally:
            self.set_app_state_normal()

    def load_last_opened_controller(self) -> None:
        file = get_env(ENV_LAST_OPEN_L5X, default=None, cast_type=str)
        if file and os.path.isfile(file):
            self.load_controller(file)
        else:
            set_env(ENV_LAST_OPEN_L5X, '')

    def new_controller(self) -> None:
        """Create a new controller instance."""
        log(self).info('Creating new controller instance...')
        raise NotImplementedError('New controller creation is not yet implemented.')

    def refresh(
        self,
        restore_app_state: bool = True
    ) -> None:
        self.set_app_state_busy()
        self.set_app_title()

        if restore_app_state:
            self.set_app_state_normal()

    def save_controller(
        self,
        file_location: Optional[str] = None
    ) -> None:
        if not self.controller:
            log(self).warning('No controller to save.')
            return

        file_location = file_location or self.controller.file_location

        if not file_location or not self.controller or not self.controller.meta_data:
            return

        if not file_location.endswith('.L5X'):
            file_location += '.L5X'

        try:
            ControllerInstanceManager.save_controller_to_file_location(
                controller=self.controller,
                file_location=file_location,
            )
        finally:
            self.refresh()
            self.set_app_state_normal()

    def set_app_title(self) -> None:
        """Set the application title based on the controller name and file location.
        """
        title = EnvManager.get('PYROX_WINDOW_TITLE', 'Pyrox Application', str)
        ctrl = ControllerInstanceManager.get_controller()

        if ctrl:
            self.window.set_title(
                f'{title} - [{ctrl.name}] - [{ctrl.file_location or "Unsaved*"}]'
            )
        else:
            self.window.set_title(title)

    def get_controller(self) -> Optional[IController]:
        """Get the current controller for the application.
        Returns:
            Optional[IController]: The current controller instance, or None if not set.
        """
        return ControllerInstanceManager.get_controller()

    def set_controller(
        self,
        controller: Optional[IController]
    ) -> None:
        """Set the current controller for the application.
        Args:
            controller (Optional[IController]): The controller instance to set.
        """
        if controller and not isinstance(controller, IController):
            raise TypeError(f'Expected {type(IController)}, got {type(controller)}')

        ControllerInstanceManager.set_controller(controller)
        self.invalidate()
        self.refresh()

        if controller and controller.file_location:
            set_env(ENV_LAST_OPEN_L5X, controller.file_location)


__all__ = [
    'ControllerApplication',
]
