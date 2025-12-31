"""Protocols module for PLC interfaces."""
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    Protocol,
    runtime_checkable,
    _ProtocolMeta,
    TYPE_CHECKING,
    TypeVar,
)
from pyrox.models import HashList, FactoryTypeMeta
from pyrox.models.abc.meta import T as META

if TYPE_CHECKING:
    from .aoi import IAddOnInstruction
    from .datatype import IDatatype
    from .controller import IController
    from .instruction import ILogicInstruction
    from .meta import IPlcObject
    from .module import IModule
    from .program import IProgram
    from .routine import IRoutine
    from .rung import IRung
    from .tag import ITag


# PLC TypeVar definitions
AOI = TypeVar('AOI', bound='IAddOnInstruction')
DT = TypeVar('DT', bound='IDatatype')
CTRL = TypeVar('CTRL', bound='IController')
INST = TypeVar('INST', bound='ILogicInstruction')
MOD = TypeVar('MOD', bound='IModule')
PROG = TypeVar('PROG', bound='IProgram')
ROUT = TypeVar('ROUT', bound='IRoutine')
RUNG = TypeVar('RUNG', bound='IRung')
TAG = TypeVar('TAG', bound='ITag')


class IFactoryMixinProtocolMeta(FactoryTypeMeta, _ProtocolMeta):
    """Metaclass for factory mixin protocols."""

    @classmethod
    def get_factory(cls):
        """Get the factory associated with this protocol."""
        return None


@runtime_checkable
class ICanEnableDisable(Protocol, metaclass=IFactoryMixinProtocolMeta):
    """Protocol for objects that can be enabled or disabled."""

    def enable(self) -> None:
        """Enable the object."""
        ...

    def disable(self) -> None:
        """Disable the object."""
        ...

    def is_enabled(self) -> bool:
        """Check if the object is enabled."""
        ...


@runtime_checkable
class ICanBeSafe(Protocol, metaclass=IFactoryMixinProtocolMeta):
    """Protocol for objects that can be set to safe mode."""

    def set_safe(self) -> None:
        """Set the object to safe mode."""
        ...

    def set_unsafe(self) -> None:
        """Set the object to unsafe mode."""
        ...

    def is_safe(self) -> bool:
        """Check if the object is in safe mode."""
        ...


@runtime_checkable
class IHasRevision(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have a revision number."""

    @property
    def revision(self) -> str:
        """Get the revision number of this object."""
        return self.get_revision()

    @revision.setter
    def revision(self, revision: str) -> None:
        self.set_revision(revision)

    def get_revision(self) -> str:
        """Get the revision number of this object.

        Returns:
            str: The revision number of this object.
        """
        ...

    def set_revision(self, revision: str) -> None:
        """Set the revision number of this object.

        Args:
            revision (str): The revision number to set.
        """
        ...


@runtime_checkable
class IHasController(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have a controller."""

    @property
    def controller(self) -> Optional['IController']:
        """Get the controller of this object."""
        ...

    @controller.setter
    def controller(self, controller: Optional['IController']) -> None:
        self.set_controller(controller)

    def get_controller(self) -> Optional['IController']:
        """Get the controller of this object.

        Returns:
            IController: The controller of this object.
        """
        ...

    def set_controller(
        self,
        controller: Optional['IController']
    ) -> None:
        """Set the controller of this object.

        Args:
            controller (IController): The controller to set.
        """
        ...


@runtime_checkable
class IHasInstructions(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have instructions."""

    @property
    def instructions(self) -> list['ILogicInstruction']:
        """Get the list of instructions."""
        ...

    @property
    def raw_instructions(self) -> list[dict]:
        """Get the raw list of instructions."""
        ...

    def add_instruction(
        self,
        instruction: 'ILogicInstruction',
        inhibit_invalidate: bool = False,
    ) -> None:
        """Add an instruction to this container.

        Args:
            instruction: The instruction to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_instructions(
        self,
        instructions: list['ILogicInstruction']
    ) -> None:
        """Add multiple instructions to this container.

        Args:
            instructions (list): The list of instructions to add.
        """
        ...

    def compile_instructions(self) -> None:
        """Compile the instructions."""
        ...

    def clear_instructions(self) -> None:
        """Clear all instructions from this container."""
        ...

    def get_filtered_instructions(
        self,
        instruction_filter: str = '',
        operand_filter: str = ''
    ) -> list['ILogicInstruction']:
        """Get the list of instructions filtered by instruction and operand.

        Args:
            instruction_filter (str): Filter for instruction type.
            operand_filter (str): Filter for operand.
        Returns:
            list: List of filtered instructions.
        """
        ...

    def get_instructions(
        self,
        instruction_filter: str = '',
        operand_filter: str = ''
    ) -> list['ILogicInstruction']:
        """Get the list of instructions.

        Args:
            instruction_filter (str): Filter for instruction type.
            operand_filter (str): Filter for operand.
        Returns:
            list: List of instructions.
        """
        ...

    def get_input_instructions(self) -> list['ILogicInstruction']:
        """Get the list of input instructions."""
        ...

    def get_output_instructions(self) -> list['ILogicInstruction']:
        """Get the list of output instructions."""
        ...

    def get_raw_instructions(
        self
    ) -> list[dict]:
        """Get the raw list of instructions."""
        ...

    def has_instruction(
        self,
        instruction: 'ILogicInstruction'
    ) -> bool:
        """Check if the container contains a specific instruction.

        Args:
            instruction: The instruction to check for
        Returns:
            bool: True if the instruction exists in the container
        """
        ...

    def remove_instruction(
        self,
        instruction: 'ILogicInstruction',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove an instruction from this container.

        Args:
            instruction: The instruction to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_instruction_by_index(
        self,
        index: int,
    ) -> None:
        """Remove an instruction from this container by index.

        Args:
            index: The index of the instruction to remove.
        """
        ...

    def remove_instructions(
        self,
        instructions: list['ILogicInstruction']
    ) -> None:
        """Remove multiple instructions from this container.

        Args:
            instructions (list): The list of instructions to remove.
        """
        ...

    def set_instructions(
        self,
        instructions: list['ILogicInstruction']
    ) -> None:
        """Set the instructions for this container.

        Args:
            instructions (list): The list of instructions to set.
        """
        ...


@runtime_checkable
class IHasSequencedInstructions(
    IHasInstructions,
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have sequenced instructions."""

    def compile_instruction_sequence(self) -> None:
        """Compile the instruction sequence from the current instructions."""
        ...

    def tokenize_instruction_sequence(self) -> list[str]:
        """Tokenize the instruction sequence for easier processing."""
        ...


@runtime_checkable
class IHasMetaData(
    Generic[META],
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have meta data."""

    @property
    def meta_data(self) -> META:
        """Get the meta data of this object."""
        return self.get_meta_data()

    @meta_data.setter
    def meta_data(
        self,
        meta_data: META
    ) -> None:
        self.set_meta_data(meta_data)

    def get_meta_data(self) -> META:
        """Get the meta data of this object.

        Returns:
            Union[dict, str]: The meta data of this object.
        """
        ...

    def set_meta_data(
        self,
        meta_data: META
    ) -> None:
        """Set the meta data of this object.

        Args:
            meta_data (Union[dict, str]): The meta data to set.
        """
        ...


@runtime_checkable
class ISupportsMetaDataListAssignment(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that support meta data list assignment."""

    def add_asset_to_meta_data(
        self,
        asset: 'IPlcObject',
        asset_list: HashList,
        raw_asset_list: list[dict],
        index: Optional[int] = None,
        inhibit_invalidate: bool = False,
        invalidate_method: Optional[Callable] = None
    ) -> None:
        """Add an asset to this object's metadata.

        Args:
            asset: The asset to add.
            asset_list (HashList): The list of assets.
            raw_asset_list (list): The raw list of assets.
            index (int, optional): The index to insert the asset at. Defaults to None.
            inhibit_invalidate (bool): Whether to inhibit invalidation. Defaults to False.
            invalidate_method (Callable, optional): The method to call for invalidation. Defaults to None.
        """
        ...

    def remove_asset_from_meta_data(
        self,
        asset: 'IPlcObject',
        asset_list: HashList,
        raw_asset_list: list[dict],
        inhibit_invalidate: bool = False,
        invalidate_method: Optional[Callable] = None
    ) -> None:
        """Remove an asset from this object's metadata.

        Args:
            asset: The asset to remove.
            asset_list: The HashList containing the asset.
            raw_asset_list: The raw metadata list.
            inhibit_invalidate: If True, does not invalidate the object after removing.
            invalidate_method: Optional method to call to invalidate the object.

        Raises:
            ValueError: If asset is wrong type or doesn't exist.
        """
        ...


@runtime_checkable
class IHasAOIs(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have AOIs."""

    @property
    def aois(self) -> HashList['IAddOnInstruction']:
        """Get the list of AOIs."""
        ...

    @property
    def raw_aois(self) -> list[dict]:
        """Get the raw list of AOIs."""
        ...

    def add_aoi(
        self,
        aoi: Any,
        inhibit_invalidate: bool = False
    ) -> None:
        """Add an AOI to this container.

        Args:
            aoi: The AOI to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_aois(
        self,
        aois: list['IAddOnInstruction']
    ) -> None:
        """Add multiple AOIs to this container.

        Args:
            aois (list): The list of AOIs to add.
        """
        ...

    def compile_aois(self) -> None:
        """Compile the AOIs."""
        ...

    def get_aois(self) -> HashList['IAddOnInstruction']:
        """Get the list of AOIs."""
        ...

    def get_raw_aois(self) -> list[dict]:
        """Get the raw list of AOIs."""
        ...

    def invalidate_aois(self) -> None:
        """Invalidate all AOIs."""
        ...

    def remove_aoi(
        self,
        aoi: 'IAddOnInstruction',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove an AOI from this container.

        Args:
            aoi: The AOI to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_aois(
        self,
        aois: list['IAddOnInstruction']
    ) -> None:
        """Remove multiple AOIs from this container.

        Args:
            aois (list): The list of AOIs to remove.
        """
        ...


@runtime_checkable
class IHasDatatypes(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have datatypes."""

    @property
    def datatypes(self) -> HashList['IDatatype']:
        """Get the list of datatypes."""
        ...

    @property
    def raw_datatypes(self) -> list[dict]:
        """Get the raw list of datatypes."""
        ...

    def add_datatype(
        self,
        datatype: 'IDatatype',
        inhibit_invalidate: bool = False
    ) -> None:
        """Add a datatype to this container.

        Args:
            datatype: The datatype to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_datatypes(
        self,
        datatypes: list['IDatatype']
    ) -> None:
        """Add multiple datatypes to this container.

        Args:
            datatypes (list): The list of datatypes to add.
        """
        ...

    def compile_datatypes(self) -> None:
        """Compile the datatypes."""
        ...

    def get_datatypes(self) -> HashList['IDatatype']:
        """Get the list of datatypes."""
        ...

    def get_raw_datatypes(self) -> list[dict]:
        """Get the raw list of datatypes."""
        ...

    def invalidate_datatypes(self) -> None:
        """Invalidate all datatypes."""
        ...

    def remove_datatype(
        self,
        datatype: 'IDatatype',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a datatype from this container.

        Args:
            datatype: The datatype to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_datatypes(
        self,
        datatypes: list['IDatatype']
    ) -> None:
        """Remove multiple datatypes from this container.

        Args:
            datatypes (list): The list of datatypes to remove.
        """
        ...


@runtime_checkable
class IHasModules(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have modules."""

    @property
    def modules(self) -> HashList['IModule']:
        """Get the list of modules."""
        ...

    @property
    def raw_modules(self) -> list[dict]:
        """Get the raw list of modules."""
        ...

    def add_module(
        self,
        module: 'IModule',
        inhibit_invalidate: bool = False
    ) -> None:
        """Add a module to this container.

        Args:
            module: The module to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_modules(
        self,
        modules: list['IModule']
    ) -> None:
        """Add multiple modules to this container.

        Args:
            modules (list): The list of modules to add.
        """
        ...

    def compile_modules(self) -> None:
        """Compile the modules."""
        ...

    def get_modules(self) -> HashList['IModule']:
        """Get the list of modules."""
        ...

    def get_raw_modules(self) -> list[dict]:
        """Get the raw list of modules."""
        ...

    def invalidate_modules(self) -> None:
        """Invalidate all modules."""
        ...

    def remove_module(
        self,
        module: 'IModule',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a module from this container.

        Args:
            module: The module to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_modules(
        self,
        modules: list['IModule']
    ) -> None:
        """Remove multiple modules from this container.

        Args:
            modules (list): The list of modules to remove.
        """
        ...


@runtime_checkable
class IHasRoutines(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have routines."""

    @property
    def routines(self) -> HashList['IRoutine']:
        """Get the list of routines."""
        ...

    @property
    def raw_routines(self) -> list[dict]:
        """Get the raw list of routines."""
        ...

    def add_routine(
        self,
        routine: 'IRoutine',
        inhibit_invalidate: bool = False
    ) -> None:
        """Add a routine to this container.

        Args:
            routine: The routine to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_routines(
        self,
        routines: list['IRoutine']
    ) -> None:
        """Add multiple routines to this container.

        Args:
            routines (list): The list of routines to add.
        """
        ...

    def block_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        """Block a routine in this program.

        Args:
            routine_name(str): Name of the routine to block.
            blocking_bit(str): Tag name of the bit to use for blocking.
        """
        ...

    def compile_routines(self) -> None:
        """Compile the routines."""
        ...

    def get_routines(self) -> HashList['IRoutine']:
        """Get the list of routines."""
        ...

    def get_raw_routines(self) -> list[dict]:
        """Get the raw list of routines."""
        ...

    def get_main_routine(self) -> Optional['IRoutine']:
        """Get the main routine."""
        ...

    def invalidate_routines(self) -> None:
        """Invalidate all routines."""
        ...

    def remove_routine(
        self,
        routine: 'IRoutine',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a routine from this container.

        Args:
            routine: The routine to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_routines(
        self,
        routines: list['IRoutine']
    ) -> None:
        """Remove multiple routines from this container.

        Args:
            routines (list): The list of routines to remove.
        """
        ...

    def unblock_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        """Unblock a routine in this program.

        Args:
            routine_name(str): Name of the routine to unblock.
            blocking_bit(str): Tag name of the bit to use for blocking.
        """
        ...


@runtime_checkable
class IHasRungs(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have rungs."""

    @property
    def rungs(self) -> list['IRung']:
        """Get the list of rungs."""
        ...

    @property
    def raw_rungs(self) -> list[dict]:
        """Get the raw list of rungs."""
        ...

    def add_rung(
        self,
        rung: 'IRung',
        index: int = -1,
        inhibit_invalidate: bool = False
    ) -> None:
        """Add a rung to this container.

        Args:
            rung: The rung to add.
            index: The index to insert the rung at.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_rungs(
        self,
        rungs: list['IRung']
    ) -> None:
        """Add multiple rungs to this container.

        Args:
            rungs (list): The list of rungs to add.
        """
        ...

    def clear_rungs(
        self
    ) -> None:
        """Clear all rungs from this container."""
        ...

    def compile_rungs(
        self
    ) -> None:
        """Compile all rungs in this container."""
        ...

    def get_rungs(
        self
    ) -> list['IRung']:
        """Get all rungs in this container.

        Returns:
            A list of all rungs in this container.
        """
        ...

    def get_raw_rungs(
        self
    ) -> list[dict]:
        """Get the raw list of rungs."""
        ...

    def set_raw_rungs(
        self,
        raw_rungs: list[dict]
    ) -> None:
        """Set the raw list of rungs.

        Args:
            raw_rungs (list): The raw list of rungs to set.
        """
        ...

    def invalidate_rungs(
        self
    ) -> None:
        """Invalidate all rungs in this container."""
        ...

    def remove_rung(
        self,
        rung: 'IRung',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a rung from this container.

        Args:
            rung: The rung to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_rung_by_index(
        self,
        index: int,
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a rung from this container by index.

        Args:
            index: The index of the rung to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_rungs(
        self,
        rungs: list['IRung']
    ) -> None:
        """Remove multiple rungs from this container.

        Args:
            rungs (list): The list of rungs to remove.
        """
        ...


@runtime_checkable
class IHasPrograms(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have programs."""

    @property
    def programs(self) -> HashList['IProgram']:
        """Get the list of programs."""
        ...

    @property
    def safety_programs(self) -> HashList['IProgram']:
        """Get the list of safety programs."""
        ...

    @property
    def standard_programs(self) -> HashList['IProgram']:
        """Get the list of standard programs."""
        ...

    @property
    def raw_programs(self) -> list[dict]:
        """Get the raw list of programs."""
        ...

    def add_program(
        self,
        program: 'IProgram',
        inhibit_invalidate: bool = False
    ) -> None:
        """Add a program to this container.

        Args:
            program: The program to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_programs(
        self,
        programs: list['IProgram']
    ) -> None:
        """Add multiple programs to this container.

        Args:
            programs (list): The list of programs to add.
        """
        ...

    def compile_programs(self) -> None:
        """Compile the programs."""
        ...

    def get_programs(self) -> HashList['IProgram']:
        """Get the list of programs."""
        ...

    def get_safety_programs(self) -> HashList['IProgram']:
        """Get the list of safety programs."""
        ...

    def get_standard_programs(self) -> HashList['IProgram']:
        """Get the list of standard programs."""
        ...

    def get_raw_programs(self) -> list[dict]:
        """Get the raw list of programs."""
        ...

    def invalidate_programs(self) -> None:
        """Invalidate all programs."""
        ...

    def set_programs(
        self,
        programs: list['IProgram']
    ) -> None:
        """Set the programs for this container.

        Args:
            programs (list): The list of programs to set.
        """
        ...

    def remove_program(
        self,
        program: 'IProgram',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a program from this container.

        Args:
            program: The program to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_programs(
        self,
        programs: list['IProgram'],
    ) -> None:
        """Remove multiple programs from this container.

        Args:
            programs (list): The list of programs to remove.
        """
        ...


@runtime_checkable
class IHasTags(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have tags."""

    @property
    def safety_tags(self) -> HashList['ITag']:
        """Get the list of safety tags."""
        ...

    @property
    def standard_tags(self) -> HashList['ITag']:
        """Get the list of standard tags."""
        ...

    @property
    def tags(self) -> HashList['ITag']:
        """Get the list of tags."""
        ...

    @property
    def raw_tags(self) -> list[dict]:
        """Get the raw list of tags."""
        ...

    def add_tag(
        self,
        tag: 'ITag',
        inhibit_invalidate: bool = False
    ) -> None:
        """Add a tag to this container.

        Args:
            tag: The tag to add.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def add_tags(
        self,
        tags: list['ITag']
    ) -> None:
        """Add multiple tags to this container.

        Args:
            tags (list): The list of tags to add.
        """
        ...

    def compile_tags(self) -> None:
        """Compile the tags."""
        ...

    def get_tags(self) -> HashList['ITag']:
        """Get the list of tags."""
        ...

    def get_safety_tags(self) -> HashList['ITag']:
        """Get the list of safety tags."""
        ...

    def get_standard_tags(self) -> HashList['ITag']:
        """Get the list of standard tags."""
        ...

    def get_raw_tags(self) -> list[dict]:
        """Get the raw list of tags."""
        ...

    def invalidate_tags(self) -> None:
        """Invalidate all tags."""
        ...

    def remove_tag(
        self,
        tag: 'ITag',
        inhibit_invalidate: bool = False
    ) -> None:
        """Remove a tag from this container.

        Args:
            tag: The tag to remove.
            inhibit_invalidate (bool): Whether to inhibit invalidation.
        """
        ...

    def remove_tags(
        self,
        tags: list['ITag']
    ) -> None:
        """Remove multiple tags from this container.

        Args:
            tags (list): The list of tags to remove.
        """
        ...


@runtime_checkable
class IHasConnectionTags(
    Protocol,
    metaclass=IFactoryMixinProtocolMeta
):
    """Protocol for objects that have connection tags."""

    @property
    def config_connection_point(self) -> int:
        """The configuration connection point of the module."""
        return self.get_config_connection_point()

    @property
    def config_connection_size(self) -> int:
        """The configuration size of the module."""
        return self.get_config_connection_size()

    @property
    def input_connection_point(self) -> int:
        """The input connection point of the module."""
        return self.get_input_connection_point()

    @property
    def input_connection_size(self) -> int:
        """The input size of the module."""
        return self.get_input_connection_size()

    @property
    def output_connection_point(self) -> int:
        """The output connection point of the module."""
        return self.get_output_connection_point()

    @property
    def output_connection_size(self) -> int:
        """The output connection size of the module."""
        return self.get_output_connection_size()

    def get_config_connection_point(self) -> int:
        """The configuration connection point of the module."""
        ...

    def get_config_connection_size(self) -> int:
        """The configuration size of the module."""
        ...

    def get_config_tag(self) -> Any:
        """The configuration tag of the module."""
        ...

    def get_input_connection_point(self) -> int:
        """The input connection point of the module."""
        ...

    def get_input_connection_size(self) -> int:
        """The input size of the module."""
        ...

    def get_input_tag(self) -> Any:
        """The input tag of the module."""
        ...

    def get_output_connection_point(self) -> int:
        """The output connection point of the module."""
        ...

    def get_output_connection_size(self) -> int:
        """The output size of the module."""
        ...

    def get_output_tag(self) -> Any:
        """The output tag of the module."""
        ...


__all__ = [
    # TypeVars
    "AOI",
    "CTRL",
    "DT",
    "INST",
    "MOD",
    "PROG",
    "ROUT",
    "RUNG",
    "TAG",
    "META",

    # Protocols
    "IHasAOIs",
    "ICanEnableDisable",
    "ICanBeSafe",
    "IHasConnectionTags",
    "IHasController",
    "IHasDatatypes",
    "IHasInstructions",
    "IHasMetaData",
    "IHasModules",
    "IHasRoutines",
    "IHasRungs",
    "IHasPrograms",
    "IHasTags",
    "ISupportsMetaDataListAssignment",
]
