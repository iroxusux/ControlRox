"""Instruction module for PLC models.
"""
import re
from typing import (
    Optional,
)
from controlrox.interfaces import (
    INPUT_INSTRUCTIONS,
    OUTPUT_INSTRUCTIONS,
    INSTR_JSR,
    IRung,
    LogicInstructionType
)
from controlrox.models.plc.instruction import LogicInstruction

from .meta import (
    RaPlcObject,
    INST_TYPE_RE_PATTERN,
)


class RaLogicInstruction(
    RaPlcObject[str],
    LogicInstruction
):
    """Logix instruction.
    """

    def __init__(
        self,
        meta_data: str,
        rung: Optional[IRung] = None,
    ):
        super().__init__(
            meta_data=meta_data,
            rung=rung
        )

    def get_aliased_meta_data(self) -> str:
        if self._aliased_meta_data:
            return self._aliased_meta_data

        self._aliased_meta_data = self.meta_data

        for operand in self.operands:
            self._aliased_meta_data = self._aliased_meta_data.replace(
                operand.meta_data,
                operand.as_aliased
            )

        return self._aliased_meta_data

    def get_instruction_name(self) -> str:
        if self._instruction_name:
            return self._instruction_name

        matches = re.findall(INST_TYPE_RE_PATTERN, str(self._meta_data))
        if not matches or len(matches) < 1:
            raise ValueError("Corrupt meta data for instruction, no type found!")

        if not matches[0]:
            raise ValueError(f"Corrupt meta data for instruction, invalid type found: '{self._meta_data}'")

        self._instruction_name = matches[0]
        return self._instruction_name

    def get_instruction_type(self) -> LogicInstructionType:
        """get the instruction type for this instruction

        Returns:
            :class:`LogixInstructionType`
        """
        if self.name in INPUT_INSTRUCTIONS:
            return LogicInstructionType.INPUT
        elif self.name in [x[0] for x in OUTPUT_INSTRUCTIONS]:
            return LogicInstructionType.OUTPUT
        elif self.name == INSTR_JSR:
            return LogicInstructionType.JSR
        else:
            return LogicInstructionType.UNKNOWN
