"""Unit tests for controlrox.models.plc.introspective module."""
import unittest
from unittest.mock import Mock

from controlrox.interfaces import (
    ModuleControlsType,
    IModule,
    IRung,
)
from controlrox.models.tasks.introspective import (
    IntrospectiveModule
)


class TestIntrospectiveModule(unittest.TestCase):
    """Test cases for IntrospectiveModule class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=IModule)
        self.mock_module.name = 'TestModule'
        self.mock_module.catalog_number = '1234-ABCD'
        self.mock_module.input_connection_point = 1
        self.mock_module.output_connection_point = 2
        self.mock_module.config_connection_point = 3
        self.mock_module.input_connection_size = 10
        self.mock_module.output_connection_size = 20
        self.mock_module.config_connection_size = 5

    def test_init_with_module(self):
        """Test initialization with a module."""
        introspective = IntrospectiveModule(module=self.mock_module)

        self.assertIsNotNone(introspective)
        self.assertEqual(introspective._module, self.mock_module)

    def test_get_base_module(self):
        """Test get_base_module returns the wrapped module."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_base_module()

        self.assertIs(result, self.mock_module)

    def test_set_base_module(self):
        """Test set_base_module updates the wrapped module."""
        introspective = IntrospectiveModule(module=self.mock_module)
        new_module = Mock(spec=IModule)
        new_module.name = 'NewModule'

        introspective.set_base_module(new_module)

        self.assertIs(introspective._module, new_module)
        self.assertEqual(introspective.get_base_module(), new_module)

    def test_get_catalog_number_returns_empty_string(self):
        """Test get_catalog_number returns empty string by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_catalog_number()

        self.assertEqual(result, '')

    def test_get_module_controls_type_returns_unknown(self):
        """Test get_module_controls_type returns UNKNOWN by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_module_controls_type()

        self.assertEqual(result, ModuleControlsType.UNKOWN)

    def test_get_required_imports_returns_empty_list(self):
        """Test get_required_imports returns empty list by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_imports()

        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_get_required_safety_rungs_returns_empty_list(self):
        """Test get_required_safety_rungs returns empty list by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_safety_rungs()

        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_get_required_safety_rungs_accepts_kwargs(self):
        """Test get_required_safety_rungs accepts arbitrary kwargs."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_safety_rungs(
            some_param='value',
            another_param=123
        )

        self.assertEqual(result, [])

    def test_get_required_standard_rungs_returns_empty_list(self):
        """Test get_required_standard_rungs returns empty list by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_standard_rungs()

        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_get_required_standard_rungs_accepts_kwargs(self):
        """Test get_required_standard_rungs accepts arbitrary kwargs."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_standard_rungs(
            param1='test',
            param2=456
        )

        self.assertEqual(result, [])

    def test_get_required_standard_to_safety_mapping_returns_empty_tuple(self):
        """Test get_required_standard_to_safety_mapping returns empty tuple by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_standard_to_safety_mapping()

        self.assertEqual(result, ('', ''))
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_get_required_standard_to_safety_mapping_accepts_kwargs(self):
        """Test get_required_standard_to_safety_mapping accepts arbitrary kwargs."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_standard_to_safety_mapping(
            mapping_param='value'
        )

        self.assertEqual(result, ('', ''))

    def test_get_required_tags_returns_empty_list(self):
        """Test get_required_tags returns empty list by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_tags()

        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_get_required_tags_accepts_kwargs(self):
        """Test get_required_tags accepts arbitrary kwargs."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_required_tags(tag_param='test')

        self.assertEqual(result, [])

    def test_get_safety_input_tag_name_returns_empty_string(self):
        """Test get_safety_input_tag_name returns empty string by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_safety_input_tag_name()

        self.assertEqual(result, '')

    def test_get_safety_output_tag_name_returns_empty_string(self):
        """Test get_safety_output_tag_name returns empty string by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_safety_output_tag_name()

        self.assertEqual(result, '')

    def test_get_standard_input_tag_name_returns_empty_string(self):
        """Test get_standard_input_tag_name returns empty string by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_standard_input_tag_name()

        self.assertEqual(result, '')

    def test_get_standard_output_tag_name_returns_empty_string(self):
        """Test get_standard_output_tag_name returns empty string by default."""
        introspective = IntrospectiveModule(module=self.mock_module)

        result = introspective.get_standard_output_tag_name()

        self.assertEqual(result, '')


class TestIntrospectiveModuleSubclass(unittest.TestCase):
    """Test cases for IntrospectiveModule subclass behavior."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=IModule)
        self.mock_module.name = 'TestModule'

        # Create a concrete subclass for testing
        class ConcreteIntrospectiveModule(IntrospectiveModule):
            def get_catalog_number(self):
                return 'TEST-1234'

            def get_module_controls_type(self):
                return ModuleControlsType.ETHERNET

            def get_required_imports(self):
                return [('/path/to/import.L5X', ['Datatype', 'Tag'])]

            def get_required_safety_rungs(self, **kwargs):  # type: ignore
                return [Mock(spec=IRung)]

            def get_required_standard_rungs(self, **kwargs):  # type: ignore
                return [Mock(spec=IRung), Mock(spec=IRung)]

            def get_required_standard_to_safety_mapping(self, **kwargs):
                return ('StandardTag', 'SafetyTag')

            def get_required_tags(self, **kwargs):
                return [{'name': 'Tag1', 'datatype': 'BOOL'}]

            def get_safety_input_tag_name(self):
                return 'SafetyInputTag'

            def get_safety_output_tag_name(self):
                return 'SafetyOutputTag'

            def get_standard_input_tag_name(self):
                return 'StandardInputTag'

            def get_standard_output_tag_name(self):
                return 'StandardOutputTag'

        self.ConcreteClass = ConcreteIntrospectiveModule

    def test_subclass_get_catalog_number(self):
        """Test subclass can override get_catalog_number."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_catalog_number()

        self.assertEqual(result, 'TEST-1234')

    def test_subclass_get_module_controls_type(self):
        """Test subclass can override get_module_controls_type."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_module_controls_type()

        self.assertEqual(result, ModuleControlsType.ETHERNET)

    def test_subclass_get_required_imports(self):
        """Test subclass can override get_required_imports."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_required_imports()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ('/path/to/import.L5X', ['Datatype', 'Tag']))

    def test_subclass_get_required_safety_rungs(self):
        """Test subclass can override get_required_safety_rungs."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_required_safety_rungs()

        self.assertEqual(len(result), 1)

    def test_subclass_get_required_standard_rungs(self):
        """Test subclass can override get_required_standard_rungs."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_required_standard_rungs()

        self.assertEqual(len(result), 2)

    def test_subclass_get_required_standard_to_safety_mapping(self):
        """Test subclass can override get_required_standard_to_safety_mapping."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_required_standard_to_safety_mapping()

        self.assertEqual(result, ('StandardTag', 'SafetyTag'))

    def test_subclass_get_required_tags(self):
        """Test subclass can override get_required_tags."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_required_tags()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {'name': 'Tag1', 'datatype': 'BOOL'})

    def test_subclass_get_safety_input_tag_name(self):
        """Test subclass can override get_safety_input_tag_name."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_safety_input_tag_name()

        self.assertEqual(result, 'SafetyInputTag')

    def test_subclass_get_safety_output_tag_name(self):
        """Test subclass can override get_safety_output_tag_name."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_safety_output_tag_name()

        self.assertEqual(result, 'SafetyOutputTag')

    def test_subclass_get_standard_input_tag_name(self):
        """Test subclass can override get_standard_input_tag_name."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_standard_input_tag_name()

        self.assertEqual(result, 'StandardInputTag')

    def test_subclass_get_standard_output_tag_name(self):
        """Test subclass can override get_standard_output_tag_name."""
        introspective = self.ConcreteClass(module=self.mock_module)

        result = introspective.get_standard_output_tag_name()

        self.assertEqual(result, 'StandardOutputTag')


class TestIntrospectiveModuleIntegration(unittest.TestCase):
    """Integration tests for IntrospectiveModule workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = Mock(spec=IModule)
        self.mock_module.name = 'IntegrationTestModule'
        self.mock_module.catalog_number = 'INT-TEST-001'
        self.mock_module.input_connection_point = 5
        self.mock_module.output_connection_point = 6
        self.mock_module.config_connection_point = 7
        self.mock_module.input_connection_size = 15
        self.mock_module.output_connection_size = 25
        self.mock_module.config_connection_size = 8

    def test_create_and_use_introspective_module(self):
        """Test creating and using an IntrospectiveModule."""
        introspective = IntrospectiveModule(module=self.mock_module)

        # Verify base functionality
        self.assertIsNotNone(introspective)
        self.assertEqual(introspective.get_base_module(), self.mock_module)
        self.assertEqual(introspective.get_catalog_number(), '')
        self.assertEqual(introspective.get_module_controls_type(), ModuleControlsType.UNKOWN)
        self.assertEqual(introspective.get_required_imports(), [])
        self.assertEqual(introspective.get_required_safety_rungs(), [])
        self.assertEqual(introspective.get_required_standard_rungs(), [])
        self.assertEqual(introspective.get_required_standard_to_safety_mapping(), ('', ''))
        self.assertEqual(introspective.get_required_tags(), [])

    def test_custom_module_workflow(self):
        """Test complete workflow with custom introspective module."""
        class CustomEthernetModule(IntrospectiveModule):
            def get_catalog_number(self):
                return 'INT-TEST-001'

            def get_module_controls_type(self):
                return ModuleControlsType.ETHERNET

            def get_required_tags(self, **kwargs):
                return [
                    {'name': 'InputTag', 'datatype': 'DINT'},
                    {'name': 'OutputTag', 'datatype': 'BOOL'}
                ]

            def get_standard_input_tag_name(self):
                return 'StandardInput'

            def get_standard_output_tag_name(self):
                return 'StandardOutput'

            @property
            def catalog_number(self):
                return self.get_catalog_number()

            @property
            def input_connection_point(self):
                return 5

            @property
            def output_connection_point(self):
                return 6

            @property
            def config_connection_point(self):
                return 7

            @property
            def input_connection_size(self):
                return 15

            @property
            def output_connection_size(self):
                return 25

            @property
            def config_connection_size(self):
                return 8

        custom_module = CustomEthernetModule(module=self.mock_module)

        # Test all overridden methods
        self.assertEqual(custom_module.get_catalog_number(), 'INT-TEST-001')
        self.assertEqual(custom_module.get_module_controls_type(), ModuleControlsType.ETHERNET)

        tags = custom_module.get_required_tags()
        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0]['name'], 'InputTag')

        self.assertEqual(custom_module.get_standard_input_tag_name(), 'StandardInput')
        self.assertEqual(custom_module.get_standard_output_tag_name(), 'StandardOutput')
