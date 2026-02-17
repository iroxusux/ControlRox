import re
from pyrox.models.factory import MetaFactory
from controlrox.interfaces.plc.rung import RungElement, RungElementType, RungBranch


class InstructionSequenceBuilder:
    """Helper class to build instruction sequences from text."""

    def __init__(
        self,
        token_sequence: list[str],
    ) -> None:
        self.token_sequence = token_sequence
        self.position = 0
        self.branch_id = ''
        self.root_branch_id = ''
        self.branch_stack: list[RungBranch] = []
        self.branch_counter = 0
        self.branch_id_counter = 0
        self.branch_level = 0
        self.branch_level_history: list[int] = []
        self.branch_root_id_history: list[str] = []
        self.instruction_index = 0
        self.sequence: list[RungElement] = []
        self.branches: dict[str, RungBranch] = {}

    def _init(self) -> None:
        """Initialize the builder state.
        """
        self.position = 0
        self.branch_id = ''
        self.root_branch_id = ''
        self.branch_stack.clear()
        self.branch_counter = 0
        self.branch_level = 0
        self.branch_level_history.clear()
        self.branch_root_id_history.clear()
        self.instruction_index = 0
        self.sequence.clear()
        self.branches.clear()

    def _begin_new_branch_level(self) -> None:
        """Begin a new branch level in the current branch.
        """
        parent_branch = self._get_parent_branch()
        self._generate_new_branch_level_id()

        if self.branch_level > 1:
            # update the previous nested branch's end position
            parent_branch.nested_branches[-1].end_position = self.position - 1  # ends at the previous position

    def _begin_new_branch_sequence(self) -> RungElement:
        """Begin a new branch in the rung sequence.
        """
        branch_id = self._get_unique_branch_id()

        self.branch_counter += 1
        self.branch_level_history.append(self.branch_level)

        self.branch_level = 0  # Reset branch level for new branch

        branch = RungElement(
            element_type=RungElementType.BRANCH_START,
            branch_id=branch_id,
            root_branch_id=self.root_branch_id,
            branch_level=self.branch_level,
            position=self.position,
        )

        self.sequence.append(branch)
        return branch

    def _begin_next_branch_sequence(self) -> RungElement:
        """Begin a next branch in the rung sequence.
        """
        parent_branch = self._get_parent_branch()
        self._generate_new_branch_level_id()

        next_branch = RungElement(
            element_type=RungElementType.BRANCH_NEXT,
            branch_id=self.branch_id,
            root_branch_id=parent_branch.root_branch_id,
            branch_level=self.branch_level,
            position=self.position
        )

        self.sequence.append(next_branch)
        return next_branch

    def _begin_new_root_branch(
        self,
        new_branch_element: RungElement
    ) -> None:
        self.branch_root_id_history.append(self.root_branch_id)  # Save current root branch id
        self.root_branch_id = new_branch_element.branch_id  # Change branch id after assignment so we get the proper parent

    def _create_rung_branch(
        self,
        branch_element: RungElement
    ) -> RungBranch:
        branch = RungBranch(
            branch_id=branch_element.branch_id,
            root_branch_id=self.root_branch_id,
            start_position=self.position,
            end_position=-1,  # Will be updated later
            nested_branches=[],
        )
        self.branches[branch_element.branch_id] = branch
        return branch

    def _create_nested_branch(
        self,
    ) -> RungBranch:
        parent_branch = self._get_parent_branch()

        nested_branch = RungBranch(
            branch_id=self.branch_id,
            start_position=self.position,
            end_position=-1,
            root_branch_id=parent_branch.branch_id
        )

        parent_branch.nested_branches.append(nested_branch)
        self.branches[self.branch_id] = nested_branch
        return nested_branch

    def _finalize_active_branch(
        self,
    ) -> RungBranch:
        try:
            branch = self.branch_stack.pop()
        except IndexError:
            branch = None

        if not branch:
            raise ValueError("Branch end found without an active branch!")

        self.branches[branch.branch_id].end_position = self.position
        return branch

    def _finalize_root_branch(
        self,
        rung_branch: RungBranch
    ) -> None:
        self.root_branch_id = self.branch_root_id_history.pop()

        self.branch_id = self.branches[rung_branch.branch_id].root_branch_id
        self.branch_level = self.branch_level_history.pop()

    def _finalize_rung_branch(
        self,
        rung_branch: RungBranch
    ) -> None:

        branch_end = RungElement(
            element_type=RungElementType.BRANCH_END,
            branch_id=rung_branch.branch_id,
            root_branch_id=rung_branch.root_branch_id,
            branch_level=self.branch_level,
            position=self.position
        )

        self.sequence.append(branch_end)

    def _get_parent_branch(self) -> RungBranch:
        """Get the current parent branch from the stack.
        """
        if not self.branch_stack:
            raise ValueError("No active branch in stack!")

        return self.branch_stack[-1]

    def _generate_new_branch_level_id(self) -> None:
        """Generate a new branch level ID.
        """
        parent_branch = self._get_parent_branch()
        self.branch_level += 1
        self.branch_id = f'{parent_branch.branch_id}:{self.branch_level}'

    def _get_unique_branch_id(self) -> str:
        """Generate a unique branch ID."""
        branch_id = f"branch_{self.branch_id_counter}"
        self.branch_id_counter += 1
        return branch_id

    def _update_branch_end_position(
        self,
        branch: RungBranch,
        position: int
    ) -> None:
        """Update the end position of a branch.
        """
        self.branches[branch.branch_id].end_position = position

    def _update_nested_branch_end_position(
        self,
        branch: RungBranch,
        position: int
    ) -> None:
        """Update the end position of the last nested branch.
        """
        if not self.branches[branch.branch_id].nested_branches:
            raise ValueError("Branch has no nested branches; sequence is invalid! Expected ',' markers but none found.")

        end_nested_branch = self.branches[branch.branch_id].nested_branches[-1]
        if not end_nested_branch:
            raise ValueError("No nested branch found to update end position!")

        end_nested_branch.end_position = position

    def _process_branch_start(self) -> None:
        """Process a branch start token and update the rung sequence accordingly.
        """
        branch_element = self._begin_new_branch_sequence()
        branch = self._create_rung_branch(branch_element)
        self.branch_stack.append(branch)  # Tracking master branches
        self._begin_new_root_branch(branch_element)
        self.position += 1

    def _process_branch_end(self) -> None:
        """Process a branch end token and update the rung sequence accordingly.
        """
        branch = self._finalize_active_branch()
        self._update_nested_branch_end_position(branch, self.position - 1)
        self._finalize_root_branch(branch)
        self._finalize_rung_branch(branch)
        self.position += 1

    def _process_branch_next(self) -> None:
        """Process a next branch token and update the rung sequence accordingly.
        """
        branch_element = self._begin_next_branch_sequence()
        branch = self._create_rung_branch(branch_element)
        parent_branch = self._get_parent_branch()
        parent_branch.nested_branches.append(branch)
        self.position += 1

    def _process_instruction(self, token: str) -> None:
        """Process an instruction token and update the rung sequence accordingly.
        """
        if not token:
            raise ValueError("Empty instruction token encountered!")

        element = RungElement(
            element_type=RungElementType.INSTRUCTION,
            instruction=token,
            position=self.position,
            branch_id=self.branch_id,
            root_branch_id=self.root_branch_id,
            branch_level=self.branch_level
        )

        self.sequence.append(element)
        self.position += 1
        self.instruction_index += 1

    def _process_token(self, token: str) -> None:
        """Process a single token and update the rung sequence accordingly.
        """
        # Implementation would go here
        if token == '[':
            self._process_branch_start()
        elif token == ']':
            self._process_branch_end()
        elif token == ',':
            self._process_branch_next()
        else:
            self._process_instruction(token)

    def build_sequence(self) -> list[RungElement]:
        """Build the rung sequence from tokenized text.
        """
        self._init()
        for token in self.token_sequence:
            self._process_token(token)

        return self.sequence


class InstructionFactory(MetaFactory):
    pass


def extract_instruction_strings(
    text
) -> list[str]:
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
