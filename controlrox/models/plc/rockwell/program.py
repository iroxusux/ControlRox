"""Program module for pyrox
"""
from typing import Optional
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.interfaces import (
    ILogicInstruction,
    IRoutine,
)
from controlrox.models.plc import Program
from controlrox.services import ControllerInstanceManager
from controlrox.services.plc.program import ProgramFactory
from .meta import RaPlcObject, PLC_PROG_FILE


class RaProgram(
    RaPlcObject[dict],
    Program,
    metaclass=FactoryTypeMeta['RaProgram', ProgramFactory]
):

    default_l5x_file_path = PLC_PROG_FILE
    default_l5x_asset_key = 'Program'

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Name',
            '@TestEdits',
            '@MainRoutineName',
            '@Disabled',
            '@Class',
            '@UseAsFolder',
            'Description',
            'Tags',
            'Routines',
        ]

    @property
    def disabled(self) -> str:
        return self['@Disabled']

    @property
    def main_routine(self) -> Optional[IRoutine]:
        """get the main routine for this program

        Returns:
            Routine: The main routine of this program.
        """
        if not self.main_routine_name:
            return None
        return self.routines.get(self.main_routine_name, None)

    @property
    def main_routine_name(self) -> str:
        return self['@MainRoutineName']

    @property
    def raw_routines(self) -> list[dict]:
        return self.get_raw_routines()

    @property
    def test_edits(self) -> str:
        return self['@TestEdits']

    @property
    def use_as_folder(self) -> str:
        return self['@UseAsFolder']

    @classmethod
    def get_factory(cls):
        return ProgramFactory

    def block_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        """block a routine in this program

        Args:
            routine_name (str): name of the routine to block
            blocking_bit (str): tag name of the bit to use for blocking
        """
        jsrs = self.get_instructions(instruction_filter='JSR')
        for jsr in jsrs:
            operands = jsr.get_operands()

            if not operands:
                raise ValueError(f'JSR instruction {jsr.name} has no operands!')

            if jsr.get_operands()[0].meta_data != routine_name:
                continue
            rung = jsr.get_rung()
            if not rung:
                raise ValueError(f'JSR instruction {jsr.name} has no rung!')
            if rung.get_rung_text().startswith(f'XIC({blocking_bit})'):
                continue
            rung.set_rung_text(f'XIC({blocking_bit}){rung.get_rung_text()}')

    def compile_instructions(self) -> None:
        """Compile instructions for this program."""
        self._instructions = []
        for routine in self.get_routines():
            self._instructions.extend(routine.get_instructions())

    def compile_routines(self) -> None:
        """Compile routines for this program."""
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError('Controller is not set for this program!')

        self._routines.clear()
        raw_routines = self.get_asset_from_meta_data('Routines', 'Routine')
        for routine_data in raw_routines:
            self._routines.append(
                ctrl.create_routine(
                    container=self,
                    meta_data=routine_data
                ))

    def compile_tags(self) -> None:
        """Compile tags for this program."""
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError('Controller is not set for this program!')

        self._tags.clear()
        raw_tags = self.get_asset_from_meta_data('Tags', 'Tag')
        for tag_data in raw_tags:
            self._tags.append(
                ctrl.create_tag(
                    container=self,
                    controller=self.controller,
                    meta_data=tag_data
                ))

    def get_instructions(
        self,
        instruction_filter: str = '',
        operand_filter: str = ''
    ) -> list[ILogicInstruction]:
        if not self._instructions:
            self.compile_instructions()

        if not instruction_filter and not operand_filter:
            return self._instructions

        filtered_inst: list[ILogicInstruction] = []
        for inst in self._instructions:
            if instruction_filter:
                if inst.name != instruction_filter:
                    continue

            if operand_filter:
                operands = inst.get_operands()
                if not operands:
                    continue
                operand_names = [op.meta_data for op in operands]
                if operand_filter not in operand_names:
                    continue

            filtered_inst.append(inst)
        return filtered_inst

    def get_main_routine(self) -> Optional[IRoutine]:
        """get the main routine for this program

        Returns:
            Routine: The main routine of this program.
        """
        if not self.main_routine_name:
            return None
        return self.routines.get(self.main_routine_name, None)

    def get_raw_routines(self) -> list[dict]:
        """Get the raw routines metadata.

        Returns:
            list[dict]: List of raw routine metadata dictionaries.
        """
        meta_data = self.get_meta_data()
        if not isinstance(meta_data, dict):
            raise TypeError("Meta data must be a dictionary!")

        if not meta_data['Routines']:
            meta_data['Routines'] = {'Routine': []}
        if not isinstance(meta_data['Routines']['Routine'], list):
            meta_data['Routines']['Routine'] = [meta_data['Routines']['Routine']]
        return meta_data['Routines']['Routine']

    def is_safe(self) -> bool:
        return self.meta_data.get('@Class', '').lower() == 'safety'

    def unblock_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        """unblock a routine in this program

        Args:
            routine_name (str): name of the routine to unblock
            blocking_bit (str): tag name of the bit to use for blocking
        """
        jsrs = self.get_instructions(instruction_filter='JSR')
        for jsr in jsrs:
            if jsr.get_operands()[0] != routine_name:
                continue
            rung = jsr.get_rung()
            if not rung:
                raise ValueError(f'JSR instruction {jsr.name} has no rung!')
            if not rung.get_rung_text().startswith(f'XIC({blocking_bit})'):
                continue
            rung.set_rung_text(rung.get_rung_text().replace(f'XIC({blocking_bit})', '', 1))
