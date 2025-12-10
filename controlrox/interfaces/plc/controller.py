"""PLC type module for Pyrox framework."""
from abc import abstractmethod
from typing import (
    Any,
    List,
    Optional,
)


from .meta import IPlcObject
from .protocols import (
    IHasAOIs,
    IHasDatatypes,
    IHasModules,
    IHasPrograms,
    IHasRoutines,
    IHasTags,
)

from .aoi import IAddOnInstruction
from .datatype import IDatatype
from .module import IModule
from .program import IProgram
from .routine import IRoutine
from .rung import IRung
from .tag import ITag


class IController(
    IPlcObject[dict],
    IHasAOIs,
    IHasDatatypes,
    IHasModules,
    IHasPrograms,
    IHasTags,
):

    @property
    def file_location(self) -> str:
        """Get the file location of the controller."""
        return self.get_file_location()

    @property
    def safety_info(self) -> 'IControllerSafetyInfo':
        """Get the safety info of the controller."""
        return self.get_controller_safety_info()

    @classmethod
    @abstractmethod
    def from_file(
        cls,
        file_location: str,
        meta_data: Optional[dict] = None
    ) -> 'IController':
        """Create a controller instance from a file.

        Args:
            file_location: The path to the file.
            meta_data: Optional metadata for the controller.
        Returns:
            IController: The created controller instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a controller from a file.")

    @classmethod
    @abstractmethod
    def from_meta_data(
        cls,
        meta_data: dict,
        file_location: str = '',
        comms_path: str = '',
        slot: int = 0
    ) -> 'IController':
        """Create a controller instance from metadata.

        Args:
            meta_data: The metadata dictionary.
            file_location: Optional file location.
            comms_path: Optional communication path.
            slot: Optional slot number.
        Returns:
            IController: The created controller instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a controller from metadata.")

    @abstractmethod
    def compile_aois(self) -> None:
        """Compile all AOIs in this controller."""
        raise NotImplementedError("This method should be overridden by subclasses to compile AOIs.")

    @abstractmethod
    def compile_datatypes(self) -> None:
        """Compile all datatypes in this controller."""
        raise NotImplementedError("This method should be overridden by subclasses to compile datatypes.")

    @abstractmethod
    def compile_modules(self) -> None:
        """Compile all modules in this controller."""
        raise NotImplementedError("This method should be overridden by subclasses to compile modules.")

    @abstractmethod
    def compile_tags(self) -> None:
        """Compile all tags in this controller."""
        raise NotImplementedError("This method should be overridden by subclasses to compile tags.")

    @abstractmethod
    def create_aoi(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IAddOnInstruction:
        """Create an Add-On Instruction (AOI) instance.

        Args:
            name: The name of the AOI.
            description: The description of the AOI.
            meta_data: Optional metadata for the AOI.
        Returns:
            IAddOnInstruction: The created AOI instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create an AOI.")

    @abstractmethod
    def create_datatype(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IDatatype:
        """Create a datatype instance.

        Args:
            name: The name of the datatype.
            description: The description of the datatype.
            meta_data: Optional metadata for the datatype.
        Returns:
            IDatatype: The created datatype instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a datatype.")

    @abstractmethod
    def create_module(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IModule:
        """Create a module instance.

        Args:
            name: The name of the module.
            description: The description of the module.
            meta_data: Optional metadata for the module.
        Returns:
            IModule: The created module instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a module.")

    @abstractmethod
    def create_program(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None
    ) -> IProgram:
        """Create a program instance.

        Args:
            name: The name of the program.
            description: The description of the program.
            meta_data: Optional metadata for the program.
        Returns:
            IProgram: The created program instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a program.")

    @abstractmethod
    def create_routine(
        self,
        name: str = '',
        description: str = '',
        meta_data: Optional[dict] = None,
        container: Optional[IHasRoutines] = None
    ) -> IRoutine:
        """Create a routine instance.

        Args:
            name: The name of the routine.
            description: The description of the routine.
            meta_data: Optional metadata for the routine.
        Returns:
            IRoutine: The created routine instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a routine.")

    @abstractmethod
    def create_rung(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        routine: Optional['IRoutine'] = None,
        comment: str = '',
        rung_text: str = '',
        rung_number: int = -1
    ) -> IRung:
        """Create a rung instance.

        Args:
            meta_data: Optional metadata for the rung.
            name: The name of the rung.
            description: The description of the rung.
            routine: The routine to associate with the rung.
            comment: The comment for the rung.
            rung_text: The text of the rung.
            rung_number: The number of the rung.
        Returns:
            IRung: The created rung instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a rung.")

    @abstractmethod
    def create_tag(
        self,
        name: str = '',
        datatype: str = '',
        description: str = '',
        container: Optional[IHasTags] = None,
        meta_data: Optional[dict] = None,
        **kwargs,
    ) -> ITag:
        """Create a tag instance.

        Args:
            name: The name of the tag.
            data_type: The data type of the tag.
            description: The description of the tag.
            container: The container object for the tag.
            meta_data: Optional metadata for the tag.
        Returns:
            ITag: The created tag instance.
        """
        raise NotImplementedError("This method should be overridden by subclasses to create a tag.")

    @abstractmethod
    def get_comms_path(self) -> Optional[str]:
        """Get the communication path of the controller.

        Returns:
            Optional[str]: The communication path, or None if not set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the comm path.")

    @abstractmethod
    def get_controller_safety_info(self) -> 'IControllerSafetyInfo':
        """Get the safety info of the controller.

        Returns:
            IControllerSafetyInfo: The controller safety info.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get controller safety info.")

    @abstractmethod
    def get_file_location(self) -> str:
        """Get the file location of the controller.

        Returns:
            str: The file location.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the file location.")

    @abstractmethod
    def get_slot(self) -> int:
        """Get the slot number of the controller.

        Returns:
            int: The slot number, or None if not set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the slot.")

    @abstractmethod
    def import_assets_from_file(
        self,
        file_location: str,
        asset_types: Optional[List[str]]
    ) -> None:
        """Import assets into this controller from an L5X file.

        Args:
            file_location: The path to the L5X file.
            asset_types: A list of asset types to import , or None to import all types.
        """
        raise NotImplementedError("This method should be overridden by subclasses to import assets from a file.")

    @abstractmethod
    def set_comms_path(self, comms_path: str) -> None:
        """Set the communication path of the controller.

        Args:
            comms_path: The communication path to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the comm path.")

    @abstractmethod
    def set_file_location(self, file_location: Optional[str]) -> None:
        """Set the file location of the controller.

        Args:
            file_location: The file location to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the file location.")

    @abstractmethod
    def set_slot(self, slot: int) -> None:
        """Set the slot number of the controller.

        Args:
            slot: The slot number to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the slot.")


class IControllerSafetyInfo:

    @property
    def configure_safety_io_always(self) -> bool:
        """Get whether safety IO is always configured.

        Returns:
            bool: True if always configured, False otherwise.
        """
        return self.get_configure_safety_io_always()

    @property
    def safety_level(self) -> str:
        """Get the safety level of the controller.

        Returns:
            str: The safety level.
        """
        return self.get_safety_level()

    @property
    def safety_locked(self) -> bool:
        """Get whether the controller is safety locked.

        Returns:
            bool: True if safety locked, False otherwise.
        """
        return self.get_safety_locked()

    @property
    def safety_tag_map(self) -> Any:
        """Get the safety tag map.

        Returns:
            Any: The safety tag map.
        """
        return self.get_safety_tag_map()

    @property
    def signature_runmode_protected(self) -> bool:
        """Get whether signature run mode protection is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self.get_signature_runmode_protected()

    @abstractmethod
    def get_safety_locked(self) -> bool:
        """Get whether the controller is safety locked.

        Returns:
            bool: True if safety locked, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get safety locked status.")

    @abstractmethod
    def set_safety_locked(
        self,
        safety_locked: bool
    ) -> None:
        """Set whether the controller is safety locked.

        Args:
            safety_locked: True to set safety locked, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set safety locked status.")

    @abstractmethod
    def get_signature_runmode_protected(self) -> bool:
        """Get whether signature run mode protection is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get signature run mode protection status.")

    @abstractmethod
    def set_signature_runmode_protected(
        self,
        signature_runmode_protected: bool
    ) -> None:
        """Set whether signature run mode protection is enabled.

        Args:
            signature_runmode_protected: True to enable, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set signature run mode protection status.")

    @abstractmethod
    def get_configure_safety_io_always(self) -> bool:
        """Get whether safety IO is always configured.

        Returns:
            bool: True if always configured, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get safety IO configuration status.")

    @abstractmethod
    def set_configure_safety_io_always(
        self,
        configure_safety_io_always: bool
    ) -> None:
        """Set whether safety IO is always configured.

        Args:
            configure_safety_io_always: True to always configure, False otherwise.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set safety IO configuration status.")

    @abstractmethod
    def get_safety_level(self) -> str:
        """Get the safety level of the controller.

        Returns:
            str: The safety level.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the safety level.")

    @abstractmethod
    def set_safety_level(
        self,
        safety_level: str
    ) -> None:
        """Set the safety level of the controller.

        Args:
            safety_level: The safety level to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the safety level.")

    @abstractmethod
    def get_safety_tag_map(self) -> Any:
        """Get the safety tag map.

        Returns:
            Any: The safety tag map.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the safety tag map.")

    @abstractmethod
    def set_safety_tag_map(
        self,
        safety_tag_map: str
    ) -> None:
        """Set the safety tag map from a string.

        Args:
            safety_tag_map: The safety tag map string.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the safety tag map.")

    @abstractmethod
    def add_safety_tag_mapping(
        self,
        tag_name: str,
        safety_tag_name: str
    ) -> None:
        """Add a new safety tag mapping to the safety tag map.

        Args:
            tag_name (str): The standard tag name
            safety_tag_name (str): The corresponding safety tag name

        Raises:
            ValueError: If tag names are not strings
        """
        raise NotImplementedError("This method should be overridden by subclasses to add a safety tag mapping.")

    @abstractmethod
    def remove_safety_tag_mapping(
        self,
        tag_name: str,
        safety_tag_name: str
    ) -> None:
        """Remove a safety tag mapping from the safety tag map.

        Args:
            tag_name (str): The standard tag name
            safety_tag_name (str): The corresponding safety tag name
        Raises:
            ValueError: If tag names are not strings
        """
        raise NotImplementedError("This method should be overridden by subclasses to remove a safety tag mapping.")


__all__ = (
    'IController',
    'IControllerSafetyInfo',
)
