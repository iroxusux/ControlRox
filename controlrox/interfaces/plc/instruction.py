"""Logic instruction interface."""
from abc import abstractmethod
from typing import Optional, TYPE_CHECKING
from .meta import IPlcObject, LogicInstructionType
from .operand import ILogicOperand

if TYPE_CHECKING:
    from controlrox.interfaces.plc.rung import IRung


class ILogicInstruction(
    IPlcObject[str]
):
    """Logic instruction interface.
    """

    @property
    def instruction_name(self) -> str:
        """get the instruction name for this instruction

        Returns:
            :class:`str`
        """
        return self.get_instruction_name()

    @property
    def instruction_type(self) -> 'LogicInstructionType':
        """get the instruction type for this instruction

        Returns:
            :class:`LogixInstructionType`
        """
        return self.get_instruction_type()

    @property
    def operands(self) -> list['ILogicOperand']:
        """get the instruction operands

        Returns:
            :class:`list[LogixOperand]`
        """
        return self.get_operands()

    @property
    def rung(self) -> Optional['IRung']:
        """get the parent rung for this instruction

        Returns:
            :class:`Optional[IRung]`
        """
        return self.get_rung()

    @abstractmethod
    def get_instruction_name(self) -> str:
        """get the instruction name for this instruction

        Returns:
            :class:`str`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the instruction name.")

    @abstractmethod
    def get_instruction_type(self) -> 'LogicInstructionType':
        """get the instruction type for this instruction

        Returns:
            :class:`LogixInstructionType`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the instruction type.")

    @abstractmethod
    def get_operands(self) -> list['ILogicOperand']:
        """get the instruction operands

        Returns:
            :class:`list[LogixOperand]`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the instruction operands.")

    @abstractmethod
    def get_rung(self) -> Optional['IRung']:
        """get the parent rung for this instruction

        Returns:
            :class:`Optional[IRung]`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the parent rung.")

    @abstractmethod
    def set_rung(
        self,
        rung: 'IRung'
    ) -> None:
        """set the parent rung for this instruction

        Args:
            rung: The parent rung to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the parent rung.")


__all__ = [
    'ILogicInstruction',
]
