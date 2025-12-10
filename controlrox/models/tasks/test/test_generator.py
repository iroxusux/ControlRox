"""Unit tests for controlrox.models.plc.generator module."""
import unittest
from unittest.mock import Mock, patch

from controlrox.interfaces import (
    IModule,
    IRoutine,
    IRung,
    ITag,
    ModuleControlsType,
)
from controlrox.models.plc.controller import Controller
from controlrox.models.tasks.mod import ControllerModificationSchema
from controlrox.models.tasks.generator import EmulationGenerator


class TestEmulationGenerator(unittest.TestCase):
    """Test cases for EmulationGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self) -> str:
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self) -> str:
                return 'StandardProgram'

            @property
            def base_tags(self):
                return [
                    ('Uninhibit', 'DINT', 'Uninhibit tag'),
                    ('Inhibit', 'DINT', 'Inhibit tag'),
                    ('ToggleInhibit', 'BOOL', 'Toggle inhibit'),
                    ('LocalMode', 'DINT', 'Local mode'),
                ]

            @property
            def custom_tags(self):
                return [
                    ('CustomTag1', 'BOOL', 'Custom tag 1', None),
                    ('CustomTag2', 'DINT', 'Custom tag 2', '10'),
                ]

            @property
            def uninhibit_tag(self):
                return self.base_tags[0][0]

            @property
            def inhibit_tag(self):
                return self.base_tags[1][0]

            @property
            def toggle_inhibit_tag(self):
                return self.base_tags[2][0]

            @property
            def local_mode_tag(self):
                return self.base_tags[3][0]

            @property
            def test_mode_tag(self):
                return 'TestMode'

            @property
            def emulation_safety_routine(self):
                return self._emulation_safety_routine

            @property
            def emulation_standard_routine(self):
                return self._emulation_standard_routine

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_safety_routine_description(self):
                return 'Safety emulation routine'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

            def get_emulation_standard_routine_description(self):
                return 'Standard emulation routine'

            def set_emulation_safety_routine(self, routine):
                self._emulation_safety_routine = routine

            def set_emulation_standard_routine(self, routine):
                self._emulation_standard_routine = routine

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = Mock()
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    def test_init_with_controller(self):
        """Test initialization with controller."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        self.assertIs(generator.controller, self.mock_controller)
        self.assertIsInstance(generator.schema, ControllerModificationSchema)
        self.assertIsNone(generator._emulation_standard_routine)
        self.assertIsNone(generator._emulation_safety_routine)

    def test_init_creates_schema(self):
        """Test that initialization creates a ControllerModificationSchema."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        self.assertIsNotNone(generator.schema)
        self.assertIsInstance(generator.schema, ControllerModificationSchema)
        self.assertIs(generator.schema.destination, self.mock_controller)

    def test_controller_property_raises_when_not_set(self):
        """Test controller property raises ValueError when not set."""
        generator = self.ConcreteClass.__new__(self.ConcreteClass)
        generator._controller = None

        with self.assertRaises(ValueError) as context:
            _ = generator.controller

        self.assertIn("Controller is not set", str(context.exception))

    def test_emulation_safety_program_name_property(self):
        """Test emulation_safety_program_name property."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        self.assertEqual(generator.emulation_safety_program_name, 'SafetyProgram')

    def test_emulation_standard_program_name_property(self):
        """Test emulation_standard_program_name property."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        self.assertEqual(generator.emulation_standard_program_name, 'StandardProgram')

    def test_get_factory_returns_factory_class(self):
        """Test get_factory class method."""
        from controlrox.services.tasks.generator import EmulationGeneratorFactory

        factory = self.ConcreteClass.get_factory()

        self.assertIs(factory, EmulationGeneratorFactory)

    def test_base_tags_property(self):
        """Test base_tags property returns expected tags."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        tags = generator.base_tags

        self.assertEqual(len(tags), 4)
        self.assertEqual(tags[0][0], 'Uninhibit')
        self.assertEqual(tags[1][0], 'Inhibit')
        self.assertEqual(tags[2][0], 'ToggleInhibit')
        self.assertEqual(tags[3][0], 'LocalMode')

    def test_custom_tags_property(self):
        """Test custom_tags property returns expected tags."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        tags = generator.custom_tags

        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0][0], 'CustomTag1')
        self.assertEqual(tags[1][0], 'CustomTag2')


class TestEmulationGeneratorHelperMethods(unittest.TestCase):
    """Test cases for EmulationGenerator helper methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self):
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self):
                return 'StandardProgram'

            @property
            def base_tags(self):
                return [('Tag1', 'BOOL', 'Description')]

            @property
            def custom_tags(self):  # type: ignore[override]
                return [('Tag2', 'DINT', 'Description', None)]

            @property
            def uninhibit_tag(self):
                return 'Uninhibit'

            @property
            def inhibit_tag(self):
                return 'Inhibit'

            @property
            def toggle_inhibit_tag(self):
                return 'ToggleInhibit'

            @property
            def local_mode_tag(self):
                return 'LocalMode'

            @property
            def test_mode_tag(self):
                return 'TestMode'

            @property
            def emulation_safety_routine(self):
                return self._emulation_safety_routine

            @property
            def emulation_standard_routine(self):
                return self._emulation_standard_routine

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_safety_routine_description(self):
                return 'Safety emulation routine'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

            def get_emulation_standard_routine_description(self):
                return 'Standard emulation routine'

            def set_emulation_safety_routine(self, routine):
                self._emulation_safety_routine = routine

            def set_emulation_standard_routine(self, routine):
                self._emulation_standard_routine = routine

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = Mock()
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    def test_add_rung_common(self):
        """Test _add_rung_common helper method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_rung = Mock(spec=IRung)
        generator.schema.add_rung = Mock()

        generator._add_rung_common(
            rung=mock_rung,
            program_name='TestProgram',
            routine_name='TestRoutine'
        )

        generator.schema.add_rung.assert_called_once_with(
            program_name='TestProgram',
            routine_name='TestRoutine',
            rung=mock_rung
        )

    def test_add_l5x_imports(self):
        """Test add_l5x_imports method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.add_import_from_file = Mock()

        imports = [
            ('/path/to/file1.L5X', ['Datatype', 'Tag']),
            ('/path/to/file2.L5X', ['AOI']),
        ]

        generator.add_l5x_imports(imports)

        self.assertEqual(generator.schema.add_import_from_file.call_count, 2)
        generator.schema.add_import_from_file.assert_any_call(
            file_location='/path/to/file1.L5X',
            asset_types=['Datatype', 'Tag']
        )
        generator.schema.add_import_from_file.assert_any_call(
            file_location='/path/to/file2.L5X',
            asset_types=['AOI']
        )

    def test_add_controller_tag(self):
        """Test add_controller_tag method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_tag = Mock(spec=ITag)
        self.mock_controller.create_tag = Mock(return_value=mock_tag)
        generator.schema.add_controller_tag = Mock(return_value=mock_tag)

        result = generator.add_controller_tag(
            tag_name='TestTag',
            datatype='BOOL',
            description='Test description'
        )

        self.assertIs(result, mock_tag)
        generator.schema.add_controller_tag.assert_called_once()

    def test_add_controller_tags(self):
        """Test add_controller_tags method with multiple tags."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.add_controller_tag = Mock()

        tags = [
            {'tag_name': 'Tag1', 'datatype': 'BOOL', 'description': 'First'},
            {'tag_name': 'Tag2', 'datatype': 'DINT', 'description': 'Second'},
        ]

        generator.add_controller_tags(tags)

        self.assertEqual(generator.add_controller_tag.call_count, 2)

    def test_add_program_tag(self):
        """Test add_program_tag method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_tag = Mock(spec=ITag)
        self.mock_controller.create_tag = Mock(return_value=mock_tag)
        generator.schema.add_program_tag = Mock(return_value=mock_tag)

        result = generator.add_program_tag(
            program_name='TestProgram',
            tag_name='TestTag',
            datatype='BOOL'
        )

        self.assertIs(result, mock_tag)
        generator.schema.add_program_tag.assert_called_once()

    def test_add_routine(self):
        """Test add_routine method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        mock_routine.name = 'TestRoutine'
        self.mock_controller.create_routine = Mock(return_value=mock_routine)
        generator.schema.add_routine = Mock()
        self.mock_controller.programs.get = Mock(return_value=None)

        result = generator.add_routine(
            program_name='TestProgram',
            routine_name='TestRoutine',
            routine_description='Test Description',
            call_from_main=False
        )

        self.assertIs(result, mock_routine)
        mock_routine.set_name.assert_called_once_with('TestRoutine')
        mock_routine.set_description.assert_called_once_with('Test Description')
        generator.schema.add_routine.assert_called_once()

    def test_add_routine_with_jsr_call(self):
        """Test add_routine with JSR call to main routine."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        mock_routine.name = 'TestRoutine'
        mock_main_routine = Mock()
        mock_main_routine.name = 'MainRoutine'
        mock_main_routine.check_for_jsr = Mock(return_value=False)
        mock_program = Mock()
        mock_program.get_main_routine = Mock(return_value=mock_main_routine)

        self.mock_controller.create_routine = Mock(return_value=mock_routine)
        self.mock_controller.programs.get = Mock(return_value=mock_program)
        generator.schema.add_routine = Mock()
        generator.schema.add_rung = Mock()

        result = generator.add_routine(
            program_name='TestProgram',
            routine_name='TestRoutine',
            routine_description='Test Description',
            call_from_main=True,
            rung_position=0
        )

        self.assertIs(result, mock_routine)
        generator.schema.add_rung.assert_called_once()
        call_args = generator.schema.add_rung.call_args
        self.assertEqual(call_args.kwargs['program_name'], 'TestProgram')
        self.assertEqual(call_args.kwargs['routine_name'], 'MainRoutine')
        self.assertEqual(call_args.kwargs['rung_number'], 0)

    def test_add_routine_skips_jsr_if_exists(self):
        """Test add_routine skips JSR if already exists."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        mock_routine.name = 'TestRoutine'
        mock_main_routine = Mock()
        mock_main_routine.name = 'MainRoutine'
        mock_main_routine.check_for_jsr = Mock(return_value=True)
        mock_program = Mock()
        mock_program.get_main_routine = Mock(return_value=mock_main_routine)

        self.mock_controller.create_routine = Mock(return_value=mock_routine)
        self.mock_controller.programs.get = Mock(return_value=mock_program)
        generator.schema.add_routine = Mock()
        generator.schema.add_rung = Mock()

        result = generator.add_routine(
            program_name='TestProgram',
            routine_name='TestRoutine',
            routine_description='Test Description',
            call_from_main=True
        )

        self.assertIs(result, mock_routine)
        generator.schema.add_rung.assert_not_called()

    def test_add_rung(self):
        """Test add_rung method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_rung = Mock(spec=IRung)
        generator.schema.add_rung = Mock(return_value=mock_rung)

        result = generator.add_rung(
            program_name='TestProgram',
            routine_name='TestRoutine',
            new_rung=mock_rung,
            rung_number=5
        )

        self.assertIs(result, mock_rung)
        generator.schema.add_rung.assert_called_once_with(
            program_name='TestProgram',
            routine_name='TestRoutine',
            rung_number=5,
            rung=mock_rung
        )

    def test_add_rungs(self):
        """Test add_rungs method adds multiple rungs."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_rungs = [Mock(spec=IRung), Mock(spec=IRung), Mock(spec=IRung)]
        generator.add_rung = Mock()

        generator.add_rungs(
            program_name='TestProgram',
            routine_name='TestRoutine',
            new_rungs=mock_rungs,  # type: ignore
            rung_number=10
        )

        self.assertEqual(generator.add_rung.call_count, 3)
        # Check positions are incremented
        calls = generator.add_rung.call_args_list
        self.assertEqual(calls[0].kwargs['rung_number'], 10)
        self.assertEqual(calls[1].kwargs['rung_number'], 11)
        self.assertEqual(calls[2].kwargs['rung_number'], 12)

    def test_add_rungs_with_default_position(self):
        """Test add_rungs with default position (end)."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_rungs = [Mock(spec=IRung), Mock(spec=IRung)]
        generator.add_rung = Mock()

        generator.add_rungs(
            program_name='TestProgram',
            routine_name='TestRoutine',
            new_rungs=mock_rungs,  # type: ignore
            rung_number=None
        )

        self.assertEqual(generator.add_rung.call_count, 2)
        # Check all positions are -1 (end)
        calls = generator.add_rung.call_args_list
        self.assertEqual(calls[0].kwargs['rung_number'], -1)
        self.assertEqual(calls[1].kwargs['rung_number'], -1)

    def test_add_rung_to_safety_routine(self):
        """Test add_rung_to_safety_routine method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator._emulation_safety_routine = mock_routine
        mock_rung = Mock(spec=IRung)
        generator._add_rung_common = Mock()

        generator.add_rung_to_safety_routine(mock_rung)

        generator._add_rung_common.assert_called_once_with(
            rung=mock_rung,
            program_name='SafetyProgram',
            routine_name='SafetyEmulation'
        )

    def test_add_rung_to_safety_routine_raises_if_not_created(self):
        """Test add_rung_to_safety_routine raises if routine not created."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator._emulation_safety_routine = None
        mock_rung = Mock(spec=IRung)

        with self.assertRaises(ValueError) as context:
            generator.add_rung_to_safety_routine(mock_rung)

        self.assertIn("Safety emulation routine has not been created", str(context.exception))

    def test_add_rung_to_standard_routine(self):
        """Test add_rung_to_standard_routine method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator._emulation_standard_routine = mock_routine
        mock_rung = Mock(spec=IRung)
        generator._add_rung_common = Mock()

        generator.add_rung_to_standard_routine(mock_rung)

        generator._add_rung_common.assert_called_once_with(
            rung=mock_rung,
            program_name='StandardProgram',
            routine_name='StandardEmulation'
        )

    def test_add_rung_to_standard_routine_raises_if_not_created(self):
        """Test add_rung_to_standard_routine raises if routine not created."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator._emulation_standard_routine = None
        mock_rung = Mock(spec=IRung)

        with self.assertRaises(ValueError) as context:
            generator.add_rung_to_standard_routine(mock_rung)

        self.assertIn("Emulation routine has not been created", str(context.exception))

    def test_add_safety_tag_mapping(self):
        """Test add_safety_tag_mapping method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.add_safety_tag_mapping = Mock()

        generator.add_safety_tag_mapping(
            standard_tag='StdTag',
            safety_tag='SftyTag'
        )

        generator.schema.add_safety_tag_mapping.assert_called_once_with(
            std_tag='StdTag',
            sfty_tag='SftyTag'
        )

    def test_add_safety_tag_mapping_skips_empty_tags(self):
        """Test add_safety_tag_mapping skips if tags are empty."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.add_safety_tag_mapping = Mock()

        # Test with empty standard tag
        generator.add_safety_tag_mapping(standard_tag='', safety_tag='SftyTag')
        generator.schema.add_safety_tag_mapping.assert_not_called()

        # Test with empty safety tag
        generator.add_safety_tag_mapping(standard_tag='StdTag', safety_tag='')
        generator.schema.add_safety_tag_mapping.assert_not_called()


class TestEmulationGeneratorGenerationMethods(unittest.TestCase):
    """Test cases for EmulationGenerator generation methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self):
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self):
                return 'StandardProgram'

            @property
            def base_tags(self):
                return [
                    ('Uninhibit', 'DINT', 'Uninhibit tag'),
                    ('Inhibit', 'DINT', 'Inhibit tag'),
                ]

            @property
            def custom_tags(self):  # type: ignore
                return [('CustomTag', 'BOOL', 'Custom tag', None)]

            @property
            def uninhibit_tag(self):
                return 'Uninhibit'

            @property
            def inhibit_tag(self):
                return 'Inhibit'

            @property
            def toggle_inhibit_tag(self):
                return 'ToggleInhibit'

            @property
            def local_mode_tag(self):
                return 'LocalMode'

            @property
            def test_mode_tag(self):
                return 'TestMode'

            @property
            def emulation_safety_routine(self):
                return self._emulation_safety_routine

            @property
            def emulation_standard_routine(self):
                return self._emulation_standard_routine

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_safety_routine_description(self):
                return 'Safety emulation routine'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

            def get_emulation_standard_routine_description(self):
                return 'Standard emulation routine'

            def set_emulation_safety_routine(self, routine):
                self._emulation_safety_routine = routine

            def set_emulation_standard_routine(self, routine):
                self._emulation_standard_routine = routine

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = Mock()
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    def test_generate_base_tags(self):
        """Test _generate_base_tags method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.add_controller_tag = Mock()

        generator._generate_base_tags()

        # Should call add_controller_tag for each base tag
        self.assertEqual(generator.add_controller_tag.call_count, 2)
        generator.add_controller_tag.assert_any_call(
            'Uninhibit', 'DINT', description='Uninhibit tag'
        )
        generator.add_controller_tag.assert_any_call(
            'Inhibit', 'DINT', description='Inhibit tag'
        )

    def test_generate_custom_tags(self):
        """Test _generate_custom_tags method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.add_controller_tag = Mock()

        generator._generate_custom_tags()

        # Should call add_controller_tag for each custom tag
        generator.add_controller_tag.assert_called_once_with(
            'CustomTag', 'BOOL', description='Custom tag', dimensions=None
        )

    def test_generate_base_standard_routine(self):
        """Test _generate_base_standard_routine method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator.add_routine = Mock(return_value=mock_routine)

        generator._generate_base_standard_routine()

        generator.add_routine.assert_called_once_with(
            program_name='StandardProgram',
            routine_name='StandardEmulation',
            routine_description='Standard emulation routine',
            call_from_main=True,
            rung_position=0
        )
        self.assertIs(generator._emulation_standard_routine, mock_routine)

    def test_generate_base_safety_routine(self):
        """Test _generate_base_safety_routine method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator.add_routine = Mock(return_value=mock_routine)

        generator._generate_base_safety_routine()

        generator.add_routine.assert_called_once_with(
            program_name='SafetyProgram',
            routine_name='SafetyEmulation',
            routine_description='Safety emulation routine',
            call_from_main=True,
            rung_position=0
        )
        self.assertIs(generator._emulation_safety_routine, mock_routine)

    def test_generate_base_standard_rungs(self):
        """Test _generate_base_standard_rungs method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator._emulation_standard_routine = mock_routine
        generator.add_rung_to_standard_routine = Mock()
        generator._generate_module_inhibit_rungs = Mock()

        generator._generate_base_standard_rungs()

        # Should clear rungs first
        mock_routine.clear_rungs.assert_called_once()
        # Should add 3 rungs (NOP, setup, inhibit logic)
        self.assertEqual(generator.add_rung_to_standard_routine.call_count, 3)
        # Should call module inhibit rungs generation
        generator._generate_module_inhibit_rungs.assert_called_once()

    def test_generate_base_standard_rungs_raises_if_routine_not_set(self):
        """Test _generate_base_standard_rungs raises if routine not set."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator._emulation_standard_routine = None

        with self.assertRaises(ValueError) as context:
            generator._generate_base_standard_rungs()

        self.assertIn("Emulation routine has not been created", str(context.exception))

    def test_generate_base_safety_rungs(self):
        """Test _generate_base_safety_rungs method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator._emulation_safety_routine = mock_routine
        generator.add_rung_to_safety_routine = Mock()

        generator._generate_base_safety_rungs()

        # Should clear rungs first
        mock_routine.clear_rungs.assert_called_once()
        # Should add 1 NOP rung
        generator.add_rung_to_safety_routine.assert_called_once()

    def test_generate_base_safety_rungs_raises_if_routine_not_set(self):
        """Test _generate_base_safety_rungs raises if routine not set."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator._emulation_safety_routine = None

        with self.assertRaises(ValueError) as context:
            generator._generate_base_safety_rungs()

        self.assertIn("Safety emulation routine has not been created", str(context.exception))

    def test_generate_module_inhibit_rungs(self):
        """Test _generate_module_inhibit_rungs method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        mock_routine = Mock(spec=IRoutine)
        generator._emulation_standard_routine = mock_routine

        # Create mock modules
        mock_module1 = Mock(spec=IModule)
        mock_module1.name = 'Module1'
        mock_module2 = Mock(spec=IModule)
        mock_module2.name = 'Local'  # Should be skipped
        mock_module3 = Mock(spec=IModule)
        mock_module3.name = 'Module3'

        self.mock_controller.modules = [mock_module1, mock_module2, mock_module3]
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_module_inhibit_rungs()

        # Should add rungs for Module1 and Module3, but skip Local
        self.assertEqual(generator.add_rung_to_standard_routine.call_count, 2)

    def test_generate_module_inhibit_rungs_raises_if_routine_not_set(self):
        """Test _generate_module_inhibit_rungs raises if routine not set."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator._emulation_standard_routine = None

        with self.assertRaises(ValueError) as context:
            generator._generate_module_inhibit_rungs()

        self.assertIn("Emulation routine has not been created", str(context.exception))

    @patch('controlrox.models.tasks.generator.IntrospectiveModuleWarehouseFactory')
    def test_generate_builtin_common(self, mock_warehouse):
        """Test _generate_builtin_common method."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Create mock introspective modules
        mock_imodule1 = Mock()
        mock_imodule1.base_module = Mock()
        mock_imodule1.base_module.name = 'EthernetModule1'
        mock_imodule1.get_required_imports = Mock(return_value=[])
        mock_imodule1.get_required_tags = Mock(return_value=[])
        mock_imodule1.get_required_standard_to_safety_mapping = Mock(return_value=('', ''))
        mock_imodule1.get_required_standard_rungs = Mock(return_value=[])
        mock_imodule1.get_required_safety_rungs = Mock(return_value=[])

        mock_warehouse.filter_modules_by_type = Mock(return_value=[mock_imodule1])

        generator.add_l5x_imports = Mock()
        generator.add_controller_tags = Mock()
        generator.add_safety_tag_mapping = Mock()
        generator.add_rungs = Mock()

        generator._generate_builtin_common(ModuleControlsType.ETHERNET)

        # Verify calls were made
        mock_warehouse.filter_modules_by_type.assert_called_once()
        generator.add_l5x_imports.assert_called_once()
        generator.add_controller_tags.assert_called_once()
        generator.add_safety_tag_mapping.assert_called_once()
        self.assertEqual(generator.add_rungs.call_count, 2)  # Standard and safety

    def test_generate_base_emulation(self):
        """Test _generate_base_emulation orchestration method."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Mock all the called methods
        generator._generate_base_tags = Mock()
        generator._generate_custom_tags = Mock()
        generator._generate_base_standard_routine = Mock()
        generator._generate_base_standard_rungs = Mock()
        generator._generate_base_safety_routine = Mock()
        generator._generate_base_safety_rungs = Mock()
        generator._generate_base_module_emulation = Mock()
        generator._generate_custom_standard_routines = Mock()
        generator._generate_custom_standard_rungs = Mock()
        generator._generate_custom_safety_routines = Mock()
        generator._generate_custom_safety_rungs = Mock()

        generator._generate_base_emulation()

        # Verify all methods were called
        generator._generate_base_tags.assert_called_once()
        generator._generate_custom_tags.assert_called_once()
        generator._generate_base_standard_routine.assert_called_once()
        generator._generate_base_standard_rungs.assert_called_once()
        generator._generate_base_safety_routine.assert_called_once()
        generator._generate_base_safety_rungs.assert_called_once()
        generator._generate_base_module_emulation.assert_called_once()
        generator._generate_custom_standard_routines.assert_called_once()
        generator._generate_custom_standard_rungs.assert_called_once()
        generator._generate_custom_safety_routines.assert_called_once()
        generator._generate_custom_safety_rungs.assert_called_once()

    def test_generate_base_module_emulation(self):
        """Test _generate_base_module_emulation method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator._generate_builtin_common = Mock()

        generator._generate_base_module_emulation()

        # Should call _generate_builtin_common for each ModuleControlsType
        call_count = generator._generate_builtin_common.call_count
        self.assertGreater(call_count, 0)
        # Verify it was called with ModuleControlsType enum values
        for call_args in generator._generate_builtin_common.call_args_list:
            self.assertIsInstance(call_args[0][0], ModuleControlsType)


class TestEmulationGeneratorMainMethods(unittest.TestCase):
    """Test cases for EmulationGenerator main entry point methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self):
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self):
                return 'StandardProgram'

            @property
            def base_tags(self):
                return []

            @property
            def custom_tags(self):
                return []

            @property
            def uninhibit_tag(self):
                return 'Uninhibit'

            @property
            def inhibit_tag(self):
                return 'Inhibit'

            @property
            def toggle_inhibit_tag(self):
                return 'ToggleInhibit'

            @property
            def local_mode_tag(self):
                return 'LocalMode'

            @property
            def test_mode_tag(self):
                return 'TestMode'

            @property
            def emulation_safety_routine(self):
                return self._emulation_safety_routine

            @property
            def emulation_standard_routine(self):
                return self._emulation_standard_routine

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_safety_routine_description(self):
                return 'Safety emulation routine'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

            def get_emulation_standard_routine_description(self):
                return 'Standard emulation routine'

            def set_emulation_safety_routine(self, routine):
                self._emulation_safety_routine = routine

            def set_emulation_standard_routine(self, routine):
                self._emulation_standard_routine = routine

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = Mock()
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    def test_generate_emulation_logic(self):
        """Test generate_emulation_logic main entry point."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Mock the orchestration methods
        generator._generate_base_emulation = Mock()
        generator._generate_custom_module_emulation = Mock()
        generator._generate_custom_logic = Mock()
        generator.schema.execute = Mock()

        result = generator.generate_emulation_logic()

        # Verify all orchestration methods were called
        generator._generate_base_emulation.assert_called_once()
        generator._generate_custom_module_emulation.assert_called_once()
        generator._generate_custom_logic.assert_called_once()
        generator.schema.execute.assert_called_once()

        # Verify it returns the schema
        self.assertIs(result, generator.schema)

    def test_remove_emulation_logic(self):
        """Test remove_emulation_logic main entry point."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Mock the removal methods
        generator.remove_base_emulation = Mock()
        generator.remove_module_emulation = Mock()
        generator.remove_custom_logic = Mock()
        generator.schema.execute = Mock()

        result = generator.remove_emulation_logic()

        # Verify all removal methods were called
        generator.remove_base_emulation.assert_called_once()
        generator.remove_module_emulation.assert_called_once()
        generator.remove_custom_logic.assert_called_once()
        generator.schema.execute.assert_called_once()

        # Verify it returns the schema
        self.assertIs(result, generator.schema)


class TestEmulationGeneratorRemovalMethods(unittest.TestCase):
    """Test cases for EmulationGenerator removal helper methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self):
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self):
                return 'StandardProgram'

            @property
            def base_tags(self):
                return []

            @property
            def custom_tags(self):
                return []

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'

    def test_remove_controller_tag(self):
        """Test remove_controller_tag method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.remove_controller_tag = Mock()

        generator.remove_controller_tag('TestTag')

        generator.schema.remove_controller_tag.assert_called_once_with(tag_name='TestTag')

    def test_remove_program_tag(self):
        """Test remove_program_tag method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.remove_program_tag = Mock()

        generator.remove_program_tag('TestProgram', 'TestTag')

        generator.schema.remove_program_tag.assert_called_once_with(
            program_name='TestProgram',
            tag_name='TestTag'
        )

    def test_remove_datatype(self):
        """Test remove_datatype method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.remove_datatype = Mock()

        generator.remove_datatype('TestDatatype')

        generator.schema.remove_datatype.assert_called_once_with(datatype_name='TestDatatype')

    def test_remove_routine(self):
        """Test remove_routine method."""
        generator = self.ConcreteClass(controller=self.mock_controller)
        generator.schema.remove_routine = Mock()

        generator.remove_routine('TestProgram', 'TestRoutine')

        generator.schema.remove_routine.assert_called_once_with('TestProgram', 'TestRoutine')


class TestEmulationGeneratorQueryMethods(unittest.TestCase):
    """Test cases for EmulationGenerator query methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self):
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self):
                return 'StandardProgram'

            @property
            def base_tags(self):
                return []

            @property
            def custom_tags(self):
                return []

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'

    @patch('controlrox.models.tasks.generator.IntrospectiveModuleWarehouseFactory')
    def test_get_modules_by_type(self, mock_warehouse):
        """Test get_modules_by_type method."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Create mock modules and introspective modules
        mock_module1 = Mock(spec=IModule)
        mock_module2 = Mock(spec=IModule)
        mock_module3 = Mock(spec=IModule)

        mock_imodule1 = Mock()
        mock_imodule1.module_controls_type = ModuleControlsType.ETHERNET
        mock_imodule2 = Mock()
        mock_imodule2.module_controls_type = ModuleControlsType.BLOCK
        mock_imodule3 = Mock()
        mock_imodule3.module_controls_type = ModuleControlsType.ETHERNET

        self.mock_controller.modules = [mock_module1, mock_module2, mock_module3]

        # Mock the warehouse to return introspective modules
        mock_warehouse.get_imodule_from_meta_data = Mock(
            side_effect=[mock_imodule1, mock_imodule2, mock_imodule3]
        )

        result = generator.get_modules_by_type(ModuleControlsType.ETHERNET)  # type: ignore

        # Should return modules 1 and 3 (ETHERNET type)
        self.assertEqual(len(result), 2)
        self.assertIn(mock_module1, result)
        self.assertIn(mock_module3, result)
        self.assertNotIn(mock_module2, result)

    @patch('controlrox.models.tasks.generator.IntrospectiveModuleWarehouseFactory')
    def test_get_modules_by_type_skips_none(self, mock_warehouse):
        """Test get_modules_by_type skips modules with no introspective module."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        mock_module1 = Mock(spec=IModule)
        mock_module2 = Mock(spec=IModule)

        self.mock_controller.modules = [mock_module1, mock_module2]

        # Mock warehouse to return None for first module, valid for second
        mock_imodule2 = Mock()
        mock_imodule2.module_controls_type = ModuleControlsType.ETHERNET
        mock_warehouse.get_imodule_from_meta_data = Mock(side_effect=[None, mock_imodule2])

        result = generator.get_modules_by_type(ModuleControlsType.ETHERNET)  # type: ignore

        # Should only return module 2
        self.assertEqual(len(result), 1)
        self.assertIn(mock_module2, result)

    def test_get_modules_by_description_pattern(self):
        """Test get_modules_by_description_pattern method."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Create mock modules with descriptions
        mock_module1 = Mock(spec=IModule)
        mock_module1.description = 'Ethernet module for network'
        mock_module2 = Mock(spec=IModule)
        mock_module2.description = 'Safety input block'
        mock_module3 = Mock(spec=IModule)
        mock_module3.description = 'Ethernet switch module'
        mock_module4 = Mock(spec=IModule)
        mock_module4.description = None

        self.mock_controller.modules = [
            mock_module1, mock_module2, mock_module3, mock_module4
        ]

        result = generator.get_modules_by_description_pattern('Ethernet')

        # Should return modules 1 and 3 (contain 'Ethernet')
        self.assertEqual(len(result), 2)
        self.assertIn(mock_module1, result)
        self.assertIn(mock_module3, result)
        self.assertNotIn(mock_module2, result)
        self.assertNotIn(mock_module4, result)


class TestEmulationGeneratorAbstractMethods(unittest.TestCase):
    """Test cases for EmulationGenerator abstract/overridable methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteEmulationGenerator(EmulationGenerator):
            supporting_class = Mock

            @property
            def emulation_safety_program_name(self):
                return 'SafetyProgram'

            @property
            def emulation_standard_program_name(self):
                return 'StandardProgram'

            @property
            def base_tags(self):
                return []

            @property
            def custom_tags(self):
                return []

            def get_emulation_safety_routine_name(self):
                return 'SafetyEmulation'

            def get_emulation_standard_routine_name(self):
                return 'StandardEmulation'

        self.ConcreteClass = ConcreteEmulationGenerator
        self.mock_controller = Mock(spec=Controller)
        self.mock_controller.name = 'TestController'

    def test_generate_custom_logic_is_empty_by_default(self):
        """Test _generate_custom_logic is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator._generate_custom_logic()

    def test_generate_custom_module_emulation_is_empty_by_default(self):
        """Test _generate_custom_module_emulation is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator._generate_custom_module_emulation()

    def test_generate_custom_safety_routines_is_empty_by_default(self):
        """Test _generate_custom_safety_routines is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator._generate_custom_safety_routines()

    def test_generate_custom_safety_rungs_is_empty_by_default(self):
        """Test _generate_custom_safety_rungs is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator._generate_custom_safety_rungs()

    def test_generate_custom_standard_routines_is_empty_by_default(self):
        """Test _generate_custom_standard_routines is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator._generate_custom_standard_routines()

    def test_generate_custom_standard_rungs_is_empty_by_default(self):
        """Test _generate_custom_standard_rungs is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator._generate_custom_standard_rungs()

    def test_remove_base_emulation_is_empty_by_default(self):
        """Test remove_base_emulation is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator.remove_base_emulation()

    def test_remove_module_emulation_is_empty_by_default(self):
        """Test remove_module_emulation is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator.remove_module_emulation()

    def test_remove_custom_logic_is_empty_by_default(self):
        """Test remove_custom_logic is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator.remove_custom_logic()

    def test_block_routine_jsr_is_empty_by_default(self):
        """Test block_routine_jsr is a no-op by default."""
        generator = self.ConcreteClass(controller=self.mock_controller)

        # Should not raise an error
        generator.block_routine_jsr('TestProgram', 'TestRoutine')


class TestEmulationGeneratorInheritance(unittest.TestCase):
    """Test cases for EmulationGenerator inheritance and metaclass."""

    def test_inherits_from_plc_object(self):
        """Test EmulationGenerator inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        self.assertTrue(issubclass(EmulationGenerator, PlcObject))

    def test_implements_iemulation_generator(self):
        """Test EmulationGenerator implements IEmulationGenerator."""
        from controlrox.interfaces import IEmulationGenerator

        self.assertTrue(issubclass(EmulationGenerator, IEmulationGenerator))

    def test_has_factory_metaclass(self):
        """Test EmulationGenerator uses FactoryTypeMeta."""
        from pyrox.models import FactoryTypeMeta

        self.assertIsInstance(type(EmulationGenerator), type(FactoryTypeMeta))

    def test_supports_registering_set_by_init_subclass(self):
        """Test __init_subclass__ sets supports_registering to True."""
        class TestSubclass(EmulationGenerator):
            @property
            def emulation_safety_program_name(self):
                return 'Test'

            @property
            def emulation_standard_program_name(self):
                return 'Test'

            @property
            def base_tags(self):
                return []

            @property
            def custom_tags(self):
                return []

            def get_emulation_safety_routine_name(self):
                return 'Test'

            def get_emulation_standard_routine_name(self):
                return 'Test'

        self.assertTrue(TestSubclass.supports_registering)


if __name__ == '__main__':
    unittest.main()
