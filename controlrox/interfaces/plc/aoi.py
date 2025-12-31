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
        return self.get_revision()

    @property
    @abstractmethod
    def parameters(self) -> list[dict]:
        """Get the parameters of the Add-On Instruction.

        Returns:
            list[dict]: The list of parameter definitions.
        """
        return self.get_parameters()

    @abstractmethod
    def get_parameters(self) -> list[dict]:
        """Get the parameters of the Add-On Instruction.

        Returns:
            list[dict]: The list of parameter definitions.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the parameters.")

    @abstractmethod
    def set_parameters(self, parameters: list[dict]) -> None:
        """Set the parameters of the Add-On Instruction.

        Args:
            parameters: The list of parameter definitions to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the parameters.")

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
