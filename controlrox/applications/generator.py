"""Base Emulation Generator class for all Emulation Generators.
"""
from typing import Optional
from controlrox.models.plc import rockwell as plc
from controlrox.models.tasks import generator


class BaseEmulationGenerator(generator.EmulationGenerator):
    """Base class for emulation logic generators."""
    supporting_class = plc.RaController

    def __init__(
        self,
        controller: plc.RaController
    ) -> None:
        super().__init__(controller)

    def get_base_tags(self) -> list[tuple[str, str, str]]:
        return [
            ('zz_Demo3D_Uninhibit', 'INT', 'Uninhibit mode for the controller.'),
            ('zz_Demo3D_Inhibit', 'INT', 'Inhibit mode for the controller.'),
            ('zz_Demo3D_ToggleInhibit', 'BOOL', 'Toggle inhibit mode for the controller.'),
            ('zz_Demo3D_LocalMode', 'INT', 'Local mode for the controller.'),
            ('zz_Demo3D_TestMode', 'BOOL', 'Demo 3D\nEmulation Test Mode\n-----\nREMOVE IF FOUND IN PRODUCTION'),
        ]

    def get_custom_tags(self) -> list[tuple[str, str, str, Optional[str]]]:
        return []

    def get_emulation_safety_routine_description(self) -> str:
        return self.get_emulation_standard_routine_description()

    def get_emulation_safety_routine_name(self) -> str:
        return 'zzz_s_Emulation'

    def get_emulation_standard_routine_description(self) -> str:
        return ''.join([
            'Emulation routine for automation controller.\n',
            'This routine is auto-generated.\n',
            'Do not modify.'
        ])

    def get_emulation_standard_routine_name(self) -> str:
        return 'zzz_Emulation'

    def get_emulation_safety_program_name(self) -> str:
        return 'MainProgram'

    def get_emulation_standard_program_name(self) -> str:
        return 'MainProgram'

    def get_inhibit_tag(self) -> str:
        return self.base_tags[1][0]

    def get_local_mode_tag(self) -> str:
        return self.base_tags[3][0]

    def get_test_mode_tag(self) -> str:
        return self.base_tags[4][0]

    def get_toggle_inhibit_tag(self) -> str:
        return self.base_tags[2][0]

    def get_uninhibit_tag(self) -> str:
        return self.base_tags[0][0]
