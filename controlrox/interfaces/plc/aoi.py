"""AddOn Instruction Definition interface for PLCs.
"""
from abc import abstractmethod
from .meta import IPlcObject
from .protocols import (
    IHasInstructions,
    IHasRoutines,
    IHasTags
)


class IAddOnInstruction(
    IPlcObject[dict],
    IHasInstructions,
    IHasRoutines,
    IHasTags,
):
    """AddOn Instruction Definition interface for PLCs.
    """

    @property
    @abstractmethod
    def revision(self) -> str:
        """Get the revision of the Add-On Instruction.

        Returns:
            str: The revision string.
        """
        raise NotImplementedError("This property should be overridden by subclasses to get the revision.")

    @abstractmethod
    def get_revision(self) -> str:
        """Get the revision of the Add-On Instruction.

        Returns:
            str: The revision string.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the revision.")

    @abstractmethod
    def set_revision(self, revision: str) -> None:
        """Set the revision of the Add-On Instruction.

        Args:
            revision: The revision string to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the revision.")


__all__ = [
    'IAddOnInstruction',
]
