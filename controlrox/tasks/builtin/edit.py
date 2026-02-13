""" Edit tasks
"""
from pyrox.services import execute_file_as_subprocess, log
from controlrox.models import ControllerApplicationTask
from controlrox.services import ControllerInstanceManager


class LaunchToStudioTask(ControllerApplicationTask):
    """Launch to Studio 5000 Task
    This task launches the Studio 5000 application with the current controller file.
    """

    def launch_studio(self):
        ctrl = ControllerInstanceManager.get_controller()

        if not ctrl:
            log(self).warning('No controller loaded, cannot launch Studio 5000.')
            return

        ControllerInstanceManager.save_controller_to_file_location(
            ctrl,
            file_location=ctrl.file_location
        )

        if not ctrl:
            log(self).error('Controller file location is not set, cannot launch Studio 5000.')
            return

        execute_file_as_subprocess(ctrl.file_location)

    def inject(self) -> None:
        self.edit_menu.add_item(
            label='Launch to Studio 5000',
            command=self.launch_studio,
        )
