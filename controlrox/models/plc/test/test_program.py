"""Unit tests for controlrox.models.plc.program module."""
import unittest
from unittest.mock import Mock
from pyrox.models import HashList
from controlrox.models.plc.program import Program


class TestProgram(unittest.TestCase):
    """Test cases for Program class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteProgram(Program):
            def compile_instructions(self):
                self._instructions = [Mock(), Mock()]

            def compile_routines(self):
                self._routines = [Mock(), Mock(), Mock()]

            def compile_tags(self):
                self._tags = [Mock(), Mock()]

            def enable(self):
                self._enabled = True

            def disable(self):
                self._enabled = False

            def add_rung(self, rung):
                pass

            def remove_rung(self, rung):
                pass

            def clear_rungs(self):
                pass

            def block_routine(self, routine_name, blocking_bit):
                pass

            def unblock_routine(self, routine_name, blocking_bit):
                pass

            def get_main_routine(self):
                return self._routines[0] if self._routines else None

        self.ConcreteClass = ConcreteProgram

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        program = self.ConcreteClass()

        self.assertIsNotNone(program)
        self.assertTrue(program.is_enabled())  # Default is enabled=True
        self.assertFalse(program.is_safe())

    def test_init_enabled_true(self):
        """Test initialization with enabled=True."""
        program = self.ConcreteClass(enabled=True)

        self.assertTrue(program.is_enabled())

    def test_init_enabled_false(self):
        """Test initialization with enabled=False."""
        program = self.ConcreteClass(enabled=False)

        self.assertFalse(program.is_enabled())

    def test_init_with_metadata(self):
        """Test initialization with metadata dict."""
        meta_data = {'@Name': 'MainProgram', '@Type': 'Normal'}
        program = self.ConcreteClass(meta_data=meta_data)

        self.assertEqual(program.meta_data, meta_data)

    def test_init_with_name_and_description(self):
        """Test initialization with name and description."""
        program = self.ConcreteClass(
            name='TestProgram',
            description='Test Description'
        )

        self.assertEqual(program.name, 'TestProgram')
        self.assertEqual(program.description, 'Test Description')

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        meta_data = {'@Name': 'CustomProgram'}
        program = self.ConcreteClass(
            enabled=False,
            meta_data=meta_data,
            name='OverrideName',
            description='Custom Description'
        )

        self.assertFalse(program.is_enabled())
        self.assertEqual(program.name, 'OverrideName')
        self.assertEqual(program.description, 'Custom Description')

    def test_enable_method(self):
        """Test enable method."""
        program = self.ConcreteClass(enabled=False)

        program.enable()

        self.assertTrue(program.is_enabled())

    def test_disable_method(self):
        """Test disable method."""
        program = self.ConcreteClass(enabled=True)

        program.disable()

        self.assertFalse(program.is_enabled())

    def test_has_instructions_list(self):
        """Test Program has _instructions list from HasInstructions."""
        program = self.ConcreteClass()

        self.assertTrue(hasattr(program, '_instructions'))
        self.assertIsInstance(program._instructions, list)

    def test_has_routines_list(self):
        """Test Program has _routines list from HasRoutines."""
        program = self.ConcreteClass()

        self.assertTrue(hasattr(program, '_routines'))
        self.assertIsInstance(program._routines, HashList)

    def test_has_tags_lists(self):
        """Test Program has tag lists from HasTags."""
        program = self.ConcreteClass()

        self.assertTrue(hasattr(program, '_tags'))
        self.assertTrue(hasattr(program, '_safety_tags'))
        self.assertTrue(hasattr(program, '_standard_tags'))
        self.assertIsInstance(program._tags, HashList)

    def test_compile_instructions(self):
        """Test compile_instructions method."""
        program = self.ConcreteClass()

        program.compile_instructions()

        self.assertEqual(len(program._instructions), 2)

    def test_compile_routines(self):
        """Test compile_routines method."""
        program = self.ConcreteClass()

        program.compile_routines()

        self.assertEqual(len(program._routines), 3)

    def test_compile_tags(self):
        """Test compile_tags method."""
        program = self.ConcreteClass()

        program.compile_tags()

        self.assertEqual(len(program._tags), 2)

    def test_get_main_routine(self):
        """Test get_main_routine method."""
        program = self.ConcreteClass()
        program.compile_routines()

        main_routine = program.get_main_routine()

        self.assertIsNotNone(main_routine)


class TestProgramInheritance(unittest.TestCase):
    """Test Program inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test Program inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        program = Program()

        self.assertIsInstance(program, PlcObject)

    def test_inherits_from_can_enable_disable(self):
        """Test Program inherits from CanEnableDisable."""
        from controlrox.models.plc.protocols import CanEnableDisable

        program = Program()

        self.assertIsInstance(program, CanEnableDisable)

    def test_inherits_from_has_instructions(self):
        """Test Program inherits from HasInstructions."""
        from controlrox.models.plc.protocols import HasInstructions

        program = Program()

        self.assertIsInstance(program, HasInstructions)

    def test_inherits_from_has_routines(self):
        """Test Program inherits from HasRoutines."""
        from controlrox.models.plc.protocols import HasRoutines

        program = Program()

        self.assertIsInstance(program, HasRoutines)

    def test_inherits_from_has_tags(self):
        """Test Program inherits from HasTags."""
        from controlrox.models.plc.protocols import HasTags

        program = Program()

        self.assertIsInstance(program, HasTags)

    def test_implements_iprogram(self):
        """Test Program implements IProgram."""
        from controlrox.interfaces import IProgram

        program = Program()

        self.assertIsInstance(program, IProgram)


class TestProgramProtocolMethods(unittest.TestCase):
    """Test Program protocol methods from mixins."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteProgram(Program):
            def compile_instructions(self):
                self._instructions = [Mock()]
                self._input_instructions = [Mock()]
                self._output_instructions = [Mock()]

            def compile_routines(self):
                self._routines = [Mock()]

            def compile_tags(self):
                self._tags = [Mock()]
                self._safety_tags = []
                self._standard_tags = [Mock()]

            def enable(self):
                self._enabled = True

            def disable(self):
                self._enabled = False

            def add_rung(self, rung):
                pass

            def remove_rung(self, rung):
                pass

            def clear_rungs(self):
                pass

            def block_routine(self, routine_name, blocking_bit):
                pass

            def unblock_routine(self, routine_name, blocking_bit):
                pass

            def get_main_routine(self):
                return None

        self.ConcreteClass = ConcreteProgram

    def test_get_instructions(self):
        """Test get_instructions from HasInstructions."""
        program = self.ConcreteClass()

        instructions = program.get_instructions()

        self.assertEqual(len(instructions), 1)

    def test_get_input_instructions(self):
        """Test get_input_instructions from HasInstructions."""
        program = self.ConcreteClass()

        instructions = program.get_input_instructions()

        self.assertEqual(len(instructions), 1)

    def test_get_output_instructions(self):
        """Test get_output_instructions from HasInstructions."""
        program = self.ConcreteClass()

        instructions = program.get_output_instructions()

        self.assertEqual(len(instructions), 1)

    def test_get_routines(self):
        """Test get_routines from HasRoutines."""
        program = self.ConcreteClass()
        program.compile_routines()

        routines = program.get_routines()

        self.assertEqual(len(routines), 1)

    def test_get_tags(self):
        """Test get_tags from HasTags."""
        program = self.ConcreteClass()

        tags = program.get_tags()

        self.assertEqual(len(tags), 1)

    def test_get_safety_tags(self):
        """Test get_safety_tags from HasTags."""
        program = self.ConcreteClass()

        tags = program.get_safety_tags()

        self.assertEqual(len(tags), 0)

    def test_get_standard_tags(self):
        """Test get_standard_tags from HasTags."""
        program = self.ConcreteClass()

        tags = program.get_standard_tags()

        self.assertEqual(len(tags), 1)


class TestProgramEdgeCases(unittest.TestCase):
    """Test edge cases for Program class."""

    def test_init_with_empty_strings(self):
        """Test initialization with empty strings."""
        program = Program(name='', description='')

        self.assertEqual(program.name, '')
        self.assertEqual(program.description, '')

    def test_init_with_none_metadata(self):
        """Test initialization with None metadata."""
        program = Program(meta_data=None)

        self.assertEqual(program.meta_data, {})

    def test_default_enabled_is_true(self):
        """Test default enabled state is True."""
        program = Program()

        # Default for Program is enabled=True
        self.assertTrue(program.is_enabled())

    def test_multiple_enable_disable_cycles(self):
        """Test multiple enable/disable cycles."""
        class ConcreteProgram(Program):
            def enable(self):
                self._enabled = True

            def disable(self):
                self._enabled = False

            def compile_instructions(self):
                pass

            def compile_routines(self):
                pass

            def compile_tags(self):
                pass

            def add_rung(self, rung):
                pass

            def remove_rung(self, rung):
                pass

            def clear_rungs(self):
                pass

            def block_routine(self, routine_name, blocking_bit):
                pass

            def unblock_routine(self, routine_name, blocking_bit):
                pass

            def get_main_routine(self):
                return None

        program = ConcreteProgram()

        program.disable()
        self.assertFalse(program.is_enabled())

        program.enable()
        self.assertTrue(program.is_enabled())

        program.disable()
        self.assertFalse(program.is_enabled())


if __name__ == '__main__':
    unittest.main(verbosity=2)
