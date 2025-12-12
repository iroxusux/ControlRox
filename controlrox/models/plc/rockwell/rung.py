"""Rung model for PLC.
"""
from typing import (
    Dict,
    List,
    Optional,
    Union
)
import re
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.interfaces import LogicInstructionType, ILogicInstruction, IRoutine
from controlrox.models.plc.rockwell.meta import PLC_RUNG_FILE
from controlrox.models.plc import LogicInstruction, Rung
from controlrox.services.plc.rung import RungFactory
from .meta import INST_RE_PATTERN, RaPlcObject


class RaRung(
    RaPlcObject[dict],
    Rung,
    metaclass=FactoryTypeMeta['RaRung', RungFactory]
):
    _branch_id_counter: int = 0  # Static counter for unique branch IDs

    default_l5x_file_path = PLC_RUNG_FILE
    default_l5x_asset_key = 'Rung'

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        routine: Optional[IRoutine] = None,
        rung_number: Union[int, str] = 0,
        rung_text: str = '',
        comment: str = ''
    ):
        """type class for plc Rung"""
        super().__init__(
            meta_data=meta_data,
            name='',
            comment=comment,
            routine=routine,
            rung_text=rung_text,
        )

        if rung_text:
            self.set_rung_text(rung_text)
        if comment:
            self.set_rung_comment(comment)
        if rung_number:
            self.set_rung_number(rung_number)

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Number',
            '@Type',
            'Comment',
            'Text'
        ]

    @property
    def comment(self) -> str:
        return self.get_rung_comment()

    @property
    def number(self) -> str:
        return self.get_rung_number()

    @property
    def text(self) -> str:
        return self.get_rung_text()

    @property
    def type(self) -> str:
        return self['@Type']

    @staticmethod
    def _extract_instructions(
        text
    ) -> List[str]:
        """Extract instructions with properly balanced parentheses.

        Args:
            text (str): The rung text to extract instructions from.

        Returns:
            List[str]: A list of extracted instructions.
        """
        instructions = []

        # Find instruction starts
        starts = list(re.finditer(r'[A-Za-z0-9_]+\(', text))

        for match in starts:
            start_pos = match.start()
            paren_pos = match.end() - 1  # Position of opening parenthesis

            # Find matching closing parenthesis
            paren_count = 1
            pos = paren_pos + 1

            while pos < len(text) and paren_count > 0:
                if text[pos] == '(':
                    paren_count += 1
                elif text[pos] == ')':
                    paren_count -= 1
                pos += 1

            if paren_count == 0:  # Found matching closing parenthesis
                instruction = text[start_pos:pos]
                instructions.append(instruction)

        return instructions

    @staticmethod
    def _insert_branch_tokens(
        original_tokens: List[str],
        start_pos: int,
        end_pos: int,
        branch_instructions: List[str]
    ) -> List[str]:
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

    @classmethod
    def get_factory(cls):
        return RungFactory

    def _build_sequence_from_tokens(
        self,
        tokens: List[str]
    ) -> None:
        """Build the rung sequence from tokenized text.
        """
        position = 0
        root_branch_id = None  # Track each branch's parent, since the symbols appear on the parent rail
        branch_id = None
        branch_stack: list[RungBranch] = []
        branch_counter = 0
        branch_level = 0
        branch_level_history: list[int] = []  # Track branch levels for nesting
        branch_root_id_history: list[str] = []  # Track root branch IDs for nesting
        instruction_index = 0

        for token in tokens:
            if token == '[':  # Branch start
                branch_id = self._get_unique_branch_id()
                branch_counter += 1
                branch_level_history.append(branch_level)
                branch_level = 0  # Reset branch level for new branch

                branch_start = RungElement(
                    element_type=RungElementType.BRANCH_START,
                    branch_id=branch_id,
                    root_branch_id=root_branch_id,
                    branch_level=branch_level,
                    position=position,
                    rung=self,
                    rung_number=int(self.number)
                )

                branch = RungBranch(
                    branch_id=branch_id,
                    root_branch_id=root_branch_id,
                    start_position=position,
                    end_position=-1,
                    nested_branches=[],
                )

                branch_stack.append(branch)
                self._branches[branch_id] = branch
                self._rung_sequence.append(branch_start)
                branch_root_id_history.append(root_branch_id)  # Save current root branch id # type: ignore
                root_branch_id = branch_id  # Change branch id after assignment so we get the proper parent
                position += 1

            elif token == ']':  # Branch end
                branch = branch_stack.pop()
                self._branches[branch.branch_id].end_position = position
                if not self._branches[branch.branch_id].nested_branches:
                    # If no nested branches, we need to delete this major branch and reconstruct the rung again
                    fresh_tokens = self._remove_token_by_index(self._tokenize_rung_text(self.text), position)
                    fresh_tokens = self._remove_token_by_index(fresh_tokens, branch.start_position)
                    self.set_rung_text("".join(fresh_tokens))
                    self._refresh_internal_structures()
                    return

                self._branches[branch.branch_id].nested_branches[-1].end_position = position - 1
                root_branch_id = branch_root_id_history.pop() if branch_root_id_history else None
                branch_id = self._branches[branch.branch_id].root_branch_id
                branch_level = branch_level_history.pop() if branch_level_history else 0

                branch_end = RungElement(
                    element_type=RungElementType.BRANCH_END,
                    branch_id=branch.branch_id,
                    root_branch_id=branch.root_branch_id,
                    branch_level=branch_level,
                    position=position,
                    rung=self,
                    rung_number=int(self.number)
                )

                self._rung_sequence.append(branch_end)
                position += 1

            elif token == ',':  # Next branch marker
                parent_branch = branch_stack[-1] if branch_stack else None
                if not parent_branch:
                    raise ValueError("Next branch marker found without an active branch!")

                branch_level += 1
                branch_id = f'{parent_branch.branch_id}:{branch_level}'

                if branch_level > 1:
                    # update the previous nested branch's end position
                    parent_branch.nested_branches[-1].end_position = position - 1  # ends at the previous position

                next_branch = RungElement(
                    element_type=RungElementType.BRANCH_NEXT,
                    branch_id=branch_id,
                    root_branch_id=root_branch_id,
                    branch_level=branch_level,
                    position=position,
                    rung=self,
                    rung_number=int(self.number)
                )
                nested_branch = RungBranch(branch_id=branch_id, start_position=position,
                                           end_position=-1, root_branch_id=parent_branch.branch_id)

                parent_branch.nested_branches.append(nested_branch)
                self._branches[branch_id] = nested_branch
                self._rung_sequence.append(next_branch)
                position += 1

            else:  # Regular instruction
                instruction = self._find_instruction_by_text(token, instruction_index)
                if instruction:
                    element = RungElement(
                        element_type=RungElementType.INSTRUCTION,
                        instruction=instruction,
                        position=position,
                        branch_id=branch_id,
                        root_branch_id=root_branch_id,
                        branch_level=branch_level,
                        rung=self,
                        rung_number=int(self.number)
                    )

                    self._rung_sequence.append(element)
                    position += 1
                    instruction_index += 1
                else:
                    raise ValueError(f"Instruction '{token}' not found in rung text.")

    def _find_instruction_by_text(self, text: str, index: int) -> Optional[ILogicInstruction]:
        """Find an instruction object by its text representation."""
        # First try exact match
        for instruction in self._instructions:
            if instruction.get_meta_data() == text:
                return instruction

        # If no exact match, try by index (fallback)
        if 0 <= index < len(self._instructions):
            return self._instructions[index]

        return None

    def _find_instruction_index_in_text(self, instruction_text: str, occurrence: int = 0) -> int:
        """Find the index of an instruction in the text by its occurrence.

        Args:
            instruction_text (str): The instruction text to find
            occurrence (int): Which occurrence to find (0-based)

        Returns:
            int: The index of the instruction

        Raises:
            ValueError: If instruction not found or occurrence out of range
        """
        tokens = self._tokenize_rung_text(self.text)
        # existing_instructions = re.findall(INST_RE_PATTERN, self.text)
        matches = [i for i, token in enumerate(tokens) if token == instruction_text]

        if not matches:
            raise ValueError(f"Instruction '{instruction_text}' not found in rung")

        if occurrence >= len(matches):
            raise ValueError(f"Occurrence {occurrence} not found. Only {len(matches)} occurrences exist.")

        return matches[occurrence]

    def _get_element_at_position(
        self,
        position: int
    ) -> Optional[RungElement]:
        """Get the RungElement at a specific position in the rung sequence.
        Args:
            position (int): The position in the rung sequence
        Returns:
            Optional[RungElement]: The RungElement at the specified position, or None if not found
        """
        if position < 0 or position >= len(self._rung_sequence) or position is None:
            raise IndexError("Position out of range in rung sequence.")

        return self._rung_sequence[position]

    def compile_instructions(self):
        """Extract instructions from rung text."""
        if not self.text:
            return

        meta_data_instructions = self._extract_instructions(self.text)
        if not meta_data_instructions:
            return

        from controlrox.models.plc.rockwell.instruction import RaLogicInstruction  # noqa: F811

        instructions = []
        for meta_data in meta_data_instructions:
            instruction = RaLogicInstruction(
                meta_data=meta_data,
            )
            instructions.append(instruction)

        instrs = []
        for instr in meta_data_instructions:
            instrs.append(RaLogicInstruction(meta_data=instr))

        self.set_instructions(instrs)

    def _get_unique_branch_id(self) -> str:
        """Generate a unique branch ID."""
        branch_id = f"rung_{self.number}_branch_{self._branch_id_counter}"
        self._branch_id_counter += 1
        return branch_id

    def _parse_rung_sequence(self):
        """Parse the rung text to identify instruction sequence and branches."""
        self._refresh_internal_structures()
        self.compile_instructions()
        self._build_sequence_from_tokens(self._tokenize_rung_text(self.text))

    def _tokenize_rung_text(self, text: str) -> List[str]:
        """Tokenize rung text to identify instructions and branch markers."""

        tokens = []

        # First, extract all instructions using the balanced parentheses method
        instructions = self._extract_instructions(text)
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
                        segment_instructions = self._extract_instructions(current_segment)
                        tokens.extend(segment_instructions)
                        current_segment = ""

                    # Add the branch marker
                    tokens.append(char)
            else:
                current_segment += char

            i += 1

        # Process any remaining segment
        if current_segment.strip():
            segment_instructions = self._extract_instructions(current_segment)
            tokens.extend(segment_instructions)

        return tokens

    def _reconstruct_text_with_branches(self, instructions: List[str],
                                        branch_markers: List[str],
                                        original_text: str) -> str:
        """Reconstruct text preserving branch structure.

        This is a complex operation that attempts to maintain the relative positioning
        of branch markers with the instruction sequence.
        """
        # Get original tokens to understand structure
        original_tokens = self._tokenize_rung_text(original_text)

        # Create a map of instruction positions to branch operations
        instruction_index = 0
        result_tokens = []

        for token in original_tokens:
            if token in ['[', ']', ',']:
                # Preserve branch markers
                result_tokens.append(token)
            else:
                # Replace with new instruction if available
                if instruction_index < len(instructions):
                    result_tokens.append(instructions[instruction_index])
                    instruction_index += 1

        # Add any remaining instructions at the end
        while instruction_index < len(instructions):
            result_tokens.append(instructions[instruction_index])
            instruction_index += 1

        return "".join(result_tokens)

    def _refresh_internal_structures(self):
        """Refresh the internal instruction and sequence structures after text changes."""
        self._instructions.clear()
        self._rung_sequence.clear()
        self._branches.clear()
        self._branch_id_counter = 0
        self._input_instructions.clear()
        self._output_instructions.clear()

    def _remove_token_by_index(self, tokens: List[str], index: int) -> List[str]:
        """Remove a token at a specific index from the token list.

        Args:
            tokens (List[str]): List of tokens
            index (int): Index of the token to remove

        Returns:
            List[str]: New token list with the specified token removed
        """
        if index < 0 or index >= len(tokens):
            raise IndexError("Index out of range!")

        return tokens[:index] + tokens[index + 1:]

    def _remove_tokens(self, tokens: List[str], start: int, end: int) -> List[str]:
        """Remove a range of tokens from the token list.

        Args:
            tokens (List[str]): List of tokens
            start (int): Start index of the range to remove
            end (int): End index of the range to remove

        Returns:
            List[str]: New token list with the specified range removed
        """
        if start < 0 or end >= len(tokens) or start > end:
            raise IndexError("Invalid start or end indices for removal!")

        return tokens[:start] + tokens[end + 1:]

    def add_instruction(
        self,
        instruction: ILogicInstruction,
        index: Optional[int] = None
    ) -> None:
        """Add an instruction to this rung at the specified position.

        Args:
            instruction_text (str): The instruction text to add (e.g., "XIC(Tag1)")
            position (Optional[int]): Position to insert at. If None, appends to end.
        """
        data = instruction.get_meta_data()
        if not data or not isinstance(data, str):
            raise ValueError("Instruction text must be a non-empty string!")

        # Validate instruction format
        if not re.match(INST_RE_PATTERN, data):
            raise ValueError(f"Invalid instruction format: {data}")

        current_text = self.text or ""

        if not current_text.strip():
            # Empty rung, just set the instruction
            current_tokens = [data]
        else:
            # Parse existing instructions to find insertion point
            current_tokens = self._tokenize_rung_text(current_text)

            if index is None or index >= len(current_tokens):
                # Append to end
                current_tokens.append(data)
            elif index == 0:
                # Insert at beginning
                current_tokens.insert(0, data)

            else:
                # Insert at specific position
                current_tokens.insert(index, data)

        # Refresh internal structures
        self.set_rung_text("".join(current_tokens))

    def find_instruction_positions(self, instruction_text: str) -> List[int]:
        """Find all positions of a specific instruction in the rung.

        Args:
            instruction_text (str): The instruction text to find

        Returns:
            List[int]: List of positions where the instruction appears
        """
        import re
        existing_instructions = re.findall(INST_RE_PATTERN, self.text) if self.text else []
        return [i for i, inst in enumerate(existing_instructions) if inst == instruction_text]

    def find_matching_branch_end(self, start_position: int) -> Optional[int]:
        """Find the matching end position for a branch start.

        Args:
            start_position (int): Position where branch starts

        Returns:
            Optional[int]: Position where branch ends, or None if not found
        """
        if not self.text:
            return None

        tokens = self._tokenize_rung_text(self.text)
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

        return None

    def get_branch_count(self) -> int:
        """Get the number of branches in this rung."""
        return len(self._branches)

    def get_branch_internal_nesting_level(self, branch_position: int) -> int:
        """Get nesting levels of elements inside of a branch.
        """
        end_position = self.find_matching_branch_end(branch_position)
        if end_position is None:
            raise ValueError(f"No matching end found for branch starting at position {branch_position}.")

        tokens = self._tokenize_rung_text(self.text)
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

        tokens = self._tokenize_rung_text(self.text)
        nesting_level = 0

        for index, token in enumerate(tokens):
            if token == '[':
                nesting_level += 1
            elif token == ']':
                nesting_level -= 1
            if index == instruction_position:
                return nesting_level

        return 0

    def get_comment_lines(self) -> int:
        """Get the number of comment lines in this rung.
        """
        if not self.comment:
            return 0

        # Count the number of comment lines by splitting on newlines
        return len(self.comment.splitlines())

    def get_execution_sequence(self) -> List[Dict]:
        """Get the logical execution sequence of the rung."""
        sequence = []

        for i, element in enumerate(self._rung_sequence):
            if not element.instruction:
                continue

            if element.element_type == RungElementType.INSTRUCTION:
                sequence.append({
                    'step': i,
                    'instruction_type': element.instruction.get_instruction_name(),
                    'instruction_text': element.instruction.meta_data,
                    'operands': [op.meta_data for op in element.instruction.get_operands()],
                    'is_input': element.instruction.get_instruction_type() == LogicInstructionType.INPUT,
                    'is_output': element.instruction.get_instruction_type() == LogicInstructionType.OUTPUT
                })
            elif element.element_type in [RungElementType.BRANCH_START, RungElementType.BRANCH_END]:
                sequence.append({
                    'step': i,
                    'element_type': element.element_type.value,
                    'branch_id': element.branch_id
                })

        return sequence

    def get_instruction_count(self) -> int:
        """Get the total number of instructions in this rung."""
        return len(self.instructions)

    def get_instruction_at_position(
        self,
        position: int
    ) -> Optional[ILogicInstruction]:
        """Get the instruction at a specific position.

        Args:
            position (int): The position index

        Returns:
            Optional[LogicInstruction]: The instruction at that position, or None
        """
        if 0 <= position < len(self.instructions):
            return self.instructions[position]
        return None

    def get_instruction_summary(self) -> Dict[str, int]:
        """Get a summary of instruction types and their counts.

        Returns:
            Dict[str, int]: Dictionary mapping instruction names to their counts
        """
        summary = {}
        for instruction in self.instructions:
            inst_name = instruction.name
            summary[inst_name] = summary.get(inst_name, 0) + 1
        return summary

    def get_max_branch_depth(self) -> int:
        """Get the maximum nesting depth of branches in this rung.

        Returns:
            int: Maximum branch depth (0 = no branches, 1+ = nested levels)
        """
        if not self.text:
            return 0

        tokens = self._tokenize_rung_text(self.text)
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

    def get_rung_comment(self) -> str:
        if self['Comment'] is None:
            return ""
        return self['Comment']

    def get_rung_number(self) -> str:
        return self['@Number']

    def get_rung_text(self) -> str:
        if self['Text'] is None:
            return ""
        return self['Text']

    def has_instruction(
        self,
        instruction: ILogicInstruction
    ) -> bool:
        meta_data = instruction.get_meta_data()
        if not isinstance(meta_data, str):
            raise ValueError("Instruction meta data must be a string!")
        return len(self.find_instruction_positions(meta_data)) > 0

    def has_branches(self) -> bool:
        """Check if this rung contains any branches."""
        return len(self._branches) > 0

    def insert_branch(
        self,
        start_position: int = 0,
        end_position: int = 0
    ) -> None:
        """Insert a new branch structure in the rung.

        Args:
            start_position (int): Position where the branch should start (0-based)
            end_position (int): Position where the branch should end (0-based)

        Raises:
            ValueError: If positions are invalid
            IndexError: If positions are out of range
        """
        original_tokens = self._tokenize_rung_text(self.text)

        if start_position < 0 or end_position < 0:
            raise ValueError("Branch positions must be non-negative!")

        if start_position > len(original_tokens) or end_position > len(original_tokens):
            raise IndexError("Branch positions out of range!")

        if start_position > end_position:
            raise ValueError("Start position must be less than or equal to end position!")

        new_tokens = self._insert_branch_tokens(
            original_tokens,
            start_position,
            end_position,
            []
        )

        self.set_rung_text("".join(new_tokens))

    def insert_branch_level(self,
                            branch_position: int = 0,):
        """Insert a new branch level in the existing branch structure.
        """
        original_tokens = self._tokenize_rung_text(self.text)
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
        self.set_rung_text("".join(new_tokens))

    def move_instruction(self, instruction: Union[LogicInstruction, str, int],
                         new_position: int, occurrence: int = 0):
        """Move an instruction to a new position in the rung.

        Args:
            instruction: The instruction to move (LogicInstruction, str, or int index)
            new_position (int): The new position for the instruction
            occurrence (int): Which occurrence to move if there are duplicates (0-based)
        """
        current_tokens = self._tokenize_rung_text(self.text)

        if not current_tokens:
            raise ValueError("No instructions found in rung!")

        if new_position < 0 or new_position >= len(current_tokens):
            raise IndexError(f"New position {new_position} out of range!")

        # Find the instruction to move
        if isinstance(instruction, LogicInstruction):
            try:
                old_index = self._find_instruction_index_in_text(instruction.meta_data, occurrence)
            except ValueError:
                raise ValueError(f"Instruction '{instruction.meta_data}' not found in rung!")

        elif isinstance(instruction, str):
            try:
                old_index = self._find_instruction_index_in_text(instruction, occurrence)
            except ValueError:
                raise ValueError(f"Instruction '{instruction}' not found in rung!")

        elif isinstance(instruction, int):
            if instruction < 0 or instruction >= len(current_tokens):
                raise IndexError(f"Instruction index {instruction} out of range!")
            old_index = instruction
        else:
            raise TypeError("Instruction must be LogicInstruction, str, or int!")

        if old_index == new_position:
            return  # No move needed

        # Move the instruction
        moved_instruction = current_tokens.pop(old_index)
        current_tokens.insert(new_position, moved_instruction)

        # Rebuild text with reordered instructions
        self.set_rung_text("".join(current_tokens))

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

        tokens = self._tokenize_rung_text(self.text)
        tokens = self._remove_tokens(tokens, branch.start_position, branch.end_position)
        for b in branch.nested_branches:
            if b.branch_id in self._branches:
                del self._branches[b.branch_id]
        del self._branches[branch_id]
        self.set_rung_text("".join(tokens))

    def remove_instruction(
        self,
        instruction: Union[ILogicInstruction, str, int],
        occurrence: int = 0
    ):
        """Remove an instruction from this rung.

        Args:
            instruction: The instruction to remove. Can be:
                - LogicInstruction object
                - str: instruction text to remove
                - int: index of instruction to remove
            occurrence (int): Which occurrence to remove if there are duplicates (0-based).
                            Only used when instruction is a string.
        """
        if not self.text:
            raise ValueError("Cannot remove instruction from empty rung!")

        existing_instructions = re.findall(INST_RE_PATTERN, self.text)
        current_tokens = self._tokenize_rung_text(self.text)

        if not existing_instructions:
            raise ValueError("No instructions found in rung!")

        # Determine which instruction to remove
        if isinstance(instruction, ILogicInstruction):
            # Find the instruction by its meta_data
            try:
                remove_index = self._find_instruction_index_in_text(instruction.meta_data, occurrence)
            except ValueError:
                raise ValueError(f"Instruction '{instruction.meta_data}' not found in rung!")

        elif isinstance(instruction, str):
            # Remove by instruction text
            try:
                remove_index = self._find_instruction_index_in_text(instruction, occurrence)
            except ValueError:
                raise ValueError(f"Instruction '{instruction}' not found in rung!")

        elif isinstance(instruction, int):
            # Remove by index
            if instruction < 0 or instruction >= len(current_tokens):
                raise IndexError(f"Instruction index {instruction} out of range!")
            remove_index = instruction
        else:
            raise TypeError("Instruction must be LogicInstruction, str, or int!")

        # Remove the instruction and rebuild text
        current_tokens.pop(remove_index)

        if not current_tokens:
            # Last instruction removed, clear the rung
            self.set_rung_text("")
        else:
            # Rebuild text with remaining instructions
            self.set_rung_text("".join(current_tokens))

    def replace_instruction(self, old_instruction: Union[LogicInstruction, str, int],
                            new_instruction_text: str, occurrence: int = 0):
        """Replace an instruction in this rung.

        Args:
            old_instruction: The instruction to replace (LogicInstruction, str, or int index)
            new_instruction_text (str): The new instruction text
            occurrence (int): Which occurrence to replace if there are duplicates (0-based)
        """
        if not new_instruction_text or not isinstance(new_instruction_text, str):
            raise ValueError("New instruction text must be a non-empty string!")

        # Validate new instruction format
        import re
        if not re.match(INST_RE_PATTERN, new_instruction_text):
            raise ValueError(f"Invalid instruction format: {new_instruction_text}")

        current_tokens = self._tokenize_rung_text(self.text)

        if not current_tokens:
            raise ValueError("No instructions found in rung!")

        # Determine which instruction to replace
        if isinstance(old_instruction, LogicInstruction):
            instruction_text = old_instruction.meta_data
            try:
                replace_index = self._find_instruction_index_in_text(instruction_text, occurrence)
            except ValueError:
                raise ValueError(f"Instruction '{instruction_text}' not found in rung!")

        elif isinstance(old_instruction, str):
            try:
                replace_index = self._find_instruction_index_in_text(old_instruction, occurrence)
            except ValueError:
                raise ValueError(f"Instruction '{old_instruction}' not found in rung!")

        elif isinstance(old_instruction, int):
            if old_instruction < 0 or old_instruction >= len(current_tokens):
                raise IndexError(f"Instruction index {old_instruction} out of range!")
            replace_index = old_instruction
        else:
            raise TypeError("Old instruction must be LogicInstruction, str, or int!")

        # Replace the instruction
        current_tokens[replace_index] = new_instruction_text

        # Rebuild text with updated instructions
        self.set_rung_text("".join(current_tokens))

    def set_rung_comment(self, comment: str):
        if not isinstance(comment, str):
            raise ValueError("Comment must be a string!")
        self['Comment'] = comment

    def set_rung_number(self, rung_number: Union[str, int]):
        if not isinstance(rung_number, (str, int)):
            raise ValueError("Rung number must be a string or int!")
        self['@Number'] = str(rung_number)

    def set_rung_text(self, text: str) -> None:
        if text is not None and not text.endswith(';'):
            text += ';'
        self['Text'] = text
        self._parse_rung_sequence()

    def validate_branch_structure(self) -> bool:
        """Validate that branch markers are properly paired.

        Returns:
            bool: True if branch structure is valid, False otherwise
        """
        if not self.text:
            return True

        tokens = self._tokenize_rung_text(self.text)
        bracket_count = 0

        for token in tokens:
            if token == '[':
                bracket_count += 1
            elif token == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    return False

        return bracket_count == 0

    def wrap_instructions_in_branch(self, start_position: int, end_position: int) -> str:
        """Wrap existing instructions in a new branch structure.

        Args:
            start_position (int): Start position of instructions to wrap
            end_position (int): End position of instructions to wrap

        Returns:
            str: The branch ID that was created

        Raises:
            ValueError: If positions are invalid
            IndexError: If positions are out of range
        """
        if not self.text:
            raise ValueError("Cannot wrap instructions in empty rung!")

        current_instructions = re.findall(INST_RE_PATTERN, self.text)
        if not current_instructions:
            raise ValueError("No instructions found in rung!")

        if start_position < 0 or end_position < 0:
            raise ValueError("Positions must be non-negative!")

        if start_position >= len(current_instructions) or end_position > len(current_instructions):
            raise IndexError("Positions out of range!")

        if start_position > end_position:
            raise ValueError("Start position must be less than or equal to end position!")

        # Remove the original instructions
        for i in range(start_position, end_position):
            self.remove_instruction(i)

        # Insert branch with wrapped instructions
        self.insert_branch(start_position, start_position)

        return ''  # TODO: return branch ID
