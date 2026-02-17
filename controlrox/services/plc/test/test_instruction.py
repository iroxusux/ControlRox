"""Unit tests for controlrox.services.plc.instruction module."""
import unittest
from unittest.mock import Mock

from controlrox.interfaces.plc.rung import RungElement, RungElementType, RungBranch
from controlrox.services.plc.instruction import (
    InstructionSequenceBuilder,
    InstructionFactory,
    extract_instruction_strings,
)


# ============================================================================
# InstructionSequenceBuilder Initialization Tests
# ============================================================================

class TestInstructionSequenceBuilderInitialization(unittest.TestCase):
    """Test cases for InstructionSequenceBuilder initialization."""

    def test_init_with_token_sequence(self):
        """Test initialization with token sequence."""
        tokens = ['XIC(A)', 'OTE(B)']
        builder = InstructionSequenceBuilder(tokens)

        self.assertEqual(builder.token_sequence, tokens)
        self.assertEqual(builder.position, 0)
        self.assertEqual(builder.branch_id, '')
        self.assertEqual(builder.root_branch_id, '')
        self.assertEqual(len(builder.branch_stack), 0)
        self.assertEqual(builder.branch_counter, 0)
        self.assertEqual(builder.branch_id_counter, 0)
        self.assertEqual(builder.branch_level, 0)
        self.assertEqual(len(builder.sequence), 0)
        self.assertEqual(len(builder.branches), 0)

    def test_init_with_empty_sequence(self):
        """Test initialization with empty token sequence."""
        builder = InstructionSequenceBuilder([])

        self.assertEqual(len(builder.token_sequence), 0)
        self.assertEqual(builder.position, 0)

    def test_init_with_complex_sequence(self):
        """Test initialization with complex token sequence including branches."""
        tokens = ['XIC(A)', '[', 'XIC(B)', ',', 'XIC(C)', ']', 'OTE(D)']
        builder = InstructionSequenceBuilder(tokens)

        self.assertEqual(len(builder.token_sequence), 7)
        self.assertIsInstance(builder.branch_stack, list)
        self.assertIsInstance(builder.branches, dict)


# ============================================================================
# InstructionSequenceBuilder State Management Tests
# ============================================================================

class TestInstructionSequenceBuilderStateManagement(unittest.TestCase):
    """Test cases for InstructionSequenceBuilder state management."""

    def test_init_method_resets_state(self):
        """Test _init method resets all state variables."""
        builder = InstructionSequenceBuilder(['XIC(A)'])

        # Modify state
        builder.position = 10
        builder.branch_id = 'test_branch'
        builder.root_branch_id = 'root'
        builder.branch_counter = 5
        builder.branch_level = 3
        builder.instruction_index = 7
        builder.branch_stack.append(Mock())
        builder.branch_level_history.append(2)
        builder.branch_root_id_history.append('old_root')

        # Reset state
        builder._init()

        # Verify reset
        self.assertEqual(builder.position, 0)
        self.assertEqual(builder.branch_id, '')
        self.assertEqual(builder.root_branch_id, '')
        self.assertEqual(builder.branch_counter, 0)
        self.assertEqual(builder.branch_level, 0)
        self.assertEqual(builder.instruction_index, 0)
        self.assertEqual(len(builder.branch_stack), 0)
        self.assertEqual(len(builder.branch_level_history), 0)
        self.assertEqual(len(builder.branch_root_id_history), 0)

    def test_get_unique_branch_id_generates_unique_ids(self):
        """Test _get_unique_branch_id generates unique branch IDs."""
        builder = InstructionSequenceBuilder([])

        id1 = builder._get_unique_branch_id()
        id2 = builder._get_unique_branch_id()
        id3 = builder._get_unique_branch_id()

        self.assertNotEqual(id1, id2)
        self.assertNotEqual(id2, id3)
        self.assertIn('branch_0', id1)
        self.assertIn('branch_1', id2)
        self.assertIn('branch_2', id3)

    def test_get_unique_branch_id_increments_counter(self):
        """Test _get_unique_branch_id increments branch_id_counter."""
        builder = InstructionSequenceBuilder([])

        initial_counter = builder.branch_id_counter
        builder._get_unique_branch_id()

        self.assertEqual(builder.branch_id_counter, initial_counter + 1)


# ============================================================================
# InstructionSequenceBuilder Branch Management Tests
# ============================================================================

class TestInstructionSequenceBuilderBranchManagement(unittest.TestCase):
    """Test cases for branch management operations."""

    def test_get_parent_branch_with_empty_stack_raises_error(self):
        """Test _get_parent_branch raises ValueError when stack is empty."""
        builder = InstructionSequenceBuilder([])

        with self.assertRaises(ValueError) as context:
            builder._get_parent_branch()

        self.assertIn('No active branch in stack', str(context.exception))

    def test_get_parent_branch_returns_last_branch(self):
        """Test _get_parent_branch returns the last branch on stack."""
        builder = InstructionSequenceBuilder([])

        branch1 = RungBranch(
            branch_id='branch_0',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        branch2 = RungBranch(
            branch_id='branch_1',
            root_branch_id='',
            start_position=1,
            end_position=-1,
            nested_branches=[]
        )

        builder.branch_stack.append(branch1)
        builder.branch_stack.append(branch2)

        parent = builder._get_parent_branch()

        self.assertEqual(parent, branch2)

    def test_create_rung_branch(self):
        """Test _create_rung_branch creates and stores branch."""
        builder = InstructionSequenceBuilder([])

        branch_element = RungElement(
            element_type=RungElementType.BRANCH_START,
            branch_id='test_branch',
            root_branch_id='',
            branch_level=0,
            position=0
        )

        branch = builder._create_rung_branch(branch_element)

        self.assertIsNotNone(branch)
        self.assertEqual(branch.branch_id, 'test_branch')
        self.assertIn('test_branch', builder.branches)
        self.assertEqual(builder.branches['test_branch'], branch)

    def test_create_nested_branch(self):
        """Test _create_nested_branch creates nested branch."""
        builder = InstructionSequenceBuilder([])

        # Create parent branch
        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branch_stack.append(parent)
        builder.branch_id = 'nested_branch'

        nested = builder._create_nested_branch()

        self.assertIsNotNone(nested)
        self.assertEqual(nested.branch_id, 'nested_branch')
        self.assertEqual(nested.root_branch_id, 'parent')
        self.assertIn(nested, parent.nested_branches)
        self.assertIn('nested_branch', builder.branches)

    def test_update_branch_end_position(self):
        """Test _update_branch_end_position updates position."""
        builder = InstructionSequenceBuilder([])

        branch = RungBranch(
            branch_id='test_branch',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branches['test_branch'] = branch

        builder._update_branch_end_position(branch, 10)

        self.assertEqual(builder.branches['test_branch'].end_position, 10)

    def test_update_nested_branch_end_position(self):
        """Test _update_nested_branch_end_position updates nested branch."""
        builder = InstructionSequenceBuilder([])

        nested = RungBranch(
            branch_id='nested',
            root_branch_id='parent',
            start_position=1,
            end_position=-1,
            nested_branches=[]
        )
        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[nested]
        )
        builder.branches['parent'] = parent

        builder._update_nested_branch_end_position(parent, 5)

        self.assertEqual(nested.end_position, 5)

    def test_update_nested_branch_end_position_no_nested_raises_error(self):
        """Test _update_nested_branch_end_position raises error with no nested branches."""
        builder = InstructionSequenceBuilder([])

        branch = RungBranch(
            branch_id='branch',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branches['branch'] = branch

        with self.assertRaises(ValueError) as context:
            builder._update_nested_branch_end_position(branch, 5)

        self.assertIn('no nested branches', str(context.exception))


# ============================================================================
# InstructionSequenceBuilder Branch Sequence Tests
# ============================================================================

class TestInstructionSequenceBuilderBranchSequence(unittest.TestCase):
    """Test cases for branch sequence operations."""

    def test_begin_new_branch_sequence(self):
        """Test _begin_new_branch_sequence creates branch element."""
        builder = InstructionSequenceBuilder([])
        builder.position = 5

        branch_element = builder._begin_new_branch_sequence()

        self.assertIsNotNone(branch_element)
        self.assertEqual(branch_element.element_type, RungElementType.BRANCH_START)
        self.assertIn(branch_element, builder.sequence)
        self.assertEqual(builder.branch_counter, 1)

    def test_begin_next_branch_sequence(self):
        """Test _begin_next_branch_sequence creates next branch element."""
        builder = InstructionSequenceBuilder([])

        # Set up parent branch
        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branch_stack.append(parent)
        builder.branches['parent'] = parent

        next_element = builder._begin_next_branch_sequence()

        self.assertIsNotNone(next_element)
        self.assertEqual(next_element.element_type, RungElementType.BRANCH_NEXT)
        self.assertEqual(next_element.branch_id, 'parent:1')
        self.assertIn(next_element, builder.sequence)

    def test_begin_new_root_branch(self):
        """Test _begin_new_root_branch updates root branch tracking."""
        builder = InstructionSequenceBuilder([])
        builder.root_branch_id = 'old_root'

        branch_element = RungElement(
            element_type=RungElementType.BRANCH_START,
            branch_id='new_root',
            root_branch_id='',
            branch_level=0,
            position=0
        )

        builder._begin_new_root_branch(branch_element)

        self.assertEqual(builder.root_branch_id, 'new_root')
        self.assertIn('old_root', builder.branch_root_id_history)

    def test_finalize_active_branch(self):
        """Test _finalize_active_branch removes and updates branch."""
        builder = InstructionSequenceBuilder([])

        branch = RungBranch(
            branch_id='test_branch',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branch_stack.append(branch)
        builder.branches['test_branch'] = branch
        builder.position = 5

        finalized = builder._finalize_active_branch()

        self.assertEqual(finalized, branch)
        self.assertEqual(len(builder.branch_stack), 0)
        self.assertEqual(builder.branches['test_branch'].end_position, 5)

    def test_finalize_active_branch_empty_stack_raises_error(self):
        """Test _finalize_active_branch raises error with empty stack."""
        builder = InstructionSequenceBuilder([])

        with self.assertRaises(ValueError) as context:
            builder._finalize_active_branch()

        self.assertIn('Branch end found without an active branch', str(context.exception))

    def test_finalize_root_branch(self):
        """Test _finalize_root_branch restores previous state."""
        builder = InstructionSequenceBuilder([])

        nested = RungBranch(
            branch_id='nested',
            root_branch_id='parent',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[nested]
        )

        builder.branches['parent'] = parent
        builder.branches['nested'] = nested
        builder.root_branch_id = 'nested'
        builder.branch_root_id_history.append('')
        builder.branch_level = 1
        builder.branch_level_history.append(0)

        builder._finalize_root_branch(nested)

        self.assertEqual(builder.root_branch_id, '')
        self.assertEqual(builder.branch_id, 'parent')
        self.assertEqual(builder.branch_level, 0)

    def test_finalize_rung_branch(self):
        """Test _finalize_rung_branch adds branch end element."""
        builder = InstructionSequenceBuilder([])
        builder.position = 10

        branch = RungBranch(
            branch_id='test_branch',
            root_branch_id='',
            start_position=0,
            end_position=10,
            nested_branches=[]
        )

        builder._finalize_rung_branch(branch)

        self.assertGreater(len(builder.sequence), 0)
        last_element = builder.sequence[-1]
        self.assertEqual(last_element.element_type, RungElementType.BRANCH_END)
        self.assertEqual(last_element.branch_id, 'test_branch')

    def test_begin_new_branch_level(self):
        """Test _begin_new_branch_level updates branch level."""
        builder = InstructionSequenceBuilder([])

        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branch_stack.append(parent)
        initial_level = builder.branch_level

        builder._begin_new_branch_level()

        self.assertEqual(builder.branch_level, initial_level + 1)
        self.assertIn('parent:', builder.branch_id)


# ============================================================================
# InstructionSequenceBuilder Token Processing Tests
# ============================================================================

class TestInstructionSequenceBuilderTokenProcessing(unittest.TestCase):
    """Test cases for token processing operations."""

    def test_process_instruction_creates_element(self):
        """Test _process_instruction creates instruction element."""
        builder = InstructionSequenceBuilder([])
        builder.position = 0

        builder._process_instruction('XIC(A)')

        self.assertEqual(len(builder.sequence), 1)
        element = builder.sequence[0]
        self.assertEqual(element.element_type, RungElementType.INSTRUCTION)
        self.assertEqual(element.instruction, 'XIC(A)')
        self.assertEqual(builder.position, 1)
        self.assertEqual(builder.instruction_index, 1)

    def test_process_instruction_empty_token_raises_error(self):
        """Test _process_instruction raises error with empty token."""
        builder = InstructionSequenceBuilder([])

        with self.assertRaises(ValueError) as context:
            builder._process_instruction('')

        self.assertIn('Empty instruction token', str(context.exception))

    def test_process_branch_start(self):
        """Test _process_branch_start handles branch opening."""
        builder = InstructionSequenceBuilder([])
        builder.position = 0

        builder._process_branch_start()

        self.assertEqual(len(builder.sequence), 1)
        self.assertEqual(builder.sequence[0].element_type, RungElementType.BRANCH_START)
        self.assertEqual(len(builder.branch_stack), 1)
        self.assertEqual(builder.position, 1)

    def test_process_branch_end(self):
        """Test _process_branch_end handles branch closing."""
        builder = InstructionSequenceBuilder([])

        # Set up a branch to close
        branch = RungBranch(
            branch_id='test_branch',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[
                RungBranch(
                    branch_id='nested',
                    root_branch_id='test_branch',
                    start_position=1,
                    end_position=-1,
                    nested_branches=[]
                )
            ]
        )
        builder.branch_stack.append(branch)
        builder.branches['test_branch'] = branch
        builder.branch_level_history.append(0)
        builder.branch_root_id_history.append('')
        builder.position = 5

        builder._process_branch_end()

        self.assertEqual(len(builder.branch_stack), 0)
        self.assertEqual(builder.position, 6)

    def test_process_next_branch(self):
        """Test _process_next_branch handles branch comma separator."""
        builder = InstructionSequenceBuilder([])

        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branch_stack.append(parent)
        builder.branches['parent'] = parent
        builder.position = 3

        builder._process_branch_next()

        self.assertGreater(len(builder.sequence), 0)
        self.assertEqual(builder.position, 4)
        self.assertGreater(len(parent.nested_branches), 0)

    def test_process_token_instruction(self):
        """Test _process_token routes instruction correctly."""
        builder = InstructionSequenceBuilder([])

        builder._process_token('XIC(A)')

        self.assertEqual(len(builder.sequence), 1)
        self.assertEqual(builder.sequence[0].element_type, RungElementType.INSTRUCTION)

    def test_process_token_branch_start(self):
        """Test _process_token routes '[' to branch start."""
        builder = InstructionSequenceBuilder([])

        builder._process_token('[')

        self.assertEqual(len(builder.sequence), 1)
        self.assertEqual(builder.sequence[0].element_type, RungElementType.BRANCH_START)

    def test_process_token_branch_end(self):
        """Test _process_token routes ']' to branch end."""
        builder = InstructionSequenceBuilder([])

        # Set up branch to close
        branch = RungBranch(
            branch_id='test',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[Mock()]
        )
        builder.branch_stack.append(branch)
        builder.branches['test'] = branch
        builder.branch_level_history.append(0)
        builder.branch_root_id_history.append('')

        builder._process_token(']')

        # Should have branch end element
        self.assertTrue(any(e.element_type == RungElementType.BRANCH_END for e in builder.sequence))

    def test_process_token_comma(self):
        """Test _process_token routes ',' to next branch."""
        builder = InstructionSequenceBuilder([])

        parent = RungBranch(
            branch_id='parent',
            root_branch_id='',
            start_position=0,
            end_position=-1,
            nested_branches=[]
        )
        builder.branch_stack.append(parent)
        builder.branches['parent'] = parent

        builder._process_token(',')

        # Should have branch next element
        self.assertTrue(any(e.element_type == RungElementType.BRANCH_NEXT for e in builder.sequence))


# ============================================================================
# InstructionSequenceBuilder Build Sequence Tests
# ============================================================================

class TestInstructionSequenceBuilderBuildSequence(unittest.TestCase):
    """Test cases for building complete sequences."""

    def test_build_sequence_simple_instructions(self):
        """Test build_sequence with simple instruction tokens."""
        tokens = ['XIC(A)', 'XIC(B)', 'OTE(C)']
        builder = InstructionSequenceBuilder(tokens)

        sequence = builder.build_sequence()

        self.assertEqual(len(sequence), 3)
        self.assertTrue(all(e.element_type == RungElementType.INSTRUCTION for e in sequence))

    def test_build_sequence_with_single_branch(self):
        """Test build_sequence with single branch."""
        tokens = ['XIC(A)', '[', 'XIC(B)', ',', 'XIC(C)', ']', 'OTE(D)']
        builder = InstructionSequenceBuilder(tokens)

        sequence = builder.build_sequence()

        self.assertGreater(len(sequence), 4)
        # Should have branch start, instructions, branch next, and branch end
        element_types = [e.element_type for e in sequence]
        self.assertIn(RungElementType.BRANCH_START, element_types)
        self.assertIn(RungElementType.BRANCH_NEXT, element_types)
        self.assertIn(RungElementType.BRANCH_END, element_types)

    def test_build_sequence_with_nested_branches(self):
        """Test build_sequence with nested branches."""
        tokens = ['[', '[', 'XIC(A)', ',', 'XIC(B)', ']', ',', 'XIC(C)' ']', 'OTE(D)']
        builder = InstructionSequenceBuilder(tokens)

        sequence = builder.build_sequence()

        # Should have multiple branch levels
        self.assertGreater(len(sequence), 5)
        branch_starts = sum(1 for e in sequence if e.element_type == RungElementType.BRANCH_START)
        self.assertGreaterEqual(branch_starts, 2)

    def test_build_sequence_empty_token_list(self):
        """Test build_sequence with empty token list."""
        builder = InstructionSequenceBuilder([])

        sequence = builder.build_sequence()

        self.assertEqual(len(sequence), 0)

    def test_build_sequence_resets_state(self):
        """Test build_sequence resets state before building."""
        builder = InstructionSequenceBuilder(['XIC(A)'])

        # First build
        builder.build_sequence()

        # Modify state
        builder.position = 100

        # Second build should reset
        sequence = builder.build_sequence()

        # Position should have been reset during _init
        self.assertEqual(len(sequence), 1)

    def test_build_sequence_tracks_branches(self):
        """Test build_sequence properly tracks branches in dict."""
        tokens = ['XIC(A)', '[', 'XIC(B)', ',', 'XIC(C)', ']', 'OTE(D)']
        builder = InstructionSequenceBuilder(tokens)

        builder.build_sequence()

        # Should have branches stored
        self.assertGreater(len(builder.branches), 0)
        for branch_id, branch in builder.branches.items():
            self.assertIsInstance(branch, RungBranch)
            self.assertEqual(branch.branch_id, branch_id)


# ============================================================================
# Extract Instruction Strings Tests
# ============================================================================

class TestExtractInstructionStrings(unittest.TestCase):
    """Test cases for extract_instruction_strings function."""

    def test_extract_simple_instructions(self):
        """Test extracting simple instructions."""
        text = 'XIC(TagA)XIO(TagB)OTE(Output);'

        result = extract_instruction_strings(text)

        self.assertEqual(len(result), 3)
        self.assertIn('XIC(TagA)', result)
        self.assertIn('XIO(TagB)', result)
        self.assertIn('OTE(Output)', result)

    def test_extract_instructions_with_nested_parentheses(self):
        """Test extracting instructions with nested parentheses."""
        text = 'MOV(Source,Dest)ADD(Value(1),Result);'

        result = extract_instruction_strings(text)

        self.assertGreater(len(result), 0)
        # Should handle nested parentheses
        self.assertTrue(any('MOV' in instr for instr in result))

    def test_extract_instructions_with_array_subscripts(self):
        """Test extracting instructions with array subscripts."""
        text = 'XIC(Array[0])OTE(Output[Index]);'

        result = extract_instruction_strings(text)

        self.assertEqual(len(result), 2)
        self.assertIn('XIC(Array[0])', result)
        self.assertIn('OTE(Output[Index])', result)

    def test_extract_instructions_empty_text(self):
        """Test extracting from empty text."""
        result = extract_instruction_strings('')

        self.assertEqual(len(result), 0)

    def test_extract_instructions_no_parentheses(self):
        """Test extracting from text with no instructions."""
        text = 'Just some text without instructions'

        result = extract_instruction_strings(text)

        self.assertEqual(len(result), 0)

    def test_extract_instructions_unmatched_parentheses(self):
        """Test extracting with unmatched opening parentheses."""
        text = 'XIC(TagA'

        result = extract_instruction_strings(text)

        # Should not include incomplete instruction
        self.assertEqual(len(result), 0)

    def test_extract_instructions_complex_operands(self):
        """Test extracting instructions with complex operands."""
        text = 'ADD(Tag.Value,10,Result.Output)MUL(A,B,C);'

        result = extract_instruction_strings(text)

        self.assertGreater(len(result), 0)
        self.assertTrue(any('ADD' in instr for instr in result))
        self.assertTrue(any('MUL' in instr for instr in result))

    def test_extract_instructions_with_underscores(self):
        """Test extracting instructions with underscores in names."""
        text = 'CUSTOM_INST(Tag_1,Tag_2)MY_FUNCTION(Value);'

        result = extract_instruction_strings(text)

        self.assertGreater(len(result), 0)
        self.assertTrue(any('CUSTOM_INST' in instr for instr in result))
        self.assertTrue(any('MY_FUNCTION' in instr for instr in result))

    def test_extract_instructions_with_numbers(self):
        """Test extracting instructions with numbers in names."""
        text = 'INST123(Tag)FUNC456(Value);'

        result = extract_instruction_strings(text)

        self.assertGreater(len(result), 0)
        self.assertTrue(any('INST123' in instr for instr in result))
        self.assertTrue(any('FUNC456' in instr for instr in result))

    def test_extract_instructions_preserves_order(self):
        """Test extracting preserves instruction order."""
        text = 'FIRST(A)SECOND(B)THIRD(C);'

        result = extract_instruction_strings(text)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'FIRST(A)')
        self.assertEqual(result[1], 'SECOND(B)')
        self.assertEqual(result[2], 'THIRD(C)')

    def test_extract_instructions_with_whitespace(self):
        """Test extracting instructions with whitespace."""
        text = 'XIC( Tag1 ) OTE( Tag2 );'

        result = extract_instruction_strings(text)

        self.assertGreater(len(result), 0)
        # Should extract despite whitespace
        self.assertTrue(any('XIC' in instr for instr in result))

    def test_extract_instructions_multiple_nested_levels(self):
        """Test extracting with multiple nested parentheses levels."""
        text = 'FUNC(A(B(C)),D(E));'

        result = extract_instruction_strings(text)

        # Should handle deep nesting
        self.assertGreater(len(result), 0)


# ============================================================================
# InstructionFactory Tests
# ============================================================================

class TestInstructionFactory(unittest.TestCase):
    """Test cases for InstructionFactory class."""

    def test_instruction_factory_exists(self):
        """Test InstructionFactory class exists."""
        self.assertIsNotNone(InstructionFactory)

    def test_instruction_factory_inherits_from_metafactory(self):
        """Test InstructionFactory inherits from MetaFactory."""
        from pyrox.models.factory import MetaFactory
        self.assertTrue(issubclass(InstructionFactory, MetaFactory))

    def test_instruction_factory_instantiation(self):
        """Test InstructionFactory has factory capabilities."""
        # InstructionFactory uses MetaFactory as metaclass, providing factory methods
        # Verify the factory methods are available
        self.assertTrue(hasattr(InstructionFactory, 'create_instance'))
        self.assertTrue(hasattr(InstructionFactory, 'get_registered_types'))
        self.assertTrue(hasattr(InstructionFactory, 'register_type'))
        self.assertTrue(callable(getattr(InstructionFactory, 'create_instance')))


# ============================================================================
# Integration Tests
# ============================================================================

class TestInstructionIntegration(unittest.TestCase):
    """Integration test cases for instruction processing."""

    def test_extract_and_build_sequence_simple(self):
        """Test extracting instructions and building sequence."""
        text = 'XIC(A)XIC(B)OTE(C);'

        # Extract instructions
        instructions = extract_instruction_strings(text)

        # Build sequence
        builder = InstructionSequenceBuilder(instructions)
        sequence = builder.build_sequence()

        self.assertEqual(len(instructions), 3)
        self.assertEqual(len(sequence), 3)
        self.assertTrue(all(e.element_type == RungElementType.INSTRUCTION for e in sequence))

    def test_extract_and_build_sequence_with_branches(self):
        """Test extracting and building with branches."""
        # First extract instructions (without branch markers)
        text = 'XIC(A)XIC(B)XIC(C)OTE(D);'
        instructions = extract_instruction_strings(text)

        # Add branch markers manually
        tokens = [instructions[0], '[', instructions[1], ',', instructions[2], ']', instructions[3]]

        # Build sequence
        builder = InstructionSequenceBuilder(tokens)
        sequence = builder.build_sequence()

        # Should have instructions plus branch elements
        self.assertGreater(len(sequence), len(instructions))
        element_types = [e.element_type for e in sequence]
        self.assertIn(RungElementType.BRANCH_START, element_types)
        self.assertIn(RungElementType.BRANCH_END, element_types)

    def test_complete_workflow_nested_branches(self):
        """Test complete workflow with nested branches."""
        # Extract base instructions
        text = 'XIC(Start)XIC(Flag1)XIC(Flag2)XIC(Flag3)OTE(Output);'
        instructions = extract_instruction_strings(text)

        # Build complex nested structure
        tokens = [
            instructions[0],  # XIC(Start)
            '[',
            '[',
            instructions[1],  # XIC(Flag1)
            ',',
            instructions[2],  # XIC(Flag2)
            ']',
            ',',
            instructions[3],  # XIC(Flag3)
            ']',
            instructions[4],  # OTE(Output)
        ]

        builder = InstructionSequenceBuilder(tokens)
        sequence = builder.build_sequence()

        # Verify structure
        self.assertGreater(len(sequence), len(instructions))
        self.assertGreater(len(builder.branches), 0)

        # Check for nested branches
        branch_starts = sum(1 for e in sequence if e.element_type == RungElementType.BRANCH_START)
        self.assertGreaterEqual(branch_starts, 2)

    def test_workflow_with_multiple_branches(self):
        """Test workflow with multiple separate branches."""
        text = 'XIC(A)XIC(B)XIC(C)XIC(D)OTE(E);'
        instructions = extract_instruction_strings(text)

        # Two branches: [XIC(B)] and [XIC(D)]
        tokens = [
            instructions[0],  # XIC(A)
            '[',
            instructions[1],  # XIC(B)
            ',',
            instructions[1],  # XIC(B)
            ']',
            instructions[2],  # XIC(C)
            '[',
            instructions[3],  # XIC(D)
            ',',
            instructions[3],  # XIC(D)
            ']',
            instructions[4],  # OTE(E)
        ]

        builder = InstructionSequenceBuilder(tokens)
        sequence = builder.build_sequence()

        # Should have multiple branches tracked
        self.assertGreaterEqual(len(builder.branches), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
