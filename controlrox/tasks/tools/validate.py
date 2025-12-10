"""Controller Validate Task
"""
from datetime import datetime

from pyrox.services.gui import GuiManager
from pyrox.services.logging import log
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.models.tasks import validator


class ControllerValidatorTask(ControllerApplicationTask):
    """Controller validator task.
    """

    def run(
        self,
        validate_type: str = 'full'
    ) -> None:
        if not self.application.controller:
            return
        ctrl_validator = validator.ControllerValidatorFactory.get_validator(self.application.controller)

        with self.application.multi_stream.temporary_stream(ctrl_validator.log_file_stream):
            log().info(f'--- Starting Controller Validation: {validate_type} ---')
            log().info(f'Timestamp: {datetime.now().isoformat()}')
            log().info(f'Controller: {self.application.controller.name} (ID: {self.application.controller.id})')
            log().info(f'File: {self.application.controller.file_location}')
            log().info(f'Log File: {ctrl_validator.log_file_stream.file_path}')
            log().info('')
            match validate_type:
                case 'full':
                    ctrl_validator.validate_all(self.application.controller)
                case 'properties':
                    ctrl_validator.validate_properties(self.application.controller)
                case 'datatypes':
                    ctrl_validator.validate_datatypes(self.application.controller)
                case 'aois':
                    ctrl_validator.validate_aois(self.application.controller)
                case 'tags':
                    ctrl_validator.validate_tags(self.application.controller)
                case 'modules':
                    ctrl_validator.validate_modules(self.application.controller)
                case 'programs':
                    ctrl_validator.validate_programs(self.application.controller)
                case _:
                    raise ValueError(f'Unknown Validate type: {validate_type}')
            log().info('--- Controller Validation Complete ---')

    def inject(self) -> None:
        tools_menu = self.application.menu.get_tools_menu()
        if not tools_menu:
            raise RuntimeError('Tools menu not found')

        backend = GuiManager.get_backend()
        if not backend:
            raise RuntimeError('GUI backend not found')

        dropdown_menu = backend.create_gui_menu(master=tools_menu.menu, tearoff=0)
        dropdown_menu.add_item(
            label='Validate Controller (All)',
            command=lambda: self.run('full')
        )
        dropdown_menu.add_separator()
        dropdown_menu.add_item(
            label='Validate Controller (Properties Only)',
            command=lambda: self.run('properties')
        )
        dropdown_menu.add_item(
            label='Validate Controller (Datatypes Only)',
            command=lambda: self.run('datatypes')
        )
        dropdown_menu.add_item(
            label='Validate Controller (AOIs Only)',
            command=lambda: self.run('aois')
        )
        dropdown_menu.add_item(
            label='Validate Controller (Modules Only)',
            command=lambda: self.run('modules')
        )
        dropdown_menu.add_item(
            label='Validate Controller (Tags Only)',
            command=lambda: self.run('tags')
        )
        dropdown_menu.add_item(
            label='Validate Controller (Program Only)',
            command=lambda: self.run('programs')
        )
        tools_menu.add_submenu(
            label='Validate',
            submenu=dropdown_menu
        )
