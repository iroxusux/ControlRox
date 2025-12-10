"""Rung model for PLC.
"""
from typing import (
    List,
    Optional,
    Union
)
from controlrox.interfaces import (
    IController,
    IRoutine,
    IRung,
    ILogicInstruction,
)
from .protocols import HasInstructions
from .meta import PlcObject


class Rung(
    IRung,
    HasInstructions,
    PlcObject[dict],
):

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        controller: Optional[IController] = None,
        routine: Optional[IRoutine] = None,
        comment: str = '',
        rung_text: str = '',
    ) -> None:
        """type class for plc Rung"""
        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
            controller=controller,
        )

        self._routine: Optional[IRoutine] = routine
        self._comment: str = comment
        self._rung_text: str = rung_text

    def __eq__(self, other):
        if not isinstance(other, IRung):
            return False
        if self.rung_text == other.get_rung_text() and self.number == other.get_rung_number():
            return True
        return False

    def __repr__(self):
        return (
            f'Rung(number={self.number}, '
            f'comment={self.comment}, '
            f'text={self.rung_text}, '
            f'instructions={len(self._instructions)}, '
        )

    def __str__(self):
        return self.rung_text

    @property
    def comment(self) -> str:
        return self.get_rung_comment()

    @property
    def routine(self) -> Optional[IRoutine]:
        return self.get_routine()

    @property
    def number(self) -> str:
        return self.get_rung_number()

    @property
    def rung_text(self) -> str:
        return self.get_rung_text()

    @property
    def rung_sequence(self) -> list:
        """Get the sequential elements of this rung including branches."""
        return self.get_rung_sequence()

    def add_instruction(
        self,
        instruction: ILogicInstruction,
        index: Optional[int] = -1
    ) -> None:
        """Add an instruction to this rung.

        Args:
            instruction: The instruction to add.
            index: The index to add the instruction at.
        """
        raise NotImplementedError("add_instruction method must be implemented by subclass.")

    def compile_instructions(self) -> None:
        """Compile the instructions."""
        raise NotImplementedError("compile_instructions method must be implemented by subclass.")

    def clear_instructions(self) -> None:
        """Clear all instructions from this rung."""
        raise NotImplementedError("clear_instructions method must be implemented by subclass.")

    def get_rung_comment(self) -> str:
        return self._comment

    def get_input_instructions(self) -> List[ILogicInstruction]:
        """Get the list of input instructions."""
        if not self._input_instructions:
            self.compile_instructions()
        return self._input_instructions

    def get_output_instructions(self) -> List[ILogicInstruction]:
        """Get the list of output instructions."""
        if not self._output_instructions:
            self.compile_instructions()
        return self._output_instructions

    def get_routine(self) -> Optional[IRoutine]:
        return self._routine

    def get_rung_number(self) -> str:
        raise NotImplementedError("get_rung_number method must be implemented by subclass.")

    def get_rung_sequence(self) -> list:
        raise NotImplementedError("get_rung_sequence method must be implemented by subclass.")

    def get_rung_text(self) -> str:
        return self._rung_text

    def has_instruction(
        self,
        instruction: ILogicInstruction
    ) -> bool:
        """Check if the rung contains a specific instruction.

        Args:
            instruction: The instruction to check for
        Returns:
            bool: True if the instruction exists in the rung
        """
        return instruction in self._instructions

    def remove_instruction(
        self,
        instruction: Union[ILogicInstruction, str, int]
    ) -> None:
        """Remove an instruction from this rung.

        Args:
            instruction: The instruction to remove.
        """
        raise NotImplementedError("remove_instruction method must be implemented by subclass.")

    def set_rung_comment(
        self,
        comment: str
    ) -> None:
        self._comment = comment

    def set_rung_number(
        self,
        rung_number: str
    ) -> None:
        raise NotImplementedError("set_rung_number method must be implemented by subclass.")

    def set_rung_text(
        self,
        text: str
    ) -> None:
        self._rung_text = text
