"""Ford specific emulation logic generator."""
from typing import Optional
from controlrox.applications.generator import BaseEmulationGenerator
from controlrox.interfaces import IController
from .gm import GmController


class GmEmulationGenerator(BaseEmulationGenerator):
    """General Motors specific emulation logic generator."""
    supporting_class = GmController

    @property
    def controller(self) -> GmController:
        if not self._controller:
            self.get_controller()
        if not isinstance(self._controller, GmController):
            raise ValueError(f'Controller must be of type {GmController.__name__}')
        return self._controller

    @controller.setter
    def controller(self, controller: Optional[IController]):
        if not isinstance(controller, GmController):
            raise TypeError(f'Controller must be of type {GmController.__name__}')
        self._controller = controller

    @property
    def emulation_safety_program_name(self) -> str:
        if not self.controller.safety_common_program:
            return ''
        return self.controller.safety_common_program.name

    @property
    def emulation_standard_program_name(self) -> str:
        if not self.controller.mcp_program:
            return ''
        return self.controller.mcp_program.name

    def get_custom_tags(self) -> list[tuple[str, str, str, str | None]]:
        """List of custom tags specific to the controller type.

        Returns:
            list[str]: List of tuples (tag_name, datatype, description, dimensions).
        """
        return [
            ('DeviceDataSize', 'DINT', 'Size of the DeviceData array.', None),
            ('LoopPtr', 'DINT', 'Pointer for looping through devices.', None),
        ]

    def _generate_custom_standard_rungs(self):
        self.add_rung_to_standard_routine(
            self.controller.create_rung(
                rung_text='XIC(Flash.Norm)OTE(Flash.Fast);',
                comment='// Reduce fast flash rate to limit communication issues with the 3d model.'
            )
        )

        self.add_rung_to_standard_routine(
            self.controller.create_rung(
                rung_text='SIZE(EnetStorage.DeviceData,0,DeviceDataSize)SUB(DeviceDataSize,1,DeviceDataSize)CLR(LoopPtr);',
                comment='// Prepare device data sizes for communications processing.'
            )
        )

        self.add_rung_to_standard_routine(
            self.controller.create_rung(
                rung_text=f'LBL(Loop)XIC({self.toggle_inhibit_tag})LES(LoopPtr,DeviceDataSize)ADD(LoopPtr,1,LoopPtr)OTU(EnetStorage.DeviceData[LoopPtr].Connected)OTL(EnetStorage.DeviceData[LoopPtr].LinkStatusAvail)OTL(EnetStorage.DeviceData[LoopPtr].Link.Scanned)JMP(Loop);',  # noqa: E501
                comment='Loop through the devices to force the GM Network model to accept all ethernet connections as "OK".'
            )
        )
