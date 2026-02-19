"""Instruction module for PLC models.
"""
from typing import (
    Optional,
)
from controlrox.interfaces import (
    INPUT_INSTRUCTIONS,
    OUTPUT_INSTRUCTIONS,
    INSTR_JSR,
    ILogicInstruction,
    IRung,
    ILogicInstructionType,
)
from .protocols import HasOperands
from .meta import (
    PlcObject,
)


class LogicInstruction(
    ILogicInstruction,
    HasOperands,
    PlcObject[str],
):
    """Logic instruction.
    """

    def __init__(
        self,
        meta_data: str,
        rung: Optional[IRung] = None,
        **kwargs
    ):
        HasOperands.__init__(self)
        PlcObject.__init__(
            self,
            meta_data=meta_data,
            **kwargs
        )
        self._qualified_meta_data: str = ''
        self._instruction_type: ILogicInstructionType = ILogicInstructionType.UNKNOWN
        self._rung: Optional[IRung] = rung

    @property
    def instruction_type(self) -> ILogicInstructionType:
        """get the instruction type for this instruction

        Returns:
            :class:`LogicInstructionType`
        """
        return self.get_instruction_type()

    @property
    def rung(self) -> Optional[IRung]:
        """get the parent rung for this instruction

        Returns:
            :class:`Optional[IRung]`
        """
        return self.get_rung()

    def get_name(self) -> str:
        """get the instruction name

        Returns:
            :class:`str`
        """
        if not self._name:
            # Extract the instruction name from the meta_data
            if '(' in self.meta_data:
                self._name = self.meta_data.split('(')[0].strip()
            else:
                self._name = self.meta_data.strip()
        return self._name

    @property
    def instruction_name(self) -> str:
        """Get the instruction name (e.g. 'XIC', 'OTE').

        Returns:
            str: The instruction name.
        """
        return self.get_name()

    def compile(self):
        self.compile_operands()
        return self

    def get_instruction_type(self) -> ILogicInstructionType:
        """get the instruction type for this instruction

        Returns:
            :class:`LogicInstructionType`
        """
        if self._instruction_type != ILogicInstructionType.UNKNOWN:
            return self._instruction_type

        if self.name in INPUT_INSTRUCTIONS:
            self._instruction_type = ILogicInstructionType.INPUT

        elif self.name in [x[0] for x in OUTPUT_INSTRUCTIONS]:
            self._instruction_type = ILogicInstructionType.OUTPUT

        elif self.name == INSTR_JSR:
            self._instruction_type = ILogicInstructionType.JSR

        else:
            self._instruction_type = ILogicInstructionType.UNKNOWN

        return self._instruction_type

    def get_rung(self) -> Optional[IRung]:
        """get the parent rung for this instruction

        Returns:
            :class:`Optional[IRung]`
        """
        return self._rung

    def set_rung(
        self,
        rung: IRung
    ) -> None:
        """set the parent rung for this instruction

        Args:
            rung: The parent rung to set.
        """
        if not isinstance(rung, IRung):
            raise TypeError("rung must implement IRung interface.")
        self._rung = rung
