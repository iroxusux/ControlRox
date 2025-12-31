"""Rung interface."""
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union
from .protocols import IHasInstructions
from .meta import IPlcObject
from .instruction import ILogicInstruction


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
    rung: 'IRung'  # Reference to the Rung this element belongs to
    instruction: Optional[ILogicInstruction] = None
    branch_id: str = ''
    root_branch_id: str = ''  # ID of the parent branch if this is a nested branch
    branch_level: int = 0  # Level of the branch in the rung
    position: int = 0  # Sequential position in rung
    rung_number: int = 0  # Rung number this element belongs to


@dataclass
class RungBranch:
    """Represents a branch structure in the rung."""
    branch_id: str
    start_position: int
    end_position: int
    root_branch_id: str = ''  # ID of the parent branch
    nested_branches: List['RungBranch'] = field(default_factory=list)


class IRung(
    IPlcObject[dict],
    IHasInstructions
):
    @property
    def comment(self) -> str:
        """Rung comment

        Returns:
            :class:`str`
        """
        return self.get_rung_comment()

    @property
    def number(self) -> str:
        """Rung number of this rung

        Returns:
            :class:`str`: rung number of this rung
        """
        return self.get_rung_number()

    @property
    def text(self) -> str:
        """Rung text, the ASCII makeup of how the rung is created

        Returns:
            :class:`str`: text of this rung
        """
        return self.get_rung_text()

    @abstractmethod
    def get_rung_comment(self) -> str:
        """get the comment of this rung

        Returns:
            :class:`str`
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the comment.")

    @abstractmethod
    def get_rung_number(self) -> str:
        """get the rung number of this rung

        Returns:
            :class:`str`: rung number of this rung
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the rung number.")

    @abstractmethod
    def get_rung_sequence(self) -> list[RungElement]:
        """get the sequential elements of this rung including branches

        Returns:
            :class:`list[RungElement]`: sequential elements of this rung
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the rung sequence.")

    @abstractmethod
    def get_rung_text(self) -> str:
        """get the text of this rung, the ASCII makeup of how the rung is created

        Returns:
            :class:`str`: text of this rung
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the rung text.")

    @abstractmethod
    def insert_branch(
        self,
        start_pos: int,
        end_pos: int,
    ) -> None:
        """insert a branch into the rung sequence

        Args:
            start_pos (int): position to start the branch
            end_pos (int): position to end the branch
        """
        raise NotImplementedError("This method should be overridden by subclasses to insert a branch.")

    @abstractmethod
    def remove_branch(
        self,
        branch_id: str
    ) -> None:
        """delete a branch from the rung sequence

        Args:
            branch_id (str): ID of the branch to delete
        """
        raise NotImplementedError("This method should be overridden by subclasses to delete a branch.")

    @abstractmethod
    def set_rung_comment(
        self,
        comment: str
    ) -> None:
        """set the comment of this rung

        Args:
            comment (str): comment to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the comment.")

    @abstractmethod
    def set_rung_number(
        self,
        rung_number: Union[str, int]
    ) -> None:
        """set the rung number of this rung

        Args:
            rung_number (str, int): rung number to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the rung number.")

    @abstractmethod
    def set_rung_text(
        self,
        text: str
    ) -> None:
        """set the text of this rung

        Args:
            text (str): text to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the rung text.")


__all__ = [
    'IRung',
    'RungElementType',
    'RungElement',
    'RungBranch'
]
