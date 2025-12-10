""" Edit tasks
"""
from pyrox.services.logging import log
from pyrox.services.process import execute_file_as_subprocess
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.services import ControllerInstanceManager


class LaunchToStudioTask(ControllerApplicationTask):
    """Launch to Studio 5000 Task
    This task launches the Studio 5000 application with the current controller file.
    """

    def launch_studio(self):
        ctrl = ControllerInstanceManager.get_controller()

        if not ctrl:
            log(self).error('No controller loaded, cannot launch Studio 5000.')
            return

        ControllerInstanceManager.save_controller_to_file_location(
            ctrl,
            file_location=ctrl.file_location
        )

        if not ctrl:
            log(self).error('Controller file location is not set.')
            return

        execute_file_as_subprocess(ctrl.file_location)

    def inject(self) -> None:
        if not self.application.menu:
            return

        edit_menu = self.application.menu.get_edit_menu()
        edit_menu.add_separator()
        edit_menu.add_item(
            label='Launch to Studio 5000',
            command=self.launch_studio,
            index='end',
        )
