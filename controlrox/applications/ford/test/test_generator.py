"""Unit tests for Ford Emulation Generator.

This test suite provides comprehensive testing of the FordEmulationGenerator
for Rockwell/Allen-Bradley PLC controllers.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch

from controlrox.interfaces import (
    IRung,
    ITag,
    ILogicInstruction,
)
from controlrox.models import ControllerModificationSchema
from controlrox.applications.ford.ford import (
    FordController,
    FordProgram,
    FordRoutine,
    FordRung,
    FordTag,
)
from controlrox.applications.ford.generator import FordEmulationGenerator


class TestFordEmulationGeneratorInitialization(unittest.TestCase):
    """Test cases for FordEmulationGenerator initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'FordTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_initialization_with_ford_controller(self, mock_get_controller):
        """Test FordEmulationGenerator can be initialized with FordController."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        self.assertIsInstance(generator, FordEmulationGenerator)
        self.assertIs(generator.controller, self.mock_controller)
        self.assertIsInstance(generator.schema, ControllerModificationSchema)
        self.assertIsNone(generator._target_safety_program_name)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_initialization_creates_schema(self, mock_get_controller):
        """Test initialization creates a ControllerModificationSchema."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        self.assertIsNotNone(generator.schema)
        self.assertIsInstance(generator.schema, ControllerModificationSchema)
        self.assertIs(generator.schema.destination, self.mock_controller)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_target_safety_program_name_initially_none(self, mock_get_controller):
        """Test _target_safety_program_name is None on initialization."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        self.assertIsNone(generator._target_safety_program_name)

    def test_supporting_class_is_ford_controller(self):
        """Test supporting_class is set to FordController."""
        self.assertEqual(FordEmulationGenerator.supporting_class, FordController)


class TestFordEmulationGeneratorConfiguration(unittest.TestCase):
    """Test cases for FordEmulationGenerator configuration methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'FordTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_custom_tags_returns_empty_list(self, mock_get_controller):
        """Test get_custom_tags returns an empty list for Ford."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        custom_tags = generator.get_custom_tags()

        self.assertEqual(custom_tags, [])
        self.assertIsInstance(custom_tags, list)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_emulation_standard_program_name(self, mock_get_controller):
        """Test get_emulation_standard_program_name returns 'MainProgram'."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        program_name = generator.get_emulation_standard_program_name()

        self.assertEqual(program_name, 'MainProgram')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_emulation_safety_program_name_when_none_set(self, mock_get_controller):
        """Test get_emulation_safety_program_name when no safety program is set."""
        mock_get_controller.return_value = self.mock_controller
        # Create mock safety programs
        mock_safety_prog1 = Mock()
        mock_safety_prog1.name = 'SafetyTask'
        mock_safety_prog2 = Mock()
        mock_safety_prog2.name = 'MappingInputs_Edit'
        mock_safety_prog3 = Mock()
        mock_safety_prog3.name = 'AnotherProgram'

        self.mock_controller.safety_programs = [
            mock_safety_prog1,
            mock_safety_prog2,
            mock_safety_prog3
        ]

        generator = FordEmulationGenerator()

        program_name = generator.get_emulation_safety_program_name()

        self.assertEqual(program_name, 'MappingInputs_Edit')
        self.assertEqual(generator._target_safety_program_name, 'MappingInputs_Edit')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_emulation_safety_program_name_returns_cached_value(self, mock_get_controller):
        """Test get_emulation_safety_program_name returns cached value if already set."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()
        generator._target_safety_program_name = 'CachedProgramName'

        program_name = generator.get_emulation_safety_program_name()

        self.assertEqual(program_name, 'CachedProgramName')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_emulation_safety_program_name_returns_empty_when_no_match(self, mock_get_controller):
        """Test get_emulation_safety_program_name returns empty string when no matching program."""
        mock_get_controller.return_value = self.mock_controller
        mock_safety_prog = Mock()
        mock_safety_prog.name = 'SafetyTask'
        self.mock_controller.safety_programs = [mock_safety_prog]

        generator = FordEmulationGenerator()

        program_name = generator.get_emulation_safety_program_name()

        self.assertEqual(program_name, '')
        self.assertEqual(generator._target_safety_program_name, '')


class TestFordEmulationGeneratorCommOkLogic(unittest.TestCase):
    """Test cases for Comm OK bit scraping and generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'FordTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []

        # Create mock rung with proper structure
        self.mock_rung = Mock(spec=FordRung)
        self.mock_controller.create_rung = Mock(return_value=self.mock_rung)
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=FordTag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_all_comm_ok_bits_from_single_program(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits finds CommOk bits in programs."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock instruction with CommOk in metadata
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(Device1.CommOk)'
        mock_operand = Mock()
        mock_operand.meta_data = 'Device1.CommOk'
        mock_instruction.operands = [mock_operand]

        # Create mock routine with instructions
        mock_routine = Mock(spec=FordRoutine)
        mock_routine.instructions = [mock_instruction]

        # Create mock program with comm_edit_routine
        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine

        self.mock_controller.programs = [mock_program]

        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 1)
        self.assertIn(mock_instruction, result)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_all_comm_ok_bits_filters_otl_instructions(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits includes OTL instructions."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock OTL instruction
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTL'
        mock_instruction.meta_data = 'OTL(Device2.CommOk)'
        mock_operand = Mock()
        mock_operand.meta_data = 'Device2.CommOk'
        mock_instruction.operands = [mock_operand]

        mock_routine = Mock(spec=FordRoutine)
        mock_routine.instructions = [mock_instruction]

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine

        self.mock_controller.programs = [mock_program]

        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 1)
        self.assertIn(mock_instruction, result)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_all_comm_ok_bits_ignores_non_commok_instructions(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits ignores instructions without CommOk."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create instruction without CommOk in metadata
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(Device1.Status)'

        mock_routine = Mock(spec=FordRoutine)
        mock_routine.instructions = [mock_instruction]

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine

        self.mock_controller.programs = [mock_program]

        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 0)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_all_comm_ok_bits_ignores_wrong_instruction_type(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits ignores non-OTE/OTL instructions."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create XIC instruction with CommOk (should be ignored)
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'XIC'
        mock_instruction.meta_data = 'XIC(Device1.CommOk)'

        mock_routine = Mock(spec=FordRoutine)
        mock_routine.instructions = [mock_instruction]

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine

        self.mock_controller.programs = [mock_program]

        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 0)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_all_comm_ok_bits_handles_program_without_comm_edit(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits handles programs without comm_edit_routine."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = None

        self.mock_controller.programs = [mock_program]

        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 0)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_all_comm_ok_bits_from_multiple_programs(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits aggregates from multiple programs."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create first program with CommOk bit
        mock_instruction1 = Mock(spec=ILogicInstruction)
        mock_instruction1.instruction_name = 'OTE'
        mock_instruction1.meta_data = 'OTE(Device1.CommOk)'
        mock_operand1 = Mock()
        mock_operand1.meta_data = 'Device1.CommOk'
        mock_instruction1.operands = [mock_operand1]

        mock_routine1 = Mock(spec=FordRoutine)
        mock_routine1.instructions = [mock_instruction1]

        mock_program1 = Mock(spec=FordProgram)
        mock_program1.name = 'Program1'
        mock_program1.comm_edit_routine = mock_routine1

        # Create second program with CommOk bit
        mock_instruction2 = Mock(spec=ILogicInstruction)
        mock_instruction2.instruction_name = 'OTE'
        mock_instruction2.meta_data = 'OTE(Device2.CommOk)'
        mock_operand2 = Mock()
        mock_operand2.meta_data = 'Device2.CommOk'
        mock_instruction2.operands = [mock_operand2]

        mock_routine2 = Mock(spec=FordRoutine)
        mock_routine2.instructions = [mock_instruction2]

        mock_program2 = Mock(spec=FordProgram)
        mock_program2.name = 'Program2'
        mock_program2.comm_edit_routine = mock_routine2

        self.mock_controller.programs = [mock_program1, mock_program2]

        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 2)
        self.assertIn(mock_instruction1, result)
        self.assertIn(mock_instruction2, result)


class TestFordEmulationGeneratorCustomLogic(unittest.TestCase):
    """Test cases for Ford-specific custom logic generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'FordTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []

        # Create mock tags
        self.mock_tag = Mock(spec=ITag)
        self.mock_tag.name = 'MockTag'
        self.mock_controller.create_tag = Mock(return_value=self.mock_tag)

        # Create mock rung
        self.mock_rung = Mock(spec=IRung)
        self.mock_controller.create_rung = Mock(return_value=self.mock_rung)

        self.mock_routine = Mock(spec=FordRoutine)
        self.mock_controller.create_routine = Mock(return_value=self.mock_routine)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_logic_with_no_comm_ok_bits(self, mock_get_controller):
        """Test _generate_custom_logic handles no CommOk bits gracefully."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()
        generator._scrape_all_comm_ok_bits = Mock(return_value=[])
        generator.add_controller_tag = Mock()
        generator.add_rung_to_standard_routine = Mock()
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        generator._generate_custom_logic()

        # Should still call disable method even with no bits
        generator.disable_all_comm_edit_routines.assert_called_once()
        generator.add_controller_tag.assert_not_called()
        generator.add_rung_to_standard_routine.assert_not_called()

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_logic_creates_tags_for_each_comm_ok_bit(self, mock_get_controller):
        """Test _generate_custom_logic creates comm, pwr1, and pwr2 tags for each device."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock CommOk instruction
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(TestDevice.CommOk)'
        mock_operand = Mock()
        mock_operand.meta_data = 'TestDevice.CommOk'
        mock_instruction.operands = [mock_operand]

        generator._scrape_all_comm_ok_bits = Mock(return_value=[mock_instruction])
        generator.add_controller_tag = Mock(return_value=self.mock_tag)
        generator.add_rung_to_standard_routine = Mock()
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        generator._generate_custom_logic()

        # Should create 3 tags: comm, pwr1, pwr2
        self.assertEqual(generator.add_controller_tag.call_count, 3)

        # Verify tag names
        calls = generator.add_controller_tag.call_args_list
        self.assertEqual(calls[0].kwargs['tag_name'], 'zz_Demo3D_COMM_OK_TestDevice')
        self.assertEqual(calls[1].kwargs['tag_name'], 'zz_Demo3D_Pwr1_TestDevice')
        self.assertEqual(calls[2].kwargs['tag_name'], 'zz_Demo3D_Pwr2_TestDevice')

        # Verify datatypes
        for call_item in calls:
            self.assertEqual(call_item.kwargs['datatype'], 'BOOL')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_logic_creates_emulation_rung(self, mock_get_controller):
        """Test _generate_custom_logic creates emulation rung with proper logic."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock CommOk instruction
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(Device1.CommOk)'
        mock_operand = Mock()
        mock_operand.meta_data = 'Device1.CommOk'
        mock_instruction.operands = [mock_operand]

        generator._scrape_all_comm_ok_bits = Mock(return_value=[mock_instruction])
        generator.add_controller_tag = Mock(return_value=self.mock_tag)
        generator.add_rung_to_standard_routine = Mock()
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        generator._generate_custom_logic()

        # Verify rung was created and added
        self.mock_controller.create_rung.assert_called_once()
        generator.add_rung_to_standard_routine.assert_called_once_with(self.mock_rung)

        # Verify rung text contains expected elements
        rung_call = self.mock_controller.create_rung.call_args
        rung_text = rung_call.kwargs['rung_text']

        # Check for key elements in rung logic
        self.assertIn('XIC(S:FS)', rung_text)
        self.assertIn('OTL(', rung_text)
        self.assertIn('XIC(', rung_text)
        self.assertIn('Device1.CommOk', rung_text)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_logic_handles_multiple_devices(self, mock_get_controller):
        """Test _generate_custom_logic handles multiple CommOk bits."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create multiple mock CommOk instructions
        mock_instruction1 = Mock(spec=ILogicInstruction)
        mock_instruction1.instruction_name = 'OTE'
        mock_instruction1.meta_data = 'OTE(Device1.CommOk)'
        mock_operand1 = Mock()
        mock_operand1.meta_data = 'Device1.CommOk'
        mock_instruction1.operands = [mock_operand1]

        mock_instruction2 = Mock(spec=ILogicInstruction)
        mock_instruction2.instruction_name = 'OTE'
        mock_instruction2.meta_data = 'OTE(Device2.CommOk)'
        mock_operand2 = Mock()
        mock_operand2.meta_data = 'Device2.CommOk'
        mock_instruction2.operands = [mock_operand2]

        generator._scrape_all_comm_ok_bits = Mock(
            return_value=[mock_instruction1, mock_instruction2]
        )
        generator.add_controller_tag = Mock(return_value=self.mock_tag)
        generator.add_rung_to_standard_routine = Mock()
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        generator._generate_custom_logic()

        # Should create 6 tags (3 per device)
        self.assertEqual(generator.add_controller_tag.call_count, 6)

        # Should create 2 rungs (1 per device)
        self.assertEqual(generator.add_rung_to_standard_routine.call_count, 2)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_logic_calls_disable_comm_edit_routines(self, mock_get_controller):
        """Test _generate_custom_logic calls disable_all_comm_edit_routines."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()
        generator._scrape_all_comm_ok_bits = Mock(return_value=[])
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        generator._generate_custom_logic()

        generator.disable_all_comm_edit_routines.assert_called_once()


class TestFordEmulationGeneratorCommEditDisable(unittest.TestCase):
    """Test cases for disabling Comm Edit routines."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'FordTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=FordTag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=FordRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_disable_all_comm_edit_routines_blocks_existing_routines(self, mock_get_controller):
        """Test disable_all_comm_edit_routines blocks routines in programs that have them."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock program with comm_edit_routine
        mock_routine = Mock(spec=FordRoutine)
        mock_routine.name = 'A_Comm_Edit'

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine
        mock_program.block_routine = Mock()

        self.mock_controller.programs = [mock_program]

        # Need to set test_mode_tag property
        generator.add_controller_tag = Mock()
        generator._generate_base_tags = Mock()

        generator.disable_all_comm_edit_routines()

        # Verify block_routine was called
        mock_program.block_routine.assert_called_once()
        call_args = mock_program.block_routine.call_args
        self.assertEqual(call_args[0][0], 'A_Comm_Edit')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_disable_all_comm_edit_routines_skips_programs_without_comm_edit(self, mock_get_controller):
        """Test disable_all_comm_edit_routines skips programs without comm_edit_routine."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock program without comm_edit_routine
        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = None
        mock_program.block_routine = Mock()

        self.mock_controller.programs = [mock_program]

        generator.disable_all_comm_edit_routines()

        # Verify block_routine was NOT called
        mock_program.block_routine.assert_not_called()

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_disable_all_comm_edit_routines_handles_multiple_programs(self, mock_get_controller):
        """Test disable_all_comm_edit_routines handles multiple programs."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create first program with comm_edit_routine
        mock_routine1 = Mock(spec=FordRoutine)
        mock_routine1.name = 'A_Comm_Edit'
        mock_program1 = Mock(spec=FordProgram)
        mock_program1.name = 'Program1'
        mock_program1.comm_edit_routine = mock_routine1
        mock_program1.block_routine = Mock()

        # Create second program without comm_edit_routine
        mock_program2 = Mock(spec=FordProgram)
        mock_program2.name = 'Program2'
        mock_program2.comm_edit_routine = None
        mock_program2.block_routine = Mock()

        # Create third program with comm_edit_routine
        mock_routine3 = Mock(spec=FordRoutine)
        mock_routine3.name = 'A_Comm_Edit'
        mock_program3 = Mock(spec=FordProgram)
        mock_program3.name = 'Program3'
        mock_program3.comm_edit_routine = mock_routine3
        mock_program3.block_routine = Mock()

        self.mock_controller.programs = [mock_program1, mock_program2, mock_program3]

        generator.disable_all_comm_edit_routines()

        # Verify block_routine was called for programs 1 and 3 only
        mock_program1.block_routine.assert_called_once()
        mock_program2.block_routine.assert_not_called()
        mock_program3.block_routine.assert_called_once()


class TestFordEmulationGeneratorInheritance(unittest.TestCase):
    """Test cases for FordEmulationGenerator inheritance."""

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_inherits_from_base_emulation_generator(self, mock_get_controller):
        """Test FordEmulationGenerator inherits from BaseEmulationGenerator."""
        from controlrox.applications.generator import BaseEmulationGenerator

        self.assertTrue(issubclass(FordEmulationGenerator, BaseEmulationGenerator))

    def test_supporting_class_is_ford_controller(self):
        """Test supporting_class is set correctly."""
        self.assertEqual(FordEmulationGenerator.supporting_class, FordController)


class TestFordEmulationGeneratorIntegration(unittest.TestCase):
    """Integration tests for FordEmulationGenerator workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'FordIntegrationTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []

        # Set up program with MappingInputs_Edit
        mock_safety_program = Mock()
        mock_safety_program.name = 'MainProgram_MappingInputs_Edit'
        self.mock_controller.safety_programs = [mock_safety_program]

        self.mock_controller.create_tag = Mock(return_value=Mock(spec=FordTag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=FordRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_full_generation_workflow_without_comm_bits(self, mock_get_controller):
        """Test complete generation workflow without CommOk bits."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Mock schema and its methods
        generator.schema.execute = Mock()
        generator._generate_base_emulation = Mock()
        generator._generate_custom_module_emulation = Mock()

        # Mock comm ok scraping to return empty
        generator._scrape_all_comm_ok_bits = Mock(return_value=[])
        generator.disable_all_comm_edit_routines = Mock()

        # Execute generation
        result = generator.generate_emulation_logic()

        # Verify workflow was executed
        generator._generate_base_emulation.assert_called_once()
        generator._generate_custom_module_emulation.assert_called_once()
        generator.disable_all_comm_edit_routines.assert_called_once()
        generator.schema.execute.assert_called_once()

        # Verify schema is returned
        self.assertIs(result, generator.schema)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_full_generation_workflow_with_comm_bits(self, mock_get_controller):
        """Test complete generation workflow with CommOk bits."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock CommOk instruction
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(TestDevice.CommOk)'
        mock_operand = Mock()
        mock_operand.meta_data = 'TestDevice.CommOk'
        mock_instruction.operands = [mock_operand]

        # Create mock routine and program
        mock_routine = Mock(spec=FordRoutine)
        mock_routine.instructions = [mock_instruction]

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine
        mock_program.block_routine = Mock()

        self.mock_controller.programs = [mock_program]

        # Mock schema and generation methods
        generator.schema.execute = Mock()
        generator._generate_base_emulation = Mock()
        generator._generate_custom_module_emulation = Mock()
        generator.add_controller_tag = Mock(return_value=Mock(spec=ITag, name='MockTag'))
        generator.add_rung_to_standard_routine = Mock()
        generator._emulation_standard_routine = Mock()

        # Execute generation
        result = generator.generate_emulation_logic()

        # Verify custom logic ran
        self.assertEqual(generator.add_controller_tag.call_count, 3)  # comm, pwr1, pwr2
        generator.add_rung_to_standard_routine.assert_called()
        mock_program.block_routine.assert_called()

        # Verify schema executed
        generator.schema.execute.assert_called_once()
        self.assertIs(result, generator.schema)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_safety_program_name_caching(self, mock_get_controller):
        """Test safety program name is cached after first retrieval."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # First call should search and cache
        first_call = generator.get_emulation_safety_program_name()
        self.assertEqual(first_call, 'MainProgram_MappingInputs_Edit')

        # Modify safety_programs - should not affect second call
        self.mock_controller.safety_programs = []

        # Second call should return cached value
        second_call = generator.get_emulation_safety_program_name()
        self.assertEqual(second_call, 'MainProgram_MappingInputs_Edit')


class TestFordEmulationGeneratorEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'EdgeCaseTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_logic_with_empty_programs_list(self, mock_get_controller):
        """Test _generate_custom_logic handles empty programs list."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()
        self.mock_controller.programs = []
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        # Should not raise error
        generator._generate_custom_logic()

        generator.disable_all_comm_edit_routines.assert_called_once()

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_scrape_comm_ok_bits_with_malformed_metadata(self, mock_get_controller):
        """Test _scrape_all_comm_ok_bits handles instructions with incomplete metadata."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create instruction with CommOk but no operands
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(Device.CommOk)'
        mock_instruction.operands = []  # Empty operands

        mock_routine = Mock(spec=FordRoutine)
        mock_routine.instructions = [mock_instruction]

        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'
        mock_program.comm_edit_routine = mock_routine

        self.mock_controller.programs = [mock_program]

        # Should still find the instruction (metadata check is sufficient)
        result = generator._scrape_all_comm_ok_bits()

        self.assertEqual(len(result), 1)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_disable_comm_edit_with_none_controller_programs(self, mock_get_controller):
        """Test disable_all_comm_edit_routines handles None in programs."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()
        self.mock_controller.programs = [None]

        # Should handle None with exception
        with self.assertRaises(ValueError) as context:
            generator.disable_all_comm_edit_routines()
        self.assertIn('Program cannot be None', str(context.exception))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_emulation_safety_program_with_empty_safety_programs(self, mock_get_controller):
        """Test get_emulation_safety_program_name with empty safety_programs."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()
        self.mock_controller.safety_programs = []

        result = generator.get_emulation_safety_program_name()

        self.assertEqual(result, '')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_comm_ok_device_name_extraction_with_nested_tags(self, mock_get_controller):
        """Test device name extraction handles nested tag structures."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create instruction with nested tag path
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.instruction_name = 'OTE'
        mock_instruction.meta_data = 'OTE(Device.SubTag.CommOk)'
        mock_operand = Mock()
        mock_operand.meta_data = 'Device.SubTag.CommOk'
        mock_instruction.operands = [mock_operand]

        generator._scrape_all_comm_ok_bits = Mock(return_value=[mock_instruction])
        generator.add_controller_tag = Mock(return_value=Mock(spec=ITag, name='MockTag'))
        generator.add_rung_to_standard_routine = Mock()
        generator.disable_all_comm_edit_routines = Mock()
        generator._emulation_standard_routine = Mock()

        generator._generate_custom_logic()

        # Device name should be extracted from first segment
        calls = generator.add_controller_tag.call_args_list
        self.assertIn('Device', calls[0].kwargs['tag_name'])


class TestFordEmulationGeneratorRockwellSpecific(unittest.TestCase):
    """Test cases specific to Rockwell/Allen-Bradley implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=FordController)
        self.mock_controller.name = 'RockwellTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=FordRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_ford_controller_type_compatibility(self, mock_get_controller):
        """Test FordEmulationGenerator works specifically with FordController."""
        mock_get_controller.return_value = self.mock_controller
        # This verifies the type hint and supporting_class match
        generator = FordEmulationGenerator()

        self.assertIsInstance(generator.controller, FordController)
        self.assertEqual(type(generator).__name__, 'FordEmulationGenerator')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_inherits_rockwell_base_configuration(self, mock_get_controller):
        """Test generator inherits Rockwell-specific base configurations."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Should have base_tags from BaseEmulationGenerator
        base_tags = generator.base_tags
        self.assertIsInstance(base_tags, list)
        self.assertGreater(len(base_tags), 0)

        # Check for expected base tags
        tag_names = [tag[0] for tag in base_tags]
        self.assertIn('zz_Demo3D_Uninhibit', tag_names)
        self.assertIn('zz_Demo3D_Inhibit', tag_names)
        self.assertIn('zz_Demo3D_TestMode', tag_names)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_standard_program_name_matches_rockwell_convention(self, mock_get_controller):
        """Test standard program name follows Rockwell naming conventions."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        program_name = generator.get_emulation_standard_program_name()

        # MainProgram is typical Rockwell naming
        self.assertEqual(program_name, 'MainProgram')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_comm_edit_routine_naming_convention(self, mock_get_controller):
        """Test Comm Edit routine follows Ford-specific A_Comm_Edit convention."""
        mock_get_controller.return_value = self.mock_controller
        generator = FordEmulationGenerator()

        # Create mock program
        mock_program = Mock(spec=FordProgram)
        mock_program.name = 'TestProgram'

        # Ford uses A_Comm_Edit naming convention
        mock_routine = Mock(spec=FordRoutine)
        mock_routine.name = 'A_Comm_Edit'
        mock_program.comm_edit_routine = mock_routine
        mock_program.block_routine = Mock()

        self.mock_controller.programs = [mock_program]

        generator.disable_all_comm_edit_routines()

        # Verify it was called with the Ford-specific routine name
        mock_program.block_routine.assert_called()
        call_args = mock_program.block_routine.call_args[0]
        self.assertEqual(call_args[0], 'A_Comm_Edit')


if __name__ == '__main__':
    unittest.main(verbosity=2)
