"""Unit tests for controlrox.models.plc.protocols module."""
import unittest
from unittest.mock import Mock, patch

from pyrox.models import HashList

from controlrox.models.plc.protocols import (
    CanBeSafe,
    CanEnableDisable,
    HasAOIs,
    HasController,
    HasDatatypes,
    HasInstructions,
    HasMetaData,
    HasModules,
    HasPrograms,
    HasRoutines,
    HasRungs,
    HasTags,
)


class TestHasMetaData(unittest.TestCase):
    """Test cases for HasMetaData protocol."""

    def test_init_with_no_meta_data(self):
        """Test initialization without meta_data creates empty dict."""
        obj = HasMetaData()

        self.assertEqual(obj._meta_data, {})
        self.assertIsInstance(obj.meta_data, dict)

    def test_init_with_meta_data_dict(self):
        """Test initialization with meta_data dict."""
        meta = {'@Name': 'Test', '@Value': '123'}
        obj = HasMetaData(meta_data=meta)

        self.assertEqual(obj._meta_data, meta)
        self.assertEqual(obj.meta_data, meta)

    def test_get_meta_data(self):
        """Test get_meta_data returns metadata."""
        meta = {'@Name': 'Test'}
        obj = HasMetaData(meta_data=meta)

        result = obj.get_meta_data()

        self.assertEqual(result, meta)

    def test_set_meta_data_with_dict(self):
        """Test set_meta_data with dict."""
        obj = HasMetaData()
        new_meta = {'@Name': 'NewTest'}

        obj.set_meta_data(new_meta)

        self.assertEqual(obj._meta_data, new_meta)

    def test_set_meta_data_with_string(self):
        """Test set_meta_data with string."""
        obj = HasMetaData()
        new_meta = '<RSLogix5000Content></RSLogix5000Content>'

        obj.set_meta_data(new_meta)

        self.assertEqual(obj._meta_data, new_meta)

    def test_set_meta_data_raises_type_error_for_invalid_type(self):
        """Test set_meta_data raises TypeError for invalid type."""
        obj = HasMetaData()

        with self.assertRaises(TypeError) as context:
            obj.set_meta_data(123)  # type: ignore

        self.assertIn('must be a dictionary or a string', str(context.exception))

    def test_meta_data_property_setter(self):
        """Test meta_data property setter."""
        obj = HasMetaData()
        new_meta = {'@Name': 'PropertyTest'}

        obj.meta_data = new_meta

        self.assertEqual(obj._meta_data, new_meta)


class TestCanBeSafe(unittest.TestCase):
    """Test cases for CanBeSafe protocol."""

    def test_init_default_unsafe(self):
        """Test initialization with default unsafe state."""
        obj = CanBeSafe()

        self.assertFalse(obj.is_safe())

    def test_init_with_is_safe_true(self):
        """Test initialization with is_safe=True."""
        obj = CanBeSafe(is_safe=True)

        self.assertTrue(obj.is_safe())

    def test_init_with_is_safe_false(self):
        """Test initialization with is_safe=False."""
        obj = CanBeSafe(is_safe=False)

        self.assertFalse(obj.is_safe())

    def test_set_safe(self):
        """Test set_safe method."""
        obj = CanBeSafe(is_safe=False)

        obj.set_safe()

        self.assertTrue(obj.is_safe())

    def test_set_unsafe(self):
        """Test set_unsafe method."""
        obj = CanBeSafe(is_safe=True)

        obj.set_unsafe()

        self.assertFalse(obj.is_safe())

    def test_is_safe_returns_correct_state(self):
        """Test is_safe returns the correct internal state."""
        obj = CanBeSafe(is_safe=True)

        self.assertTrue(obj.is_safe())
        self.assertEqual(obj._is_safe, obj.is_safe())


class TestCanEnableDisable(unittest.TestCase):
    """Test cases for CanEnableDisable protocol."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class ConcreteCanEnableDisable(CanEnableDisable):
            def enable(self):
                self._enabled = True

            def disable(self):
                self._enabled = False

        self.ConcreteClass = ConcreteCanEnableDisable

    def test_init_default_disabled(self):
        """Test initialization with default disabled state."""
        obj = self.ConcreteClass()

        self.assertFalse(obj.is_enabled())

    def test_init_with_enabled_true(self):
        """Test initialization with enabled=True."""
        obj = self.ConcreteClass(enabled=True)

        self.assertTrue(obj.is_enabled())

    def test_init_with_enabled_false(self):
        """Test initialization with enabled=False."""
        obj = self.ConcreteClass(enabled=False)

        self.assertFalse(obj.is_enabled())

    def test_enable(self):
        """Test enable method."""
        obj = self.ConcreteClass(enabled=False)

        obj.enable()

        self.assertTrue(obj.is_enabled())

    def test_disable(self):
        """Test disable method."""
        obj = self.ConcreteClass(enabled=True)

        obj.disable()

        self.assertFalse(obj.is_enabled())

    def test_is_enabled_returns_correct_state(self):
        """Test is_enabled returns the correct internal state."""
        obj = self.ConcreteClass(enabled=True)

        self.assertTrue(obj.is_enabled())
        self.assertEqual(obj._enabled, obj.is_enabled())

    def test_not_implemented_enable_raises_error(self):
        """Test that base class enable raises NotImplementedError."""
        obj = CanEnableDisable()

        with self.assertRaises(NotImplementedError) as context:
            obj.enable()

        self.assertIn('must be implemented by subclass', str(context.exception))

    def test_not_implemented_disable_raises_error(self):
        """Test that base class disable raises NotImplementedError."""
        obj = CanEnableDisable()

        with self.assertRaises(NotImplementedError) as context:
            obj.disable()

        self.assertIn('must be implemented by subclass', str(context.exception))


class TestHasController(unittest.TestCase):
    """Test cases for HasController protocol."""

    def test_init_with_no_controller(self):
        """Test initialization without controller."""
        obj = HasController()

        self.assertIsNone(obj.controller)

    def test_init_with_controller(self):
        """Test initialization with controller."""
        mock_controller = Mock()
        obj = HasController(controller=mock_controller)

        self.assertEqual(obj.controller, mock_controller)

    def test_get_controller(self):
        """Test get_controller returns controller."""
        mock_controller = Mock()
        obj = HasController(controller=mock_controller)

        result = obj.get_controller()

        self.assertEqual(result, mock_controller)

    def test_set_controller(self):
        """Test set_controller sets controller."""
        obj = HasController()
        mock_controller = Mock()

        obj.set_controller(mock_controller)

        self.assertEqual(obj._controller, mock_controller)

    def test_controller_property_getter(self):
        """Test controller property getter."""
        mock_controller = Mock()
        obj = HasController(controller=mock_controller)

        self.assertEqual(obj.controller, mock_controller)

    def test_controller_property_setter(self):
        """Test controller property setter."""
        obj = HasController()
        mock_controller = Mock()

        obj.controller = mock_controller

        self.assertEqual(obj._controller, mock_controller)


class TestHasAOIs(unittest.TestCase):
    """Test cases for HasAOIs protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasAOIs(HasAOIs):
            def get_raw_aois(self):
                return []

            def add_aoi(self, aoi, inhibit_invalidate=False):
                self._aois.append(aoi)

            def remove_aoi(self, aoi, inhibit_invalidate=False):
                self._aois.remove(aoi)

            def compile_aois(self):
                pass

        self.ConcreteClass = ConcreteHasAOIs

    def test_init_creates_empty_aoi_list(self):
        """Test initialization creates empty AOI list."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._aois, HashList)
        self.assertEqual(len(obj._aois), 0)

    def test_aois_property(self):
        """Test aois property."""
        obj = self.ConcreteClass()

        aois = obj.aois

        self.assertIsInstance(aois, HashList)

    def test_get_aois(self):
        """Test get_aois returns the AOI list."""
        obj = self.ConcreteClass()

        aois = obj.get_aois()

        self.assertIsInstance(aois, HashList)

    def test_add_aois_bulk(self):
        """Test add_aois adds multiple AOIs then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_aois = [Mock(), Mock(), Mock()]

        obj.add_aois(mock_aois)

        # Note: add_aois calls invalidate_aois which clears the list
        self.assertEqual(len(obj._aois), 0)

    def test_remove_aois_bulk(self):
        """Test remove_aois removes multiple AOIs."""
        obj = self.ConcreteClass()
        mock_aois = [Mock(), Mock(), Mock()]
        obj._aois.extend(mock_aois)

        obj.remove_aois(mock_aois)

        self.assertEqual(len(obj._aois), 0)

    def test_invalidate_aois(self):
        """Test invalidate_aois clears the list."""
        obj = self.ConcreteClass()
        obj._aois.extend([Mock(), Mock()])

        obj.invalidate_aois()

        self.assertEqual(len(obj._aois), 0)

    def test_get_raw_aois_not_implemented(self):
        """Test get_raw_aois raises NotImplementedError in base class."""
        obj = HasAOIs()

        with self.assertRaises(NotImplementedError):
            obj.get_raw_aois()

    def test_compile_aois_not_implemented(self):
        """Test compile_aois raises NotImplementedError in base class."""
        obj = HasAOIs()

        with self.assertRaises(NotImplementedError):
            obj.compile_aois()


class TestHasDatatypes(unittest.TestCase):
    """Test cases for HasDatatypes protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasDatatypes(HasDatatypes):
            def get_raw_datatypes(self):
                return []

            def add_datatype(self, datatype, inhibit_invalidate=False):
                self._datatypes.append(datatype)

            def remove_datatype(self, datatype, inhibit_invalidate=False):
                self._datatypes.remove(datatype)

            def compile_datatypes(self):
                pass

        self.ConcreteClass = ConcreteHasDatatypes

    def test_init_creates_empty_datatype_list(self):
        """Test initialization creates empty datatype list."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._datatypes, HashList)
        self.assertEqual(len(obj._datatypes), 0)

    def test_datatypes_property(self):
        """Test datatypes property."""
        obj = self.ConcreteClass()

        datatypes = obj.datatypes

        self.assertIsInstance(datatypes, HashList)

    def test_get_datatypes(self):
        """Test get_datatypes returns the datatype list."""
        obj = self.ConcreteClass()

        datatypes = obj.get_datatypes()

        self.assertIsInstance(datatypes, HashList)

    def test_add_datatypes_bulk(self):
        """Test add_datatypes adds multiple datatypes then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_datatypes = [Mock(), Mock(), Mock()]

        obj.add_datatypes(mock_datatypes)

        # Note: add_datatypes calls invalidate_datatypes which clears the list
        self.assertEqual(len(obj._datatypes), 0)

    def test_remove_datatypes_bulk(self):
        """Test remove_datatypes removes multiple datatypes."""
        obj = self.ConcreteClass()
        mock_datatypes = [Mock(), Mock(), Mock()]
        obj._datatypes.extend(mock_datatypes)

        obj.remove_datatypes(mock_datatypes)

        self.assertEqual(len(obj._datatypes), 0)

    def test_invalidate_datatypes(self):
        """Test invalidate_datatypes clears the list."""
        obj = self.ConcreteClass()
        obj._datatypes.extend([Mock(), Mock()])

        obj.invalidate_datatypes()

        self.assertEqual(len(obj._datatypes), 0)

    def test_get_raw_datatypes_not_implemented(self):
        """Test get_raw_datatypes raises NotImplementedError in base class."""
        obj = HasDatatypes()

        with self.assertRaises(NotImplementedError):
            obj.get_raw_datatypes()

    def test_compile_datatypes_not_implemented(self):
        """Test compile_datatypes raises NotImplementedError in base class."""
        obj = HasDatatypes()

        with self.assertRaises(NotImplementedError):
            obj.compile_datatypes()


class TestHasModules(unittest.TestCase):
    """Test cases for HasModules protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasModules(HasModules):
            def get_raw_modules(self):
                return []

            def add_module(self, module, inhibit_invalidate=False):
                self._modules.append(module)

            def remove_module(self, module, inhibit_invalidate=False):
                self._modules.remove(module)

            def compile_modules(self):
                pass

        self.ConcreteClass = ConcreteHasModules

    def test_init_creates_empty_module_list(self):
        """Test initialization creates empty module list."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._modules, HashList)
        self.assertEqual(len(obj._modules), 0)

    def test_modules_property(self):
        """Test modules property."""
        obj = self.ConcreteClass()

        modules = obj.modules

        self.assertIsInstance(modules, HashList)

    def test_get_modules(self):
        """Test get_modules returns the module list."""
        obj = self.ConcreteClass()

        modules = obj.get_modules()

        self.assertIsInstance(modules, HashList)

    def test_add_modules_bulk(self):
        """Test add_modules adds multiple modules then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_modules = [Mock(), Mock(), Mock()]

        obj.add_modules(mock_modules)

        # Note: add_modules calls invalidate_modules which clears the list
        self.assertEqual(len(obj._modules), 0)

    def test_remove_modules_bulk(self):
        """Test remove_modules removes multiple modules."""
        obj = self.ConcreteClass()
        mock_modules = [Mock(), Mock(), Mock()]
        obj._modules.extend(mock_modules)

        obj.remove_modules(mock_modules)

        self.assertEqual(len(obj._modules), 0)

    def test_invalidate_modules(self):
        """Test invalidate_modules clears the list."""
        obj = self.ConcreteClass()
        obj._modules.extend([Mock(), Mock()])

        obj.invalidate_modules()

        self.assertEqual(len(obj._modules), 0)

    def test_get_raw_modules_not_implemented(self):
        """Test get_raw_modules raises NotImplementedError in base class."""
        obj = HasModules()

        with self.assertRaises(NotImplementedError):
            obj.get_raw_modules()

    def test_compile_modules_not_implemented(self):
        """Test compile_modules raises NotImplementedError in base class."""
        obj = HasModules()

        with self.assertRaises(NotImplementedError):
            obj.compile_modules()


class TestHasInstructions(unittest.TestCase):
    """Test cases for HasInstructions protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasInstructions(HasInstructions):
            def compile_instructions(self):
                self._instructions = [Mock(), Mock()]
                self._input_instructions = [Mock()]
                self._output_instructions = [Mock()]

            def add_instruction(self, instruction, inhibit_invalidate=False):
                self._instructions.append(instruction)

            def remove_instruction(self, instruction, inhibit_invalidate=False):
                self._instructions.remove(instruction)

            def get_raw_instructions(self):
                return []

            def get_filtered_instructions(self, instruction_filter='', operand_filter=''):
                return []

            def has_instruction(self, instruction):
                return instruction in self._instructions

            def clear_instructions(self):
                self._instructions.clear()

        self.ConcreteClass = ConcreteHasInstructions

    def test_init_creates_empty_instruction_lists(self):
        """Test initialization creates empty instruction lists."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._instructions, list)
        self.assertIsInstance(obj._input_instructions, list)
        self.assertIsInstance(obj._output_instructions, list)
        self.assertEqual(len(obj._instructions), 0)

    def test_instructions_property(self):
        """Test instructions property."""
        obj = self.ConcreteClass()

        instructions = obj.instructions

        self.assertIsInstance(instructions, list)

    def test_get_instructions_calls_compile(self):
        """Test get_instructions calls compile_instructions if empty."""
        obj = self.ConcreteClass()

        instructions = obj.get_instructions()

        self.assertEqual(len(instructions), 2)

    def test_get_instructions_returns_cached(self):
        """Test get_instructions returns cached instructions."""
        obj = self.ConcreteClass()
        obj._instructions = [Mock(), Mock(), Mock()]

        instructions = obj.get_instructions()

        self.assertEqual(len(instructions), 3)

    def test_get_instructions_with_filters(self):
        """Test get_instructions with filters calls get_filtered_instructions."""
        obj = self.ConcreteClass()
        obj._instructions = [Mock(), Mock()]

        with patch.object(obj, 'get_filtered_instructions', return_value=[Mock()]) as mock_filter:
            instructions = obj.get_instructions(instruction_filter='XIC', operand_filter='Tag')

            mock_filter.assert_called_once_with(instruction_filter='XIC', operand_filter='Tag')
            self.assertEqual(len(instructions), 1)

    def test_get_input_instructions(self):
        """Test get_input_instructions."""
        obj = self.ConcreteClass()

        instructions = obj.get_input_instructions()

        self.assertEqual(len(instructions), 1)

    def test_get_output_instructions(self):
        """Test get_output_instructions."""
        obj = self.ConcreteClass()

        instructions = obj.get_output_instructions()

        self.assertEqual(len(instructions), 1)

    def test_add_instructions_bulk(self):
        """Test add_instructions adds multiple instructions then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_instructions = [Mock(), Mock(), Mock()]

        obj.add_instructions(mock_instructions)

        # Note: add_instructions calls invalidate_instructions which clears the list
        self.assertEqual(len(obj._instructions), 0)

    def test_remove_instructions_bulk(self):
        """Test remove_instructions removes multiple instructions."""
        obj = self.ConcreteClass()
        mock_instructions = [Mock(), Mock(), Mock()]
        obj._instructions.extend(mock_instructions)

        obj.remove_instructions(mock_instructions)

        self.assertEqual(len(obj._instructions), 0)

    def test_invalidate_instructions(self):
        """Test invalidate_instructions clears all lists."""
        obj = self.ConcreteClass()
        obj._instructions = [Mock()]
        obj._input_instructions = [Mock()]
        obj._output_instructions = [Mock()]

        obj.invalidate_instructions()

        self.assertEqual(len(obj._instructions), 0)
        self.assertEqual(len(obj._input_instructions), 0)
        self.assertEqual(len(obj._output_instructions), 0)

    def test_set_instructions_with_valid_instructions(self):
        """Test set_instructions with valid instructions."""
        from controlrox.interfaces import ILogicInstruction
        obj = self.ConcreteClass()
        mock_instructions = [Mock(spec=ILogicInstruction), Mock(spec=ILogicInstruction)]

        obj.set_instructions(mock_instructions)

        self.assertEqual(obj._instructions, mock_instructions)

    def test_set_instructions_raises_type_error_for_invalid_type(self):
        """Test set_instructions raises TypeError for invalid instruction."""
        obj = self.ConcreteClass()
        invalid_instructions = [Mock(), "not an instruction"]

        with self.assertRaises(TypeError) as context:
            obj.set_instructions(invalid_instructions)  # type: ignore

        self.assertIn('must implement ILogicInstruction', str(context.exception))

    def test_compile_instructions_not_implemented(self):
        """Test compile_instructions raises NotImplementedError in base class."""
        obj = HasInstructions()

        with self.assertRaises(NotImplementedError):
            obj.compile_instructions()


class TestHasRoutines(unittest.TestCase):
    """Test cases for HasRoutines protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasRoutines(HasRoutines):
            def compile_routines(self):
                self._routines.extend([Mock(), Mock()])

            def get_main_routine(self):
                return self._routines[0] if self._routines else None

            def get_raw_routines(self):
                return []

            def add_routine(self, routine, inhibit_invalidate=False):
                self._routines.append(routine)

            def remove_routine(self, routine, inhibit_invalidate=False):
                self._routines.remove(routine)

            def block_routine(self, routine_name, blocking_bit):
                pass

            def unblock_routine(self, routine_name, blocking_bit):
                pass

        self.ConcreteClass = ConcreteHasRoutines

    def test_init_creates_empty_routine_list(self):
        """Test initialization creates empty routine list."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._routines, HashList)
        self.assertEqual(len(obj._routines), 0)

    def test_routines_property(self):
        """Test routines property."""
        obj = self.ConcreteClass()

        routines = obj.routines

        self.assertIsInstance(routines, HashList)

    def test_get_routines_calls_compile(self):
        """Test get_routines calls compile_routines if empty."""
        obj = self.ConcreteClass()

        routines = obj.get_routines()

        self.assertEqual(len(routines), 2)

    def test_get_routines_returns_cached(self):
        """Test get_routines returns cached routines."""
        obj = self.ConcreteClass()
        obj._routines.extend([Mock(), Mock(), Mock()])

        routines = obj.get_routines()

        self.assertEqual(len(routines), 3)

    def test_add_routines_bulk(self):
        """Test add_routines adds multiple routines then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_routines = [Mock(), Mock(), Mock()]

        obj.add_routines(mock_routines)

        # Note: add_routines calls invalidate_routines which clears the list
        self.assertEqual(len(obj._routines), 0)

    def test_remove_routines_bulk(self):
        """Test remove_routines removes multiple routines."""
        obj = self.ConcreteClass()
        mock_routines = [Mock(), Mock(), Mock()]
        obj._routines.extend(mock_routines)

        obj.remove_routines(mock_routines)

        self.assertEqual(len(obj._routines), 0)

    def test_invalidate_routines(self):
        """Test invalidate_routines clears the list."""
        obj = self.ConcreteClass()
        obj._routines.extend([Mock(), Mock()])

        obj.invalidate_routines()

        self.assertEqual(len(obj._routines), 0)

    def test_compile_routines_not_implemented(self):
        """Test that base class compile_routines raises NotImplementedError."""
        obj = HasRoutines()

        with self.assertRaises(NotImplementedError):
            obj.compile_routines()

    def test_get_main_routine_not_implemented(self):
        """Test that base class get_main_routine raises NotImplementedError."""
        obj = HasRoutines()

        with self.assertRaises(NotImplementedError):
            obj.get_main_routine()


class TestHasRungs(unittest.TestCase):
    """Test cases for HasRungs protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasRungs(HasRungs):
            def compile_rungs(self):
                self._rungs.extend([Mock(), Mock()])

            def add_rung(self, rung, inhibit_invalidate=False):
                self._rungs.append(rung)

            def remove_rung(self, rung, inhibit_invalidate=False):
                self._rungs.remove(rung)

            def get_raw_rungs(self):
                return []

            def clear_rungs(self):
                self._rungs.clear()

        self.ConcreteClass = ConcreteHasRungs

    def test_init_creates_empty_rung_list(self):
        """Test initialization creates empty rung list."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._rungs, list)
        self.assertEqual(len(obj._rungs), 0)

    def test_rungs_property(self):
        """Test rungs property."""
        obj = self.ConcreteClass()

        rungs = obj.rungs

        self.assertIsInstance(rungs, list)

    def test_get_rungs_calls_compile(self):
        """Test get_rungs calls compile_rungs if empty."""
        obj = self.ConcreteClass()

        rungs = obj.get_rungs()

        self.assertEqual(len(rungs), 2)

    def test_get_rungs_returns_cached(self):
        """Test get_rungs returns cached rungs."""
        obj = self.ConcreteClass()
        obj._rungs = [Mock(), Mock(), Mock()]

        rungs = obj.get_rungs()

        self.assertEqual(len(rungs), 3)

    def test_add_rungs_bulk(self):
        """Test add_rungs adds multiple rungs then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_rungs = [Mock(), Mock(), Mock()]

        obj.add_rungs(mock_rungs)

        # Note: add_rungs calls invalidate_rungs which clears the list
        self.assertEqual(len(obj._rungs), 0)

    def test_remove_rungs_bulk(self):
        """Test remove_rungs removes multiple rungs."""
        obj = self.ConcreteClass()
        mock_rungs = [Mock(), Mock(), Mock()]
        obj._rungs.extend(mock_rungs)

        obj.remove_rungs(mock_rungs)

        self.assertEqual(len(obj._rungs), 0)

    def test_invalidate_rungs(self):
        """Test invalidate_rungs clears the list."""
        obj = self.ConcreteClass()
        obj._rungs.extend([Mock(), Mock()])

        obj.invalidate_rungs()

        self.assertEqual(len(obj._rungs), 0)

    def test_compile_rungs_not_implemented(self):
        """Test that base class compile_rungs raises NotImplementedError."""
        obj = HasRungs()

        with self.assertRaises(NotImplementedError):
            obj.compile_rungs()


class TestHasPrograms(unittest.TestCase):
    """Test cases for HasPrograms protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasPrograms(HasPrograms):
            def compile_programs(self):
                safe_prog = Mock()
                safe_prog.is_safe.return_value = True
                standard_prog = Mock()
                standard_prog.is_safe.return_value = False

                self._programs.extend([safe_prog, standard_prog])

            def add_program(self, program, inhibit_invalidate=False):
                self._programs.append(program)

            def remove_program(self, program, inhibit_invalidate=False):
                self._programs.remove(program)

            def get_raw_programs(self):
                return []

        self.ConcreteClass = ConcreteHasPrograms

    def test_init_creates_empty_program_lists(self):
        """Test initialization creates empty program lists."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._programs, HashList)
        self.assertIsInstance(obj._safety_programs, HashList)
        self.assertIsInstance(obj._standard_programs, HashList)
        self.assertEqual(len(obj._programs), 0)

    def test_programs_property(self):
        """Test programs property."""
        obj = self.ConcreteClass()

        programs = obj.programs

        self.assertIsInstance(programs, HashList)

    def test_get_programs_calls_compile(self):
        """Test get_programs calls compile_programs if empty."""
        obj = self.ConcreteClass()

        programs = obj.get_programs()

        self.assertEqual(len(programs), 2)

    def test_get_programs_returns_cached(self):
        """Test get_programs returns cached programs."""
        obj = self.ConcreteClass()
        obj._programs.extend([Mock(), Mock(), Mock()])

        programs = obj.get_programs()

        self.assertEqual(len(programs), 3)

    def test_compile_safety_programs(self):
        """Test compile_safety_programs filters safe programs."""
        obj = self.ConcreteClass()
        obj.compile_programs()

        obj.compile_safety_programs()

        self.assertEqual(len(obj._safety_programs), 1)
        self.assertTrue(obj._safety_programs[0].is_safe())

    def test_compile_standard_programs(self):
        """Test compile_standard_programs filters standard programs."""
        obj = self.ConcreteClass()
        obj.compile_programs()

        obj.compile_standard_programs()

        self.assertEqual(len(obj._standard_programs), 1)
        self.assertFalse(obj._standard_programs[0].is_safe())

    def test_get_safety_programs(self):
        """Test get_safety_programs."""
        obj = self.ConcreteClass()
        obj.compile_programs()

        programs = obj.get_safety_programs()

        self.assertEqual(len(programs), 1)

    def test_get_standard_programs(self):
        """Test get_standard_programs."""
        obj = self.ConcreteClass()
        obj.compile_programs()

        programs = obj.get_standard_programs()

        self.assertEqual(len(programs), 1)

    def test_add_programs_bulk(self):
        """Test add_programs adds multiple programs then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_programs = [Mock(), Mock(), Mock()]

        obj.add_programs(mock_programs)

        # Note: add_programs calls invalidate_programs which clears all program lists
        self.assertEqual(len(obj._programs), 0)

    def test_remove_programs_bulk(self):
        """Test remove_programs removes multiple programs."""
        obj = self.ConcreteClass()
        mock_programs = [Mock(), Mock(), Mock()]
        obj._programs.extend(mock_programs)

        obj.remove_programs(mock_programs)

        self.assertEqual(len(obj._programs), 0)

    def test_invalidate_programs(self):
        """Test invalidate_programs clears all lists."""
        obj = self.ConcreteClass()
        obj._programs.extend([Mock()])
        obj._safety_programs.extend([Mock()])
        obj._standard_programs.extend([Mock()])

        obj.invalidate_programs()

        self.assertEqual(len(obj._programs), 0)
        self.assertEqual(len(obj._safety_programs), 0)
        self.assertEqual(len(obj._standard_programs), 0)

    def test_set_programs_with_valid_programs(self):
        """Test set_programs with valid programs."""
        from controlrox.interfaces import IProgram
        obj = self.ConcreteClass()
        mock_programs = [Mock(spec=IProgram), Mock(spec=IProgram)]

        obj.set_programs(mock_programs)

        self.assertEqual(len(obj._programs), 2)

    def test_set_programs_raises_type_error_for_invalid_type(self):
        """Test set_programs raises TypeError for invalid program."""
        obj = self.ConcreteClass()
        invalid_programs = [Mock(), "not a program"]

        with self.assertRaises(TypeError) as context:
            obj.set_programs(invalid_programs)  # type: ignore

        self.assertIn('must implement IProgram', str(context.exception))

    def test_compile_programs_not_implemented(self):
        """Test compile_programs raises NotImplementedError in base class."""
        obj = HasPrograms()

        with self.assertRaises(NotImplementedError):
            obj.compile_programs()


class TestHasTags(unittest.TestCase):
    """Test cases for HasTags protocol."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteHasTags(HasTags):
            def compile_tags(self):
                self._tags.extend([Mock(), Mock()])
                self._safety_tags.extend([Mock()])
                self._standard_tags.extend([Mock()])

            def add_tag(self, tag, inhibit_invalidate=False):
                self._tags.append(tag)

            def remove_tag(self, tag, inhibit_invalidate=False):
                self._tags.remove(tag)

            def get_raw_tags(self):
                return []

        self.ConcreteClass = ConcreteHasTags

    def test_init_creates_empty_tag_lists(self):
        """Test initialization creates empty tag lists."""
        obj = self.ConcreteClass()

        self.assertIsInstance(obj._tags, HashList)
        self.assertIsInstance(obj._safety_tags, HashList)
        self.assertIsInstance(obj._standard_tags, HashList)
        self.assertEqual(len(obj._tags), 0)

    def test_tags_property(self):
        """Test tags property."""
        obj = self.ConcreteClass()

        tags = obj.tags

        self.assertIsInstance(tags, HashList)

    def test_get_tags_calls_compile(self):
        """Test get_tags calls compile_tags if empty."""
        obj = self.ConcreteClass()

        tags = obj.get_tags()

        self.assertEqual(len(tags), 2)

    def test_get_tags_returns_cached(self):
        """Test get_tags returns cached tags."""
        obj = self.ConcreteClass()
        obj._tags.extend([Mock(), Mock(), Mock()])

        tags = obj.get_tags()

        self.assertEqual(len(tags), 3)

    def test_get_safety_tags_calls_compile(self):
        """Test get_safety_tags calls compile_tags if empty."""
        obj = self.ConcreteClass()

        tags = obj.get_safety_tags()

        self.assertEqual(len(tags), 1)

    def test_get_safety_tags_returns_cached(self):
        """Test get_safety_tags returns cached tags."""
        obj = self.ConcreteClass()
        obj._safety_tags.extend([Mock(), Mock()])

        tags = obj.get_safety_tags()

        self.assertEqual(len(tags), 2)

    def test_get_standard_tags_calls_compile(self):
        """Test get_standard_tags calls compile_tags if empty."""
        obj = self.ConcreteClass()

        tags = obj.get_standard_tags()

        self.assertEqual(len(tags), 1)

    def test_get_standard_tags_returns_cached(self):
        """Test get_standard_tags returns cached tags."""
        obj = self.ConcreteClass()
        obj._standard_tags.extend([Mock(), Mock(), Mock()])

        tags = obj.get_standard_tags()

        self.assertEqual(len(tags), 3)

    def test_add_tags_bulk(self):
        """Test add_tags adds multiple tags then invalidates (clears)."""
        obj = self.ConcreteClass()
        mock_tags = [Mock(), Mock(), Mock()]

        obj.add_tags(mock_tags)

        # Note: add_tags calls invalidate_tags which clears all tag lists
        self.assertEqual(len(obj._tags), 0)

    def test_remove_tags_bulk(self):
        """Test remove_tags removes multiple tags."""
        obj = self.ConcreteClass()
        mock_tags = [Mock(), Mock(), Mock()]
        obj._tags.extend(mock_tags)

        obj.remove_tags(mock_tags)

        self.assertEqual(len(obj._tags), 0)

    def test_invalidate_tags(self):
        """Test invalidate_tags clears all lists."""
        obj = self.ConcreteClass()
        obj._tags.extend([Mock()])
        obj._safety_tags.extend([Mock()])
        obj._standard_tags.extend([Mock()])

        obj.invalidate_tags()

        self.assertEqual(len(obj._tags), 0)
        self.assertEqual(len(obj._safety_tags), 0)
        self.assertEqual(len(obj._standard_tags), 0)

    def test_compile_tags_not_implemented(self):
        """Test that base class compile_tags raises NotImplementedError."""
        class ConcreteHasTagsMinimal(HasTags):
            def get_raw_tags(self):
                return []

        obj = ConcreteHasTagsMinimal()

        with self.assertRaises(NotImplementedError):
            obj.compile_tags()


if __name__ == '__main__':
    unittest.main(verbosity=2)
