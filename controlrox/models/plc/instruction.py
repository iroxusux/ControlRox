"""Instruction module for PLC models.
"""
from typing import (
    Optional,
)
from controlrox.interfaces import (
    INPUT_INSTRUCTIONS,
    OUTPUT_INSTRUCTIONS,
    INSTR_JSR,
    IController,
    ILogicInstruction,
    ILogicOperand,
    IRung,
    LogicInstructionType,
)
from .meta import (
    PlcObject,
)


class LogicInstruction(
    ILogicInstruction,
    PlcObject[str],
):
    """Logic instruction.
    """

    def __init__(
        self,
        meta_data: str,
        operands: list[ILogicOperand] = [],
        controller: Optional[IController] = None,
        rung: Optional[IRung] = None,
        **kwargs
    ):
        super().__init__(
            meta_data=meta_data,
            controller=controller,
            **kwargs
        )
        self._qualified_meta_data: str = ''
        self._instruction_name: str = ''
        self._instruction_type: LogicInstructionType = LogicInstructionType.UNKNOWN
        self._operands: list[ILogicOperand] = operands
        self._rung: Optional[IRung] = rung

    @property
    def instruction_name(self) -> str:
        """get the name for this instruction

        Returns:
            :class:`str`
        """
        return self.get_instruction_name()

    @property
    def instruction_type(self) -> LogicInstructionType:
        """get the instruction type for this instruction

        Returns:
            :class:`LogicInstructionType`
        """
        return self.get_instruction_type()

    @property
    def operands(self) -> list[ILogicOperand]:
        """get the instruction operands

        Returns:
            :class:`list[logicOperand]`
        """
        return self.get_operands()

    @property
    def rung(self) -> Optional[IRung]:
        """get the parent rung for this instruction

        Returns:
            :class:`Optional[IRung]`
        """
        return self.get_rung()

    def compile_operands(self) -> None:
        """compile the operands for this instruction
        """
        raise NotImplementedError("This method should be overridden by subclasses to compile the operands.")

    def get_instruction_name(self) -> str:
        """get the instruction name for this instruction

        Returns:
            :class:`str`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the instruction name.")

    def get_instruction_type(self) -> LogicInstructionType:
        """get the instruction type for this instruction

        Returns:
            :class:`LogicInstructionType`
        """
        if self._instruction_type != LogicInstructionType.UNKNOWN:
            return self._instruction_type

        if self.instruction_name in INPUT_INSTRUCTIONS:
            self._instruction_type = LogicInstructionType.INPUT

        elif self.instruction_name in [x[0] for x in OUTPUT_INSTRUCTIONS]:
            self._instruction_type = LogicInstructionType.OUTPUT

        elif self.instruction_name == INSTR_JSR:
            self._instruction_type = LogicInstructionType.JSR

        else:
            self._instruction_type = LogicInstructionType.UNKNOWN

        return self._instruction_type

    def get_operands(self) -> list[ILogicOperand]:
        """get the operands for this instruction
        """
        if not self._operands:
            self.compile_operands()
        return self._operands

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
