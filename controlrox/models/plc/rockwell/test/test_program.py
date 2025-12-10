"""Unit tests for controlrox.models.plc.rockwell.program module."""

import unittest
from unittest.mock import Mock, patch
from controlrox.models.plc.rockwell.controller import RaController
from controlrox.models.plc.rockwell.program import RaProgram
from controlrox.models.plc.rockwell import RaRoutine, RaLogicInstruction


class TestRaProgramInit(unittest.TestCase):
    """Test RaProgram initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.basic_program_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {}
        }

    def test_init_with_meta_data(self):
        """Test RaProgram initialization with provided meta_data."""
        program = RaProgram(
            meta_data=self.basic_program_meta
        )

        self.assertEqual(program['@Name'], 'TestRaProgram')

    def test_init_without_meta_data(self):
        """Test RaProgram initialization without meta_data loads from file."""
        program = RaProgram()
        self.assertEqual(program['@Name'], 'Program_Name')

    def test_init_with_none_meta_data(self):
        """Test RaProgram initialization with None meta_data."""
        program = RaProgram(meta_data=None)
        self.assertEqual(program['@Name'], 'Program_Name')

    def test_init_without_controller(self):
        """Test RaProgram initialization without controller."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.assertIsNone(program.controller)


class TestRaProgramProperties(unittest.TestCase):
    """Test RaProgram properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock()
        self.basic_program_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {}
        }
        self.program_with_routines_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {
                'RaRoutine': [
                    {
                        '@Name': 'MainRoutine',
                        '@Type': 'RLL',
                        'RLLContent': {'Rung': []}
                    },
                    {
                        '@Name': 'SubRaRoutine1',
                        '@Type': 'RLL',
                        'RLLContent': {'Rung': []}
                    }
                ]
            }
        }

    def test_dict_key_order(self):
        """Test dict_key_order property returns correct order."""
        program = RaProgram(meta_data=self.basic_program_meta)

        expected_order = [
            '@Name',
            '@TestEdits',
            '@MainRoutineName',
            '@Disabled',
            '@Class',
            '@UseAsFolder',
            'Description',
            'Tags',
            'Routines',
        ]

        self.assertEqual(program.dict_key_order, expected_order)

    def test_disabled_property(self):
        """Test disabled property."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.assertEqual(program.disabled, 'false')

    def test_test_edits_property(self):
        """Test test_edits property."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.assertEqual(program.test_edits, 'false')

    def test_main_routine_name_property(self):
        """Test main_routine_name property."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.assertEqual(program.main_routine_name, 'MainRoutine')

    def test_use_as_folder_property(self):
        """Test use_as_folder property."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.assertEqual(program.use_as_folder, 'false')

    def test_main_routine_property_exists(self):
        """Test main_routine property when routine exists."""
        program = RaProgram(meta_data=self.program_with_routines_meta)

        # Create a mock routine with name
        mock_routine = Mock(spec=RaRoutine)
        mock_routine.name = 'MainRoutine'

        # Mock the routines property to return a mock with get method
        mock_routines = Mock()
        mock_routines.get.return_value = mock_routine

        with patch.object(type(program), 'routines', new_callable=lambda: property(lambda self: mock_routines)):
            self.assertEqual(program.main_routine.name, 'MainRoutine')  # type: ignore

    def test_main_routine_property_not_exists(self):
        """Test main_routine property when routine doesn't exist."""
        program = RaProgram(meta_data=self.basic_program_meta)

        # Mock the routines property to return a mock with get method returning None
        mock_routines = Mock()
        mock_routines.get.return_value = None

        with patch.object(type(program), 'routines', new_callable=lambda: property(lambda self: mock_routines)):
            self.assertIsNone(program.main_routine)

    def test_main_routine_property_no_name(self):
        """Test main_routine property when no main routine name."""
        meta_data = {
            '@Name': 'TestRaProgram',
            '@MainRoutineName': '',
            'RaRoutines': {}
        }
        program = RaProgram(meta_data=meta_data)

        self.assertIsNone(program.main_routine)


class TestRaProgramMethods(unittest.TestCase):
    """Test RaProgram methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.basic_program_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {}
        }
        self.program_with_routines_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {
                'RaRoutine': [
                    {
                        '@Name': 'MainRoutine',
                        '@Type': 'RLL',
                        'RLLContent': {'Rung': []}
                    },
                    {
                        '@Name': 'SubRaRoutine1',
                        '@Type': 'RLL',
                        'RLLContent': {'Rung': []}
                    }
                ]
            }
        }

    def test_get_instructions_with_filter(self):
        """Test get_instructions with instruction and operand filters."""
        program = RaProgram(
            meta_data=self.program_with_routines_meta
        )

        # Create mock instructions with different names and operands
        mock_jsr_instr1 = Mock(spec=RaLogicInstruction)
        mock_jsr_instr1.name = 'JSR'
        mock_operand1 = Mock()
        mock_operand1.meta_data = 'SubRoutine1'
        mock_jsr_instr1.get_operands.return_value = [mock_operand1]

        mock_jsr_instr2 = Mock(spec=RaLogicInstruction)
        mock_jsr_instr2.name = 'JSR'
        mock_operand2 = Mock()
        mock_operand2.meta_data = 'SubRoutine2'
        mock_jsr_instr2.get_operands.return_value = [mock_operand2]

        mock_xic_instr = Mock(spec=RaLogicInstruction)
        mock_xic_instr.name = 'XIC'
        mock_operand3 = Mock()
        mock_operand3.meta_data = 'Bit1'
        mock_xic_instr.get_operands.return_value = [mock_operand3]

        mock_ote_instr = Mock(spec=RaLogicInstruction)
        mock_ote_instr.name = 'OTE'
        mock_operand4 = Mock()
        mock_operand4.meta_data = 'SubRoutine1'
        mock_ote_instr.get_operands.return_value = [mock_operand4]

        # Set up the instruction cache
        program._instructions = [mock_jsr_instr1, mock_jsr_instr2, mock_xic_instr, mock_ote_instr]

        # Test 1: Filter by instruction name only (JSR)
        result = program.get_instructions(instruction_filter='JSR')
        self.assertEqual(len(result), 2)
        self.assertIn(mock_jsr_instr1, result)
        self.assertIn(mock_jsr_instr2, result)

        # Test 2: Filter by operand only (SubRoutine1)
        result = program.get_instructions(operand_filter='SubRoutine1')
        self.assertEqual(len(result), 2)
        self.assertIn(mock_jsr_instr1, result)
        self.assertIn(mock_ote_instr, result)

        # Test 3: Filter by both instruction name and operand
        result = program.get_instructions(instruction_filter='JSR', operand_filter='SubRoutine1')
        self.assertEqual(len(result), 1)
        self.assertIn(mock_jsr_instr1, result)

        # Test 4: Filter with no matches
        result = program.get_instructions(instruction_filter='ADD', operand_filter='NonExistent')
        self.assertEqual(len(result), 0)

        # Test 5: No filters - returns all instructions
        result = program.get_instructions()
        self.assertEqual(len(result), 4)

    def test_get_instructions_compiles_when_empty(self):
        """Test get_instructions compiles instructions when cache is empty."""
        program = RaProgram(meta_data=self.basic_program_meta)

        # Mock compile_instructions to populate _instructions
        mock_instruction = Mock(spec=RaLogicInstruction)
        mock_instruction.name = 'XIC'

        def mock_compile():
            program._instructions = [mock_instruction]

        program.compile_instructions = Mock(side_effect=mock_compile)

        result = program.get_instructions()

        # Should have called compile_instructions
        program.compile_instructions.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertIn(mock_instruction, result)

    def test_get_instructions_with_instruction_without_operands(self):
        """Test get_instructions handles instructions with no operands when filtering by operand."""
        program = RaProgram(meta_data=self.basic_program_meta)

        # Create instruction with no operands
        mock_instr = Mock(spec=RaLogicInstruction)
        mock_instr.name = 'NOP'
        mock_instr.get_operands.return_value = []

        program._instructions = [mock_instr]

        # Should not include instruction when filtering by operand
        result = program.get_instructions(operand_filter='SomeOperand')
        self.assertEqual(len(result), 0)

    def test_get_instructions_operand_filter_partial_match(self):
        """Test operand filter requires exact match in operand list."""
        program = RaProgram(meta_data=self.basic_program_meta)

        mock_instr = Mock(spec=RaLogicInstruction)
        mock_instr.name = 'ADD'
        mock_op1 = Mock()
        mock_op1.meta_data = 'Value1'
        mock_op2 = Mock()
        mock_op2.meta_data = 'Value2'
        mock_instr.get_operands.return_value = [mock_op1, mock_op2]

        program._instructions = [mock_instr]

        # Should match when operand is in list
        result = program.get_instructions(operand_filter='Value1')
        self.assertEqual(len(result), 1)

        # Should not match partial string
        result = program.get_instructions(operand_filter='Val')
        self.assertEqual(len(result), 0)


class TestRaProgramBlockRaRoutine(unittest.TestCase):
    """Test RaProgram block_routine method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.basic_program_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {}
        }
        # Create mock JSR instruction
        self.mock_jsr_instruction = Mock(spec=RaLogicInstruction)
        self.mock_jsr_instruction.name = "JSR"
        # Mock operand
        mock_operand = Mock()
        mock_operand.meta_data = "SubRaRoutine1"
        self.mock_jsr_instruction.get_operands.return_value = [mock_operand]
        # Mock rung
        self.mock_rung = Mock()
        self.mock_rung.get_rung_text.return_value = "JSR(SubRaRoutine1);"
        self.mock_jsr_instruction.get_rung.return_value = self.mock_rung

    def test_block_routine_success(self):
        """Test successful routine blocking."""
        program = RaProgram(meta_data=self.basic_program_meta)
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.block_routine('SubRaRoutine1', 'BlockingBit')

        program.get_instructions.assert_called_once_with(instruction_filter='JSR')
        self.mock_rung.set_rung_text.assert_called_once_with('XIC(BlockingBit)JSR(SubRaRoutine1);')

    def test_block_routine_already_blocked(self):
        """Test blocking routine that's already blocked."""
        program = RaProgram(meta_data=self.basic_program_meta)
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        # Set rung text to already include the blocking condition
        self.mock_rung.get_rung_text.return_value = 'XIC(BlockingBit)JSR(SubRaRoutine1);'

        program.block_routine('SubRaRoutine1', 'BlockingBit')

        # set_rung_text should not be called since already blocked
        self.mock_rung.set_rung_text.assert_not_called()

    def test_block_routine_no_matching_jsr(self):
        """Test blocking routine with no matching JSR."""
        program = RaProgram(meta_data=self.basic_program_meta)
        # Change operand to different routine
        mock_operand = Mock()
        mock_operand.meta_data = "DifferentRaRoutine"
        self.mock_jsr_instruction.get_operands.return_value = [mock_operand]
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.block_routine('SubRaRoutine1', 'BlockingBit')

        # set_rung_text should not be called since no matching JSR
        self.mock_rung.set_rung_text.assert_not_called()

    def test_block_routine_no_rung(self):
        """Test blocking routine when JSR has no rung."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_jsr_instruction.get_rung.return_value = None
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        with self.assertRaisesRegex(ValueError, r"JSR instruction .* has no rung!"):
            program.block_routine('SubRaRoutine1', 'BlockingBit')

    def test_block_routine_no_jsrs(self):
        """Test blocking routine with no JSR instructions."""
        program = RaProgram(meta_data=self.basic_program_meta)
        program.get_instructions = Mock(return_value=[])

        # Should not raise any exceptions
        program.block_routine('SubRaRoutine1', 'BlockingBit')
        program.get_instructions.assert_called_once_with(instruction_filter='JSR')


class TestRaProgramUnblockRaRoutine(unittest.TestCase):
    """Test RaProgram unblock_routine method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.basic_program_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {}
        }
        # Create mock JSR instruction
        self.mock_jsr_instruction = Mock(spec=RaLogicInstruction)
        self.mock_jsr_instruction.name = "JSR"
        # Mock get_operands to return list with routine name string
        self.mock_jsr_instruction.get_operands.return_value = ["SubRaRoutine1"]
        # Mock rung
        self.mock_rung = Mock()
        self.mock_rung.get_rung_text.return_value = "JSR(SubRaRoutine1);"
        self.mock_jsr_instruction.get_rung.return_value = self.mock_rung

    def test_unblock_routine_success(self):
        """Test successful routine unblocking."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_rung.get_rung_text.return_value = 'XIC(BlockingBit)JSR(SubRaRoutine1);'
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.unblock_routine('SubRaRoutine1', 'BlockingBit')

        program.get_instructions.assert_called_once_with(instruction_filter='JSR')
        self.mock_rung.set_rung_text.assert_called_once_with('JSR(SubRaRoutine1);')

    def test_unblock_routine_not_blocked(self):
        """Test unblocking routine that's not blocked."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_rung.get_rung_text.return_value = 'JSR(SubRaRoutine1);'
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.unblock_routine('SubRaRoutine1', 'BlockingBit')

        # set_rung_text should not be called since it doesn't start with XIC(BlockingBit)
        self.mock_rung.set_rung_text.assert_not_called()

    def test_unblock_routine_no_matching_jsr(self):
        """Test unblocking routine with no matching JSR."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_jsr_instruction.get_operands.return_value = ['DifferentRaRoutine']
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.unblock_routine('SubRaRoutine1', 'BlockingBit')

        # set_rung_text should not be called since no matching JSR
        self.mock_rung.set_rung_text.assert_not_called()

    def test_unblock_routine_no_rung(self):
        """Test unblocking routine when JSR has no rung."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_jsr_instruction.get_rung.return_value = None
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        with self.assertRaisesRegex(ValueError, r"JSR instruction .* has no rung!"):
            program.unblock_routine('SubRaRoutine1', 'BlockingBit')

    def test_unblock_routine_partial_match_blocking_bit(self):
        """Test unblocking when blocking bit appears elsewhere in text."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_rung.get_rung_text.return_value = 'XIC(OtherBit)XIC(BlockingBit)JSR(SubRaRoutine1);'
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.unblock_routine('SubRaRoutine1', 'BlockingBit')

        # set_rung_text should not be called since it doesn't START with XIC(BlockingBit)
        self.mock_rung.set_rung_text.assert_not_called()

    def test_unblock_routine_multiple_occurrences(self):
        """Test unblocking only removes first occurrence."""
        program = RaProgram(meta_data=self.basic_program_meta)
        self.mock_rung.get_rung_text.return_value = 'XIC(BlockingBit)XIC(BlockingBit)JSR(SubRaRoutine1);'
        program.get_instructions = Mock(return_value=[self.mock_jsr_instruction])

        program.unblock_routine('SubRaRoutine1', 'BlockingBit')

        # Should only remove the first occurrence
        self.mock_rung.set_rung_text.assert_called_once_with('XIC(BlockingBit)JSR(SubRaRoutine1);')


class TestRaProgramEdgeCases(unittest.TestCase):
    """Test RaProgram edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.basic_program_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {}
        }

    def test_missing_properties_in_meta_data(self):
        """Test handling of missing properties in meta_data."""
        incomplete_meta = {'@Name': 'TestRaProgram'}

        # Should not raise exceptions
        program = RaProgram(meta_data=incomplete_meta)
        _ = program.disabled

    def test_block_unblock_with_special_characters(self):
        """Test blocking/unblocking with special characters in names."""
        program = RaProgram(meta_data=self.basic_program_meta)

        # Test with routine name containing special characters
        mock_jsr_instruction = Mock(spec=RaLogicInstruction)
        mock_operand = Mock()
        mock_operand.meta_data = "Sub_RaRoutine.1"
        mock_jsr_instruction.get_operands.return_value = [mock_operand]
        mock_rung = Mock()
        mock_rung.get_rung_text.return_value = "JSR(Sub_RaRoutine.1);"
        mock_jsr_instruction.get_rung.return_value = mock_rung

        program.get_instructions = Mock(return_value=[mock_jsr_instruction])

        program.block_routine('Sub_RaRoutine.1', 'Block_Bit.1')

        mock_rung.set_rung_text.assert_called_once_with('XIC(Block_Bit.1)JSR(Sub_RaRoutine.1);')

    def test_empty_routine_name_block_unblock(self):
        """Test blocking/unblocking with empty routine name."""
        program = RaProgram(meta_data=self.basic_program_meta)
        program.get_instructions = Mock(return_value=[])

        # Should handle gracefully
        program.block_routine('', 'BlockingBit')
        program.unblock_routine('', 'BlockingBit')


# Integration-style tests
class TestRaProgramIntegration(unittest.TestCase):
    """Integration tests for RaProgram class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.program_with_routines_meta = {
            '@Name': 'TestRaProgram',
            '@TestEdits': 'false',
            '@MainRoutineName': 'MainRoutine',
            '@Disabled': 'false',
            '@Class': 'Standard',
            '@UseAsFolder': 'false',
            'Description': 'Test program description',
            'Tags': {},
            'RaRoutines': {
                'RaRoutine': [
                    {
                        '@Name': 'MainRoutine',
                        '@Type': 'RLL',
                        'RLLContent': {'Rung': []}
                    },
                    {
                        '@Name': 'SubRaRoutine1',
                        '@Type': 'RLL',
                        'RLLContent': {'Rung': []}
                    }
                ]
            }
        }

    def test_full_program_lifecycle(self):
        """Test full program creation and usage lifecycle."""
        # Create program
        program = RaProgram()

        # Verify properties
        self.assertEqual(program.name, 'Program_Name')
        self.assertEqual(program.main_routine_name, 'MainRoutine')
        self.assertEqual(program.disabled, 'false')

        # Test instruction operations
        program.get_instructions = Mock(return_value=[])
        instructions = program.get_instructions('JSR')
        self.assertEqual(instructions, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
