"""logic operand interface."""
from abc import abstractmethod
from typing import TYPE_CHECKING
from .meta import IPlcObject

if TYPE_CHECKING:
    from .instruction import ILogicInstruction


class ILogicOperand(
    IPlcObject[str]
):
    """Logic Operand interface
    """

    @property
    def all_parent_operands(self) -> list[str]:
        """Get all parent operands.

        Returns:
            list[str]: List of all parent operand names.
        """
        return self.get_all_parent_operands()

    @property
    def argument_position(self) -> int:
        """Get the argument position.

        Returns:
            int: The position of the argument in the instruction.
        """
        return self.get_argument_position()

    @property
    def base_name(self) -> str:
        """Get the base name of the operand.

        Returns:
            str: The base name of the operand.
        """
        return self.get_base_name()

    @property
    def instruction(self) -> 'ILogicInstruction':
        """Get the instruction this operand belongs to.

        Returns:
            ILogicInstruction: The instruction this operand belongs to.
        """
        return self.get_instruction()

    @property
    def trailing_name(self) -> str:
        """Get the trailing name of the operand.

        Returns:
            str: The trailing name of the operand.
        """
        return self.get_trailing_name()

    @abstractmethod
    def get_all_parent_operands(self) -> list[str]:
        """get all parent operands for this logic operand

        Returns:
            :class:`list[str]`: list of parent operands
        """
        raise NotImplementedError("This method should be overridden by subclasses to get all parents.")

    @abstractmethod
    def get_argument_position(self) -> int:
        """get the positional argument for this logic operand

        Returns:
            :class:`int`: positional argument
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the argument position.")

    @abstractmethod
    def get_base_name(self) -> str:
        """ Get the base name of this operand

        i.e., the first part before any dots. (e.g., "Tag1" for "Tag1.SubTag2.Element3")

        Returns:
            :class:`str`: base name of this operand
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the base name.")

    @abstractmethod
    def get_instruction(self) -> 'ILogicInstruction':
        """get the instruction this operand belongs to

        Returns:
            :class:`ILogicInstruction`: instruction this operand belongs to
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the instruction.")

    @abstractmethod
    def get_trailing_name(self) -> str:
        """get the trailing name of this operand

        Returns:
            :class:`str`: trailing name of this operand
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the trailing name.")


__all__ = [
    'ILogicOperand',
]
