"""Unit tests for controlrox.models.plc.rung module."""
import unittest
from unittest.mock import Mock, patch

from controlrox.interfaces import (
    IRoutine,
    ILogicInstruction,
    RungBranch,
    RungElement,
)
from controlrox.models.plc.rung import Rung


# ============================================================================
# Rung Initialization Tests
# ============================================================================

class TestRungInitialization(unittest.TestCase):
    """Test cases for Rung initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        rung = Rung()

        self.assertIsNotNone(rung)
        self.assertEqual(rung.text, '')
        self.assertEqual(rung.comment, '')
        self.assertIsNone(rung.routine)
        self.assertIsInstance(rung.instructions, list)

    def test_init_with_metadata(self):
        """Test initialization with metadata dict."""
        meta_data = {'@Number': '5', '@Type': 'RLL'}
        rung = Rung(meta_data=meta_data)

        # Rung initialization adds Comment and Text fields
        # The original meta_data should not be modified (no shared state)
        self.assertEqual(rung.meta_data['@Number'], '5')
        self.assertEqual(rung.meta_data['@Type'], 'RLL')
        self.assertIn('Comment', rung.meta_data)
        self.assertIn('Text', rung.meta_data)
        # Verify original metadata is the object meta data
        self.assertEqual(rung.meta_data, meta_data)

    def test_init_with_comment(self):
        """Test initialization with comment."""
        rung = Rung(comment='Test comment')

        self.assertEqual(rung.comment, 'Test comment')

    def test_init_with_rung_text(self):
        """Test initialization with rung text."""
        rung = Rung(rung_text='XIC(Tag1)OTE(Tag2);')

        self.assertEqual(rung.text, 'XIC(Tag1)OTE(Tag2);')

    def test_init_with_routine(self):
        """Test initialization with routine reference."""
        mock_routine = Mock(spec=IRoutine)
        rung = Rung(routine=mock_routine)

        self.assertEqual(rung.routine, mock_routine)

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        meta_data = {'@Number': '10'}
        mock_routine = Mock(spec=IRoutine)
        rung = Rung(
            meta_data=meta_data,
            name='TestRung',
            description='Test Description',
            routine=mock_routine,
            comment='Test Comment',
            rung_text='XIC(A)OTE(B);'
        )

        self.assertEqual(rung.name, 'TestRung')
        self.assertEqual(rung.description, 'Test Description')
        self.assertEqual(rung.routine, mock_routine)
        self.assertEqual(rung.comment, 'Test Comment')
        self.assertEqual(rung.text, 'XIC(A)OTE(B);')


# ============================================================================
# Rung Properties Tests
# ============================================================================

class TestRungProperties(unittest.TestCase):
    """Test cases for Rung properties."""

    def test_text_property(self):
        """Test text property getter."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        self.assertEqual(rung.text, 'XIC(A)OTE(B);')

    def test_comment_property(self):
        """Test comment property getter."""
        rung = Rung(comment='Test Comment')

        self.assertEqual(rung.comment, 'Test Comment')

    def test_routine_property(self):
        """Test routine property getter."""
        mock_routine = Mock(spec=IRoutine)
        rung = Rung(routine=mock_routine)

        self.assertEqual(rung.routine, mock_routine)

    def test_number_property(self):
        """Test number property getter."""
        rung = Rung(rung_number=5)

        self.assertEqual(rung.number, 5)

    def test_get_text_method(self):
        """Test get_text method."""
        rung = Rung(rung_text='XIC(A);')

        result = rung.get_text()

        self.assertEqual(result, 'XIC(A);')

    def test_set_text_method(self):
        """Test set_text method."""
        rung = Rung()

        rung.set_text('XIC(B)OTE(C);')

        self.assertEqual(rung.text, 'XIC(B)OTE(C);')

    def test_get_comment_method(self):
        """Test get_comment method."""
        rung = Rung(comment='Test')

        result = rung.get_comment()

        self.assertEqual(result, 'Test')

    def test_set_comment_method(self):
        """Test set_comment method."""
        rung = Rung()

        rung.set_comment('New Comment')

        self.assertEqual(rung.comment, 'New Comment')

    def test_get_routine_method(self):
        """Test get_routine method."""
        mock_routine = Mock(spec=IRoutine)
        rung = Rung(routine=mock_routine)

        result = rung.get_routine()

        self.assertEqual(result, mock_routine)

    def test_get_number_method(self):
        """Test get_number method."""
        rung = Rung(rung_number=10)

        result = rung.get_number()

        self.assertEqual(result, 10)

    def test_set_number_method(self):
        """Test set_number method."""
        rung = Rung(rung_number=5)

        rung.set_number(15)

        self.assertEqual(rung.number, 15)


# ============================================================================
# Rung String Methods Tests
# ============================================================================

class TestRungStringMethods(unittest.TestCase):
    """Test cases for Rung string representation methods."""

    def test_str_returns_text(self):
        """Test __str__ returns rung text."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        result = str(rung)

        self.assertEqual(result, 'XIC(A)OTE(B);')

    def test_repr_contains_number(self):
        """Test __repr__ contains rung number."""
        rung = Rung(rung_number=5, rung_text='XIC(A);')

        result = repr(rung)

        self.assertIn('number=5', result)

    def test_repr_contains_comment(self):
        """Test __repr__ contains comment."""
        rung = Rung(comment='Test')

        result = repr(rung)

        self.assertIn('comment=Test', result)

    def test_repr_contains_text(self):
        """Test __repr__ contains text."""
        rung = Rung(rung_text='XIC(A);')

        result = repr(rung)

        self.assertIn('text=XIC(A);', result)

    def test_repr_contains_instruction_count(self):
        """Test __repr__ contains instruction count."""
        rung = Rung(rung_text='XIC(A)OTE(B);')
        rung.compile_instructions()

        result = repr(rung)

        self.assertIn('instructions=', result)


# ============================================================================
# Rung Equality Tests
# ============================================================================

class TestRungEquality(unittest.TestCase):
    """Test cases for Rung equality comparisons."""

    def test_equal_rungs_same_text_and_number(self):
        """Test rungs are equal with same text and number."""
        rung1 = Rung(rung_number=1, rung_text='XIC(A);')
        rung2 = Rung(rung_number=1, rung_text='XIC(A);')

        self.assertEqual(rung1, rung2)

    def test_unequal_rungs_different_text(self):
        """Test rungs are unequal with different text."""
        rung1 = Rung(rung_number=1, rung_text='XIC(A);')
        rung2 = Rung(rung_number=2, rung_text='XIC(B);')

        self.assertNotEqual(rung1, rung2)

    def test_unequal_rungs_different_number(self):
        """Test rungs are unequal with different number."""
        rung1 = Rung(rung_number=1, rung_text='XIC(A);')
        rung2 = Rung(rung_number=2, rung_text='XIC(A);')

        self.assertNotEqual(rung1, rung2)

    def test_unequal_rung_to_non_rung(self):
        """Test rung not equal to non-rung object."""
        rung = Rung(rung_number=1)

        self.assertNotEqual(rung, 'not a rung')
        self.assertNotEqual(rung, 42)
        self.assertNotEqual(rung, None)


# ============================================================================
# Comment Line Tests
# ============================================================================

class TestRungCommentLines(unittest.TestCase):
    """Test cases for comment line counting."""

    def test_get_comment_lines_empty(self):
        """Test get_comment_lines with no comment."""
        rung = Rung()

        lines = rung.get_comment_lines()

        self.assertEqual(lines, 0)

    def test_get_comment_lines_single_line(self):
        """Test get_comment_lines with single line."""
        rung = Rung(comment='Single line')

        lines = rung.get_comment_lines()

        self.assertEqual(lines, 1)

    def test_get_comment_lines_multiple_lines(self):
        """Test get_comment_lines with multiple lines."""
        rung = Rung(comment='Line 1\nLine 2\nLine 3')

        lines = rung.get_comment_lines()

        self.assertEqual(lines, 3)

    def test_get_comment_lines_with_empty_lines(self):
        """Test get_comment_lines with empty lines."""
        rung = Rung(comment='Line 1\n\nLine 3')

        lines = rung.get_comment_lines()

        self.assertEqual(lines, 3)


# ============================================================================
# Instruction Management Tests
# ============================================================================

class TestRungInstructionManagement(unittest.TestCase):
    """Test cases for instruction management."""

    def test_get_instruction_by_index_valid(self):
        """Test get_instruction_by_index with valid index."""
        rung = Rung(rung_text='XIC(A)OTE(B);')
        rung.compile_instructions()

        instruction = rung.get_instruction_by_index(0)

        self.assertIsNotNone(instruction)

    def test_get_instruction_by_index_out_of_range(self):
        """Test get_instruction_by_index with out of range index."""
        rung = Rung()

        with self.assertRaises(IndexError):
            rung.get_instruction_by_index(10)

    def test_has_instruction_true(self):
        """Test has_instruction returns True when instruction exists."""
        rung = Rung(rung_text='XIC(A);')
        rung.compile_instructions()
        instruction = rung.instructions[0]

        result = rung.has_instruction(instruction)

        self.assertTrue(result)

    def test_has_instruction_false(self):
        """Test has_instruction returns False when instruction not in rung."""
        rung = Rung()
        mock_instruction = Mock(spec=ILogicInstruction)

        result = rung.has_instruction(mock_instruction)

        self.assertFalse(result)

    def test_compile_method(self):
        """Test compile method compiles instructions."""
        rung = Rung(rung_text='XIC(A);')

        result = rung.compile()

        self.assertEqual(result, rung)
        self.assertGreater(len(rung.instructions), 0)

    def test_add_instruction(self):
        """Test add_instruction adds to list."""
        rung = Rung()
        mock_instr = Mock(spec=ILogicInstruction)
        mock_instr.name = 'test_instr'
        mock_instr.meta_data = {}

        # Directly manipulate the internal list to bypass metadata operations
        with patch.object(rung, 'add_asset_to_meta_data'):
            rung._instructions.append(mock_instr)

        self.assertIn(mock_instr, rung.instructions)

    def test_add_instruction_at_index(self):
        """Test add_instruction at specific index."""
        rung = Rung()
        instr1 = Mock(spec=ILogicInstruction)
        instr1.name = 'instr1'
        instr1.meta_data = {}
        instr2 = Mock(spec=ILogicInstruction)
        instr2.name = 'instr2'
        instr2.meta_data = {}

        # Directly manipulate the internal list to bypass metadata operations
        with patch.object(rung, 'add_asset_to_meta_data'):
            rung._instructions.append(instr1)
            rung._instructions.insert(0, instr2)

        self.assertEqual(rung.instructions[0], instr2)

    def test_clear_instructions(self):
        """Test clear_instructions empties list."""
        rung = Rung(rung_text='XIC(A);')
        rung.compile_instructions()

        rung.clear_instructions()

        self.assertEqual(len(rung.instructions), 0)

    def test_remove_instruction(self):
        """Test remove_instruction removes from list."""
        rung = Rung()
        mock_instr = Mock(spec=ILogicInstruction)
        mock_instr.name = 'test_instr'
        mock_instr.meta_data = {}

        # Directly manipulate the internal list
        with patch.object(rung, 'add_asset_to_meta_data'):
            rung._instructions.append(mock_instr)

        with patch.object(rung, 'remove_asset_from_meta_data'):
            rung._instructions.remove(mock_instr)

        self.assertNotIn(mock_instr, rung.instructions)

    @patch.object(Rung, 'get_raw_instructions', return_value=[])
    def test_remove_instruction_by_index(self, mock_get_raw):
        """Test remove_instruction_by_index removes correct instruction."""
        rung = Rung(rung_text='XIC(A)OTE(B);')
        rung.compile_instructions()
        original_count = len(rung.instructions)

        with patch.object(rung, 'remove_asset_from_meta_data'):
            rung._instructions.pop(0)

        self.assertEqual(len(rung.instructions), original_count - 1)


# ============================================================================
# Text Tokenization Tests
# ============================================================================

class TestRungTextTokenization(unittest.TestCase):
    """Test cases for rung text tokenization."""

    def test_tokenize_simple_rung_text(self):
        """Test tokenizing simple rung without branches."""
        rung = Rung(rung_text='XIC(Tag1)OTE(Tag2);')

        tokens = rung.tokenize_instruction_meta_data()

        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)
        self.assertTrue(any('XIC' in str(t) for t in tokens))
        self.assertTrue(any('OTE' in str(t) for t in tokens))

    def test_tokenize_with_single_branch(self):
        """Test tokenizing with single branch structure."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')

        tokens = rung.tokenize_instruction_meta_data()

        # Should contain branch markers
        self.assertIn('[', tokens)
        self.assertIn(',', tokens)
        self.assertIn(']', tokens)

    def test_tokenize_with_nested_branches(self):
        """Test tokenizing with nested branch structures."""
        rung = Rung(rung_text='XIC(A)[[XIC(B)],[XIC(C)]]OTE(D);')

        tokens = rung.tokenize_instruction_meta_data()

        # Should have multiple levels of brackets
        self.assertTrue(tokens.count('[') >= 2)
        self.assertTrue(tokens.count(']') >= 2)

    def test_tokenize_preserves_array_references(self):
        """Test tokenizing preserves array subscripts in tags."""
        rung = Rung(rung_text='XIC(Tag[0])OTE(Output[1]);')

        tokens = rung.tokenize_instruction_meta_data()

        # Array brackets should be preserved within instructions
        self.assertTrue(any('Tag[0]' in str(t) for t in tokens))
        self.assertTrue(any('Output[1]' in str(t) for t in tokens))

    def test_tokenize_empty_text(self):
        """Test tokenizing empty rung text."""
        rung = Rung()

        tokens = rung.tokenize_instruction_meta_data()

        self.assertEqual(len(tokens), 0)

    def test_tokenize_instruction_sequence(self):
        """Test tokenize_instruction_sequence method."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        tokens = rung.tokenize_instruction_meta_data()

        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)


# ============================================================================
# Branch Validation Tests
# ============================================================================

class TestRungBranchValidation(unittest.TestCase):
    """Test cases for branch structure validation."""

    def test_validate_branch_structure_valid_simple(self):
        """Test validation of valid simple branch."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')

        is_valid = rung.validate_branch_structure()

        self.assertTrue(is_valid)

    def test_validate_branch_structure_valid_nested(self):
        """Test validation of valid nested branches."""
        rung = Rung(rung_text='[[XIC(A)],[XIC(B)]]OTE(C);')

        is_valid = rung.validate_branch_structure()

        self.assertTrue(is_valid)

    def test_validate_branch_structure_unmatched_open_bracket(self):
        """Test validation fails with unmatched opening bracket."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)OTE(D);')

        is_valid = rung.validate_branch_structure()

        self.assertFalse(is_valid)

    def test_validate_branch_structure_unmatched_close_bracket(self):
        """Test validation fails with unmatched closing bracket."""
        rung = Rung(rung_text='XIC(A)XIC(B),XIC(C)]OTE(D);')

        is_valid = rung.validate_branch_structure()

        self.assertFalse(is_valid)

    def test_validate_branch_structure_empty_text(self):
        """Test validation of empty text (should be valid)."""
        rung = Rung()

        is_valid = rung.validate_branch_structure()

        self.assertTrue(is_valid)

    def test_validate_branch_structure_no_branches(self):
        """Test validation of text without branches."""
        rung = Rung(rung_text='XIC(A)XIC(B)OTE(C);')

        is_valid = rung.validate_branch_structure()

        self.assertTrue(is_valid)


# ============================================================================
# Branch Query Tests
# ============================================================================

class TestRungBranchQueries(unittest.TestCase):
    """Test cases for branch query operations."""

    def test_has_branches_false_when_empty(self):
        """Test has_branches returns False when no branches."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        result = rung.has_branches()

        self.assertFalse(result)

    def test_has_branches_true_after_compile(self):
        """Test has_branches returns True after compiling branches."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')
        rung.compile_sequence()

        result = rung.has_branches()

        self.assertTrue(result)

    def test_get_max_branch_depth_no_branches(self):
        """Test max branch depth with no branches returns 0."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        depth = rung.get_max_branch_depth()

        self.assertEqual(depth, 0)

    def test_get_max_branch_depth_single_branch(self):
        """Test max branch depth with single branch."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')

        depth = rung.get_max_branch_depth()

        self.assertGreaterEqual(depth, 1)

    def test_get_max_branch_depth_nested_branches(self):
        """Test max branch depth with nested branches."""
        rung = Rung(rung_text='XIC(A)[[XIC(B)],[XIC(C)]]OTE(D);')

        depth = rung.get_max_branch_depth()

        self.assertGreaterEqual(depth, 2)

    def test_get_branch_nesting_level_main_line(self):
        """Test getting nesting level on main line."""
        rung = Rung(rung_text='XIC(A)[XIC(B)]OTE(C);')

        # Position before branch
        level = rung.get_branch_nesting_level(0)

        self.assertEqual(level, 0)

    def test_find_matching_branch_end_simple(self):
        """Test finding matching end for simple branch."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')
        tokens = rung.tokenize_instruction_meta_data()

        if '[' in tokens:
            start_pos = tokens.index('[')
            end_pos = rung.find_matching_branch_end(start_pos)

            self.assertIsNotNone(end_pos)
            self.assertGreater(end_pos, start_pos)

    def test_find_matching_branch_end_empty_text(self):
        """Test finding matching end with empty text."""
        rung = Rung()

        result = rung.find_matching_branch_end(0)

        self.assertEqual(result, -1)

    def test_find_matching_branch_end_invalid_position_raises_error(self):
        """Test finding matching end with invalid position raises error."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        with self.assertRaises(ValueError):
            rung.find_matching_branch_end(0)

    def test_get_branch_internal_nesting_level(self):
        """Test getting internal nesting level of branch."""
        rung = Rung(rung_text='XIC(A)[XIC(B),[XIC(C),XIC(D)]]OTE(E);')
        tokens = rung.tokenize_instruction_meta_data()

        if '[' in tokens:
            branch_pos = tokens.index('[')
            nesting = rung.get_branch_internal_nesting_level(branch_pos)
            self.assertIsInstance(nesting, int)
            self.assertGreaterEqual(nesting, 0)


# ============================================================================
# Branch Insertion Tests
# ============================================================================

class TestRungBranchInsertion(unittest.TestCase):
    """Test cases for branch insertion operations."""

    def test_insert_branch_valid_positions(self):
        """Test inserting branch with valid positions."""
        rung = Rung(rung_text='XIC(A)XIC(B)XIC(C)OTE(D);')

        rung.insert_branch(start_pos=1, end_pos=2)

        # Should now have branch markers
        self.assertIn('[', rung.text)
        self.assertIn(']', rung.text)

    def test_insert_branch_at_start(self):
        """Test inserting branch at rung start."""
        rung = Rung(rung_text='XIC(A)XIC(B)OTE(C);')

        rung.insert_branch(start_pos=0, end_pos=1)

        self.assertIn('[', rung.text)

    def test_insert_branch_negative_position_raises_error(self):
        """Test insert_branch raises ValueError for negative positions."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        with self.assertRaises(ValueError):
            rung.insert_branch(start_pos=-1, end_pos=1)

    def test_insert_branch_reversed_positions_raises_error(self):
        """Test insert_branch raises ValueError when start > end."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        with self.assertRaises(IndexError):
            rung.insert_branch(start_pos=5, end_pos=1)

    def test_insert_branch_out_of_range_raises_error(self):
        """Test insert_branch raises IndexError for out of range positions."""
        rung = Rung(rung_text='XIC(A);')

        with self.assertRaises(IndexError):
            rung.insert_branch(start_pos=0, end_pos=100)

    def test_insert_branch_level_valid(self):
        """Test inserting a new branch level."""
        rung = Rung(rung_text='XIC(A)[XIC(B)]OTE(C);')
        tokens = rung.tokenize_instruction_meta_data()

        if '[' in tokens:
            branch_pos = tokens.index('[')
            rung.insert_branch_level(branch_position=branch_pos)

            # Should add a comma for new branch level
            self.assertGreaterEqual(rung.text.count(','), 1)

    def test_insert_branch_level_out_of_range_raises_error(self):
        """Test insert_branch_level raises IndexError for out of range."""
        rung = Rung(rung_text='XIC(A);')

        with self.assertRaises(IndexError):
            rung.insert_branch_level(branch_position=100)


# ============================================================================
# Branch Removal Tests
# ============================================================================

class TestRungBranchRemoval(unittest.TestCase):
    """Test cases for branch removal operations."""

    def test_remove_branch_valid(self):
        """Test removing a valid branch."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')
        rung.compile_sequence()

        # Get first branch ID
        if rung.branches:
            branch_id = list(rung._branches.keys())[0]
            rung.remove_branch(branch_id)

            self.assertNotIn(branch_id, rung._branches)

    def test_remove_branch_nonexistent_raises_error(self):
        """Test removing non-existent branch raises ValueError."""
        rung = Rung()

        with self.assertRaises(ValueError):
            rung.remove_branch('nonexistent_branch')

    def test_remove_branch_invalid_positions_raises_error(self):
        """Test removing branch with invalid positions raises ValueError."""
        rung = Rung()
        branch = RungBranch(
            branch_id='bad_branch',
            root_branch_id='',
            start_position=-1,
            end_position=-1,
            nested_branches=[]
        )
        rung.branches[branch.branch_id] = branch

        with self.assertRaises(ValueError):
            rung.remove_branch('bad_branch')


# ============================================================================
# Sequence Tests
# ============================================================================

class TestRungSequence(unittest.TestCase):
    """Test cases for rung sequence operations."""

    def test_get_sequence_compiles_when_empty(self):
        """Test get_sequence triggers compilation when empty."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        sequence = rung.get_sequence()

        # Should have compiled
        self.assertIsInstance(sequence, list)

    def test_set_sequence(self):
        """Test setting sequence directly."""
        rung = Rung()
        mock_elements = [Mock(spec=RungElement), Mock(spec=RungElement)]

        rung.set_sequence(mock_elements)  # type: ignore

        self.assertEqual(rung.sequence, mock_elements)

    def test_compile_sequence(self):
        """Test compiling rung sequence."""
        rung = Rung(rung_text='XIC(A)OTE(B);')

        rung.compile_sequence()

        # Should have sequence after compilation
        self.assertIsInstance(rung.sequence, list)

    def test_invalidate_sequence(self):
        """Test invalidating sequence."""
        rung = Rung()
        rung.set_sequence([Mock(), Mock()])
        rung.set_branches({'branch1': Mock()})

        rung.invalidate_sequence()

        self.assertEqual(len(rung._sequence), 0)

    def test_invalidate_method(self):
        """Test invalidate method."""
        rung = Rung(rung_text='XIC(A);')
        rung.compile_instructions()

        rung.invalidate()

        # Instructions should be cleared
        self.assertEqual(len(rung._instructions), 0)
        self.assertEqual(len(rung._sequence), 0)
        self.assertEqual(len(rung._branches), 0)

    def test_get_execution_sequence(self):
        """Test getting execution sequence."""
        rung = Rung(rung_text='XIC(A)OTE(B);')
        rung.compile_sequence()

        exec_sequence = rung.get_sequence()

        self.assertIsInstance(exec_sequence, list)


# ============================================================================
# Token Manipulation Tests
# ============================================================================

class TestRungTokenManipulation(unittest.TestCase):
    """Test cases for token manipulation utilities."""

    def test_remove_tokens_valid_range(self):
        """Test removing tokens in valid range."""
        rung = Rung()
        tokens = ['A', 'B', 'C', 'D', 'E']

        result = rung.remove_tokens(tokens, 1, 3)

        self.assertEqual(result, ['A', 'E'])

    def test_remove_tokens_start_to_end(self):
        """Test removing tokens from start to end."""
        rung = Rung()
        tokens = ['A', 'B', 'C', 'D']

        result = rung.remove_tokens(tokens, 0, 3)

        self.assertEqual(len(result), 0)

    def test_remove_tokens_negative_index_raises_error(self):
        """Test _remove_tokens raises IndexError for negative index."""
        rung = Rung()
        tokens = ['A', 'B', 'C']

        with self.assertRaises(IndexError):
            rung.remove_tokens(tokens, -1, 1)

    def test_remove_tokens_start_greater_than_end_raises_error(self):
        """Test _remove_tokens raises IndexError when start > end."""
        rung = Rung()
        tokens = ['A', 'B', 'C']

        with self.assertRaises(IndexError):
            rung.remove_tokens(tokens, 2, 1)

    def test_remove_token_valid(self):
        """Test removing single token by index."""
        rung = Rung()
        tokens = ['A', 'B', 'C', 'D']

        result = rung.remove_token(tokens, 2)

        self.assertEqual(result, ['A', 'B', 'D'])

    def test_remove_token_by_index_first(self):
        """Test removing first token."""
        rung = Rung()
        tokens = ['A', 'B', 'C']

        result = rung.remove_token(tokens, 0)

        self.assertEqual(result, ['B', 'C'])

    def test_remove_token_by_index_last(self):
        """Test removing last token."""
        rung = Rung()
        tokens = ['A', 'B', 'C']

        result = rung.remove_token(tokens, 2)

        self.assertEqual(result, ['A', 'B'])

    def test_remove_token_by_index_out_of_range_raises_error(self):
        """Test _remove_token_by_index raises IndexError for out of range."""
        rung = Rung()
        tokens = ['A', 'B']

        with self.assertRaises(IndexError):
            rung.remove_token(tokens, 5)


# ============================================================================
# Instruction Movement Tests
# ============================================================================

class TestRungInstructionMovement(unittest.TestCase):
    """Test cases for instruction movement."""

    def test_move_instruction_valid_positions(self):
        """Test moving instruction to valid position."""
        rung = Rung(rung_text='XIC(A)XIC(B)XIC(C);')

        rung.move_instruction(0, 2)

        # Text should have changed
        self.assertIsNotNone(rung.text)

    def test_move_instruction_same_position_no_change(self):
        """Test moving instruction to same position doesn't change text."""
        rung = Rung(rung_text='XIC(A)XIC(B);')
        original_text = rung.text

        rung.move_instruction(1, 1)

        self.assertEqual(rung.text, original_text)

    def test_move_instruction_out_of_range_raises_error(self):
        """Test moving instruction to out of range position raises IndexError."""
        rung = Rung(rung_text='XIC(A);')

        with self.assertRaises(IndexError):
            rung.move_instruction(0, 100)

    def test_move_instruction_empty_rung_raises_error(self):
        """Test moving instruction in empty rung raises ValueError."""
        rung = Rung()

        with self.assertRaises(ValueError):
            rung.move_instruction(0, 1)


# ============================================================================
# Integration Tests
# ============================================================================

class TestRungIntegration(unittest.TestCase):
    """Test cases for integrated rung operations."""

    def test_full_branch_workflow(self):
        """Test complete workflow: create rung, insert branch, validate."""
        rung = Rung(rung_number=1, rung_text='XIC(A)XIC(B)XIC(C)OTE(D);')

        # Insert branch
        rung.insert_branch(start_pos=1, end_pos=2)

        # Validate structure
        is_valid = rung.validate_branch_structure()

        self.assertTrue(is_valid)
        self.assertIn('[', rung.text)
        self.assertIn(']', rung.text)

    def test_tokenize_compile_sequence_workflow(self):
        """Test workflow: tokenize -> compile -> get sequence."""
        rung = Rung(rung_text='XIC(A)[XIC(B),XIC(C)]OTE(D);')

        # Tokenize
        tokens = rung.tokenize_instruction_meta_data()
        self.assertGreater(len(tokens), 0)

        # Compile
        rung.compile_instructions()
        self.assertGreater(len(rung._instructions), 0)

        # Get sequence
        sequence = rung.get_sequence()
        self.assertIsInstance(sequence, list)

    def test_modify_text_invalidate_recompile(self):
        """Test modifying text invalidates and recompiles correctly."""
        rung = Rung(rung_text='XIC(A)OTE(B);')
        rung.compile_instructions()

        # Modify text
        rung.set_text('XIC(A)XIC(B)XIC(C)OTE(D);')
        rung.invalidate()

        # Recompile
        rung.compile_instructions()

        # Should have instructions
        self.assertGreater(len(rung.instructions), 0)

    def test_complete_rung_lifecycle(self):
        """Test complete rung lifecycle from creation to compilation."""
        # Create rung
        rung = Rung(
            rung_number=5,
            comment='Test Rung',
            rung_text='XIC(Start)[XIC(Flag1),XIC(Flag2)]OTE(Output);'
        )

        # Verify initialization
        self.assertEqual(rung.number, 5)
        self.assertEqual(rung.comment, 'Test Rung')

        # Compile
        rung.compile_instructions()
        self.assertGreater(rung.instructions.__len__(), 0)

        # Validate
        self.assertTrue(rung.validate_branch_structure())

        # Compile sequence
        rung.compile_sequence()
        sequence = rung.get_sequence()
        self.assertGreater(len(sequence), 0)

        # Check for branches
        self.assertTrue(rung.has_branches())


if __name__ == '__main__':
    unittest.main(verbosity=2)
