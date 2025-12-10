"""Protocols for PLC models."""
from typing import Callable, Generic, Optional, Union
from pyrox.models.abc import HashList, SupportsItemAccess
from controlrox.interfaces import (
    # Protocols
    ICanBeSafe,
    ICanEnableDisable,
    IHasAOIs,
    IHasDatatypes,
    IHasController,
    IHasInstructions,
    IHasMetaData,
    IHasModules,
    IHasRoutines,
    IHasPrograms,
    IHasRungs,
    IHasTags,
    ISupportsMetaDataListAssignment,
    META,

    # Other interfaces
    IAddOnInstruction,
    IController,
    IDatatype,
    ILogicInstruction,
    IPlcObject,
    IProgram,
    IModule,
    IRoutine,
    IRung,
    ITag,
)


class HasMetaData(
    Generic[META],
    IHasMetaData[META],
    SupportsItemAccess
):
    """Protocol for objects that have metadata.
    """

    def __init__(
        self,
        meta_data: Optional[META] = None,
        **kwargs
    ) -> None:
        if meta_data is None:
            self._meta_data: META = {}  # type: ignore
        else:
            self._meta_data: META = meta_data
        super().__init__(**kwargs)

    @property
    def meta_data(self) -> META:
        """Get the metadata dictionary."""
        return self.get_meta_data()

    @meta_data.setter
    def meta_data(self, meta_data: META) -> None:
        """Set the metadata dictionary."""
        self.set_meta_data(meta_data)

    def get_meta_data(self) -> META:
        """Get the metadata dictionary."""
        return self._meta_data

    def set_meta_data(self, meta_data: META) -> None:
        """Set the metadata dictionary.

        Args:
            meta_data (Union[dict, str]): The metadata to set.
        """
        if not isinstance(meta_data, (dict, str)):
            raise TypeError("Meta data must be a dictionary or a string!")
        self._meta_data = meta_data


class SupportsMetaDataListAssignment(
    ISupportsMetaDataListAssignment
):
    """Protocol for objects that support metadata list assignment.
    """

    def add_asset_to_meta_data(
        self,
        asset: IPlcObject,
        asset_list: Union[list, HashList],
        raw_asset_list: list[dict],
        index: Optional[int] = None,
        inhibit_invalidate: bool = False,
        invalidate_method: Optional[Callable] = None
    ) -> None:
        """Add an asset to this object's metadata.

        Args:
            asset: The asset to add.
            asset_list: The HashList containing the asset.
            raw_asset_list: The raw metadata list.
            index: The index to insert the asset at. If None, appends to the end.
            inhibit_invalidate: If True, does not invalidate the object after adding.
            invalidate_method: Optional method to call to invalidate the object.

        Raises:
            ValueError: If asset is wrong type or already exists.
        """
        if not isinstance(asset, (IPlcObject, str)):
            raise ValueError(f"asset must be of type IPlcObject or string! Got {type(asset)}")

        if not isinstance(asset_list, Union[list, HashList]):
            raise ValueError('asset list must be of type HashList or list!')

        if not isinstance(raw_asset_list, list):
            raise ValueError('raw asset list must be of type list!')

        if asset.name in asset_list:
            self.remove_asset_from_meta_data(
                asset,
                asset_list,
                raw_asset_list,
                inhibit_invalidate=True
            )

        if isinstance(asset, IPlcObject):
            if not isinstance(asset.meta_data, dict):
                raise ValueError('asset meta_data must be of type dict!')

            if index is None:
                index = index or len(raw_asset_list)

            raw_asset_list.insert(index, asset.meta_data)
            asset_list.append(asset)

        if inhibit_invalidate:
            return

        if invalidate_method and callable(invalidate_method):
            invalidate_method()
            return

    def remove_asset_from_meta_data(
        self,
        asset: IPlcObject,
        asset_list: Union[list, HashList],
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
        if not isinstance(asset, IPlcObject):
            raise ValueError("asset must be of type IPlcObject!")

        if not isinstance(asset_list, Union[list, HashList]):
            raise ValueError('asset list must be of type HashList or list!')

        if not isinstance(raw_asset_list, list):
            raise ValueError('raw asset list must be of type list!')

        if asset in asset_list:
            raw_asset_to_remove = next((x for x in raw_asset_list if x["@Name"] == asset.name), None)
            if raw_asset_to_remove is not None:
                raw_asset_list.remove(raw_asset_to_remove)

        if inhibit_invalidate:
            return

        if invalidate_method and callable(invalidate_method):
            invalidate_method()
            return


class CanBeSafe(ICanBeSafe):
    """Protocol for objects that can be set as safe or unsafe.

    Args:
        is_safe (bool): Initial safety state.
    """

    def __init__(
        self,
        is_safe: bool = False,
        **kwargs
    ) -> None:
        self._is_safe = is_safe
        super().__init__(**kwargs)

    def is_safe(self) -> bool:
        """Check if the object is set as safe."""
        return self._is_safe

    def set_safe(self) -> None:
        self._is_safe = True

    def set_unsafe(self) -> None:
        self._is_safe = False


class CanEnableDisable(ICanEnableDisable):
    """Protocol for objects that can be enabled or disabled.

    Args:
        enabled (bool): Initial enabled state.
    """

    def __init__(
        self,
        enabled: bool = False,
        **kwargs
    ) -> None:
        self._enabled = enabled
        super().__init__(**kwargs)

    def enable(self) -> None:
        """Enable the object."""
        raise NotImplementedError("enable method must be implemented by subclass.")

    def disable(self) -> None:
        """Disable the object."""
        raise NotImplementedError("disable method must be implemented by subclass.")

    def is_enabled(self) -> bool:
        """Check if the object is enabled."""
        return self._enabled


class HasAOIs(
    IHasAOIs,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have AOIs.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._aois: HashList[IAddOnInstruction] = HashList('name')
        super().__init__(**kwargs)

    @property
    def aois(self) -> HashList[IAddOnInstruction]:
        """Get the list of AOIs."""
        return self.get_aois()

    @property
    def raw_aois(self) -> list[dict]:
        """Get the raw list of AOIs."""
        return self.get_raw_aois()

    def add_aoi(
        self,
        aoi: IAddOnInstruction,
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=aoi,
            asset_list=self.get_aois(),
            raw_asset_list=self.get_raw_aois(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_aois
        )

    def add_aois(
        self,
        aois: list[IAddOnInstruction],
    ) -> None:
        for aoi in aois:
            self.add_aoi(aoi, True)
        self.invalidate_aois()

    def compile_aois(self) -> None:
        raise NotImplementedError("compile_aois method must be implemented by subclass.")

    def get_aois(self) -> HashList[IAddOnInstruction]:
        """Get the list of AOIs."""
        if not self._aois:
            self.compile_aois()
        return self._aois

    def get_raw_aois(self) -> list[dict]:
        raise NotImplementedError("get_raw_aois method must be implemented by subclass.")

    def invalidate_aois(self) -> None:
        self._aois.clear()

    def remove_aoi(
        self,
        aoi: IAddOnInstruction,
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=aoi,
            asset_list=self.get_aois(),
            raw_asset_list=self.get_raw_aois(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_aois
        )

    def remove_aois(
        self,
        aois: list[IAddOnInstruction]
    ) -> None:
        for aoi in aois:
            self.remove_aoi(aoi, True)
        self.invalidate_aois()


class HasController(
    IHasController,
):
    """Protocol for objects that have a controller.
    """

    def __init__(
        self,
        controller: Optional[IController] = None,
        **kwargs
    ) -> None:
        self._controller = controller
        super().__init__(**kwargs)

    @property
    def controller(self) -> Optional[IController]:
        return self.get_controller()

    @controller.setter
    def controller(self, controller: Optional[IController]) -> None:
        self.set_controller(controller)

    def get_controller(self) -> Optional[IController]:
        return self._controller

    def set_controller(
        self,
        controller: Optional[IController]
    ) -> None:
        self._controller = controller


class HasDatatypes(
    IHasDatatypes,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have datatypes.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._datatypes: HashList['IDatatype'] = HashList('name')
        super().__init__(**kwargs)

    @property
    def datatypes(self) -> HashList['IDatatype']:
        """Get the list of datatypes."""
        return self.get_datatypes()

    @property
    def raw_datatypes(self) -> list[dict]:
        """Get the raw list of datatypes."""
        return self.get_raw_datatypes()

    def add_datatype(
        self,
        datatype: 'IDatatype',
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=datatype,
            asset_list=self.get_datatypes(),
            raw_asset_list=self.get_raw_datatypes(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_datatypes
        )

    def add_datatypes(
        self,
        datatypes: list['IDatatype'],
    ) -> None:
        for datatype in datatypes:
            self.add_datatype(datatype, True)
        self.invalidate_datatypes()

    def compile_datatypes(self) -> None:
        raise NotImplementedError("compile_datatypes method must be implemented by subclass.")

    def get_datatypes(self) -> HashList['IDatatype']:
        """Get the list of datatypes."""
        if not self._datatypes:
            self.compile_datatypes()
        return self._datatypes

    def get_raw_datatypes(self) -> list[dict]:
        raise NotImplementedError("get_raw_datatypes method must be implemented by subclass.")

    def invalidate_datatypes(self) -> None:
        self._datatypes.clear()

    def remove_datatype(
        self,
        datatype: 'IDatatype',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=datatype,
            asset_list=self.get_datatypes(),
            raw_asset_list=self.get_raw_datatypes(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_datatypes
        )

    def remove_datatypes(
        self,
        datatypes: list['IDatatype']
    ) -> None:
        for datatype in datatypes:
            self.remove_datatype(datatype, True)
        self.invalidate_datatypes()


class HasInstructions(
    IHasInstructions,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have instructions.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._instructions: list['ILogicInstruction'] = []
        self._input_instructions: list['ILogicInstruction'] = []
        self._output_instructions: list['ILogicInstruction'] = []

        super().__init__(**kwargs)

    @property
    def instructions(self) -> list['ILogicInstruction']:
        """Get the list of instructions."""
        return self.get_instructions()

    @property
    def raw_instructions(self) -> list[dict]:
        """Get the raw list of instructions."""
        return self.get_raw_instructions()

    def add_instruction(
        self,
        instruction: 'ILogicInstruction',
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=instruction,
            asset_list=self.get_instructions(),
            raw_asset_list=self.get_raw_instructions(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_instructions
        )

    def add_instructions(
        self,
        instructions: list['ILogicInstruction']
    ) -> None:
        for instruction in instructions:
            self.add_instruction(instruction, True)
        self.invalidate_instructions()

    def clear_instructions(self) -> None:
        self.invalidate_instructions()

    def compile_instructions(self) -> None:
        raise NotImplementedError("compile_instructions method must be implemented by subclass.")

    def get_filtered_instructions(
        self,
        instruction_filter: Optional[str] = None,
        operand_filter: Optional[str] = None
    ) -> list[ILogicInstruction]:
        filtered_instructions = self._instructions

        if instruction_filter:
            filtered_instructions = [
                instr for instr in filtered_instructions
                if instruction_filter == instr.get_instruction_name()
            ]

        if operand_filter:
            filtered_instructions = [
                instr for instr in filtered_instructions
                if any(operand_filter in op.meta_data for op in instr.get_operands())
            ]

        return filtered_instructions

    def get_instructions(
        self,
        instruction_filter: str = '',
        operand_filter: str = ''
    ) -> list['ILogicInstruction']:
        if not self._instructions:
            self.compile_instructions()

        if instruction_filter or operand_filter:
            return self.get_filtered_instructions(
                instruction_filter=instruction_filter,
                operand_filter=operand_filter
            )

        return self._instructions

    def get_input_instructions(self) -> list['ILogicInstruction']:
        """Get the list of input instructions."""
        if not self._input_instructions:
            self.compile_instructions()
        return self._input_instructions

    def get_output_instructions(self) -> list['ILogicInstruction']:
        """Get the list of output instructions."""
        if not self._output_instructions:
            self.compile_instructions()
        return self._output_instructions

    def get_raw_instructions(self) -> list[dict]:
        raise NotImplementedError("get_raw_instructions method must be implemented by subclass.")

    def has_instruction(
        self,
        instruction: 'ILogicInstruction'
    ) -> bool:
        raise NotImplementedError("has_instruction method must be implemented by subclass.")

    def invalidate_instructions(self) -> None:
        self._instructions.clear()
        self._input_instructions.clear()
        self._output_instructions.clear()

    def remove_instruction(
        self,
        instruction: 'ILogicInstruction',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=instruction,
            asset_list=self.get_instructions(),
            raw_asset_list=self.get_raw_instructions(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_instructions
        )

    def remove_instructions(self, instructions: list['ILogicInstruction']) -> None:
        for instruction in instructions:
            self.remove_instruction(instruction, True)
        self.invalidate_instructions()

    def set_instructions(
        self,
        instructions: list['ILogicInstruction']
    ) -> None:
        for instr in instructions:
            if not isinstance(instr, ILogicInstruction):
                raise TypeError("All items in instructions must implement ILogicInstruction interface.")
        self._instructions = instructions


class HasModules(
    IHasModules,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have modules.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._modules: HashList['IModule'] = HashList('name')
        super().__init__(**kwargs)

    @property
    def modules(self) -> HashList['IModule']:
        """Get the list of modules."""
        return self.get_modules()

    @property
    def raw_modules(self) -> list[dict]:
        """Get the raw list of modules."""
        return self.get_raw_modules()

    def add_module(
        self,
        module: 'IModule',
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=module,
            asset_list=self.get_modules(),
            raw_asset_list=self.get_raw_modules(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_modules
        )

    def add_modules(
        self,
        modules: list['IModule'],
    ) -> None:
        for module in modules:
            self.add_module(module, True)
        self.invalidate_modules()

    def compile_modules(self) -> None:
        raise NotImplementedError("compile_modules method must be implemented by subclass.")

    def get_modules(self) -> HashList['IModule']:
        """Get the list of modules."""
        if not self._modules:
            self.compile_modules()
        return self._modules

    def get_raw_modules(self) -> list[dict]:
        raise NotImplementedError("get_raw_modules method must be implemented by subclass.")

    def invalidate_modules(self) -> None:
        self._modules.clear()

    def remove_module(
        self,
        module: 'IModule',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=module,
            asset_list=self.get_modules(),
            raw_asset_list=self.get_raw_modules(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_modules
        )

    def remove_modules(
        self,
        modules: list['IModule']
    ) -> None:
        for module in modules:
            self.remove_module(module, True)
        self.invalidate_modules()


class HasRoutines(
    IHasRoutines,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have routines.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._routines: HashList['IRoutine'] = HashList('name')
        super().__init__(**kwargs)

    @property
    def routines(self) -> HashList['IRoutine']:
        """Get the list of routines."""
        return self.get_routines()

    @property
    def raw_routines(self) -> list[dict]:
        """Get the raw list of routines."""
        return self.get_raw_routines()

    def add_routine(
        self,
        routine: 'IRoutine',
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=routine,
            asset_list=self.get_routines(),
            raw_asset_list=self.get_raw_routines(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_routines
        )

    def add_routines(
        self,
        routines: list['IRoutine'],
    ) -> None:
        for routine in routines:
            self.add_routine(routine, True)
        self.invalidate_routines()

    def block_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        raise NotImplementedError("block_routine method must be implemented by subclass.")

    def compile_routines(self) -> None:
        raise NotImplementedError("compile_routines method must be implemented by subclass.")

    def get_routines(self) -> HashList['IRoutine']:
        """Get the list of routines."""
        if not self._routines:
            self.compile_routines()
        return self._routines

    def get_raw_routines(self) -> list[dict]:
        raise NotImplementedError("get_raw_routines method must be implemented by subclass.")

    def get_main_routine(self) -> Optional['IRoutine']:
        """Get the main routine."""
        raise NotImplementedError("get_main_routine method must be implemented by subclass.")

    def invalidate_routines(self) -> None:
        self._routines.clear()

    def remove_routine(
        self,
        routine: 'IRoutine',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=routine,
            asset_list=self.get_routines(),
            raw_asset_list=self.get_raw_routines(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_routines
        )

    def remove_routines(
        self,
        routines: list['IRoutine']
    ) -> None:
        for routine in routines:
            self.remove_routine(routine, True)
        self.invalidate_routines()

    def unblock_routine(
        self,
        routine_name: str,
        blocking_bit: str
    ) -> None:
        raise NotImplementedError("unblock_routine method must be implemented by subclass.")


class HasRungs(
    IHasRungs,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have rungs.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._rungs: list['IRung'] = []
        super().__init__(**kwargs)

    @property
    def rungs(self) -> list['IRung']:
        """Get the list of rungs."""
        return self.get_rungs()

    @property
    def raw_rungs(self) -> list[dict]:
        """Get the raw list of rungs."""
        return self.get_raw_rungs()

    def add_rung(
        self,
        rung: 'IRung',
        index: int = -1,
        inhibit_invalidate: bool = False
    ) -> None:
        if not isinstance(rung, IRung):
            raise ValueError("Rung must be an instance of Rung!")

        if index == -1 or index >= len(self.rungs):
            index = len(self.rungs)

        self.add_asset_to_meta_data(
            asset=rung,
            asset_list=self.get_rungs(),
            raw_asset_list=self.get_raw_rungs(),
            index=index,
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_rungs
        )

        self.reassign_rung_numbers()
        self.invalidate_rungs()

    def add_rungs(
        self,
        rungs: list['IRung']
    ) -> None:
        for rung in rungs:
            self.add_rung(rung, True)
        self.invalidate_rungs()

    def clear_rungs(self) -> None:
        self.set_raw_rungs([])
        self.invalidate_rungs()

    def compile_rungs(self) -> None:
        raise NotImplementedError("compile_rungs method must be implemented by subclass.")

    def get_rungs(self) -> list['IRung']:
        """Get the list of rungs."""
        if not self._rungs:
            self.compile_rungs()
        return self._rungs

    def get_raw_rungs(self) -> list[dict]:
        raise NotImplementedError("get_raw_rungs method must be implemented by subclass.")

    def set_raw_rungs(
        self,
        raw_rungs: list[dict]
    ) -> None:
        self.raw_rungs.clear()
        self.raw_rungs.extend(raw_rungs)

    def invalidate_rungs(self) -> None:
        self._rungs.clear()

    def reassign_rung_numbers(self) -> None:
        for index, rung in enumerate(self.get_rungs()):
            rung.set_rung_number(index)

    def remove_rung(
        self,
        rung: 'IRung',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=rung,
            asset_list=self.get_rungs(),
            raw_asset_list=self.get_raw_rungs(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_rungs
        )

    def remove_rung_by_index(
        self,
        index: int,
        inhibit_invalidate: bool = False
    ) -> None:
        rungs = self.get_rungs()
        if index < 0 or index >= len(rungs):
            raise IndexError("Rung index out of range!")

        self.remove_asset_from_meta_data(
            asset=rungs[index],
            asset_list=self.get_rungs(),
            raw_asset_list=self.get_raw_rungs(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_rungs
        )

    def remove_rungs(self, rungs: list['IRung']) -> None:
        for rung in rungs:
            self.remove_rung(rung, True)
        self.invalidate_rungs()


class HasPrograms(
    IHasPrograms,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have programs.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._programs: HashList['IProgram'] = HashList('name')
        self._safety_programs: HashList['IProgram'] = HashList('name')
        self._standard_programs: HashList['IProgram'] = HashList('name')
        super().__init__(**kwargs)

    @property
    def programs(self) -> HashList['IProgram']:
        """Get the list of programs."""
        return self.get_programs()

    @property
    def safety_programs(self) -> HashList['IProgram']:
        """Get the list of safety programs."""
        return self.get_safety_programs()

    @property
    def standard_programs(self) -> HashList['IProgram']:
        """Get the list of standard programs."""
        return self.get_standard_programs()

    @property
    def raw_programs(self) -> list[dict]:
        """Get the raw list of programs."""
        return self.get_raw_programs()

    def add_program(
        self,
        program: 'IProgram',
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=program,
            asset_list=self.get_programs(),
            raw_asset_list=self.get_raw_programs(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_programs
        )

    def add_programs(
        self,
        programs: list['IProgram'],
    ) -> None:
        for program in programs:
            self.add_program(program, True)
        self.invalidate_programs()

    def compile_programs(self) -> None:
        raise NotImplementedError("compile_programs method must be implemented by subclass.")

    def compile_safety_programs(self) -> None:
        self._safety_programs.clear()
        self._safety_programs.extend([x for x in self.programs if x.is_safe()])

    def compile_standard_programs(self) -> None:
        self._standard_programs.clear()
        self._standard_programs.extend([x for x in self.programs if not x.is_safe()])

    def get_programs(self) -> HashList['IProgram']:
        """Get the list of programs."""
        if not self._programs:
            self.compile_programs()
        return self._programs

    def get_raw_programs(self) -> list[dict]:
        raise NotImplementedError("get_raw_programs method must be implemented by subclass.")

    def get_safety_programs(self) -> HashList['IProgram']:
        """Get the list of safety programs."""
        if not self._safety_programs:
            self.compile_safety_programs()
        return self._safety_programs

    def get_standard_programs(self) -> HashList['IProgram']:
        """Get the list of standard programs."""
        if not self._standard_programs:
            self.compile_standard_programs()
        return self._standard_programs

    def invalidate_programs(self) -> None:
        self._programs.clear()
        self._safety_programs.clear()
        self._standard_programs.clear()

    def remove_program(
        self,
        program: 'IProgram',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=program,
            asset_list=self.get_programs(),
            raw_asset_list=self.get_raw_programs(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_programs
        )

    def remove_programs(
        self,
        programs: list['IProgram']
    ) -> None:
        for program in programs:
            self.remove_program(program, True)
        self.invalidate_programs()

    def set_programs(self, programs: list['IProgram']) -> None:
        for prog in programs:
            if not isinstance(prog, IProgram):
                raise TypeError("All items in programs must implement IProgram interface.")
        self._programs.clear()
        self._programs.extend(programs)


class HasTags(
    IHasTags,
    SupportsMetaDataListAssignment,
):
    """Protocol for objects that have tags.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._tags: HashList['ITag'] = HashList('name')
        self._safety_tags: HashList['ITag'] = HashList('name')
        self._standard_tags: HashList['ITag'] = HashList('name')
        super().__init__(**kwargs)

    @property
    def tags(self) -> HashList['ITag']:
        """Get the list of tags."""
        return self.get_tags()

    @property
    def safety_tags(self) -> HashList['ITag']:
        """Get the list of safety tags."""
        return self.get_safety_tags()

    @property
    def standard_tags(self) -> HashList['ITag']:
        """Get the list of standard tags."""
        return self.get_standard_tags()

    @property
    def raw_tags(self) -> list[dict]:
        """Get the raw list of tags."""
        return self.get_raw_tags()

    def add_tag(
        self,
        tag: 'ITag',
        inhibit_invalidate: bool = False
    ) -> None:
        self.add_asset_to_meta_data(
            asset=tag,
            asset_list=self.get_tags(),
            raw_asset_list=self.get_raw_tags(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_tags
        )

    def add_tags(
        self,
        tags: list['ITag'],
    ) -> None:
        for tag in tags:
            self.add_tag(tag, True)
        self.invalidate_tags()

    def compile_tags(self) -> None:
        raise NotImplementedError("compile_tags method must be implemented by subclass.")

    def get_tags(self) -> HashList['ITag']:
        """Get the list of tags."""
        if not self._tags:
            self.compile_tags()
        return self._tags

    def get_safety_tags(self) -> HashList['ITag']:
        """Get the list of safety tags."""
        if not self._safety_tags:
            self.compile_tags()
        return self._safety_tags

    def get_standard_tags(self) -> HashList['ITag']:
        """Get the list of standard tags."""
        if not self._standard_tags:
            self.compile_tags()
        return self._standard_tags

    def get_raw_tags(self) -> list[dict]:
        raise NotImplementedError("get_raw_tags method must be implemented by subclass.")

    def invalidate_tags(self) -> None:
        self._safety_tags.clear()
        self._standard_tags.clear()
        self._tags.clear()

    def remove_tag(
        self,
        tag: 'ITag',
        inhibit_invalidate: bool = False
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=tag,
            asset_list=self.get_tags(),
            raw_asset_list=self.get_raw_tags(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=self.invalidate_tags
        )

    def remove_tags(
        self,
        tags: list['ITag']
    ) -> None:
        for tag in tags:
            self.remove_tag(tag, True)
        self.invalidate_tags()


__all__ = [
    "CanBeSafe",
    "CanEnableDisable",
    "HasAOIs",
    "HasController",
    "HasDatatypes",
    "HasInstructions",
    "HasMetaData",
    "HasModules",
    "HasRoutines",
    "HasPrograms",
    "HasRungs",
    "HasTags",
]
