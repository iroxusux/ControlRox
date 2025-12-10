"""Unit tests for controlrox.models.plc.rung module."""
import unittest
from unittest.mock import Mock

from controlrox.interfaces import ILogicInstruction
from controlrox.models.plc.rung import Rung


class TestRung(unittest.TestCase):
    """Test cases for Rung class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteRung(Rung):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._comment = ''
                self._rung_number = '0'
                self._rung_text = ''

            def compile_instructions(self):
                pass

            def get_rung_comment(self):
                return self._comment

            def get_rung_number(self):
                return self._rung_number

            def get_rung_text(self):
                return self._rung_text

            def get_rung_sequence(self):
                return []

            def set_rung_comment(self, comment):
                self._comment = comment

            def set_rung_number(self, rung_number):
                self._rung_number = rung_number

            def set_rung_text(self, text):
                self._rung_text = text

            def add_instruction(self, instruction, index=-1):
                if index == -1:
                    self._instructions.append(instruction)
                else:
                    self._instructions.insert(index, instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.ConcreteClass = ConcreteRung

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        rung = self.ConcreteClass()

        self.assertIsNotNone(rung)
        self.assertIsInstance(rung._instructions, list)

    def test_init_with_metadata(self):
        """Test initialization with metadata dict."""
        meta_data = {'@Number': '5', 'Comment': 'Test rung'}
        rung = self.ConcreteClass(meta_data=meta_data)

        self.assertEqual(rung.meta_data, meta_data)

    def test_init_with_name_and_description(self):
        """Test initialization with name and description."""
        rung = self.ConcreteClass(name='TestRung', description='Test Description')

        self.assertEqual(rung.name, 'TestRung')
        self.assertEqual(rung.description, 'Test Description')

    def test_comment_property(self):
        """Test comment property."""
        rung = self.ConcreteClass()
        rung._comment = 'Test Comment'

        self.assertEqual(rung.comment, 'Test Comment')

    def test_rung_number_property(self):
        """Test rung_number property."""
        rung = self.ConcreteClass()
        rung._rung_number = '42'

        self.assertEqual(rung.number, '42')

    def test_rung_text_property(self):
        """Test rung_text property."""
        rung = self.ConcreteClass()
        rung._rung_text = 'XIC(Tag1)OTE(Tag2);'

        self.assertEqual(rung.rung_text, 'XIC(Tag1)OTE(Tag2);')

    def test_rung_sequence_property(self):
        """Test rung_sequence property."""
        rung = self.ConcreteClass()

        sequence = rung.rung_sequence

        self.assertIsInstance(sequence, list)

    def test_str_returns_rung_text(self):
        """Test __str__ returns rung_text."""
        rung = self.ConcreteClass()
        rung._rung_text = 'XIC(Tag)OTE(Output);'

        self.assertEqual(str(rung), 'XIC(Tag)OTE(Output);')

    def test_repr_returns_formatted_string(self):
        """Test __repr__ returns formatted representation."""
        rung = self.ConcreteClass()
        rung._rung_number = '10'
        rung._comment = 'Test'
        rung._rung_text = 'XIC(A);'

        repr_str = repr(rung)

        self.assertIn('Rung', repr_str)
        self.assertIn('number=10', repr_str)
        self.assertIn('comment=Test', repr_str)

    def test_eq_same_rung(self):
        """Test equality with same rung."""
        rung1 = self.ConcreteClass()
        rung1._rung_text = 'XIC(A)OTE(B);'
        rung1._rung_number = '5'

        rung2 = self.ConcreteClass()
        rung2._rung_text = 'XIC(A)OTE(B);'
        rung2._rung_number = '5'

        self.assertEqual(rung1, rung2)

    def test_eq_different_text(self):
        """Test inequality with different rung text."""
        rung1 = self.ConcreteClass()
        rung1._rung_text = 'XIC(A);'
        rung1._rung_number = '5'

        rung2 = self.ConcreteClass()
        rung2._rung_text = 'XIC(B);'
        rung2._rung_number = '5'

        self.assertNotEqual(rung1, rung2)

    def test_eq_different_number(self):
        """Test inequality with different rung number."""
        rung1 = self.ConcreteClass()
        rung1._rung_text = 'XIC(A);'
        rung1._rung_number = '5'

        rung2 = self.ConcreteClass()
        rung2._rung_text = 'XIC(A);'
        rung2._rung_number = '10'

        self.assertNotEqual(rung1, rung2)

    def test_eq_with_non_rung(self):
        """Test inequality with non-Rung object."""
        rung = self.ConcreteClass()

        self.assertNotEqual(rung, "not a rung")
        self.assertNotEqual(rung, 123)
        self.assertNotEqual(rung, None)

    def test_has_instruction_true(self):
        """Test has_instruction returns True when instruction exists."""
        rung = self.ConcreteClass()
        mock_instruction = Mock()
        rung._instructions.append(mock_instruction)

        self.assertTrue(rung.has_instruction(mock_instruction))

    def test_has_instruction_false(self):
        """Test has_instruction returns False when instruction doesn't exist."""
        rung = self.ConcreteClass()
        mock_instruction = Mock()

        self.assertFalse(rung.has_instruction(mock_instruction))


class TestRungInstructions(unittest.TestCase):
    """Test cases for Rung instruction management."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteRung(Rung):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._compiled = False

            def compile_instructions(self):
                self._compiled = True
                self._instructions = [Mock(), Mock()]
                self._input_instructions = [Mock()]
                self._output_instructions = [Mock()]

            def get_rung_comment(self):
                return ''

            def get_rung_number(self):
                return '0'

            def get_rung_text(self):
                return ''

            def get_rung_sequence(self):
                return []

            def set_rung_comment(self, comment):
                pass

            def set_rung_number(self, rung_number):
                pass

            def set_rung_text(self, text):
                pass

            def add_instruction(self, instruction, index=-1):
                if index == -1:
                    self._instructions.append(instruction)
                else:
                    self._instructions.insert(index, instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.ConcreteClass = ConcreteRung

    def test_get_instructions_compiles_when_empty(self):
        """Test get_instructions compiles when instruction list is empty."""
        rung = self.ConcreteClass()

        instructions = rung.get_instructions()

        self.assertTrue(rung._compiled)
        self.assertEqual(len(instructions), 2)

    def test_get_instructions_returns_cached(self):
        """Test get_instructions returns cached instructions."""
        rung = self.ConcreteClass()
        mock_instr = Mock()
        rung._instructions = [mock_instr]

        instructions = rung.get_instructions()

        self.assertEqual(len(instructions), 1)
        self.assertIn(mock_instr, instructions)

    def test_get_input_instructions_compiles_when_empty(self):
        """Test get_input_instructions compiles when list is empty."""
        rung = self.ConcreteClass()

        instructions = rung.get_input_instructions()

        self.assertTrue(rung._compiled)
        self.assertEqual(len(instructions), 1)

    def test_get_input_instructions_returns_cached(self):
        """Test get_input_instructions returns cached instructions."""
        rung = self.ConcreteClass()
        mock_instr = Mock()
        rung._input_instructions = [mock_instr, mock_instr]

        instructions = rung.get_input_instructions()

        self.assertEqual(len(instructions), 2)

    def test_get_output_instructions_compiles_when_empty(self):
        """Test get_output_instructions compiles when list is empty."""
        rung = self.ConcreteClass()

        instructions = rung.get_output_instructions()

        self.assertTrue(rung._compiled)
        self.assertEqual(len(instructions), 1)

    def test_get_output_instructions_returns_cached(self):
        """Test get_output_instructions returns cached instructions."""
        rung = self.ConcreteClass()
        mock_instr1 = Mock()
        mock_instr2 = Mock()
        rung._output_instructions = [mock_instr1, mock_instr2]

        instructions = rung.get_output_instructions()

        self.assertEqual(len(instructions), 2)


class TestRungNotImplemented(unittest.TestCase):
    """Test NotImplementedError cases for Rung."""

    def test_compile_instructions_not_implemented(self):
        """Test compile_instructions raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.compile_instructions()

    def test_get_rung_number_not_implemented(self):
        """Test get_rung_number raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.get_rung_number()

    def test_get_rung_sequence_not_implemented(self):
        """Test get_rung_sequence raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.get_rung_sequence()

    def test_set_rung_number_not_implemented(self):
        """Test set_rung_number raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.set_rung_number('5')

    def test_add_instruction_not_implemented(self):
        """Test add_instruction raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.add_instruction(Mock())

    def test_clear_instructions_not_implemented(self):
        """Test clear_instructions raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.clear_instructions()

    def test_remove_instruction_not_implemented(self):
        """Test remove_instruction raises NotImplementedError."""
        rung = Rung()

        with self.assertRaises(NotImplementedError):
            rung.remove_instruction(Mock())


class TestRungInheritance(unittest.TestCase):
    """Test Rung inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test Rung inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        rung = Rung()

        self.assertIsInstance(rung, PlcObject)

    def test_inherits_from_has_instructions(self):
        """Test Rung inherits from HasInstructions."""
        from controlrox.models.plc.protocols import HasInstructions

        rung = Rung()

        self.assertIsInstance(rung, HasInstructions)

    def test_implements_irung(self):
        """Test Rung implements IRung."""
        from controlrox.interfaces import IRung

        rung = Rung()

        self.assertIsInstance(rung, IRung)

    def test_has_instructions_list(self):
        """Test Rung has _instructions list from HasInstructions."""
        rung = Rung()

        self.assertTrue(hasattr(rung, '_instructions'))
        self.assertIsInstance(rung._instructions, list)


class TestRungRoutineIntegration(unittest.TestCase):
    """Test Rung with routine integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IRoutine

        self.mock_routine = Mock(spec=IRoutine)
        self.mock_routine.name = 'MainRoutine'

        class TestableRung(Rung):
            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                self._instructions.append(instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRung = TestableRung

    def test_rung_with_routine(self):
        """Test rung initialized with routine."""
        rung = self.TestableRung(routine=self.mock_routine)

        self.assertEqual(rung.routine, self.mock_routine)

    def test_rung_get_routine(self):
        """Test getting routine from rung."""
        rung = self.TestableRung(routine=self.mock_routine)

        routine = rung.get_routine()

        self.assertEqual(routine, self.mock_routine)

    def test_rung_without_routine(self):
        """Test rung without routine."""
        rung = self.TestableRung()

        self.assertIsNone(rung.routine)


class TestRungMetaDataIntegration(unittest.TestCase):
    """Test Rung metadata integration."""

    def test_rung_metadata_as_dict(self):
        """Test rung metadata stored as dict."""
        meta_data = {'@Number': '5', 'Comment': 'Test rung'}
        rung = Rung(meta_data=meta_data)

        self.assertEqual(rung.meta_data, meta_data)
        self.assertIsInstance(rung.meta_data, dict)

    def test_rung_name_from_metadata(self):
        """Test rung name extracted from metadata."""
        meta_data = {'@Name': 'RungFromMeta'}
        rung = Rung(meta_data=meta_data)

        self.assertEqual(rung.name, 'RungFromMeta')

    def test_rung_explicit_name_overrides_metadata(self):
        """Test explicit name parameter overrides metadata."""
        meta_data = {'@Name': 'MetaName'}
        rung = Rung(meta_data=meta_data, name='ExplicitName')

        self.assertEqual(rung.name, 'ExplicitName')

    def test_rung_with_empty_metadata(self):
        """Test rung with empty metadata dict."""
        rung = Rung(meta_data={})

        self.assertEqual(rung.meta_data, {})


class TestRungInstructionsManagement(unittest.TestCase):
    """Test rung instruction management."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_instruction = Mock(spec=ILogicInstruction)
        self.mock_instruction.name = 'XIC'

        class TestableRung(Rung):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.compiled_instructions = False

            def compile_instructions(self):
                self.compiled_instructions = True
                self._instructions = [Mock(spec=ILogicInstruction) for _ in range(3)]
                self._input_instructions = [Mock(spec=ILogicInstruction)]
                self._output_instructions = [Mock(spec=ILogicInstruction)]

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                if index == -1:
                    self._instructions.append(instruction)
                else:
                    self._instructions.insert(index, instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRung = TestableRung

    def test_get_instructions_triggers_compile(self):
        """Test get_instructions triggers compile when empty."""
        rung = self.TestableRung()

        instructions = rung.get_instructions()

        self.assertTrue(rung.compiled_instructions)
        self.assertEqual(len(instructions), 3)

    def test_add_instruction(self):
        """Test adding instruction to rung."""
        rung = self.TestableRung()

        rung.add_instruction(self.mock_instruction)

        self.assertIn(self.mock_instruction, rung._instructions)

    def test_add_instruction_at_index(self):
        """Test adding instruction at specific index."""
        rung = self.TestableRung()
        rung._instructions = [Mock(), Mock()]

        rung.add_instruction(self.mock_instruction, index=1)

        self.assertEqual(rung._instructions[1], self.mock_instruction)

    def test_remove_instruction(self):
        """Test removing instruction from rung."""
        rung = self.TestableRung()
        rung._instructions = [self.mock_instruction]

        rung.remove_instruction(self.mock_instruction)

        self.assertNotIn(self.mock_instruction, rung._instructions)

    def test_clear_instructions(self):
        """Test clearing all instructions."""
        rung = self.TestableRung()
        rung._instructions = [Mock(), Mock(), Mock()]

        rung.clear_instructions()

        self.assertEqual(len(rung._instructions), 0)

    def test_has_instruction(self):
        """Test checking if instruction exists."""
        rung = self.TestableRung()
        rung._instructions = [self.mock_instruction]

        result = rung.has_instruction(self.mock_instruction)

        self.assertTrue(result)

    def test_get_input_instructions(self):
        """Test getting input instructions."""
        rung = self.TestableRung()

        instructions = rung.get_input_instructions()

        self.assertTrue(rung.compiled_instructions)
        self.assertEqual(len(instructions), 1)

    def test_get_output_instructions(self):
        """Test getting output instructions."""
        rung = self.TestableRung()

        instructions = rung.get_output_instructions()

        self.assertTrue(rung.compiled_instructions)
        self.assertEqual(len(instructions), 1)


class TestRungCommentManagement(unittest.TestCase):
    """Test rung comment management."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_get_rung_comment(self):
        """Test getting rung comment."""
        rung = self.TestableRung(comment='Test Comment')

        comment = rung.get_rung_comment()

        self.assertEqual(comment, 'Test Comment')

    def test_set_rung_comment(self):
        """Test setting rung comment."""
        rung = self.TestableRung()

        rung.set_rung_comment('New Comment')

        self.assertEqual(rung.comment, 'New Comment')

    def test_comment_property(self):
        """Test comment property."""
        rung = self.TestableRung(comment='Property Comment')

        self.assertEqual(rung.comment, 'Property Comment')


class TestRungTextManagement(unittest.TestCase):
    """Test rung text management."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_get_rung_text(self):
        """Test getting rung text."""
        rung = self.TestableRung(rung_text='XIC(Tag1)OTE(Tag2);')

        text = rung.get_rung_text()

        self.assertEqual(text, 'XIC(Tag1)OTE(Tag2);')

    def test_set_rung_text(self):
        """Test setting rung text."""
        rung = self.TestableRung()

        rung.set_rung_text('XIC(A)OTE(B);')

        self.assertEqual(rung.rung_text, 'XIC(A)OTE(B);')

    def test_rung_text_property(self):
        """Test rung_text property."""
        rung = self.TestableRung(rung_text='XIC(Test);')

        self.assertEqual(rung.rung_text, 'XIC(Test);')


class TestRungNumberManagement(unittest.TestCase):
    """Test rung number management."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._rung_number = '0'

            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return self._rung_number

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                self._rung_number = str(rung_number)

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_get_rung_number(self):
        """Test getting rung number."""
        rung = self.TestableRung()
        rung._rung_number = '42'

        number = rung.get_rung_number()

        self.assertEqual(number, '42')

    def test_set_rung_number(self):
        """Test setting rung number."""
        rung = self.TestableRung()

        rung.set_rung_number('15')

        self.assertEqual(rung.number, '15')

    def test_number_property(self):
        """Test number property."""
        rung = self.TestableRung()
        rung._rung_number = '7'

        self.assertEqual(rung.number, '7')


class TestRungSequence(unittest.TestCase):
    """Test rung sequence functionality."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._sequence = []

            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return self._sequence

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_get_rung_sequence_empty(self):
        """Test getting empty rung sequence."""
        rung = self.TestableRung()

        sequence = rung.get_rung_sequence()

        self.assertIsInstance(sequence, list)
        self.assertEqual(len(sequence), 0)

    def test_get_rung_sequence_with_elements(self):
        """Test getting rung sequence with elements."""
        rung = self.TestableRung()
        rung._sequence = ['XIC', 'OTE', 'Branch']

        sequence = rung.get_rung_sequence()

        self.assertEqual(len(sequence), 3)
        self.assertIn('XIC', sequence)

    def test_rung_sequence_property(self):
        """Test rung_sequence property."""
        rung = self.TestableRung()
        rung._sequence = ['A', 'B']

        self.assertEqual(rung.rung_sequence, ['A', 'B'])


class TestRungEquality(unittest.TestCase):
    """Test rung equality operations."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def __init__(self, **kwargs):
                # Extract number before calling super()
                number = kwargs.pop('number', '0')
                super().__init__(**kwargs)
                self._rung_number = number

            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return self._rung_number

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                self._rung_number = rung_number

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_equal_rungs(self):
        """Test equality of identical rungs."""
        rung1 = self.TestableRung(rung_text='XIC(A)OTE(B);', number='5')
        rung2 = self.TestableRung(rung_text='XIC(A)OTE(B);', number='5')

        self.assertEqual(rung1, rung2)

    def test_unequal_text(self):
        """Test inequality with different text."""
        rung1 = self.TestableRung(rung_text='XIC(A);', number='5')
        rung2 = self.TestableRung(rung_text='XIC(B);', number='5')

        self.assertNotEqual(rung1, rung2)

    def test_unequal_number(self):
        """Test inequality with different number."""
        rung1 = self.TestableRung(rung_text='XIC(A);', number='5')
        rung2 = self.TestableRung(rung_text='XIC(A);', number='10')

        self.assertNotEqual(rung1, rung2)

    def test_not_equal_to_non_rung(self):
        """Test inequality with non-IRung objects."""
        rung = self.TestableRung()

        self.assertNotEqual(rung, 'string')
        self.assertNotEqual(rung, 123)
        self.assertNotEqual(rung, None)
        self.assertNotEqual(rung, [])


class TestRungStringRepresentation(unittest.TestCase):
    """Test rung string representation."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def __init__(self, **kwargs):
                # Extract number before calling super()
                number = kwargs.pop('number', '0')
                super().__init__(**kwargs)
                self._rung_number = number

            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return self._rung_number

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_str_returns_rung_text(self):
        """Test __str__ returns rung text."""
        rung = self.TestableRung(rung_text='XIC(Tag1)OTE(Tag2);')

        self.assertEqual(str(rung), 'XIC(Tag1)OTE(Tag2);')

    def test_repr_contains_rung_info(self):
        """Test __repr__ contains rung information."""
        rung = self.TestableRung(
            rung_text='XIC(A);',
            comment='Test Comment',
            number='10'
        )

        repr_str = repr(rung)

        self.assertIn('Rung', repr_str)
        self.assertIn('number=10', repr_str)
        self.assertIn('comment=Test Comment', repr_str)
        self.assertIn('text=XIC(A);', repr_str)


class TestRungSpecialCases(unittest.TestCase):
    """Test special cases and edge conditions."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_rung_with_none_values(self):
        """Test rung with None for optional parameters."""
        rung = self.TestableRung(
            meta_data=None,
            name=None,
            description=None,
            routine=None
        )

        self.assertIsNotNone(rung)

    def test_rung_with_empty_comment(self):
        """Test rung with empty comment."""
        rung = self.TestableRung(comment='')

        self.assertEqual(rung.comment, '')

    def test_rung_with_empty_text(self):
        """Test rung with empty rung text."""
        rung = self.TestableRung(rung_text='')

        self.assertEqual(rung.rung_text, '')

    def test_rung_multiple_property_access(self):
        """Test accessing rung properties multiple times."""
        rung = self.TestableRung(
            rung_text='XIC(A);',
            comment='Test'
        )

        text1 = rung.rung_text
        text2 = rung.rung_text
        comment1 = rung.comment
        comment2 = rung.comment

        self.assertEqual(text1, text2)
        self.assertEqual(comment1, comment2)

    def test_rung_initialization_order(self):
        """Test rung initializes properly with various parameter orders."""
        rung1 = self.TestableRung(name='Rung1', comment='Comment1')
        rung2 = self.TestableRung(comment='Comment2', name='Rung2')

        self.assertEqual(rung1.name, 'Rung1')
        self.assertEqual(rung2.name, 'Rung2')


class TestRungEdgeCases(unittest.TestCase):
    """Test edge cases for Rung class."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRung(Rung):
            def compile_instructions(self):
                pass

            def get_rung_number(self):
                return '0'

            def get_rung_sequence(self):
                return []

            def set_rung_number(self, rung_number):
                pass

            def add_instruction(self, instruction, index=-1):
                pass

            def clear_instructions(self):
                pass

            def remove_instruction(self, instruction):
                pass

        self.TestableRung = TestableRung

    def test_rung_with_very_long_text(self):
        """Test rung with very long rung text."""
        long_text = 'XIC(Tag)' * 100
        rung = self.TestableRung(rung_text=long_text)

        self.assertEqual(len(rung.rung_text), len(long_text))

    def test_rung_with_special_characters_in_comment(self):
        """Test rung with special characters in comment."""
        rung = self.TestableRung(comment='Test: @#$%^&*()!')

        self.assertEqual(rung.comment, 'Test: @#$%^&*()!')

    def test_rung_with_multiline_comment(self):
        """Test rung with multiline comment."""
        rung = self.TestableRung(comment='Line1\\nLine2\\nLine3')

        self.assertIn('\\n', rung.comment)

    def test_rung_has_instruction_with_empty_list(self):
        """Test has_instruction with empty instruction list."""
        rung = self.TestableRung()
        mock_instruction = Mock()

        result = rung.has_instruction(mock_instruction)

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
