"""Pyrox routine model
"""
from typing import (
    Self,
)
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.models.plc.rockwell.meta import PLC_ROUT_FILE
from controlrox.interfaces import ILogicInstructionType
from controlrox.models.plc import Routine
from controlrox.services.plc.routine import RoutineFactory
from .meta import RaPlcObject


class RaRoutine(
    RaPlcObject[dict],
    Routine,
    metaclass=FactoryTypeMeta['RaRoutine', RoutineFactory]
):
    default_l5x_file_path = PLC_ROUT_FILE
    default_l5x_asset_key = 'Routine'

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Name',
            '@Type',
            'Description',
            'RLLContent',
        ]

    def compile(self) -> Self:
        """compile this object from its meta data

        This method should be overridden by subclasses to provide specific compilation logic.
        """
        self.compile_rungs()
        self.compile_instructions()
        return self

    def compile_instructions(self):
        """compile the instructions in this routine

        This method compiles the instructions from the rungs and initializes the lists.
        """
        self._input_instructions = []
        self._output_instructions = []
        self._instructions = []

        for rung in self.rungs:
            self._input_instructions.extend(rung.get_input_instructions())
            self._output_instructions.extend(rung.get_output_instructions())
            self._instructions.extend(rung.get_instructions())

    def invalidate(self):
        self._instructions.clear()
        self._input_instructions.clear()
        self._output_instructions.clear()
        self._rungs.clear()

    def check_for_jsr(
        self,
        routine_name: str,
    ) -> bool:
        """Check if this routine contains a JSR instruction to the specified routine.

        Args:
            routine_name (str): The name of the routine to check for in JSR instructions.

        Returns:
            bool: True if a JSR instruction to the specified routine is found, False otherwise.
        """
        for instruction in self.instructions:
            if instruction.get_instruction_type() == ILogicInstructionType.JSR and instruction.get_operands():
                if str(instruction.get_operands()[0]) == routine_name:
                    return True
        return False

    def get_raw_rungs(self) -> list[dict]:
        """Get the raw rungs from the routine metadata.

        Returns:
            list[dict]: A list of raw rung metadata dictionaries.
        """
        if not self['RLLContent']:
            self['RLLContent'] = {'Rung': []}
        if not isinstance(self['RLLContent']['Rung'], list):
            self['RLLContent']['Rung'] = [self['RLLContent']['Rung']]
        return self['RLLContent']['Rung']
