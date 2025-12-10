"""Unit tests for controlrox.models.plc.routine module."""
import unittest
from unittest.mock import Mock

from controlrox.interfaces import ILogicInstruction
from controlrox.models.plc.routine import Routine


class TestRoutine(unittest.TestCase):
    """Test cases for Routine class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteRoutine(Routine):
            @property
            def rungs(self):
                return self.get_rungs()

            def compile_instructions(self):
                self._instructions = [Mock(), Mock()]

            def compile_rungs(self):
                self._rungs = [Mock(), Mock(), Mock()]

            def add_rung(self, rung):
                self._rungs.append(rung)

            def remove_rung(self, rung):
                self._rungs.remove(rung)

            def clear_rungs(self):
                self._rungs.clear()

            def block(self):
                self._blocked = True

            def unblock(self):
                self._blocked = False

            def check_for_jsr(self, routine_name):
                return False

        self.ConcreteClass = ConcreteRoutine

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        routine = self.ConcreteClass()

        self.assertIsNotNone(routine)
        self.assertIsInstance(routine._instructions, list)
        self.assertIsInstance(routine._rungs, list)

    def test_init_with_metadata(self):
        """Test initialization with metadata dict."""
        meta_data = {'@Name': 'MainRoutine', '@Type': 'RLL'}
        routine = self.ConcreteClass(meta_data=meta_data)

        self.assertEqual(routine.meta_data, meta_data)

    def test_init_with_name_and_description(self):
        """Test initialization with name and description."""
        routine = self.ConcreteClass(
            name='TestRoutine',
            description='Test Description'
        )

        self.assertEqual(routine.name, 'TestRoutine')
        self.assertEqual(routine.description, 'Test Description')

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        meta_data = {'@Name': 'CustomRoutine'}
        routine = self.ConcreteClass(
            meta_data=meta_data,
            name='OverrideName',
            description='Custom Description'
        )

        self.assertEqual(routine.name, 'OverrideName')
        self.assertEqual(routine.description, 'Custom Description')

    def test_has_instructions_list(self):
        """Test Routine has _instructions list from HasInstructions."""
        routine = self.ConcreteClass()

        self.assertTrue(hasattr(routine, '_instructions'))
        self.assertIsInstance(routine._instructions, list)

    def test_has_rungs_list(self):
        """Test Routine has _rungs list from HasRungs."""
        routine = self.ConcreteClass()

        self.assertTrue(hasattr(routine, '_rungs'))
        self.assertIsInstance(routine._rungs, list)

    def test_compile_instructions_method(self):
        """Test compile_instructions method."""
        routine = self.ConcreteClass()

        routine.compile_instructions()

        self.assertEqual(len(routine._instructions), 2)

    def test_compile_rungs_method(self):
        """Test compile_rungs method."""
        routine = self.ConcreteClass()

        routine.compile_rungs()

        self.assertEqual(len(routine._rungs), 3)

    def test_add_rung_method(self):
        """Test add_rung method."""
        routine = self.ConcreteClass()
        mock_rung = Mock()

        routine.add_rung(mock_rung)

        self.assertIn(mock_rung, routine._rungs)

    def test_remove_rung_method(self):
        """Test remove_rung method."""
        routine = self.ConcreteClass()
        mock_rung = Mock()
        routine._rungs.append(mock_rung)

        routine.remove_rung(mock_rung)

        self.assertNotIn(mock_rung, routine._rungs)

    def test_clear_rungs_method(self):
        """Test clear_rungs method."""
        routine = self.ConcreteClass()
        routine._rungs = [Mock(), Mock(), Mock()]

        routine.clear_rungs()

        self.assertEqual(len(routine._rungs), 0)

    def test_block_method(self):
        """Test block method."""
        routine = self.ConcreteClass()
        routine._blocked = False

        routine.block()

        self.assertTrue(routine._blocked)

    def test_unblock_method(self):
        """Test unblock method."""
        routine = self.ConcreteClass()
        routine._blocked = True

        routine.unblock()

        self.assertFalse(routine._blocked)

    def test_check_for_jsr_method(self):
        """Test check_for_jsr method."""
        routine = self.ConcreteClass()

        result = routine.check_for_jsr('SomeRoutine')

        self.assertIsInstance(result, bool)


class TestRoutineNotImplemented(unittest.TestCase):
    """Test NotImplementedError cases for Routine."""

    def test_block_not_implemented(self):
        """Test block raises NotImplementedError."""
        routine = Routine()

        with self.assertRaises(NotImplementedError) as context:
            routine.block()

        self.assertIn('must be implemented by subclass', str(context.exception))

    def test_unblock_not_implemented(self):
        """Test unblock raises NotImplementedError."""
        routine = Routine()

        with self.assertRaises(NotImplementedError) as context:
            routine.unblock()

        self.assertIn('must be implemented by subclass', str(context.exception))

    def test_check_for_jsr_not_implemented(self):
        """Test check_for_jsr raises NotImplementedError."""
        routine = Routine()

        with self.assertRaises(NotImplementedError) as context:
            routine.check_for_jsr('TestRoutine')

        self.assertIn('must be implemented by subclass', str(context.exception))


class TestRoutineInheritance(unittest.TestCase):
    """Test Routine inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test Routine inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        routine = Routine()

        self.assertIsInstance(routine, PlcObject)

    def test_inherits_from_has_instructions(self):
        """Test Routine inherits from HasInstructions."""
        from controlrox.models.plc.protocols import HasInstructions

        routine = Routine()

        self.assertIsInstance(routine, HasInstructions)

    def test_inherits_from_has_rungs(self):
        """Test Routine inherits from HasRungs."""
        from controlrox.models.plc.protocols import HasRungs

        routine = Routine()

        self.assertIsInstance(routine, HasRungs)

    def test_implements_iroutine(self):
        """Test Routine implements IRoutine."""
        from controlrox.interfaces import IRoutine

        routine = Routine()

        self.assertIsInstance(routine, IRoutine)

    def test_has_name_property(self):
        """Test Routine has name property."""
        routine = Routine(name='TestRoutine')

        self.assertEqual(routine.name, 'TestRoutine')

    def test_has_description_property(self):
        """Test Routine has description property."""
        routine = Routine(description='Test Description')

        self.assertEqual(routine.description, 'Test Description')


class TestRoutineEdgeCases(unittest.TestCase):
    """Test edge cases for Routine class."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteRoutine(Routine):
            @property
            def rungs(self):
                return self.get_rungs()

            def compile_instructions(self):
                pass

            def compile_rungs(self):
                pass

            def add_rung(self, rung):
                pass

            def remove_rung(self, rung):
                pass

            def clear_rungs(self):
                pass

            def block(self):
                pass

            def unblock(self):
                pass

            def check_for_jsr(self, routine_name):
                return True if routine_name == 'FoundRoutine' else False

        self.ConcreteClass = ConcreteRoutine

    def test_init_with_none_metadata(self):
        """Test initialization with None metadata."""
        routine = self.ConcreteClass(meta_data=None)

        self.assertEqual(routine.meta_data, {})

    def test_init_with_empty_name(self):
        """Test initialization with empty name."""
        routine = self.ConcreteClass(name='')

        self.assertEqual(routine.name, '')

    def test_init_with_empty_description(self):
        """Test initialization with empty description."""
        routine = self.ConcreteClass(description='')

        self.assertEqual(routine.description, '')

    def test_check_for_jsr_found(self):
        """Test check_for_jsr when routine is found."""
        routine = self.ConcreteClass()

        result = routine.check_for_jsr('FoundRoutine')

        self.assertTrue(result)

    def test_check_for_jsr_not_found(self):
        """Test check_for_jsr when routine is not found."""
        routine = self.ConcreteClass()

        result = routine.check_for_jsr('NotFoundRoutine')

        self.assertFalse(result)


class TestRoutineContainerIntegration(unittest.TestCase):
    """Test Routine with container integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.models.plc.protocols import HasRoutines

        self.mock_container = Mock(spec=HasRoutines)
        self.mock_container.name = 'TestProgram'

        class TestableRoutine(Routine):
            def compile_instructions(self):
                pass

            def compile_rungs(self):
                pass

            def add_rung(self, rung):
                self._rungs.append(rung)

            def remove_rung(self, rung):
                self._rungs.remove(rung)

            def clear_rungs(self):
                self._rungs.clear()

            def block(self):
                pass

            def unblock(self):
                pass

            def check_for_jsr(self, routine_name):
                return False

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

            def add_instruction(self, instruction, index=-1):
                self._instructions.append(instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def get_filtered_instructions(self, instruction_filter='', operand_filter=''):
                return []

            def has_instruction(self, instruction):
                return instruction in self._instructions

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRoutine = TestableRoutine

    def test_routine_with_container(self):
        """Test routine initialized with container."""
        routine = self.TestableRoutine(container=self.mock_container)

        self.assertEqual(routine.container, self.mock_container)

    def test_routine_get_container(self):
        """Test getting container from routine."""
        routine = self.TestableRoutine(container=self.mock_container)

        container = routine.get_container()

        self.assertEqual(container, self.mock_container)

    def test_routine_set_container(self):
        """Test setting container after initialization."""
        routine = self.TestableRoutine()

        routine.set_container(self.mock_container)

        self.assertEqual(routine.get_container(), self.mock_container)

    def test_routine_container_not_set_raises_error(self):
        """Test accessing container when not set raises ValueError."""
        routine = self.TestableRoutine()

        with self.assertRaises(ValueError) as context:
            _ = routine.container

        self.assertIn('Container is not set', str(context.exception))

    def test_get_container_not_set_raises_error(self):
        """Test get_container when not set raises ValueError."""
        routine = self.TestableRoutine()

        with self.assertRaises(ValueError) as context:
            routine.get_container()

        self.assertIn('Container is not set', str(context.exception))

    def test_set_container_type_validation(self):
        """Test set_container validates type."""
        routine = self.TestableRoutine()

        with self.assertRaises(TypeError) as context:
            routine.set_container("not a container")  # type: ignore

        self.assertIn('HasRoutines', str(context.exception))


class TestRoutineMetaDataIntegration(unittest.TestCase):
    """Test Routine metadata integration."""

    def test_routine_metadata_as_dict(self):
        """Test routine metadata stored as dict."""
        meta_data = {'@Name': 'MainRoutine', '@Type': 'RLL'}
        routine = Routine(meta_data=meta_data)

        self.assertEqual(routine.meta_data, meta_data)
        self.assertIsInstance(routine.meta_data, dict)

    def test_routine_name_from_metadata(self):
        """Test routine name extracted from metadata."""
        meta_data = {'@Name': 'RoutineFromMeta'}
        routine = Routine(meta_data=meta_data)

        self.assertEqual(routine.name, 'RoutineFromMeta')

    def test_routine_description_from_metadata(self):
        """Test routine description extracted from metadata."""
        meta_data = {'@Name': 'MyRoutine', '@Description': 'Test Routine Description'}
        routine = Routine(meta_data=meta_data)

        self.assertEqual(routine.description, 'Test Routine Description')

    def test_routine_explicit_name_overrides_metadata(self):
        """Test explicit name parameter overrides metadata."""
        meta_data = {'@Name': 'MetaName'}
        routine = Routine(meta_data=meta_data, name='ExplicitName')

        self.assertEqual(routine.name, 'ExplicitName')

    def test_routine_with_empty_metadata(self):
        """Test routine with empty metadata dict."""
        routine = Routine(meta_data={})

        self.assertEqual(routine.meta_data, {})


class TestRoutineInstructionsManagement(unittest.TestCase):
    """Test routine instruction management."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import ILogicInstruction

        self.mock_instruction = Mock(spec=ILogicInstruction)
        self.mock_instruction.name = 'XIC'

        class TestableRoutine(Routine):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.compiled_instructions = False

            def compile_instructions(self):
                self.compiled_instructions = True
                self._instructions = [Mock(spec=ILogicInstruction) for _ in range(3)]

            def compile_rungs(self):
                pass

            def add_rung(self, rung):
                self._rungs.append(rung)

            def remove_rung(self, rung):
                self._rungs.remove(rung)

            def clear_rungs(self):
                self._rungs.clear()

            def block(self):
                pass

            def unblock(self):
                pass

            def check_for_jsr(self, routine_name):
                return False

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

            def add_instruction(self, instruction, index=-1):
                if index == -1:
                    self._instructions.append(instruction)
                else:
                    self._instructions.insert(index, instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def get_filtered_instructions(self, instruction_filter='', operand_filter=''):
                filtered = []
                for instr in self._instructions:
                    if instruction_filter and hasattr(instr, 'name') and instruction_filter in instr.name:
                        filtered.append(instr)
                    elif operand_filter:
                        filtered.append(instr)
                return filtered

            def has_instruction(self, instruction):
                return instruction in self._instructions

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRoutine = TestableRoutine

    def test_get_instructions_triggers_compile(self):
        """Test get_instructions triggers compile when empty."""
        routine = self.TestableRoutine()

        instructions = routine.get_instructions()

        self.assertTrue(routine.compiled_instructions)
        self.assertEqual(len(instructions), 3)

    def test_add_instruction(self):
        """Test adding instruction to routine."""
        routine = self.TestableRoutine()

        routine.add_instruction(self.mock_instruction)

        self.assertIn(self.mock_instruction, routine._instructions)

    def test_add_instruction_at_index(self):
        """Test adding instruction at specific index."""
        routine = self.TestableRoutine()
        routine._instructions = [Mock(), Mock()]

        routine.add_instruction(self.mock_instruction, index=1)

        self.assertEqual(routine._instructions[1], self.mock_instruction)

    def test_remove_instruction(self):
        """Test removing instruction from routine."""
        routine = self.TestableRoutine()
        routine._instructions = [self.mock_instruction]

        routine.remove_instruction(self.mock_instruction)

        self.assertNotIn(self.mock_instruction, routine._instructions)

    def test_clear_instructions(self):
        """Test clearing all instructions."""
        routine = self.TestableRoutine()
        routine._instructions = [Mock(), Mock(), Mock()]

        routine.clear_instructions()

        self.assertEqual(len(routine._instructions), 0)

    def test_has_instruction(self):
        """Test checking if instruction exists."""
        routine = self.TestableRoutine()
        routine._instructions = [self.mock_instruction]

        result = routine.has_instruction(self.mock_instruction)

        self.assertTrue(result)

    def test_get_filtered_instructions(self):
        """Test getting filtered instructions."""
        routine = self.TestableRoutine()
        instr1 = Mock(spec=ILogicInstruction)
        instr1.name = 'XIC'
        instr2 = Mock(spec=ILogicInstruction)
        instr2.name = 'OTE'
        routine._instructions = [instr1, instr2]

        filtered = routine.get_filtered_instructions(instruction_filter='XIC')

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, 'XIC')


class TestRoutineRungsManagement(unittest.TestCase):
    """Test routine rung management."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IRung

        self.mock_rung = Mock(spec=IRung)
        self.mock_rung.number = 0

        class TestableRoutine(Routine):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.compiled_rungs = False

            def compile_instructions(self):
                pass

            def compile_rungs(self):
                self.compiled_rungs = True
                self._rungs = [Mock(spec=IRung) for _ in range(5)]

            def add_rung(self, rung):
                self._rungs.append(rung)

            def remove_rung(self, rung):
                self._rungs.remove(rung)

            def clear_rungs(self):
                self._rungs.clear()

            def block(self):
                pass

            def unblock(self):
                pass

            def check_for_jsr(self, routine_name):
                return False

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

            def add_instruction(self, instruction, index=-1):
                self._instructions.append(instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def get_filtered_instructions(self, instruction_filter='', operand_filter=''):
                return []

            def has_instruction(self, instruction):
                return instruction in self._instructions

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRoutine = TestableRoutine

    def test_get_rungs_triggers_compile(self):
        """Test compile_rungs populates rungs list."""
        routine = self.TestableRoutine()

        # Initially empty
        self.assertFalse(routine.compiled_rungs)
        self.assertEqual(len(routine._rungs), 0)

        # After compile
        routine.compile_rungs()

        self.assertTrue(routine.compiled_rungs)
        self.assertEqual(len(routine.get_rungs()), 5)

    def test_add_rung(self):
        """Test adding rung to routine."""
        routine = self.TestableRoutine()

        routine.add_rung(self.mock_rung)

        self.assertIn(self.mock_rung, routine._rungs)

    def test_remove_rung(self):
        """Test removing rung from routine."""
        routine = self.TestableRoutine()
        routine._rungs = [self.mock_rung]

        routine.remove_rung(self.mock_rung)

        self.assertNotIn(self.mock_rung, routine._rungs)

    def test_clear_rungs(self):
        """Test clearing all rungs."""
        routine = self.TestableRoutine()
        routine._rungs = [Mock(), Mock(), Mock()]

        routine.clear_rungs()

        self.assertEqual(len(routine._rungs), 0)

    def test_rungs_property(self):
        """Test rungs property access."""
        routine = self.TestableRoutine()
        routine._rungs = [Mock(), Mock()]

        rungs = routine.rungs

        self.assertEqual(len(rungs), 2)


class TestRoutineBlockingFunctionality(unittest.TestCase):
    """Test routine blocking and unblocking."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRoutine(Routine):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._blocked = False

            def compile_instructions(self):
                pass

            def compile_rungs(self):
                pass

            def add_rung(self, rung):
                self._rungs.append(rung)

            def remove_rung(self, rung):
                self._rungs.remove(rung)

            def clear_rungs(self):
                self._rungs.clear()

            def block(self):
                self._blocked = True

            def unblock(self):
                self._blocked = False

            def is_blocked(self):
                return self._blocked

            def check_for_jsr(self, routine_name):
                return False

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

            def add_instruction(self, instruction, index=-1):
                self._instructions.append(instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def get_filtered_instructions(self, instruction_filter='', operand_filter=''):
                return []

            def has_instruction(self, instruction):
                return instruction in self._instructions

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRoutine = TestableRoutine

    def test_routine_not_blocked_initially(self):
        """Test routine is not blocked initially."""
        routine = self.TestableRoutine()

        self.assertFalse(routine.is_blocked())

    def test_block_routine(self):
        """Test blocking a routine."""
        routine = self.TestableRoutine()

        routine.block()

        self.assertTrue(routine.is_blocked())

    def test_unblock_routine(self):
        """Test unblocking a routine."""
        routine = self.TestableRoutine()
        routine.block()

        routine.unblock()

        self.assertFalse(routine.is_blocked())

    def test_multiple_block_calls(self):
        """Test multiple block calls."""
        routine = self.TestableRoutine()

        routine.block()
        routine.block()

        self.assertTrue(routine.is_blocked())


class TestRoutineJSRDetection(unittest.TestCase):
    """Test JSR (Jump to Subroutine) detection."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableRoutine(Routine):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._jsr_targets = set()

            def compile_instructions(self):
                pass

            def compile_rungs(self):
                pass

            def add_rung(self, rung):
                self._rungs.append(rung)

            def remove_rung(self, rung):
                self._rungs.remove(rung)

            def clear_rungs(self):
                self._rungs.clear()

            def block(self):
                pass

            def unblock(self):
                pass

            def check_for_jsr(self, routine_name):
                return routine_name in self._jsr_targets

            def add_jsr_target(self, routine_name):
                self._jsr_targets.add(routine_name)

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

            def add_instruction(self, instruction, index=-1):
                self._instructions.append(instruction)

            def clear_instructions(self):
                self._instructions.clear()

            def get_filtered_instructions(self, instruction_filter='', operand_filter=''):
                return []

            def has_instruction(self, instruction):
                return instruction in self._instructions

            def remove_instruction(self, instruction):
                self._instructions.remove(instruction)

        self.TestableRoutine = TestableRoutine

    def test_check_for_jsr_not_found(self):
        """Test checking for JSR when not present."""
        routine = self.TestableRoutine()

        result = routine.check_for_jsr('NonExistentRoutine')

        self.assertFalse(result)

    def test_check_for_jsr_found(self):
        """Test checking for JSR when present."""
        routine = self.TestableRoutine()
        routine.add_jsr_target('SubRoutine')

        result = routine.check_for_jsr('SubRoutine')

        self.assertTrue(result)

    def test_check_for_multiple_jsrs(self):
        """Test checking for multiple JSR targets."""
        routine = self.TestableRoutine()
        routine.add_jsr_target('SubRoutine1')
        routine.add_jsr_target('SubRoutine2')

        result1 = routine.check_for_jsr('SubRoutine1')
        result2 = routine.check_for_jsr('SubRoutine2')
        result3 = routine.check_for_jsr('SubRoutine3')

        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertFalse(result3)


class TestRoutineStringRepresentation(unittest.TestCase):
    """Test routine string representation."""

    def test_routine_str_returns_name(self):
        """Test __str__ returns routine name."""
        routine = Routine(name='MyRoutineName')

        self.assertEqual(str(routine), 'MyRoutineName')

    def test_routine_repr_returns_name(self):
        """Test __repr__ returns routine name."""
        routine = Routine(name='MyRoutineName')

        self.assertEqual(repr(routine), 'MyRoutineName')


class TestRoutineSpecialCases(unittest.TestCase):
    """Test special cases and edge conditions."""

    def test_routine_with_none_values(self):
        """Test routine with None for optional parameters."""
        routine = Routine(
            meta_data=None,
            name=None,
            description=None,
            container=None
        )

        self.assertIsNotNone(routine)

    def test_routine_multiple_property_access(self):
        """Test accessing routine properties multiple times."""
        routine = Routine(name='TestRoutine', description='Test Desc')

        name1 = routine.name
        name2 = routine.name
        desc1 = routine.description
        desc2 = routine.description

        self.assertEqual(name1, name2)
        self.assertEqual(desc1, desc2)

    def test_routine_instructions_property_access(self):
        """Test routine class inherits instructions property from HasInstructions."""
        from controlrox.models.plc.protocols import HasInstructions

        # Verify Routine inherits from HasInstructions
        self.assertTrue(issubclass(Routine, HasInstructions))
        # Verify HasInstructions has the instructions property
        self.assertTrue(hasattr(HasInstructions, 'instructions'))

    def test_routine_initialization_order(self):
        """Test routine initializes properly with various parameter orders."""
        routine1 = Routine(name='Rout1', description='Desc1')
        routine2 = Routine(description='Desc2', name='Rout2')

        self.assertEqual(routine1.name, 'Rout1')
        self.assertEqual(routine2.name, 'Rout2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
