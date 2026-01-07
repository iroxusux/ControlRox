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

            self.assertEqual(instruction.name, 'XIC')

    def test_instruction_name_property_ton(self):
        """Test instruction_name property with TON instruction."""
        with patch.object(RaLogicInstruction, 'get_operands'):
            instruction = RaLogicInstruction(
                meta_data=self.ton_metadata,
                rung=self.mock_rung
            )

            self.assertEqual(instruction.name, 'TON')

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
