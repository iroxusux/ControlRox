"""Interface for PLC Routines.
"""
from abc import abstractmethod
from .protocols import IHasRoutines, IHasRungs, IHasInstructions
from .meta import IPlcObject


class IRoutine(
    IPlcObject[dict],
    IHasInstructions,
    IHasRungs,
):

    @property
    def container(self) -> IHasRoutines:
        """Container of this routine.

        Returns:
            IHasRoutines: The container that holds this routine.
        """
        return self.get_container()

    @abstractmethod
    def block(self) -> None:
        """Block this routine.
        """
        raise NotImplementedError("This method should be overridden by subclasses to block the routine.")

    @abstractmethod
    def check_for_jsr(
        self,
        routine_name: str,
    ) -> bool:
        """Check if this routine contains a JSR instruction to the specified routine.

        Args:
            routine_name (str): The name of the routine to check for in JSR instructions.

        Returns:
            bool: True if a JSR instruction to the specified routine is found, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to check for JSR instructions.")

    @abstractmethod
    def get_container(self) -> IHasRoutines:
        """Get the container of this routine.

        Returns:
            IHasRoutines: The container that holds this routine.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the routine's container.")

    @abstractmethod
    def set_container(self, container) -> None:
        """Set the container of this routine.

        Args:
            container (IHasRoutines): The container to set for this routine.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the routine's container.")

    @abstractmethod
    def unblock(self) -> None:
        """Unblock this routine.
        """
        raise NotImplementedError("This method should be overridden by subclasses to unblock the routine.")


__all__ = [
    'IRoutine',
]
