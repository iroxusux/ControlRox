"""Emulation Generator interface for PLC applications."""
from abc import abstractmethod
from typing import Optional
from .meta import IPlcObject
from .routine import IRoutine


class IEmulationGenerator(IPlcObject):
    """Interface for emulation logic generators.

    This interface defines the contract for generating emulation logic
    for PLC controllers. Implementations should provide the necessary
    routines, tags, and logic to support emulation modes.
    """

    @property
    def base_tags(self) -> list[tuple[str, str, str]]:
        """List of base tags common to all controllers.

        Returns:
            list[tuple[str, str, str]]: List of tuples (tag_name, datatype, description).
        """
        return self.get_base_tags()

    @property
    def custom_tags(self) -> list[tuple[str, str, str, Optional[str]]]:
        """List of custom tags specific to the controller type.

        Returns:
            list[tuple[str, str, str, Optional[str]]]: List of tuples (tag_name, datatype, description, dimensions).
        """
        return self.get_custom_tags()

    @property
    def emulation_safety_routine(self) -> Optional[IRoutine]:
        """The safety emulation routine, if created.

        Returns:
            Optional[IRoutine]: The safety emulation routine or None.
        """
        return self.get_emulation_safety_routine()

    @property
    def emulation_standard_routine(self) -> Optional[IRoutine]:
        """The standard emulation routine, if created.

        Returns:
            Optional[IRoutine]: The standard emulation routine or None.
        """
        return self.get_emulation_standard_routine()

    @property
    def inhibit_tag(self) -> str:
        """Name of the inhibit tag.

        Returns:
            str: Name of the inhibit tag.
        """
        return self.get_inhibit_tag()

    @property
    def local_mode_tag(self) -> str:
        """Name of the local mode tag.

        Returns:
            str: Name of the local mode tag.
        """
        return self.get_local_mode_tag()

    @property
    def test_mode_tag(self) -> str:
        """Name of the test mode tag.

        Returns:
            str: Name of the test mode tag.
        """
        return self.get_test_mode_tag()

    @property
    def toggle_inhibit_tag(self) -> str:
        """Name of the toggle inhibit tag.

        Returns:
            str: Name of the toggle inhibit tag.
        """
        return self.get_toggle_inhibit_tag()

    @property
    def uninhibit_tag(self) -> str:
        """Name of the uninhibit tag.

        Returns:
            str: Name of the uninhibit tag.
        """
        return self.get_uninhibit_tag()

    @property
    def emulation_safety_program_name(self) -> str:
        """Name of the safety program to add emulation logic to.

        Returns:
            str: Name of the safety program.
        """
        return self.get_emulation_safety_program_name()

    @property
    def emulation_standard_program_name(self) -> str:
        """Name of the standard program to add emulation logic to.

        Returns:
            str: Name of the standard program.
        """
        return self.get_emulation_standard_program_name()

    @abstractmethod
    def get_base_tags(self) -> list[tuple[str, str, str]]:
        """Get the list of base tags common to all controllers.

        Returns:
            list[tuple[str, str, str]]: List of tuples (tag_name, datatype, description).
        """
        raise NotImplementedError("Subclasses must implement 'get_base_tags' method")

    @abstractmethod
    def get_custom_tags(self) -> list[tuple[str, str, str, Optional[str]]]:
        """Get the list of custom tags specific to the controller type.

        Returns:
            list[tuple[str, str, str, Optional[str]]]: List of tuples (tag_name, datatype, description, dimensions).
        """
        raise NotImplementedError("Subclasses must implement 'get_custom_tags' method")

    @abstractmethod
    def get_emulation_safety_routine(self) -> Optional[IRoutine]:
        """Get the safety emulation routine, if created.

        Returns:
            Optional[IRoutine]: The safety emulation routine or None.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_safety_routine' method")

    @abstractmethod
    def get_emulation_safety_routine_description(self) -> str:
        """Get the description for the safety routine to add emulation logic to.

        Returns:
            str: Description of the safety routine.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_safety_routine_description' method")

    @abstractmethod
    def get_emulation_safety_routine_name(self) -> str:
        """Get the name for the safety routine to add emulation logic to.

        Returns:
            str: Name of the safety routine.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_safety_routine_name' method")

    @abstractmethod
    def get_emulation_standard_routine(self) -> Optional[IRoutine]:
        """Get the standard emulation routine, if created.

        Returns:
            Optional[IRoutine]: The standard emulation routine or None.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_standard_routine' method")

    @abstractmethod
    def get_emulation_standard_routine_description(self) -> str:
        """Get the description for the standard routine to add emulation logic to.

        Returns:
            str: Description of the standard routine.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_standard_routine_description' method")

    @abstractmethod
    def get_emulation_standard_routine_name(self) -> str:
        """Get the name for the standard routine to add emulation logic to.

        Returns:
            str: Name of the standard routine.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_standard_routine_name' method")

    @abstractmethod
    def get_emulation_safety_program_name(self) -> str:
        """Get the name of the safety program to add emulation logic to.

        Returns:
            str: Name of the safety program.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_safety_program_name' method")

    @abstractmethod
    def get_emulation_standard_program_name(self) -> str:
        """Get the name of the standard program to add emulation logic to.

        Returns:
            str: Name of the standard program.
        """
        raise NotImplementedError("Subclasses must implement 'get_emulation_standard_program_name' method")

    @abstractmethod
    def get_inhibit_tag(self) -> str:
        """Get the name of the inhibit tag.

        Returns:
            str: Name of the inhibit tag.
        """
        raise NotImplementedError("Subclasses must implement 'get_inhibit_tag' method")

    @abstractmethod
    def get_local_mode_tag(self) -> str:
        """Get the name of the local mode tag.

        Returns:
            str: Name of the local mode tag.
        """
        raise NotImplementedError("Subclasses must implement 'get_local_mode_tag' method")

    @abstractmethod
    def get_test_mode_tag(self) -> str:
        """Get the name of the test mode tag.

        Returns:
            str: Name of the test mode tag.
        """
        raise NotImplementedError("Subclasses must implement 'get_test_mode_tag' method")

    @abstractmethod
    def get_toggle_inhibit_tag(self) -> str:
        """Get the name of the toggle inhibit tag.

        Returns:
            str: Name of the toggle inhibit tag.
        """
        raise NotImplementedError("Subclasses must implement 'get_toggle_inhibit_tag' method")

    @abstractmethod
    def get_uninhibit_tag(self) -> str:
        """Get the name of the uninhibit tag.

        Returns:
            str: Name of the uninhibit tag.
        """
        raise NotImplementedError("Subclasses must implement 'get_uninhibit_tag' method")

    @abstractmethod
    def set_emulation_safety_routine(
        self,
        routine: Optional[IRoutine]
    ) -> None:
        """Set the safety emulation routine.

        Args:
            routine: The safety emulation routine or None.
        """
        raise NotImplementedError("Subclasses must implement 'set_emulation_safety_routine' method")

    @abstractmethod
    def set_emulation_safety_routine_description(
        self,
        description: str
    ) -> None:
        """Set the description for the safety routine to add emulation logic to.

        Args:
            description: Description of the safety routine.
        """
        raise NotImplementedError("Subclasses must implement 'set_emulation_safety_routine_description' method")

    @abstractmethod
    def set_emulation_safety_routine_name(
        self,
        name: str
    ) -> None:
        """Set the name for the safety routine to add emulation logic to.

        Args:
            name: Name of the safety routine.
        """
        raise NotImplementedError("Subclasses must implement 'set_emulation_safety_routine_name' method")

    @abstractmethod
    def set_emulation_standard_routine(
        self,
        routine: Optional[IRoutine]
    ) -> None:
        """Set the standard emulation routine.

        Args:
            routine: The standard emulation routine or None.
        """
        raise NotImplementedError("Subclasses must implement 'set_emulation_standard_routine' method")

    @abstractmethod
    def set_emulation_standard_routine_description(
        self,
        description: str
    ) -> None:
        """Set the description for the standard routine to add emulation logic to.

        Args:
            description: Description of the standard routine.
        """
        raise NotImplementedError("Subclasses must implement 'set_emulation_standard_routine_description' method")

    @abstractmethod
    def set_emulation_standard_routine_name(
        self,
        name: str
    ) -> None:
        """Set the name for the standard routine to add emulation logic to.

        Args:
            name: Name of the standard routine.
        """
        raise NotImplementedError("Subclasses must implement 'set_emulation_standard_routine_name' method")

    @abstractmethod
    def generate_emulation_logic(self):
        """Main entry point to generate emulation logic.

        Returns:
            The modification schema with all changes.
        """
        raise NotImplementedError("Subclasses must implement 'generate_emulation_logic' method")

    @abstractmethod
    def remove_emulation_logic(self):
        """Remove previously added emulation logic.

        Returns:
            The modification schema with all removals.
        """
        raise NotImplementedError("Subclasses must implement 'remove_emulation_logic' method")


__all__ = (
    'IEmulationGenerator',
)
