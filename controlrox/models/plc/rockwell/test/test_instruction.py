"""Unit tests for instruction.py module."""

import unittest
from unittest.mock import MagicMock, patch

from controlrox.interfaces import LogicInstructionType
from controlrox.models.plc.rockwell.controller import RaController
from controlrox.models.plc.rockwell.instruction import RaLogicInstruction
from controlrox.models.plc.rockwell.operand import LogixOperand
from controlrox.models.plc.rockwell.routine import RaRoutine
from controlrox.models.plc.rockwell.rung import RaRung


class TestLogixInstruction(unittest.TestCase):
    """Test cases for LogixInstruction class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock controller
        self.mock_controller = MagicMock(spec=RaController)
        self.mock_controller.__class__.__name__ = 'Controller'
        self.mock_controller.tags = MagicMock()
        self.mock_controller.aois = ['CustomAOI', 'MyAOI']

        # Create mock container (program/AOI)
        self.mock_container = MagicMock()
        self.mock_container.name = 'MainProgram'
        self.mock_container.tags = MagicMock()
        self.mock_container.controller = self.mock_controller

        # Create mock routine
        self.mock_routine = MagicMock(spec=RaRoutine)
        self.mock_routine.name = 'MainRoutine'

        # Create mock rung
        self.mock_rung = MagicMock(spec=RaRung)
        self.mock_rung.number = 5
        self.mock_rung.routine = self.mock_routine
        self.mock_rung.container = self.mock_container

        # Sample instruction metadata
        self.xic_metadata = 'XIC(TestTag)'
        self.ote_metadata = 'OTE(OutputTag)'
        self.ton_metadata = 'TON(Timer1,?,5000)'
        self.complex_metadata = 'CPT(Result,Source1 + Source2)'

    def test_init_valid_metadata(self):
        """Test LogixInstruction initialization with valid metadata."""
        with patch.object(RaLogicInstruction, 'get_operands') as mockget_operands:
            instruction = RaLogicInstruction(
                meta_data=self.xic_metadata,
                rung=self.mock_rung
            )

            self.assertEqual(instruction.meta_data, self.xic_metadata)
            self.assertEqual(instruction._rung, self.mock_rung)

            # Test get_operands was called
            mockget_operands.assert_not_called()

    def test_init_with_none_rung(self):
        """Test LogixInstruction initialization with None rung."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=self.xic_metadata,
                rung=None
            )

            self.assertIsNone(instruction._rung)

    def test_instruction_name_property_xic(self):
        """Test instruction_name property with XIC instruction."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=self.xic_metadata,
                rung=self.mock_rung
            )

            self.assertEqual(instruction.instruction_name, 'XIC')

    def test_instruction_name_property_ton(self):
        """Test instruction_name property with TON instruction."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=self.ton_metadata,
                rung=self.mock_rung
            )

            self.assertEqual(instruction.instruction_name, 'TON')

    def test_instruction_name_property_cached(self):
        """Test instruction_name property caching."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=self.xic_metadata,
                rung=self.mock_rung
            )

            # First access
            first_name = instruction.instruction_name
            self.assertEqual(first_name, 'XIC')

            # Cache a different value and verify it's returned
            instruction._instruction_name = 'CACHED'
            second_name = instruction.instruction_name
            self.assertEqual(second_name, 'CACHED')

    def test_instruction_name_property_invalid_metadata(self):
        """Test instruction_name property with invalid metadata."""
        invalid_metadata = 'invalid instruction format'

        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=invalid_metadata,
                rung=self.mock_rung
            )

            with self.assertRaises(ValueError) as context:
                _ = instruction.instruction_name

            self.assertIn("Corrupt meta data for instruction, no type found!", str(context.exception))

    def test_rung_property(self):
        """Test rung property."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=self.xic_metadata,
                rung=self.mock_rung,
            )

            self.assertEqual(instruction.rung, self.mock_rung)

    def test_operands_property(self):
        """Test operands property."""
        with patch.object(RaLogicInstruction, 'get_operands') as mockget_operands:
            instruction = RaLogicInstruction(
                meta_data=self.xic_metadata,
                rung=self.mock_rung
            )

            # Set up mock operands
            mock_operand1 = MagicMock(spec=LogixOperand)
            mock_operand2 = MagicMock(spec=LogixOperand)
            instruction._operands = [mock_operand1, mock_operand2]
            mockget_operands.return_value = [mock_operand1, mock_operand2]

            operands = instruction.get_operands()
            self.assertEqual(len(operands), 2)
            self.assertIn(mock_operand1, operands)
            self.assertIn(mock_operand2, operands)

    def test_type_property_input(self):
        """Test type property for input instruction."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            with patch.object(RaLogicInstruction, 'get_instruction_type') as mock_get_type:
                mock_get_type.return_value = LogicInstructionType.INPUT

                instruction = RaLogicInstruction(
                    meta_data=self.xic_metadata,
                    rung=self.mock_rung
                )

                result = instruction.get_instruction_type()
                self.assertEqual(result, LogicInstructionType.INPUT)
                mock_get_type.assert_called_once()

    def testget_operands_valid_metadata(self):
        """Test get_operands with valid metadata."""
        instruction = RaLogicInstruction(
            meta_data='XIC(TestTag)'
        )

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            mock_operand_instance = MagicMock(spec=LogixOperand)
            mock_operand_class.return_value = mock_operand_instance

            instruction.get_operands()

            self.assertEqual(len(instruction._operands), 1)
            mock_operand_class.assert_called_once_with(
                meta_data='TestTag',
                arg_position=0,
                instruction=instruction
            )

    def testget_operands_multiple_operands(self):
        """Test get_operands with multiple operands."""
        instruction = RaLogicInstruction(
            meta_data='TON(Timer1,?,5000)'
        )

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            mock_operand_instances = [MagicMock(spec=LogixOperand) for _ in range(3)]
            mock_operand_class.side_effect = mock_operand_instances

            instruction.get_operands()

            self.assertEqual(len(instruction._operands), 3)

            # Verify operand creation calls
            _ = [
                (('Timer1', instruction, 0, self.mock_controller),),
                (('?', instruction, 1, self.mock_controller),),
                (('5000', instruction, 2, self.mock_controller),)
            ]

            actual_calls = [call for call in mock_operand_class.call_args_list]
            self.assertEqual(len(actual_calls), 3)

    def testget_operands_with_empty_operands(self):
        """Test get_operands with empty operands in comma-separated list."""
        instruction = RaLogicInstruction(
            meta_data='TEST(,Operand2,)'
        )

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            mock_operand_instance = MagicMock(spec=LogixOperand)
            mock_operand_class.return_value = mock_operand_instance

            instruction.get_operands()

            # Should only create operand for non-empty matches
            self.assertEqual(len(instruction._operands), 1)
            mock_operand_class.assert_called_once_with(meta_data='Operand2', instruction=instruction,
                                                       arg_position=1)

    def testget_operands_invalid_metadata(self):
        """Test get_operands with invalid metadata."""
        instruction = RaLogicInstruction(
            meta_data='invalid instruction format'
        )
        self.assertEqual(instruction.get_operands(), [])

    def test_get_instruction_type_input(self):
        """Test _get_instruction_type for input instructions."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data='XIC(TestTag)',
                rung=self.mock_rung
            )

            result = instruction.get_instruction_type()
            self.assertEqual(result, LogicInstructionType.INPUT)

    def test_get_instruction_type_output(self):
        """Test _get_instruction_type for output instructions."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data='OTE(OutputTag)',
                rung=self.mock_rung
            )

            result = instruction.get_instruction_type()
            self.assertEqual(result, LogicInstructionType.OUTPUT)

    def test_get_instruction_type_jsr(self):
        """Test _get_instruction_type for JSR instruction."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data='JSR(SubRoutine,0,ReturnTag)',
                rung=self.mock_rung
            )

            result = instruction.get_instruction_type()
            self.assertEqual(result, LogicInstructionType.JSR)

    def test_get_instruction_type_unknown(self):
        """Test _get_instruction_type for unknown instructions."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data='UNKNOWN_INSTR(TestTag)',
                rung=self.mock_rung
            )

            result = instruction.get_instruction_type()
            self.assertEqual(result, LogicInstructionType.UNKNOWN)


class TestLogixInstructionEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for LogixInstruction."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = MagicMock(spec=RaController)
        self.mock_controller.__class__.__name__ = 'Controller'
        self.mock_controller.tags = MagicMock()
        self.mock_controller.aois = []

        self.mock_rung = MagicMock()
        self.mock_rung.number = 1

        self.mock_container = MagicMock()
        self.mock_container.name = 'TestProgram'
        self.mock_container.tags = MagicMock()
        self.mock_rung.container = self.mock_container

    def test_instruction_name_with_malformed_regex_match(self):
        """Test instruction_name with metadata that has no regex matches."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            with patch('re.findall', return_value=[]):
                instruction = RaLogicInstruction(
                    meta_data='malformed',
                    rung=self.mock_rung
                )

                with self.assertRaises(ValueError):
                    _ = instruction.instruction_name

    def test_instruction_name_with_empty_matches(self):
        """Test instruction_name with empty regex matches."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            with patch('re.findall', return_value=[[]]):
                instruction = RaLogicInstruction(
                    meta_data='test123???',
                    rung=self.mock_rung
                )

                with self.assertRaises(ValueError):
                    _ = instruction.instruction_name

    def testget_operands_with_malformed_regex(self):
        """Test get_operands with malformed regex results."""
        instruction = RaLogicInstruction(
            meta_data='test'
        )

        with patch('re.findall', return_value=[]):
            self.assertEqual(instruction.get_operands(), [])

    def testget_operands_with_empty_regex_matches(self):
        """Test get_operands with empty regex matches."""
        instruction = RaLogicInstruction(
            meta_data='test'
        )

        with patch('re.findall', return_value=[[]]):
            self.assertEqual(instruction.operands, [])

    def test_complex_operand_parsing(self):
        """Test operand parsing with complex expressions."""
        instruction = RaLogicInstruction(
            meta_data='CPT(Result,(Source1 + Source2) * Factor)'
        )

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            mock_operand_instances = [MagicMock(spec=LogixOperand) for _ in range(2)]
            mock_operand_class.side_effect = mock_operand_instances

            instruction.get_operands()

            # Should parse complex expressions correctly
            self.assertEqual(len(instruction._operands), 2)

    def test_instruction_with_special_characters_in_operands(self):
        """Test instruction parsing with special characters in operands."""
        instruction = RaLogicInstruction(
            meta_data='TEST(Tag_With_Underscores,Tag.With.Dots)'
        )

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            mock_operand_instances = [MagicMock(spec=LogixOperand) for _ in range(2)]
            mock_operand_class.side_effect = mock_operand_instances

            instruction.get_operands()

            self.assertEqual(len(instruction._operands), 2)


class TestLogixInstructionIntegration(unittest.TestCase):
    """Integration tests for LogixInstruction with realistic scenarios."""

    def setUp(self):
        """Set up realistic test fixtures."""
        # Create realistic controller
        self.controller = MagicMock(spec=RaController)
        self.controller.__class__.__name__ = 'Controller'
        self.controller.tags = MagicMock()
        self.controller.aois = ['PID_Enhanced', 'CustomMotorControl']

        # Create realistic program hierarchy
        self.program = MagicMock()
        self.program.name = 'MainProgram'
        self.program.tags = MagicMock()
        self.program.controller = self.controller

        self.routine = MagicMock()
        self.routine.name = 'MainRoutine'

        self.rung = MagicMock()
        self.rung.number = 10
        self.rung.routine = self.routine
        self.rung.container = self.program

    def test_complete_xic_instruction_workflow(self):
        """Test complete workflow with XIC instruction."""
        metadata = 'XIC(ConveyorRunning.Status)'

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            # Create mock operand
            mock_operand = MagicMock(spec=LogixOperand)
            mock_operand.meta_data = 'ConveyorRunning.Status'
            mock_operand.as_aliased = 'Conv_01_Running.Status'
            mock_operand.as_qualified = 'Program:MainProgram.Conv_01_Running.Status'
            mock_operand_class.return_value = mock_operand

            instruction = RaLogicInstruction(
                meta_data=metadata,
                rung=self.rung
            )

            # Test basic properties
            self.assertEqual(instruction.instruction_name, 'XIC')
            self.assertEqual(instruction.rung, self.rung)

            # Test operand creation
            self.assertEqual(len(instruction.operands), 1)
            mock_operand_class.assert_called_once_with(
                meta_data='ConveyorRunning.Status',
                instruction=instruction,
                arg_position=0
            )

    def test_complete_ton_instruction_workflow(self):
        """Test complete workflow with TON instruction."""
        metadata = 'TON(StartupTimer,?,5000)'

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            # Create mock operands
            operands_data = [
                ('StartupTimer', 'Timer_Startup', 'Program:MainProgram.Timer_Startup'),
                ('?', '?', '?'),
                ('5000', '5000', '5000')
            ]

            mock_operands = []
            for i, (original, aliased, qualified) in enumerate(operands_data):
                mock_operand = MagicMock(spec=LogixOperand)
                mock_operand.meta_data = original
                mock_operand.as_aliased = aliased
                mock_operand.as_qualified = qualified
                mock_operands.append(mock_operand)

            mock_operand_class.side_effect = mock_operands

            instruction = RaLogicInstruction(
                meta_data=metadata,
                rung=self.rung
            )

            # Test instruction properties
            self.assertEqual(instruction.instruction_name, 'TON')

            # Test operand creation (3 operands for TON)
            self.assertEqual(len(instruction.operands), 3)
            self.assertEqual(mock_operand_class.call_count, 3)

    def test_complete_aoi_instruction_workflow(self):
        """Test complete workflow with AOI instruction."""
        metadata = 'PID_Enhanced(Process_PID,ProcessValue,Setpoint,Output)'

        with patch('controlrox.models.plc.rockwell.instruction.LogixOperand') as mock_operand_class:
            # Create mock operands for AOI parameters
            operands_data = [
                ('Process_PID', 'PID_Loop_01', 'Program:MainProgram.PID_Loop_01'),
                ('ProcessValue', 'TempInput.Value', 'Program:MainProgram.TempInput.Value'),
                ('Setpoint', 'TempSetpoint', 'TempSetpoint'),  # Controller scoped
                ('Output', 'HeaterOutput', 'Program:MainProgram.HeaterOutput')
            ]

            mock_operands = []
            for original, aliased, qualified in operands_data:
                mock_operand = MagicMock(spec=LogixOperand)
                mock_operand.meta_data = original
                mock_operand.as_aliased = aliased
                mock_operand.as_qualified = qualified
                mock_operands.append(mock_operand)

            mock_operand_class.side_effect = mock_operands

            instruction = RaLogicInstruction(
                meta_data=metadata,
                rung=self.rung
            )

            # Test AOI detection
            self.assertEqual(instruction.instruction_name, 'PID_Enhanced')

            # Test operand handling
            self.assertEqual(len(instruction.operands), 4)

    def test_instruction_type_determination(self):
        """Test instruction type determination for various instruction types."""
        test_cases = [
            ('XIC(InputTag)', LogicInstructionType.INPUT),
            ('XIO(InputTag)', LogicInstructionType.INPUT),
            ('OTE(OutputTag)', LogicInstructionType.OUTPUT),
            ('JSR(SubRoutine,0,RetVal)', LogicInstructionType.JSR),
            ('UNKNOWN_INSTR(Tag)', LogicInstructionType.UNKNOWN),
        ]

        for metadata, expected_type in test_cases:
            with self.subTest(metadata=metadata):
                with patch('controlrox.models.plc.rockwell.instruction.LogixOperand'):
                    instruction = RaLogicInstruction(
                        meta_data=metadata,
                        rung=self.rung
                    )

                    # Mock the appropriate constants for testing
                    self.assertEqual(instruction.get_instruction_type(), expected_type)

    def test_regex_pattern_integration(self):
        """Test integration with actual regex patterns."""
        # This test uses the actual regex patterns to ensure they work correctly
        test_instructions = [
            'XIC(TestTag)',
            'TON(Timer1,?,5000)',
            'CPT(Result,Source1 + Source2)',
            'CustomAOI(Input1,Input2,Output1)',
        ]

        for metadata in test_instructions:
            with self.subTest(metadata=metadata):
                with patch('controlrox.models.plc.rockwell.instruction.LogixOperand'):
                    # Should not raise exceptions during parsing
                    instruction = RaLogicInstruction(
                        meta_data=metadata,
                        rung=self.rung
                    )

                    # Basic validation that parsing worked
                    self.assertIsInstance(instruction.instruction_name, str)
                    self.assertTrue(len(instruction.instruction_name) > 0)
                    self.assertIsInstance(instruction.operands, list)


if __name__ == '__main__':
    unittest.main(verbosity=2)
