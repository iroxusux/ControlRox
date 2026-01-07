"""Rung interface."""
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .protocols import IHasSequencedInstructions
from .meta import IPlcObject


class RungElementType(Enum):
    """Types of elements in a rung sequence."""
    INSTRUCTION = "instruction"
    BRANCH_START = "branch_start"
    BRANCH_END = "branch_end"
    BRANCH_NEXT = "branch_next"


@dataclass
class RungElement:
    """Represents an element in the rung sequence."""
    element_type: RungElementType
    instruction: str = ''  # logical text instruction
    branch_id: str = ''
    root_branch_id: str = ''  # ID of the parent branch if this is a nested branch
    branch_level: int = 0  # Level of the branch in the rung
    position: int = 0  # Sequential position in rung


@dataclass
class RungBranch:
    """Represents a branch structure in the rung."""
    branch_id: str
    start_position: int
    end_position: int
    root_branch_id: str = ''  # ID of the parent branch
    nested_branches: List['RungBranch'] = field(default_factory=list)


class IRung(
    IHasSequencedInstructions,
    IPlcObject[dict],
):
    @property
    def comment(self) -> str:
        """Rung comment

        Returns:
            :class:`str`
        """
        return self.get_comment()

    @property
    def number(self) -> int:
        """Rung number of this rung

        Returns:
            :class:`str`: rung number of this rung
        """
        return self.get_number()

    @abstractmethod
    def get_comment(self) -> str:
        """get the comment of this rung

        Returns:
            :class:`str`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the comment.")

    @abstractmethod
    def get_comment_lines(self) -> int:
        """Get the number of comment lines in this rung.

        Returns:
            :class:`int`: number of comment lines
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the number of comment lines.")

    @abstractmethod
    def get_number(self) -> int:
        """get the rung number of this rung

        Returns:
            :class:`int`: rung number of this rung
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the rung number.")

    @abstractmethod
    def set_comment(
        self,
        comment: str
    ) -> None:
        """set the comment of this rung

        Args:
            comment (str): comment to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the comment.")

    @abstractmethod
    def set_number(
        self,
        rung_number: int
    ) -> None:
        """set the rung number of this rung

        Args:
            rung_number: rung number to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the rung number.")


__all__ = [
    'IRung',
    'RungElementType',
    'RungElement',
    'RungBranch'
]
