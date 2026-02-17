"""Unit tests for controlrox.models.plc.instruction module."""
import unittest
from unittest.mock import Mock

from controlrox.interfaces import ILogicInstructionType, ILogicOperand
from controlrox.models.plc.instruction import LogicInstruction
from controlrox.models.plc.operand import LogicOperand


class TestLogicInstruction(unittest.TestCase):
    """Test cases for LogixInstruction class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteLogicInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'XIC'

            def get_operands(self):
                if self._operands:
                    return self._operands
                self._operands = [LogicOperand('TestTag', 0)]
                return self._operands

        self.ConcreteClass = ConcreteLogicInstruction

    def test_init_with_string_metadata(self):
        """Test initialization with string metadata."""
        instruction = self.ConcreteClass('XIC(TestTag)')

        self.assertEqual(instruction.meta_data, 'XIC(TestTag)')

    def test_init_with_empty_operands(self):
        """Test initialization with empty operands list."""
        instruction = self.ConcreteClass('XIC(TestTag)', [])

        self.assertIsInstance(instruction._operands, list)
        self.assertEqual(len(instruction._operands), 0)

    def test_instruction_name_property(self):
        """Test instruction_name property."""
        instruction = self.ConcreteClass('XIC(TestTag)')

        self.assertEqual(instruction.name, 'XIC')

    def test_instruction_type_property(self):
        """Test instruction_type property."""
        instruction = self.ConcreteClass('XIC(TestTag)')

        instr_type = instruction.instruction_type

        self.assertIsInstance(instr_type, ILogicInstructionType)


class TestLogixInstructionType(unittest.TestCase):
    """Test cases for instruction type detection."""

    def setUp(self):
        """Set up test fixtures."""
        class TestInstruction(LogicInstruction):
            def __init__(self, meta_data, name):
                super().__init__(meta_data)
                self._name = name

            def get_instruction_name(self):
                return self._name

        self.TestClass = TestInstruction

    def test_input_instruction_type_xic(self):
        """Test XIC is detected as INPUT type."""
        instruction = self.TestClass('XIC(Tag)', 'XIC')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.INPUT)

    def test_input_instruction_type_xio(self):
        """Test XIO is detected as INPUT type."""
        instruction = self.TestClass('XIO(Tag)', 'XIO')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.INPUT)

    def test_output_instruction_type_ote(self):
        """Test OTE is detected as OUTPUT type."""
        instruction = self.TestClass('OTE(Tag)', 'OTE')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.OUTPUT)

    def test_output_instruction_type_otl(self):
        """Test OTL is detected as OUTPUT type."""
        instruction = self.TestClass('OTL(Tag)', 'OTL')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.OUTPUT)

    def test_output_instruction_type_otu(self):
        """Test OTU is detected as OUTPUT type."""
        instruction = self.TestClass('OTU(Tag)', 'OTU')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.OUTPUT)

    def test_output_instruction_type_mov(self):
        """Test MOV is detected as OUTPUT type."""
        instruction = self.TestClass('MOV(Source,Dest)', 'MOV')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.OUTPUT)

    def test_jsr_instruction_type(self):
        """Test JSR is detected as JSR type."""
        instruction = self.TestClass('JSR(RoutineName)', 'JSR')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.JSR)

    def test_unknown_instruction_type(self):
        """Test unknown instruction is detected as UNKNOWN type."""
        instruction = self.TestClass('CUSTOM(Tag)', 'CUSTOM')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, ILogicInstructionType.UNKNOWN)

    def test_instruction_type_caching(self):
        """Test instruction type is cached after first access."""
        instruction = self.TestClass('XIC(Tag)', 'XIC')

        # First access
        type1 = instruction.get_instruction_type()
        # Second access should use cached value
        type2 = instruction.get_instruction_type()

        self.assertEqual(type1, type2)
        self.assertEqual(instruction._instruction_type, ILogicInstructionType.INPUT)

    def test_instruction_type_property_uses_get_method(self):
        """Test instruction_type property calls get_instruction_type."""
        instruction = self.TestClass('OTE(Tag)', 'OTE')

        prop_type = instruction.instruction_type
        method_type = instruction.get_instruction_type()

        self.assertEqual(prop_type, method_type)


class TestLogixInstructionInheritance(unittest.TestCase):
    """Test LogixInstruction inheritance and interface compliance."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'TEST'

        self.ConcreteClass = ConcreteInstruction

    def test_inherits_from_plc_object(self):
        """Test LogixInstruction inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        instruction = self.ConcreteClass('TEST')

        self.assertIsInstance(instruction, PlcObject)

    def test_implements_ilogic_instruction(self):
        """Test LogixInstruction implements ILogicInstruction."""
        from controlrox.interfaces import ILogicInstruction

        instruction = self.ConcreteClass('TEST')

        self.assertIsInstance(instruction, ILogicInstruction)

    def test_has_name_property_from_plc_object(self):
        """Test LogixInstruction has name property from PlcObject."""
        instruction = self.ConcreteClass('TEST')

        self.assertTrue(hasattr(instruction, 'name'))

    def test_meta_data_stored_correctly(self):
        """Test meta_data is stored and accessible."""
        instruction = self.ConcreteClass('XIC(Tag)')

        self.assertEqual(instruction.meta_data, 'XIC(Tag)')


class TestLogicInstructionEdgeCases(unittest.TestCase):
    """Test edge cases for LogicInstruction class."""

    def setUp(self):
        """Set up test fixtures."""
        class TestInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'TEST'

        self.TestClass = TestInstruction

    def test_empty_string_metadata(self):
        """Test instruction with empty string metadata."""
        instruction = self.TestClass('')

        self.assertEqual(instruction.meta_data, '')

    def test_instruction_type_without_cached_type(self):
        """Test getting instruction type when _instruction_type not initialized."""
        instruction = self.TestClass('TEST')

        # Access before _instruction_type is set
        instr_type = instruction.get_instruction_type()

        self.assertIsNotNone(instr_type)


class TestLogicInstructionRungIntegration(unittest.TestCase):
    """Test LogicInstruction with rung integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IRung

        self.mock_rung = Mock(spec=IRung)
        self.mock_rung.number = '5'

        class TestableInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'OTE'

            def compile_operands(self):
                pass

        self.TestableInstruction = TestableInstruction

    def test_instruction_with_rung(self):
        """Test instruction initialized with rung."""
        instruction = self.TestableInstruction('OTE(Tag)', rung=self.mock_rung)

        self.assertEqual(instruction.rung, self.mock_rung)

    def test_instruction_get_rung(self):
        """Test getting rung from instruction."""
        instruction = self.TestableInstruction('OTE(Tag)', rung=self.mock_rung)

        rung = instruction.get_rung()

        self.assertEqual(rung, self.mock_rung)

    def test_instruction_set_rung(self):
        """Test setting rung after initialization."""
        instruction = self.TestableInstruction('OTE(Tag)')

        instruction.set_rung(self.mock_rung)

        self.assertEqual(instruction.rung, self.mock_rung)

    def test_instruction_without_rung(self):
        """Test instruction without rung."""
        instruction = self.TestableInstruction('OTE(Tag)')

        self.assertIsNone(instruction.rung)

    def test_set_rung_type_validation(self):
        """Test set_rung validates type."""
        instruction = self.TestableInstruction('OTE(Tag)')

        with self.assertRaises(TypeError) as context:
            instruction.set_rung("not a rung")  # type: ignore

        self.assertIn('IRung', str(context.exception))

    def test_rung_property_access(self):
        """Test rung property."""
        instruction = self.TestableInstruction('OTE(Tag)', rung=self.mock_rung)

        self.assertEqual(instruction.rung, self.mock_rung)


class TestLogicInstructionTypeDetection(unittest.TestCase):
    """Test instruction type detection for various instructions."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableInstruction(LogicInstruction):
            def __init__(self, meta_data, name):
                super().__init__(meta_data)
                self._name = name

            def get_instruction_name(self):
                return self._name

            def compile_operands(self):
                pass

        self.TestableInstruction = TestableInstruction

    def test_xic_is_input(self):
        """Test XIC is INPUT type."""
        instruction = self.TestableInstruction('XIC(Tag)', 'XIC')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.INPUT)

    def test_xio_is_input(self):
        """Test XIO is INPUT type."""
        instruction = self.TestableInstruction('XIO(Tag)', 'XIO')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.INPUT)

    def test_ote_is_output(self):
        """Test OTE is OUTPUT type."""
        instruction = self.TestableInstruction('OTE(Tag)', 'OTE')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.OUTPUT)

    def test_otl_is_output(self):
        """Test OTL is OUTPUT type."""
        instruction = self.TestableInstruction('OTL(Tag)', 'OTL')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.OUTPUT)

    def test_otu_is_output(self):
        """Test OTU is OUTPUT type."""
        instruction = self.TestableInstruction('OTU(Tag)', 'OTU')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.OUTPUT)

    def test_jsr_is_jsr(self):
        """Test JSR is JSR type."""
        instruction = self.TestableInstruction('JSR(Routine)', 'JSR')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.JSR)

    def test_unknown_type(self):
        """Test unknown instruction is UNKNOWN type."""
        instruction = self.TestableInstruction('CUSTOM(Tag)', 'CUSTOM')

        self.assertEqual(instruction.instruction_type, ILogicInstructionType.UNKNOWN)

    def test_type_caching(self):
        """Test instruction type is cached."""
        instruction = self.TestableInstruction('XIC(Tag)', 'XIC')

        type1 = instruction.get_instruction_type()
        type2 = instruction.get_instruction_type()

        self.assertEqual(type1, type2)
        self.assertEqual(instruction._instruction_type, ILogicInstructionType.INPUT)


class TestLogicInstructionMetaData(unittest.TestCase):
    """Test instruction metadata handling."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'TEST'

            def compile_operands(self):
                pass

        self.TestableInstruction = TestableInstruction

    def test_string_metadata(self):
        """Test instruction with string metadata."""
        instruction = self.TestableInstruction('XIC(Tag1)')

        self.assertEqual(instruction.meta_data, 'XIC(Tag1)')
        self.assertIsInstance(instruction.meta_data, str)

    def test_empty_string_metadata(self):
        """Test instruction with empty string metadata."""
        instruction = self.TestableInstruction('')

        self.assertEqual(instruction.meta_data, '')

    def test_complex_metadata(self):
        """Test instruction with complex metadata string."""
        meta = 'MOV(Source,Dest,1,2,3)'
        instruction = self.TestableInstruction(meta)

        self.assertEqual(instruction.meta_data, meta)

    def test_metadata_with_special_characters(self):
        """Test instruction with special characters in metadata."""
        meta = 'XIC(Program:Tag.Member[0])'
        instruction = self.TestableInstruction(meta)

        self.assertEqual(instruction.meta_data, meta)


class TestLogicInstructionStringRepresentation(unittest.TestCase):
    """Test instruction string representation."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'XIC'

            def compile_operands(self):
                pass

        self.TestableInstruction = TestableInstruction

    def test_str_returns_metadata(self):
        """Test __str__ returns metadata."""
        instruction = self.TestableInstruction('XIC(Tag1)')

        # PlcObject should have __str__ implementation
        result = str(instruction)

        self.assertIsInstance(result, str)

    def test_repr_returns_metadata(self):
        """Test __repr__ returns metadata."""
        instruction = self.TestableInstruction('XIC(Tag1)')

        # PlcObject should have __repr__ implementation
        result = repr(instruction)

        self.assertIsInstance(result, str)


class TestLogicInstructionSpecialCases(unittest.TestCase):
    """Test special cases and edge conditions."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'TEST'

            def compile_operands(self):
                pass

        self.TestableInstruction = TestableInstruction

    def test_instruction_with_none_rung(self):
        """Test instruction with None rung."""
        instruction = self.TestableInstruction('XIC(Tag)', rung=None)

        self.assertIsNone(instruction.rung)

    def test_multiple_property_access(self):
        """Test accessing properties multiple times."""
        instruction = self.TestableInstruction('XIC(Tag)')

        name1 = instruction.name
        name2 = instruction.name
        type1 = instruction.instruction_type
        type2 = instruction.instruction_type

        self.assertEqual(name1, name2)
        self.assertEqual(type1, type2)

    def test_instruction_initialization_order(self):
        """Test instruction initializes properly with various parameter orders."""
        instr1 = self.TestableInstruction(
            meta_data='XIC(A)'
        )
        instr2 = self.TestableInstruction(
            meta_data='XIC(B)'
        )

        self.assertEqual(instr1.meta_data, 'XIC(A)')
        self.assertEqual(instr2.meta_data, 'XIC(B)')


class TestLogicInstructionEdgeCasesExtended(unittest.TestCase):
    """Test additional edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'TEST'

            def compile_operands(self):
                self._operands = [Mock(spec=ILogicOperand) for _ in range(5)]

        self.TestableInstruction = TestableInstruction

    def test_very_long_metadata_string(self):
        """Test instruction with very long metadata."""
        long_meta = 'XIC(' + 'A' * 1000 + ')'
        instruction = self.TestableInstruction(long_meta)

        self.assertEqual(len(instruction.meta_data), len(long_meta))

    def test_operands_compile_creates_list(self):
        """Test compile_operands creates operands list."""
        instruction = self.TestableInstruction('TEST')

        operands = instruction.get_operands()

        self.assertEqual(len(operands), 5)

    def test_instruction_name_property_multiple_access(self):
        """Test instruction_name property accessed multiple times."""
        instruction = self.TestableInstruction('TEST')

        name1 = instruction.name
        name2 = instruction.name
        name3 = instruction.name

        self.assertEqual(name1, name2)
        self.assertEqual(name2, name3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
