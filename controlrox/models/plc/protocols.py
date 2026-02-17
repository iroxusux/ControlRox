"""Protocols for PLC models."""
from typing import (
    Callable,
    Generic,
    Optional,
    Union
)
from pyrox.models import HashList
from pyrox.models.meta import SupportsItemAccess
from controlrox.interfaces import (
    # Protocols
    ICanBeSafe,
    ICanEnableDisable,
    IHasAOIs,
    IHasDatatypes,
    IHasController,
    IHasInstructions,
    IHasOperands,
    IHasRungText,
    IHasBranches,
    IHasSequencedInstructions,
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
    ILogicOperand,

    # Rung related data classes
    RungElement,
    RungBranch,
)
from controlrox.interfaces.plc.dialect import IHasInstructionsTranslator, IHasOperandsTranslator, IHasRungsTranslator
from controlrox.services import extract_instruction_strings, ControllerInstanceManager, DialectTranslatorFactory
from controlrox.services.plc.instruction import InstructionSequenceBuilder


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
            self._meta_data: META = dict()  # type: ignore
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
    Generic[META],
    ISupportsMetaDataListAssignment,
    HasMetaData[META],
):
    """Protocol for objects that support metadata list assignment.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        HasMetaData.__init__(self=self, **kwargs)

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

            # Please fix this holy, wow
            if isinstance(asset_list, HashList):
                asset_list.insert(asset, index)
            elif isinstance(asset_list, list):
                asset_list.insert(index, asset)

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
        invalidate_method: Optional[Callable] = None,
        dict_lookup_key: str = '@Name',
        object_attribute: str = 'name'
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

        if not dict_lookup_key or not object_attribute:
            raise ValueError("dict_lookup_key and object_attribute must be provided!")

        if asset in asset_list:
            raw_asset_to_remove = next((x for x in raw_asset_list if x[dict_lookup_key] == getattr(asset, object_attribute)), None)
            if raw_asset_to_remove is not None:
                raw_asset_list.remove(raw_asset_to_remove)
                asset_list.remove(asset)
        else:
            raise ValueError(f"Asset '{asset.name}' not found in asset list!")

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
        **__
    ) -> None:
        self._instructions: list['ILogicInstruction'] = []
        self._input_instructions: list['ILogicInstruction'] = []
        self._output_instructions: list['ILogicInstruction'] = []

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
        """Clear meta data of all instructions."""
        raise NotImplementedError("clear_instructions method must be implemented by subclass.")

    def create_instruction_from_text(
        self,
        instruction_text: str
    ) -> ILogicInstruction | None:
        """Create an instruction object from instruction text.

        Args:
            instruction_text (str): The instruction text to parse.
        Returns:
            ILogicInstruction | None: The created instruction object, or None if parsing failed.
        """
        from .instruction import LogicInstruction
        return LogicInstruction(meta_data=instruction_text)

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
                if instruction_filter == instr.name
            ]

        if operand_filter:
            filtered_instructions = [
                instr for instr in filtered_instructions
                if any(operand_filter in op.meta_data for op in instr.get_operands())
            ]

        return filtered_instructions

    def get_instruction_translator(self) -> IHasInstructionsTranslator:
        """Get the instruction translator for this object.

        Returns:
            IHasInstructionsTranslator: The instruction translator.
        """
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError("No active controller found for getting instruction translator.")

        dialect = ctrl.dialect
        return DialectTranslatorFactory.get_instruction_translator(dialect)

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
        return instruction in self.instructions

    def invalidate_instructions(self) -> None:
        self._instructions.clear()
        self._input_instructions.clear()
        self._output_instructions.clear()

    def remove_instruction(
        self,
        instruction: 'ILogicInstruction',
        inhibit_invalidate: bool = False,
        invalidate_method: Optional[Callable] = None
    ) -> None:
        self.remove_asset_from_meta_data(
            asset=instruction,
            asset_list=self.get_instructions(),
            raw_asset_list=self.get_raw_instructions(),
            inhibit_invalidate=inhibit_invalidate,
            invalidate_method=invalidate_method or self.invalidate_instructions
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


class HasOperands(
    IHasOperands,
    HasInstructions,
):
    """Protocol for objects that have operands.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._operands: list['ILogicOperand'] = []
        HasInstructions.__init__(self=self, **kwargs)

    def compile_operands(self) -> None:
        """Compile the operands for this object."""
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError("No active controller found for compiling rungs.")

        self.invalidate_operands()
        matches = self.get_operand_transformer().get_instruction_operands(str(self.meta_data))

        if not matches or len(matches) < 1:
            return

        for index, match in enumerate(matches):
            self._operands.append(ctrl.create_operand(meta_data=match))

    def get_operand_transformer(self) -> IHasOperandsTranslator:
        """Get the operand transformer for this object.

        Returns:
            IHasOperandsTranslator: The operand transformer.
        """
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError("No active controller found for getting operand translator.")

        dialect = ctrl.dialect
        return DialectTranslatorFactory.get_operand_translator(dialect)

    def get_operands(self) -> list['ILogicOperand']:
        """Get the list of operands."""
        if not self._operands:
            self.compile_operands()
        return self._operands

    def invalidate_operands(self) -> None:
        """Invalidate all operands."""
        self._operands.clear()


class HasRungText(
    IHasRungText,
    HasOperands,
):
    """Protocol for objects that have rung text.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._text: str = ""
        HasOperands.__init__(self=self, **kwargs)

    def get_text(self) -> str:
        return self._text

    def set_text(
        self,
        text: str
    ) -> None:
        self._text = text

    def tokenize_instruction_meta_data(self) -> list[str]:
        """Tokenize instruction meta_data to identify instructions and branch markers."""

        tokens = []
        text = self.text

        # First, extract all instructions using the balanced parentheses method
        instructions = extract_instruction_strings(text)
        instruction_ranges = []

        # Find the positions of each instruction in the text
        search_start = 0
        for instruction in instructions:
            pos = text.find(instruction, search_start)
            if pos != -1:
                instruction_ranges.append((pos, pos + len(instruction)))
                search_start = pos + len(instruction)

        # Process the text character by character
        i = 0
        current_segment = ""

        while i < len(text):
            char = text[i]

            if char in ['[', ']', ',']:
                # Check if this symbol is inside any instruction
                inside_instruction = any(start <= i < end for start, end in instruction_ranges)

                if inside_instruction:
                    # This bracket is part of an instruction (array reference), keep it
                    current_segment += char
                else:
                    # This is a branch marker or next-branch marker
                    if current_segment.strip():
                        # Extract instructions from current segment using our method
                        segment_instructions = extract_instruction_strings(current_segment)
                        tokens.extend(segment_instructions)
                        current_segment = ""

                    # Add the branch marker
                    tokens.append(char)
            else:
                current_segment += char

            i += 1

        # Process any remaining segment
        if current_segment.strip():
            segment_instructions = extract_instruction_strings(current_segment)
            tokens.extend(segment_instructions)

        return tokens

    def remove_token(
        self,
        tokens: list[str],
        index: int
    ) -> list[str]:
        """Remove a single token from a token list by index.

        Args:
            tokens (List[str]): Original token list
            index (int): Index of the token to remove
        Returns:
            List[str]: New token list with the specified token removed
        """
        if index < 0 or index >= len(tokens):
            raise IndexError("Index must be within the bounds of the token list!")

        new_tokens = [
            token for i, token in enumerate(tokens)
            if i != index
        ]

        return new_tokens

    def remove_tokens(
        self,
        tokens: list[str],
        start_index: int,
        end_index: int
    ) -> list[str]:
        """Remove tokens from a token list between specified positions.

        Args:
            tokens (List[str]): Original token list
            start_index (int): Start index to remove
            end_index (int): End index to remove
        Returns:
            List[str]: New token list with specified tokens removed
        Raises:
            IndexError: If start_index or end_index are out of bounds or invalid
        """
        if start_index < 0 or end_index < 0:
            raise IndexError("Start and end positions must be non-negative!")

        if end_index < start_index:
            raise IndexError("End position must be greater than or equal to start position!")

        new_tokens = [
            token for index, token in enumerate(tokens)
            if index < start_index or index > end_index
        ]

        return new_tokens


class HasBranches(
    IHasBranches,
    HasRungText,
):
    """Protocol for objects that have branches.
    """

    _branch_tokens = ['[', ']', ',']

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._branches: dict[str, RungBranch] = {}
        HasRungText.__init__(self=self, **kwargs)

    def compile_branches(self) -> None:
        raise NotImplementedError("compile_branches method must be implemented by subclass.")

    def create_branch(
        self,
        branch_id: str,
        start_position: int,
        end_position: int
    ) -> RungBranch:
        branch = RungBranch(
            branch_id=branch_id,
            start_position=start_position,
            end_position=end_position,
        )
        self._branches[branch.branch_id] = branch
        return branch

    def get_branch_start_token(self) -> str:
        return self._branch_tokens[0]

    def get_branch_end_token(self) -> str:
        return self._branch_tokens[1]

    def get_branch_next_token(self) -> str:
        return self._branch_tokens[2]

    def get_branch_tokens(self) -> list[str]:
        return self._branch_tokens

    def get_branches(self) -> dict[str, 'RungBranch']:
        if not self._branches:
            self.compile_branches()
        return self._branches

    def set_branches(
        self,
        branches: dict[str, 'RungBranch']
    ) -> None:
        self._branches = branches

    def has_branches(self) -> bool:
        return len(self.branches) > 0

    def invalidate_branches(self) -> None:
        self._branches.clear()

    @staticmethod
    def _insert_branch_tokens(
        original_tokens: list[str],
        start_pos: int,
        end_pos: int,
        branch_instructions: list[str]
    ) -> list[str]:
        """Insert branch markers and instructions into token sequence.

        Args:
            original_tokens (List[str]): Original token sequence
            start_pos (int): Start position for branch
            end_pos (int): End position for branch
            branch_instructions (List[str]): Instructions to place in branch

        Returns:
            List[str]: New token sequence with branch inserted
        """
        new_tokens = []

        if end_pos < start_pos:
            raise ValueError("End position must be greater than or equal to start position!")

        if not original_tokens:
            original_tokens = ['']

        def write_branch_end():
            new_tokens.append(',')
            for instr in branch_instructions:
                new_tokens.append(instr)
            new_tokens.append(']')

        for index, token in enumerate(original_tokens):
            if index == start_pos:
                new_tokens.append('[')
            if index == end_pos:
                write_branch_end()
            if token:
                new_tokens.append(token)
            if (end_pos == len(original_tokens) and index == len(original_tokens) - 1):
                write_branch_end()

        return new_tokens

    def find_matching_branch_end(
        self,
        start_position: int
    ) -> int:
        """Find the matching end position for a branch start.

        Args:
            start_position (int): Position where branch starts

        Returns:
            int: Position where branch ends, -1 if not found
        """
        if not self.text:
            return -1

        tokens = self.tokenize_instruction_meta_data()

        if len(tokens) <= start_position or tokens[start_position] != '[':
            raise ValueError("Start position must be a valid branch start token position.")

        bracket_count = 1  # Since we start on a bracket
        instruction_count = start_position

        for token in tokens[start_position+1:]:
            instruction_count += 1
            if token == '[':
                bracket_count += 1
            elif token == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    return instruction_count

        return -1

    def get_branch_internal_nesting_level(
        self,
        branch_position: int
    ) -> int:
        """Get nesting levels of elements inside of a branch.
        """
        end_position = self.find_matching_branch_end(branch_position)
        if end_position is None:
            raise ValueError(f"No matching end found for branch starting at position {branch_position}.")

        tokens = self.tokenize_instruction_meta_data()
        open_counter, nesting_counter, nesting_level = 0, 0, 0
        indexed_tokens = tokens[branch_position+1:end_position]
        for token in indexed_tokens:
            if open_counter < 0:
                raise ValueError("Mismatched brackets in rung text.")
            if token == '[':
                open_counter += 1
            elif token == ',' and open_counter:
                nesting_counter += 1
                if nesting_counter > nesting_level:
                    nesting_level = nesting_counter
            elif token == ']':
                open_counter -= 1

        return nesting_level

    def get_branch_nesting_level(self, instruction_position: int) -> int:
        """Get the nesting level of branches at a specific instruction position.

        Args:
            instruction_position (int): Position of the instruction (0-based)

        Returns:
            int: Nesting level (0 = main line, 1+ = inside branches)
        """
        if not self.text:
            return 0

        tokens = self.tokenize_instruction_meta_data()
        nesting_level = 0

        for index, token in enumerate(tokens):
            if token == '[':
                nesting_level += 1
            elif token == ']':
                nesting_level -= 1
            if index == instruction_position:
                return nesting_level

        return 0

    def get_max_branch_depth(self) -> int:
        """Get the maximum nesting depth of branches in this rung.

        Returns:
            int: Maximum branch depth (0 = no branches, 1+ = nested levels)
        """
        if not self.text:
            return 0

        tokens = self.tokenize_instruction_meta_data()
        first_branch_token_found = False
        current_depth = 0
        max_depth = 0
        restore_depth = 0

        for token in tokens:
            if token == '[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif token == ',':
                # ',' increases the nested branch count
                # But the first occurence is included with the '[' token
                # So, ignore the first one and set a flag
                # Additionally, mark where to restore the depth level when this branch sequence ends
                if first_branch_token_found is False:
                    first_branch_token_found = True
                    restore_depth = current_depth
                    continue
                else:
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)

            elif token == ']':
                current_depth -= 1
                first_branch_token_found = False
                current_depth = restore_depth

        return max_depth

    def insert_branch(
        self,
        start_pos: int = 0,
        end_pos: int = 0
    ) -> None:
        """Insert a new branch structure in the rung.

        Args:
            start_position (int): Position where the branch should start (0-based)
            end_position (int): Position where the branch should end (0-based)

        Raises:
            ValueError: If positions are invalid
            IndexError: If positions are out of range
        """
        original_tokens = self.tokenize_instruction_meta_data()

        if start_pos < 0 or end_pos < 0:
            raise ValueError("Branch positions must be non-negative!")

        if start_pos > len(original_tokens) or end_pos > len(original_tokens):
            raise IndexError("Branch positions out of range!")

        if start_pos > end_pos:
            raise ValueError("Start position must be less than or equal to end position!")

        new_tokens = self._insert_branch_tokens(
            original_tokens,
            start_pos,
            end_pos,
            []
        )

        self.set_text("".join(new_tokens))

    def insert_branch_level(
        self,
        branch_position: int = 0,
    ):
        """Insert a new branch level in the existing branch structure.
        """
        original_tokens = self.tokenize_instruction_meta_data()

        if branch_position < 0 or branch_position >= len(original_tokens):
            raise IndexError("Start position out of range!")

        if original_tokens[branch_position] != '[' and original_tokens[branch_position] != ',':
            raise ValueError("Start position must be on a branch start token!")

        # Find index of first 'next branch' marker after the start position, which is a ',' token
        next_branch_index = branch_position + 1
        nested_branch_count = 0

        while next_branch_index < len(original_tokens):
            if original_tokens[next_branch_index] == '[':
                nested_branch_count += 1
            elif original_tokens[next_branch_index] == ']':
                if nested_branch_count <= 0:
                    break
                nested_branch_count -= 1
            elif original_tokens[next_branch_index] == ',' and nested_branch_count <= 0:
                break
            next_branch_index += 1

        if next_branch_index >= len(original_tokens):
            raise ValueError("No next branch marker found after the start position!")

        if original_tokens[next_branch_index] != ',' and original_tokens[next_branch_index] != ']':
            raise ValueError("Next branch marker must be a ',' token!")

        # Insert a ',' at the next branch index
        new_tokens = original_tokens[:next_branch_index] + [','] + original_tokens[next_branch_index:]

        # Reconstruct text
        self.set_text("".join(new_tokens))

    def remove_branch(self, branch_id: str):
        """Remove a branch structure from the rung.

        Args:
            branch_id (str): ID of the branch to remove
            keep_instructions (bool): If True, keep branch instructions in main line

        Raises:
            ValueError: If branch ID doesn't exist
        """
        if branch_id not in self._branches:
            raise ValueError(f"Branch '{branch_id}' not found in rung!")

        branch = self._branches[branch_id]
        if branch.start_position < 0 or branch.end_position < 0:
            raise ValueError("Branch start or end position is invalid!")

        tokens = self.tokenize_instruction_meta_data()
        tokens = self.remove_tokens(tokens, branch.start_position, branch.end_position)
        for b in branch.nested_branches:
            if b.branch_id in self._branches:
                del self._branches[b.branch_id]
        del self._branches[branch_id]
        self.set_text("".join(tokens))

    def validate_branch_structure(self) -> bool:
        """Validate that branch markers are properly paired.

        Returns:
            bool: True if branch structure is valid, False otherwise
        """
        if not self.text:
            return True

        tokens = self.tokenize_instruction_meta_data()
        bracket_count = 0

        for token in tokens:
            if token == '[':
                bracket_count += 1
            elif token == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    return False

        return bracket_count == 0


class HasSequencedInstructions(
    IHasSequencedInstructions,
    HasBranches,
):
    """Protocol for objects that have sequenced instructions.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._sequence: list[RungElement] = []
        self._sequence_tracked_branches: list[RungBranch] = []
        HasBranches.__init__(self=self, **kwargs)

    def _process_branch_start_token(
        self,
        token: str,
        index: int,
    ) -> None:
        new_branch = self.create_branch(
            branch_id=f'branch_{index}',
            start_position=index,
            end_position=-1,
        )
        self._sequence_tracked_branches.append(new_branch)

    def _process_branch_end_token(
        self,
        token: str,
        index: int,
    ) -> None:
        try:
            parent_branch = self._sequence_tracked_branches.pop()
            parent_branch.end_position = index
            for nested_branch in parent_branch.nested_branches:
                nested_branch.end_position = index

            self.create_branch(
                branch_id=parent_branch.branch_id,
                start_position=parent_branch.start_position,
                end_position=index,
            )
        except IndexError:
            raise ValueError("Mismatched branch end token found!") from None

    def _process_branch_next_token(
        self,
        token: str,
        index: int,
    ) -> None:
        parent_branch = self._sequence_tracked_branches[-1]
        if not parent_branch:
            raise ValueError("Mismatched next-branch token found!")

        next_branch = self.create_branch(
            branch_id=f'{parent_branch.branch_id}:sub-{index}',
            start_position=index,
            end_position=-1,
        )

        parent_branch.nested_branches.append(next_branch)

    def _process_branch_token(
        self,
        token: str,
        index: int,
    ) -> None:
        if token == self.get_branch_end_token():
            self._process_branch_end_token(token, index)

        elif token == self.get_branch_start_token():
            self._process_branch_start_token(token, index)

        elif token == self.get_branch_next_token():
            self._process_branch_next_token(token, index)

    def _process_instruction_token(
        self,
        token: str,
    ) -> None:
        instruction = self.create_instruction_from_text(token)
        if not instruction:
            raise ValueError(f"Failed to create instruction from text: {token}")
        self._instructions.append(instruction)

    def build_sequence(self) -> None:
        self.invalidate_sequence()
        sequence_builder = InstructionSequenceBuilder(self.tokenize_instruction_meta_data())
        self._sequence = sequence_builder.build_sequence()

    def clear_instructions(self) -> None:
        self.invalidate_instructions()
        self.invalidate_sequence()
        self.set_text('')

    def compile_branches(self) -> None:
        self.invalidate()
        self.compile_instructions()

    def compile_instructions(self) -> None:
        self.invalidate_instructions()
        self._sequence_tracked_branches.clear()
        tokens = self.tokenize_instruction_meta_data()

        for index, token in enumerate(tokens):
            if token in self.branch_tokens:
                self._process_branch_token(token, index)
                continue

            else:
                self._process_instruction_token(token)

    def compile_sequence(self) -> None:
        self.invalidate_instructions()
        self.invalidate_sequence()
        self.compile_instructions()
        self.build_sequence()

    def get_instruction_by_index(
        self,
        index: int
    ) -> ILogicInstruction:
        """Get the instruction at a specific index.

        Args:
            index (int): The index

        Returns:
            ILogicInstruction: The instruction at that index
        """
        if 0 <= index < len(self.instructions):
            return self.instructions[index]
        raise IndexError("Instruction index out of range!")

    def get_sequence(self) -> list[RungElement]:
        if not self._sequence:
            self.compile_sequence()
        return self._sequence

    def set_sequence(self, sequence: list[RungElement]) -> None:
        self._sequence = sequence

    def invalidate(self) -> None:
        self.invalidate_branches()
        self.invalidate_instructions()
        self.invalidate_sequence()

    def invalidate_sequence(self) -> None:
        self._sequence.clear()

    def move_instruction(
        self,
        old_position: int,
        new_position: int,
    ) -> None:
        """Move an instruction to a new position in the rung.

        Args:
            instruction: The instruction to move (LogicInstruction, str, or int index)
            new_position (int): The new position for the instruction
            occurrence (int): Which occurrence to move if there are duplicates (0-based)
        """
        current_tokens = self.tokenize_instruction_meta_data()

        if not current_tokens:
            raise ValueError("No instructions found in rung!")

        if new_position < 0 or new_position >= len(current_tokens):
            raise IndexError(f"New position {new_position} out of range!")

        if old_position < 0 or old_position >= len(current_tokens):
            raise IndexError(f"Instruction index {old_position} out of range!")

        old_index = old_position
        if old_index == new_position:
            return  # No move needed

        # Move the instruction
        moved_instruction = current_tokens.pop(old_index)
        current_tokens.insert(new_position, moved_instruction)

        # Rebuild text with reordered instructions
        self.invalidate()
        self.set_text("".join(current_tokens))

    def remove_instruction_by_index(
        self,
        index: int
    ) -> None:
        """Remove the instruction at a specific index.

        Args:
            index (int): The index
        """
        if 0 <= index < len(self.instructions):
            instruction = self.instructions[index]
            self.remove_instruction(
                instruction,
                False,
                self.invalidate
            )
            return
        raise IndexError("Instruction index out of range!")


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
        **__
    ) -> None:
        self._routines: HashList['IRoutine'] = HashList('name')

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
    SupportsMetaDataListAssignment[dict],
):
    """Protocol for objects that have rungs.
    """

    def __init__(
        self,
        **kwargs
    ) -> None:
        self._rungs: list['IRung'] = []
        SupportsMetaDataListAssignment.__init__(self=self, **kwargs)

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
            asset_list=self.rungs,
            raw_asset_list=self.raw_rungs,
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
        for index, rung in enumerate(rungs):
            self.add_rung(
                rung,
                index=index,
                inhibit_invalidate=True
            )
        self.invalidate_rungs()

    def clear_rungs(self) -> None:
        self.set_raw_rungs([])
        self.invalidate_rungs()

    def compile_rungs(self) -> None:
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError("No active controller found for compiling rungs.")

        self.invalidate_rungs()
        for index, rung in enumerate(self.raw_rungs):
            self._rungs.append(ctrl.create_rung(
                meta_data=rung,
                routine=self if isinstance(self, IRoutine) else None,  # TODO: i'm not sure i like this
                rung_number=index
            ))

    def get_rung_translator(self) -> IHasRungsTranslator:
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise RuntimeError("No controller instance available for rung translation!")
        return DialectTranslatorFactory.get_rungs_translator(ctrl.dialect)

    def get_rungs(self) -> list['IRung']:
        """Get the list of rungs."""
        if not self._rungs:
            self.compile_rungs()
        return self._rungs

    def get_raw_rungs(self) -> list[dict]:
        return self.rung_translator.get_raw_rungs(self.meta_data)

    def set_raw_rungs(
        self,
        raw_rungs: list[dict]
    ) -> None:
        self.raw_rungs.clear()
        self.raw_rungs.extend(raw_rungs)

    def invalidate_rungs(self) -> None:
        self._rungs.clear()

    def reassign_rung_numbers(self) -> None:
        for index, rung in enumerate(self.rungs):
            rung.set_number(index)

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
            invalidate_method=self.invalidate_rungs,
            dict_lookup_key='@Number',
            object_attribute='number'
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
        **__
    ) -> None:
        self._tags: HashList['ITag'] = HashList('name')
        self._safety_tags: HashList['ITag'] = HashList('name')
        self._standard_tags: HashList['ITag'] = HashList('name')

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
