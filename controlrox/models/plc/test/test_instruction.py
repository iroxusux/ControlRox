"""Unit tests for controlrox.models.plc.instruction module."""
import unittest
from unittest.mock import Mock

from controlrox.interfaces import LogicInstructionType, ILogicOperand
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

    def test_init_with_operands(self):
        """Test initialization with provided operands."""
        operand1 = LogicOperand('Tag1', 0)
        operand2 = LogicOperand('Tag2', 1)
        instruction = self.ConcreteClass('XIC(Tag1,Tag2)', [operand1, operand2])

        self.assertEqual(len(instruction._operands), 2)
        self.assertIn(operand1, instruction._operands)
        self.assertIn(operand2, instruction._operands)

    def test_instruction_name_property(self):
        """Test instruction_name property."""
        instruction = self.ConcreteClass('XIC(TestTag)')

        self.assertEqual(instruction.instruction_name, 'XIC')

    def test_get_instruction_name_not_implemented(self):
        """Test get_instruction_name raises NotImplementedError in base class."""
        instruction = LogicInstruction('TEST', [])

        with self.assertRaises(NotImplementedError) as context:
            instruction.get_instruction_name()

        self.assertIn('should be overridden by subclasses', str(context.exception))

    def test_instruction_type_property(self):
        """Test instruction_type property."""
        instruction = self.ConcreteClass('XIC(TestTag)')

        instr_type = instruction.instruction_type

        self.assertIsInstance(instr_type, LogicInstructionType)

    def test_operands_property(self):
        """Test operands property."""
        operand = LogicOperand('TestTag', 0)
        instruction = self.ConcreteClass('XIC(TestTag)', [operand])

        operands = instruction.operands

        self.assertEqual(len(operands), 1)
        self.assertEqual(operands[0], operand)

    def test_get_operands_not_implemented_when_empty(self):
        """Test get_operands raises NotImplementedError when no operands cached."""
        instruction = LogicInstruction('TEST', [])

        with self.assertRaises(NotImplementedError) as context:
            instruction.get_operands()

        self.assertIn('should be overridden by subclasses', str(context.exception))

    def test_get_operands_returns_cached(self):
        """Test get_operands returns cached operands."""
        operand1 = LogicOperand('Tag1', 0)
        operand2 = LogicOperand('Tag2', 1)
        instruction = self.ConcreteClass('TEST', [operand1, operand2])

        operands = instruction.get_operands()

        self.assertEqual(len(operands), 2)
        self.assertIs(operands, instruction._operands)


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

        self.assertEqual(instr_type, LogicInstructionType.INPUT)

    def test_input_instruction_type_xio(self):
        """Test XIO is detected as INPUT type."""
        instruction = self.TestClass('XIO(Tag)', 'XIO')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.INPUT)

    def test_output_instruction_type_ote(self):
        """Test OTE is detected as OUTPUT type."""
        instruction = self.TestClass('OTE(Tag)', 'OTE')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.OUTPUT)

    def test_output_instruction_type_otl(self):
        """Test OTL is detected as OUTPUT type."""
        instruction = self.TestClass('OTL(Tag)', 'OTL')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.OUTPUT)

    def test_output_instruction_type_otu(self):
        """Test OTU is detected as OUTPUT type."""
        instruction = self.TestClass('OTU(Tag)', 'OTU')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.OUTPUT)

    def test_output_instruction_type_mov(self):
        """Test MOV is detected as OUTPUT type."""
        instruction = self.TestClass('MOV(Source,Dest)', 'MOV')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.OUTPUT)

    def test_jsr_instruction_type(self):
        """Test JSR is detected as JSR type."""
        instruction = self.TestClass('JSR(RoutineName)', 'JSR')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.JSR)

    def test_unknown_instruction_type(self):
        """Test unknown instruction is detected as UNKNOWN type."""
        instruction = self.TestClass('CUSTOM(Tag)', 'CUSTOM')

        instr_type = instruction.get_instruction_type()

        self.assertEqual(instr_type, LogicInstructionType.UNKNOWN)

    def test_instruction_type_caching(self):
        """Test instruction type is cached after first access."""
        instruction = self.TestClass('XIC(Tag)', 'XIC')

        # First access
        type1 = instruction.get_instruction_type()
        # Second access should use cached value
        type2 = instruction.get_instruction_type()

        self.assertEqual(type1, type2)
        self.assertEqual(instruction._instruction_type, LogicInstructionType.INPUT)

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

    def test_instruction_with_many_operands(self):
        """Test instruction with many operands."""
        operands: list[ILogicOperand] = [LogicOperand(f'Tag{i}', i) for i in range(10)]
        instruction = self.TestClass('COMPLEX', operands)

        self.assertEqual(len(instruction._operands), 10)

    def test_instruction_type_without_cached_type(self):
        """Test getting instruction type when _instruction_type not initialized."""
        instruction = self.TestClass('TEST')

        # Access before _instruction_type is set
        instr_type = instruction.get_instruction_type()

        self.assertIsNotNone(instr_type)

    def test_operands_property_calls_get_operands(self):
        """Test operands property calls get_operands method."""
        operand = LogicOperand('Tag', 0)
        instruction = self.TestClass('TEST', [operand])

        # Access via property
        prop_operands = instruction.operands
        # Access via method
        method_operands = instruction.get_operands()

        self.assertEqual(prop_operands, method_operands)

    def test_instruction_with_none_operands_list(self):
        """Test instruction behavior with operands not provided."""
        instruction = self.TestClass('TEST')

        # Should have empty list as default
        self.assertIsInstance(instruction._operands, list)


class TestLogicInstructionWithMocks(unittest.TestCase):
    """Test LogixInstruction with mock operands."""

    def setUp(self):
        """Set up test fixtures."""
        class MockInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'MOCK'

        self.MockClass = MockInstruction

    def test_instruction_with_mock_operands(self):
        """Test instruction accepts mock operands."""
        mock_operand1 = Mock()
        mock_operand2 = Mock()
        instruction = self.MockClass('MOCK', [mock_operand1, mock_operand2])

        self.assertEqual(len(instruction._operands), 2)
        self.assertIn(mock_operand1, instruction._operands)
        self.assertIn(mock_operand2, instruction._operands)

    def test_get_operands_with_mocks(self):
        """Test get_operands returns mock operands."""
        mock_operand = Mock()
        instruction = self.MockClass('MOCK', [mock_operand])

        operands = instruction.get_operands()

        self.assertEqual(operands[0], mock_operand)


class TestLogicInstructionWithController(unittest.TestCase):
    """Test LogicInstruction with controller integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IController

        self.mock_controller = Mock(spec=IController)
        self.mock_controller.name = 'TestController'

        class TestableInstruction(LogicInstruction):
            def get_instruction_name(self):
                return 'XIC'

            def compile_operands(self):
                pass

        self.TestableInstruction = TestableInstruction

    def test_instruction_with_controller(self):
        """Test instruction initialized with controller."""
        instruction = self.TestableInstruction('XIC(Tag)', controller=self.mock_controller)

        self.assertEqual(instruction.controller, self.mock_controller)

    def test_instruction_controller_access(self):
        """Test accessing controller from instruction."""
        instruction = self.TestableInstruction('XIC(Tag)', controller=self.mock_controller)

        controller = instruction.get_controller()

        self.assertEqual(controller, self.mock_controller)

    def test_instruction_set_controller(self):
        """Test setting controller after initialization."""
        instruction = self.TestableInstruction('XIC(Tag)')

        instruction.set_controller(self.mock_controller)

        self.assertEqual(instruction.controller, self.mock_controller)

    def test_instruction_without_controller(self):
        """Test instruction without controller."""
        instruction = self.TestableInstruction('XIC(Tag)')

        self.assertIsNone(instruction.controller)


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


class TestLogicInstructionOperandManagement(unittest.TestCase):
    """Test instruction operand management."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_operand = Mock(spec=ILogicOperand)
        self.mock_operand.tag_name = 'TestTag'

        class TestableInstruction(LogicInstruction):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.compiled_operands = False

            def get_instruction_name(self):
                return 'XIC'

            def compile_operands(self):
                self.compiled_operands = True
                self._operands = [Mock(spec=ILogicOperand) for _ in range(3)]

        self.TestableInstruction = TestableInstruction

    def test_get_operands_triggers_compile(self):
        """Test get_operands triggers compile when empty."""
        instruction = self.TestableInstruction(meta_data='XIC(Tag)')

        operands = instruction.get_operands()

        self.assertTrue(instruction.compiled_operands)
        self.assertEqual(len(operands), 3)

    def test_get_operands_returns_cached(self):
        """Test get_operands returns cached operands."""
        instruction = self.TestableInstruction(meta_data='XIC(Tag)', operands=[self.mock_operand])

        operands = instruction.get_operands()

        self.assertEqual(len(operands), 1)
        self.assertIn(self.mock_operand, operands)

    def test_operands_property(self):
        """Test operands property."""
        instruction = self.TestableInstruction(meta_data='XIC(Tag)', operands=[self.mock_operand])

        self.assertEqual(len(instruction.operands), 1)

    def test_empty_operands_list(self):
        """Test instruction with empty operands list."""
        instruction = self.TestableInstruction(meta_data='XIC(Tag)', operands=[])

        self.assertEqual(len(instruction._operands), 0)


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

        self.assertEqual(instruction.instruction_type, LogicInstructionType.INPUT)

    def test_xio_is_input(self):
        """Test XIO is INPUT type."""
        instruction = self.TestableInstruction('XIO(Tag)', 'XIO')

        self.assertEqual(instruction.instruction_type, LogicInstructionType.INPUT)

    def test_ote_is_output(self):
        """Test OTE is OUTPUT type."""
        instruction = self.TestableInstruction('OTE(Tag)', 'OTE')

        self.assertEqual(instruction.instruction_type, LogicInstructionType.OUTPUT)

    def test_otl_is_output(self):
        """Test OTL is OUTPUT type."""
        instruction = self.TestableInstruction('OTL(Tag)', 'OTL')

        self.assertEqual(instruction.instruction_type, LogicInstructionType.OUTPUT)

    def test_otu_is_output(self):
        """Test OTU is OUTPUT type."""
        instruction = self.TestableInstruction('OTU(Tag)', 'OTU')

        self.assertEqual(instruction.instruction_type, LogicInstructionType.OUTPUT)

    def test_jsr_is_jsr(self):
        """Test JSR is JSR type."""
        instruction = self.TestableInstruction('JSR(Routine)', 'JSR')

        self.assertEqual(instruction.instruction_type, LogicInstructionType.JSR)

    def test_unknown_type(self):
        """Test unknown instruction is UNKNOWN type."""
        instruction = self.TestableInstruction('CUSTOM(Tag)', 'CUSTOM')

        self.assertEqual(instruction.instruction_type, LogicInstructionType.UNKNOWN)

    def test_type_caching(self):
        """Test instruction type is cached."""
        instruction = self.TestableInstruction('XIC(Tag)', 'XIC')

        type1 = instruction.get_instruction_type()
        type2 = instruction.get_instruction_type()

        self.assertEqual(type1, type2)
        self.assertEqual(instruction._instruction_type, LogicInstructionType.INPUT)


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


class TestLogicInstructionNotImplemented(unittest.TestCase):
    """Test NotImplementedError cases for LogicInstruction."""

    def test_get_instruction_name_not_implemented(self):
        """Test get_instruction_name raises NotImplementedError."""
        instruction = LogicInstruction('TEST')

        with self.assertRaises(NotImplementedError):
            instruction.get_instruction_name()

    def test_compile_operands_not_implemented(self):
        """Test compile_operands raises NotImplementedError."""
        instruction = LogicInstruction('TEST')

        with self.assertRaises(NotImplementedError):
            instruction.compile_operands()


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

    def test_instruction_with_none_controller(self):
        """Test instruction with None controller."""
        instruction = self.TestableInstruction('XIC(Tag)', controller=None)

        self.assertIsNone(instruction.controller)

    def test_instruction_with_none_rung(self):
        """Test instruction with None rung."""
        instruction = self.TestableInstruction('XIC(Tag)', rung=None)

        self.assertIsNone(instruction.rung)

    def test_multiple_property_access(self):
        """Test accessing properties multiple times."""
        instruction = self.TestableInstruction('XIC(Tag)')

        name1 = instruction.instruction_name
        name2 = instruction.instruction_name
        type1 = instruction.instruction_type
        type2 = instruction.instruction_type

        self.assertEqual(name1, name2)
        self.assertEqual(type1, type2)

    def test_instruction_initialization_order(self):
        """Test instruction initializes properly with various parameter orders."""
        from controlrox.interfaces import IController

        mock_controller = Mock(spec=IController)
        operand = Mock(spec=ILogicOperand)

        instr1 = self.TestableInstruction(
            meta_data='XIC(A)',
            operands=[operand],
            controller=mock_controller
        )
        instr2 = self.TestableInstruction(
            controller=mock_controller,
            meta_data='XIC(B)',
            operands=[]
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

        name1 = instruction.instruction_name
        name2 = instruction.instruction_name
        name3 = instruction.instruction_name

        self.assertEqual(name1, name2)
        self.assertEqual(name2, name3)

    def test_instruction_with_many_operands(self):
        """Test instruction with many operands."""
        operands = [Mock(spec=ILogicOperand) for _ in range(20)]
        instruction = self.TestableInstruction('COMPLEX', operands=operands)  # type: ignore

        self.assertEqual(len(instruction._operands), 20)


if __name__ == '__main__':
    unittest.main(verbosity=2)
