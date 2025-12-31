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
from controlrox.interfaces import ILogicInstruction, IRoutine
from controlrox.models.plc.rockwell.meta import PLC_RUNG_FILE
from controlrox.models.plc import Rung
from controlrox.services.plc.rung import RungFactory
from .meta import INST_RE_PATTERN, RaPlcObject


class RaRung(
    RaPlcObject[dict],
    Rung,
    metaclass=FactoryTypeMeta['RaRung', RungFactory]
):

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
