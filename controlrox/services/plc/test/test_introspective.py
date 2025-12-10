"""Unit tests for controlrox.services.plc.introspective module."""
import unittest
from unittest.mock import Mock, patch

from controlrox.interfaces import (
    ModuleControlsType,
    IIntrospectiveModule,
    IModule,
)

from controlrox.models import PlcObject

from controlrox.services.plc.introspective import (
    IntrospectiveModuleWarehouseFactory,
    IntrospectiveModuleWarehouse,
)


class ConcreteIntrospectiveModule(IIntrospectiveModule, PlcObject):

    def __init__(self, base_module: IModule):
        super().__init__()
        self._base_module = base_module

    @classmethod
    def create_from_module(
        cls,
        module: IModule
    ) -> IIntrospectiveModule:
        """Create an instance of the introspective module from a base module.

        Args:
            module (IModule): The base module to create from.
        Returns:
            IIntrospectiveModule: An instance of the introspective module.
        """
        return cls(module)

    def get_base_module(self) -> IModule:
        """Get the base module of this introspective module.

        Returns:
            IModule: The base module.
        """
        return self._base_module

    def get_catalog_number(self) -> str:
        """The catalog number of the module."""
        return ''

    def get_module_controls_type(self) -> ModuleControlsType:
        """The controls type of the module."""
        return None  # type: ignore

    def get_required_imports(self) -> list[tuple[str, list[str]]]:
        """Get the required datatype imports for the module.

        Returns:
            list[tuple[str, list[str]]]: List of tuples containing the module and class name to import.
        """
        return []

    def get_required_safety_rungs(
        self,
        **__,
    ) -> list:
        """Get the required safety rungs for the module.

        Returns:
            list[IRung]: List of rungs.
        """
        return []

    def get_required_standard_rungs(
        self,
        **__,
    ) -> list:
        """Get the required standard rungs for the module.

        Returns:
            list[Rung]: List of rungs.
        """
        return []

    def get_required_standard_to_safety_mapping(
        self,
        **__,
    ) -> tuple[str, str]:
        """Get the required standard to safety mapping for the module.

        Returns:
            dict[str, str]: Dictionary of standard to safety mapping.
        """
        return ('', '')

    def get_required_tags(
        self,
        **__,
    ) -> list[dict]:
        """Get the required tags for the module.

        Returns:
            list[dict]: List of tag dictionaries.
        """
        return []

    def get_safety_input_tag_name(self) -> str:
        """Get the safety tag name for the module.

        Returns:
            str: Safety tag name.
        """
        return ''

    def get_safety_output_tag_name(self) -> str:
        """Get the safety output tag name for the module.

        Returns:
            str: Safety output tag name.
        """
        return ''

    def get_standard_input_tag_name(self) -> str:
        """Get the standard tag name for the module.

        Returns:
            str: Standard tag name.
        """
        return ''

    def get_standard_output_tag_name(self) -> str:
        """Get the standard output tag name for the module.

        Returns:
            str: Standard output tag name.
        """
        return ''

    def set_base_module(
        self,
        module: IModule
    ) -> None:
        """Set the base module of this introspective module.

        Args:
            module (IModule): The base module to set.
        """
        self._base_module = module


class TestIntrospectiveModuleWarehouseFactory(unittest.TestCase):
    """Test cases for IntrospectiveModuleWarehouseFactory class."""

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

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_registered_types')
    def test_get_all_known_modules_returns_list(self, mock_get_registered):
        """Test get_all_known_modules returns a list."""
        mock_warehouse = Mock()
        mock_warehouse.get_known_module_classes.return_value = [IIntrospectiveModule]
        mock_get_registered.return_value = {'MockWarehouse': mock_warehouse}

        result = IntrospectiveModuleWarehouseFactory.get_all_known_modules()

        self.assertIsInstance(result, list)
        mock_warehouse.get_known_module_classes.assert_called_once()

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_registered_types')
    def test_get_all_known_modules_aggregates_from_warehouses(self, mock_get_registered):
        """Test get_all_known_modules aggregates modules from multiple warehouses."""
        mock_warehouse1 = Mock()
        mock_warehouse1.get_known_module_classes.return_value = [IIntrospectiveModule]

        mock_warehouse2 = Mock()

        class CustomModule(IIntrospectiveModule):
            pass

        mock_warehouse2.get_known_module_classes.return_value = [CustomModule]

        mock_get_registered.return_value = {
            'Warehouse1': mock_warehouse1,
            'Warehouse2': mock_warehouse2
        }

        result = IntrospectiveModuleWarehouseFactory.get_all_known_modules()

        self.assertEqual(len(result), 2)
        self.assertIn(IIntrospectiveModule, result)
        self.assertIn(CustomModule, result)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_registered_types')
    @patch('controlrox.services.plc.introspective.log')
    def test_get_all_known_modules_warns_on_none_warehouse(self, mock_log, mock_get_registered):
        """Test get_all_known_modules logs warning when warehouse is None."""
        mock_warehouse = Mock()
        mock_warehouse.get_known_module_classes.return_value = [ConcreteIntrospectiveModule]

        mock_get_registered.return_value = {
            'GoodWarehouse': mock_warehouse,
            'BadWarehouse': None
        }

        result = IntrospectiveModuleWarehouseFactory.get_all_known_modules()

        mock_log.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_registered_types')
    def test_get_modules_by_type_filters_correctly(self, mock_get_registered):
        """Test get_modules_by_type filters modules by type."""
        mock_ethernet_module = Mock(spec=IIntrospectiveModule)
        mock_block_module = Mock(spec=IIntrospectiveModule)

        mock_warehouse = Mock()
        mock_warehouse.get_modules_by_type.return_value = [
            mock_ethernet_module,
            mock_block_module
        ]

        mock_get_registered.return_value = {'MockWarehouse': mock_warehouse}

        result = IntrospectiveModuleWarehouseFactory.get_modules_by_type(
            ModuleControlsType.ETHERNET
        )

        mock_warehouse.get_modules_by_type.assert_called_once_with(ModuleControlsType.ETHERNET)
        self.assertEqual(len(result), 2)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_registered_types')
    @patch('controlrox.services.plc.introspective.log')
    def test_get_modules_by_type_warns_on_none_warehouse(self, mock_log, mock_get_registered):
        """Test get_modules_by_type logs warning when warehouse is None."""
        mock_get_registered.return_value = {'BadWarehouse': None}

        result = IntrospectiveModuleWarehouseFactory.get_modules_by_type(
            ModuleControlsType.ETHERNET
        )

        mock_log.assert_called()
        self.assertEqual(result, [])

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_imodule_from_meta_data')
    def test_filter_modules_by_type_returns_matching_modules(self, mock_get_imodule):
        """Test filter_modules_by_type returns only matching modules."""
        mock_module1 = Mock(spec=IModule)
        mock_module2 = Mock(spec=IModule)
        mock_module3 = Mock(spec=IModule)

        mock_imodule1 = Mock(spec=IIntrospectiveModule)
        mock_imodule1.module_controls_type = ModuleControlsType.ETHERNET

        mock_imodule2 = Mock(spec=IIntrospectiveModule)
        mock_imodule2.module_controls_type = ModuleControlsType.BLOCK

        mock_imodule3 = Mock(spec=IIntrospectiveModule)
        mock_imodule3.module_controls_type = ModuleControlsType.ETHERNET

        mock_get_imodule.side_effect = [mock_imodule1, mock_imodule2, mock_imodule3]

        result = IntrospectiveModuleWarehouseFactory.filter_modules_by_type(
            [mock_module1, mock_module2, mock_module3],
            ModuleControlsType.ETHERNET
        )

        self.assertEqual(len(result), 2)
        self.assertIn(mock_imodule1, result)
        self.assertIn(mock_imodule3, result)
        self.assertNotIn(mock_imodule2, result)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_imodule_from_meta_data')
    @patch('controlrox.services.plc.introspective.log')
    def test_filter_modules_by_type_skips_modules_without_imodule(self, mock_log, mock_get_imodule):
        """Test filter_modules_by_type skips modules that don't have introspective module."""
        mock_module1 = Mock(spec=IModule)
        mock_module2 = Mock(spec=IModule)

        mock_imodule1 = Mock(spec=IIntrospectiveModule)
        mock_imodule1.module_controls_type = ModuleControlsType.ETHERNET

        mock_get_imodule.side_effect = [mock_imodule1, None]

        result = IntrospectiveModuleWarehouseFactory.filter_modules_by_type(
            [mock_module1, mock_module2],
            ModuleControlsType.ETHERNET
        )

        self.assertEqual(len(result), 1)
        self.assertIn(mock_imodule1, result)
        mock_log.assert_called()

    def test_get_imodule_from_meta_data_raises_on_none_module(self):
        """Test get_imodule_from_meta_data raises ValueError when module is None."""
        with self.assertRaises(ValueError) as context:
            IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(None)  # type: ignore

        self.assertIn('Module is required', str(context.exception))

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_all_known_modules')
    @patch('controlrox.services.plc.introspective.log')
    def test_get_imodule_from_meta_data_returns_none_on_no_match(self, mock_log, mock_get_all):
        """Test get_imodule_from_meta_data returns None when no match found."""
        mock_get_all.return_value = []

        result = IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(
            self.mock_module
        )

        self.assertIsNone(result)
        mock_log.assert_called()

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_all_known_modules')
    def test_get_imodule_from_meta_data_matches_exact_catalog_number(self, mock_get_all):
        """Test get_imodule_from_meta_data matches on exact catalog number."""
        class MatchingModule(ConcreteIntrospectiveModule):
            @property
            def catalog_number(self):
                return '1234-ABCD'

            @property
            def input_connection_point(self):
                return 1

            @property
            def output_connection_point(self):
                return 2

            @property
            def config_connection_point(self):
                return 3

            @property
            def input_connection_size(self):
                return 10

            @property
            def output_connection_size(self):
                return 20

            @property
            def config_connection_size(self):
                return 5

        mock_get_all.return_value = [MatchingModule]

        result = IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(
            self.mock_module
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, MatchingModule)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_all_known_modules')
    def test_get_imodule_from_meta_data_fails_on_mismatched_input_connection(self, mock_get_all):
        """Test get_imodule_from_meta_data fails when input connection doesn't match."""
        class NonMatchingModule(ConcreteIntrospectiveModule):
            @property
            def catalog_number(self):
                return '1234-ABCD'

            @property
            def input_connection_point(self):
                return 999  # Different

            @property
            def output_connection_point(self):
                return 2

            @property
            def config_connection_point(self):
                return 3

            @property
            def input_connection_size(self):
                return 10

            @property
            def output_connection_size(self):
                return 20

            @property
            def config_connection_size(self):
                return 5

        mock_get_all.return_value = [NonMatchingModule]

        result = IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(
            self.mock_module
        )

        self.assertIsNone(result)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_all_known_modules')
    def test_get_imodule_from_meta_data_lazy_match_catalog(self, mock_get_all):
        """Test get_imodule_from_meta_data uses lazy match for catalog number."""
        self.mock_module.catalog_number = '1234-ABCD-EF'

        class PartialMatchModule(ConcreteIntrospectiveModule):
            @property
            def catalog_number(self):
                return '1234-ABCD'

            @property
            def input_connection_point(self):
                return 1

            @property
            def output_connection_point(self):
                return 2

            @property
            def config_connection_point(self):
                return 3

            @property
            def input_connection_size(self):
                return 10

            @property
            def output_connection_size(self):
                return 20

            @property
            def config_connection_size(self):
                return 5

        mock_get_all.return_value = [PartialMatchModule]

        result = IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(
            self.mock_module,
            lazy_match_catalog=True
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, PartialMatchModule)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_all_known_modules')
    def test_get_imodule_from_meta_data_skips_ethernet_module_for_lazy_match(self, mock_get_all):
        """Test get_imodule_from_meta_data skips ETHERNET-MODULE for lazy matching."""
        self.mock_module.catalog_number = 'ETHERNET-MODULE'

        class TestModule(ConcreteIntrospectiveModule):
            @property
            def catalog_number(self):
                return 'ETHERNET'

        mock_get_all.return_value = [TestModule]

        result = IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(
            self.mock_module,
            lazy_match_catalog=True
        )

        self.assertIsNone(result)

    @patch.object(IntrospectiveModuleWarehouseFactory, 'get_all_known_modules')
    @patch('controlrox.services.plc.introspective.log')
    def test_get_imodule_from_meta_data_logs_debug_info(self, mock_log, mock_get_all):
        """Test get_imodule_from_meta_data logs debug information on no match."""
        mock_get_all.return_value = []

        IntrospectiveModuleWarehouseFactory.get_imodule_from_meta_data(
            self.mock_module
        )

        # Check that both warning and debug were called
        self.assertEqual(mock_log.call_count, 2)


class TestIntrospectiveModuleWarehouse(unittest.TestCase):
    """Test cases for IntrospectiveModuleWarehouse class."""

    def test_supports_registering_is_true_for_subclass(self):
        """Test supports_registering is True for subclasses."""
        class CustomWarehouse(IntrospectiveModuleWarehouse):
            pass

        self.assertTrue(CustomWarehouse.supports_registering)

    def test_get_factory_returns_correct_factory(self):
        """Test get_factory returns IntrospectiveModuleWarehouseFactory."""
        factory = IntrospectiveModuleWarehouse.get_factory()

        self.assertIs(factory, IntrospectiveModuleWarehouseFactory)

    @patch.object(IntrospectiveModuleWarehouse, 'get_registered_types')
    def test_get_known_module_classes_filters_iintrospective_modules(self, mock_get_registered):
        """Test get_known_module_classes filters for IIntrospectiveModule subclasses."""
        class ValidModule(IIntrospectiveModule):
            pass

        class InvalidClass:
            pass

        mock_get_registered.return_value = {
            'ValidModule': ValidModule,
            'InvalidClass': InvalidClass,
            'AnotherValid': IIntrospectiveModule
        }

        result = IntrospectiveModuleWarehouse.get_known_module_classes()

        self.assertEqual(len(result), 2)
        self.assertIn(ValidModule, result)
        self.assertIn(IIntrospectiveModule, result)
        self.assertNotIn(InvalidClass, result)

    @patch.object(IntrospectiveModuleWarehouse, 'get_registered_types')
    def test_get_known_module_classes_returns_empty_list_when_no_modules(self, mock_get_registered):
        """Test get_known_module_classes returns empty list when no valid modules."""
        mock_get_registered.return_value = {}

        result = IntrospectiveModuleWarehouse.get_known_module_classes()

        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
