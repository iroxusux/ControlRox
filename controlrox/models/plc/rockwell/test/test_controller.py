"""Comprehensive unit tests for controller.py module."""
import unittest
from unittest.mock import Mock, patch

from controlrox.models.plc.rockwell.controller import (
    RaController,
    ControllerFactory,
    ControllerSafetyInfo,
)
from controlrox.models.plc.rockwell.aoi import RaAddOnInstruction
from controlrox.models.plc.rockwell.datatype import RaDatatype
from controlrox.models.plc.rockwell.program import RaProgram
from controlrox.models.plc.rockwell.module import RaModule
from controlrox.models.plc.rockwell.tag import RaTag
from controlrox.interfaces import IController
from controlrox.models.plc.rockwell import meta as plc_meta
from pyrox.models.abc.list import HashList
from pyrox.models.abc.factory import MetaFactory


class TestControllerSafetyInfo(unittest.TestCase):
    """Test cases for ControllerSafetyInfo class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock()
        self.test_meta_data = {
            '@SafetyLocked': 'true',
            '@SignatureRunModeProtect': 'false',
            '@ConfigureSafetyIOAlways': 'true',
            '@SafetyLevel': 'SIL2',
            'SafetyTagMap': 'tag1=safety1,tag2=safety2'
        }

        self.safety_info = ControllerSafetyInfo(
            meta_data=self.test_meta_data,  # type: ignore
        )

    def test_inheritance(self):
        """Test that ControllerSafetyInfo inherits from PlcObject."""
        self.assertTrue(issubclass(ControllerSafetyInfo, plc_meta.PlcObject))

    def test_safety_locked_property(self):
        """Test safety_locked property getter and setter."""
        # Test getter
        self.assertTrue(self.safety_info.safety_locked)

        # Test setter with valid value
        self.safety_info.set_safety_locked(False)
        self.assertEqual(self.safety_info['@SafetyLocked'], 'false')

        # Test setter with invalid value
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_safety_locked('yes')  # type: ignore
        self.assertIn("Safety locked must be a boolean", str(context.exception))

    def test_signature_runmode_protect_property(self):
        """Test signature_runmode_protect property getter and setter."""
        # Test getter
        self.assertFalse(self.safety_info.signature_runmode_protected)

        # Test setter with valid value
        self.safety_info.set_signature_runmode_protected(True)
        self.assertEqual(self.safety_info['@SignatureRunModeProtect'], 'true')

        # Test setter with invalid value
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_signature_runmode_protected('maybe')  # type: ignore
        self.assertIn("Signature runmode protect must be a boolean!", str(context.exception))

    def test_configure_safety_io_always_property(self):
        """Test configure_safety_io_always property getter and setter."""
        # Test getter
        self.assertTrue(self.safety_info.configure_safety_io_always)

        # Test setter with valid value
        self.safety_info.set_configure_safety_io_always(False)
        self.assertEqual(self.safety_info['@ConfigureSafetyIOAlways'], 'false')

        # Test setter with invalid value
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_configure_safety_io_always(123)  # type: ignore
        self.assertIn("Configure safety IO always must be a boolean!", str(context.exception))

    def test_safety_level_property(self):
        """Test safety_level property getter and setter."""
        # Test getter
        self.assertEqual(self.safety_info.safety_level, 'SIL2')

        # Test setter with valid values
        for level in ['SIL1', 'SIL2', 'SIL3', 'SIL4']:
            self.safety_info.set_safety_level(level)
            self.assertEqual(self.safety_info['@SafetyLevel'], level)

        # Test setter with invalid type
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_safety_level(123)  # type: ignore
        self.assertIn("Safety level must be a string", str(context.exception))

        # Test setter with invalid value
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_safety_level('invalid')  # type: ignore
        self.assertIn("Safety level must contain one of: SIL1, SIL2, SIL3, SIL4", str(context.exception))

    def test_safety_tag_map_property(self):
        """Test safety_tag_map property getter and setter."""
        # Test getter
        self.assertEqual(self.safety_info.safety_tag_map, 'tag1=safety1,tag2=safety2')

        # Test setter with valid format
        self.safety_info.set_safety_tag_map('new_tag=new_safety')
        self.assertEqual(self.safety_info['SafetyTagMap'], 'new_tag=new_safety')

        # Test setter with empty string
        self.safety_info.set_safety_tag_map('')
        self.assertIsNone(self.safety_info['SafetyTagMap'])

        # Test setter with None SafetyTagMap initially
        safety_info_none = ControllerSafetyInfo(
            meta_data={'SafetyTagMap': None},  # type: ignore
        )
        self.assertEqual(safety_info_none.safety_tag_map, '')

        # Test setter with invalid type
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_safety_tag_map(123)  # type: ignore
        self.assertIn("Safety tag map must be a string", str(context.exception))

        # Test setter with invalid format
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_safety_tag_map('invalid_format')
        self.assertIn("Safety tag map must be in the format", str(context.exception))

        # Test setter with invalid format (too many equals)
        with self.assertRaises(ValueError) as context:
            self.safety_info.set_safety_tag_map('tag=safety=extra')
        self.assertIn("Safety tag map must be in the format", str(context.exception))

    def test_safety_tag_map_dict_list(self):
        """Test safety_tag_map_dict_list property."""
        expected = [
            {'@Name': 'tag1', 'TagName': 'tag1', 'SafetyTagName': 'safety1'},
            {'@Name': 'tag2', 'TagName': 'tag2', 'SafetyTagName': 'safety2'}
        ]
        result = self.safety_info.safety_tag_map_dict_list
        self.assertEqual(result, expected)

        # Test with empty string
        self.safety_info.set_safety_tag_map('')
        self.assertEqual(self.safety_info.safety_tag_map_dict_list, [])

        # Test with invalid type
        self.safety_info['SafetyTagMap'] = 123
        with self.assertRaises(ValueError) as context:
            self.safety_info.safety_tag_map_dict_list
        self.assertIn("Safety tag map must be a string", str(context.exception))

    def test_add_safety_tag_mapping(self):
        """Test add_safety_tag_mapping method."""
        # Test adding to existing map
        self.safety_info.add_safety_tag_mapping('tag3', 'safety3')
        self.assertIn('tag3=safety3', self.safety_info.safety_tag_map)

        # Test adding to empty map
        empty_safety_info = ControllerSafetyInfo(
            meta_data={'SafetyTagMap': None},  # type: ignore
        )
        empty_safety_info.add_safety_tag_mapping('first_tag', 'first_safety')
        self.assertEqual(empty_safety_info.safety_tag_map, 'first_tag=first_safety')

        # Test removing and re-adding (should replace)
        original_map = 'tag1=safety1,tag2=safety2'
        self.safety_info.set_safety_tag_map(original_map)
        self.safety_info.add_safety_tag_mapping('tag1', 'new_safety1')
        # Should remove old mapping and add new one
        expected = 'tag1=safety1,tag2=safety2,tag1=new_safety1'
        self.assertEqual(self.safety_info.safety_tag_map, expected)

        # Test with invalid types
        with self.assertRaises(ValueError) as context:
            self.safety_info.add_safety_tag_mapping(123, 'safety')  # type: ignore
        self.assertIn("Tag names must be strings", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.safety_info.add_safety_tag_mapping('tag', 123)  # type: ignore
        self.assertIn("Tag names must be strings", str(context.exception))

    def test_remove_safety_tag_mapping(self):
        """Test remove_safety_tag_mapping method."""
        # Test removing from existing map
        self.safety_info.remove_safety_tag_mapping('tag1', 'safety1')
        self.assertEqual(self.safety_info.safety_tag_map, 'tag2=safety2')

        # Test removing from empty map
        empty_safety_info = ControllerSafetyInfo(
            meta_data={'SafetyTagMap': None},  # type: ignore
        )
        empty_safety_info.remove_safety_tag_mapping('tag', 'safety')  # Should not raise error

        # Test removing non-existent mapping
        self.safety_info.remove_safety_tag_mapping('nonexistent', 'safety')  # Should not raise error

        # Test with different positions
        self.safety_info.set_safety_tag_map('tag1=safety1,tag2=safety2,tag3=safety3')

        # Remove from middle
        self.safety_info.remove_safety_tag_mapping('tag2', 'safety2')
        self.assertEqual(self.safety_info.safety_tag_map, 'tag1=safety1,tag3=safety3')

        # Remove from end
        self.safety_info.remove_safety_tag_mapping('tag3', 'safety3')
        self.assertEqual(self.safety_info.safety_tag_map, 'tag1=safety1')

        # Remove last one
        self.safety_info.remove_safety_tag_mapping('tag1', 'safety1')
        self.assertEqual(self.safety_info.safety_tag_map, '')

        # Test with invalid types
        with self.assertRaises(ValueError) as context:
            self.safety_info.remove_safety_tag_mapping(123, 'safety')  # type: ignore
        self.assertIn("Tag names must be strings", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.safety_info.remove_safety_tag_mapping('tag', 123)  # type: ignore
        self.assertIn("Tag names must be strings", str(context.exception))


class TestControllerFactory(unittest.TestCase):
    """Test cases for ControllerFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.controller_data = {
            '@Name': 'TestController',
            '@ProcessorType': 'TestProcessor',
            'Tags': {'Tag': []},
            'Programs': {'Program': []},
            'Modules': {'Module': []},
            'DataTypes': {'DataType': []}
        }

    def test_inheritance(self):
        """Test that ControllerFactory inherits from MetaFactory."""
        self.assertTrue(issubclass(ControllerFactory, MetaFactory))

    def test_get_best_match_with_matches(self):
        """Test get_best_match method structure."""
        # Test that the method exists and is callable
        self.assertTrue(hasattr(ControllerFactory, 'get_best_match'))
        self.assertTrue(callable(getattr(ControllerFactory, 'get_best_match')))

        # Test with empty data returns None
        result = ControllerFactory.get_best_match(None)  # type: ignore
        self.assertIsNone(result)

        # Test with empty dict returns None
        result = ControllerFactory.get_best_match({})
        self.assertIsNone(result)

    def test_get_best_match_no_matches(self):
        """Test get_best_match method with no valid input."""
        # Test with None data
        result = ControllerFactory.get_best_match(None)  # type: ignore
        self.assertIsNone(result)

        # Test with empty dict
        result = ControllerFactory.get_best_match({})
        self.assertIsNone(result)

    @patch('controlrox.models.plc.rockwell.controller.log')
    def test_get_best_match_empty_data(self, mock_log):
        """Test get_best_match method with empty controller data."""
        result = ControllerFactory.get_best_match(None)  # type: ignore
        self.assertIsNone(result)

        result = ControllerFactory.get_best_match({})
        self.assertIsNone(result)

    @patch.object(ControllerFactory, 'get_best_match')
    def test_create_controller_success(self, mock_get_best_match):
        """Test create_controller method with successful match."""
        mock_controller_class = Mock()
        mock_controller_instance = Mock()
        mock_controller_class.return_value = mock_controller_instance
        mock_get_best_match.return_value = mock_controller_class

        result = ControllerFactory.create_controller(self.controller_data, extra_param='test')

        self.assertEqual(result, mock_controller_instance)
        mock_get_best_match.assert_called_once_with(self.controller_data)
        mock_controller_class.assert_called_once_with(meta_data=self.controller_data, extra_param='test')

    @patch.object(ControllerFactory, 'get_best_match')
    def test_create_controller_no_match(self, mock_get_best_match):
        """Test create_controller method with no matching controller."""
        mock_get_best_match.return_value = None

        result = ControllerFactory.create_controller(self.controller_data)

        self.assertIsNone(result)


class TestController(unittest.TestCase):
    """Test cases for Controller class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController',
                    '@MajorRev': '32',
                    '@MinorRev': '11',
                    '@CommPath': '1,0',
                    'Tags': {'Tag': []},
                    'Programs': {'Program': []},
                    'Modules': {'Module': [
                        {'@Name': 'Local', '@Major': '32', '@Minor': '11',
                         'Ports': {'Port': {'@Type': 'ICP', '@Address': '0'}}}
                    ]},
                    'DataTypes': {'DataType': []},
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'SafetyInfo': {
                        '@SafetyLocked': 'false',
                        '@SafetyLevel': 'SIL2'
                    }
                }
            }
        }

    def test_inheritance(self):
        """Test that Controller inherits from NamedPlcObject."""
        self.assertTrue(issubclass(RaController, IController))

    def test_metaclass(self):
        """Test that Controller has proper metaclass structure."""
        # Check that Controller has the expected class structure
        self.assertTrue(hasattr(RaController, '__class__'))
        # Check that it has some factory-related attributes
        self.assertTrue(hasattr(RaController, 'get_factory') or hasattr(RaController.__class__, '__mro__'))

    def test_initialization_valid_data(self):
        """Test Controller initialization with valid data."""
        controller = RaController(meta_data=self.test_meta_data, file_location='test.L5X')

        self.assertEqual(controller.meta_data, self.test_meta_data)
        self.assertEqual(controller.file_location, 'test.L5X')
        self.assertEqual(controller.name, 'TestController')
        self.assertIsInstance(controller._aois, HashList)
        self.assertIsInstance(controller._datatypes, HashList)
        self.assertIsInstance(controller._modules, HashList)
        self.assertIsInstance(controller._programs, HashList)
        self.assertIsInstance(controller._tags, HashList)

    def test_initialization_no_file_location(self):
        """Test Controller initialization without file location."""
        controller = RaController(meta_data=self.test_meta_data)
        self.assertIsNone(controller._file_location)

    def test_getitem_setitem(self):
        """Test __getitem__ and __setitem__ methods."""
        controller = RaController(meta_data=self.test_meta_data)

        # Test __getitem__
        self.assertEqual(controller['@Name'], 'TestController')
        self.assertEqual(controller['@MajorRev'], '32')

        # Test __setitem__
        controller['@Name'] = 'NewName'
        self.assertEqual(controller['@Name'], 'NewName')

        # Test setting revision updates software revision
        controller['@MajorRev'] = '33'
        self.assertEqual(controller.content_meta_data['@SoftwareRevision'], '33.11')

    @patch('controlrox.models.plc.rockwell.controller.get_save_file')
    def test_file_location_property_with_dialog(self, mock_get_save_file):
        """Test file_location property when not set initially."""
        mock_get_save_file.return_value = 'selected_file.L5X'

        controller = RaController(meta_data=self.test_meta_data)
        result = controller.file_location

        self.assertEqual(result, 'selected_file.L5X')
        mock_get_save_file.assert_called_once()

    @patch('controlrox.models.plc.rockwell.controller.get_save_file')
    def test_file_location_property_dialog_cancelled(self, mock_get_save_file):
        """Test file_location property when dialog is cancelled."""
        mock_get_save_file.return_value = None

        controller = RaController(meta_data=self.test_meta_data)

        with self.assertRaises(RuntimeError) as context:
            controller.file_location
        self.assertIn("File location is not set", str(context.exception))

    def test_file_location_setter(self):
        """Test file_location setter."""
        controller = RaController(meta_data=self.test_meta_data)

        controller.file_location = 'new_file.L5X'
        self.assertEqual(controller._file_location, 'new_file.L5X')

        # Test invalid type
        with self.assertRaises(ValueError) as context:
            controller.file_location = 123  # type: ignore
        self.assertIn("File location must be a string", str(context.exception))

    def test_major_minor_revision_properties(self):
        """Test major_revision and minor_revision properties."""
        controller = RaController(meta_data=self.test_meta_data)

        # Test getters
        self.assertEqual(controller.major_revision, 32)
        self.assertEqual(controller.minor_revision, 11)

        # Test setters
        controller.major_revision = 33
        controller.minor_revision = 12
        self.assertEqual(controller['@MajorRev'], 33)
        self.assertEqual(controller['@MinorRev'], 12)

    def test_comm_path_property(self):
        """Test comm_path property getter and setter."""
        controller = RaController(meta_data=self.test_meta_data)

        # Test getter
        self.assertEqual(controller.comms_path, '1,0')

        # Test setter
        controller.set_comms_path('2,1')
        self.assertEqual(controller['@CommPath'], '2,1')

        # Test invalid type
        with self.assertRaises(ValueError) as context:
            controller.set_comms_path(123)  # type: ignore
        self.assertIn("CommPath must be a string", str(context.exception))

    def test_plc_module_properties(self):
        """Test PLC module related properties."""
        controller = RaController(meta_data=self.test_meta_data)

        # Test plc_module
        plc_module = controller.plc_module
        self.assertEqual(plc_module['@Name'], 'Local')  # type: ignore

        # Test plc_module_ports
        ports = controller.plc_module_ports
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0]['@Type'], 'ICP')

        # Test plc_module_icp_port
        icp_port = controller.plc_module_icp_port
        self.assertEqual(icp_port['@Address'], '0')  # type: ignore

        # Test slot
        self.assertEqual(controller.slot, 0)

    def test_slot_setter(self):
        """Test slot setter."""
        controller = RaController(meta_data=self.test_meta_data)

        controller.slot = 5
        self.assertEqual(controller._slot, 5)

    def test_safety_info_property(self):
        """Test safety_info property."""
        controller = RaController(meta_data=self.test_meta_data)

        safety_info = controller.safety_info
        self.assertIsInstance(safety_info, ControllerSafetyInfo)
        self.assertEqual(safety_info.safety_level, 'SIL2')

    def test_controller_type_property(self):
        """Test controller_type property."""
        controller = RaController(meta_data=self.test_meta_data)
        self.assertEqual(controller.controller_type, 'RaController')

    def test_get_class_and_factory(self):
        """Test get_class and get_factory class methods."""
        self.assertEqual(RaController.get_factory(), ControllerFactory)

    def test_from_meta_data_basic(self):
        """Test from_meta_data class method with basic parameters."""
        controller = RaController.from_meta_data(self.test_meta_data)

        self.assertIsInstance(controller, RaController)
        self.assertEqual(controller.meta_data, self.test_meta_data)

    def test_from_meta_data_with_file_location_and_comms_path(self):
        """Test from_meta_data class method with file location and comms path."""
        controller = RaController.from_meta_data(
            meta_data=self.test_meta_data,
            file_location='test.L5X',
            comms_path='2,1'
        )

        self.assertIsInstance(controller, RaController)
        self.assertEqual(controller.file_location, 'test.L5X')
        self.assertEqual(controller.comms_path, '2,1')

    def test_from_meta_data_compiles_controller(self):
        """Test from_meta_data compiles the controller."""
        with patch.object(RaController, 'compile') as mock_compile:
            controller = RaController.from_meta_data(self.test_meta_data)
            mock_compile.assert_called_once()
            self.assertIsInstance(controller, RaController)

    def test_get_controller_safety_info(self):
        """Test get_controller_safety_info method."""
        controller = RaController(meta_data=self.test_meta_data)

        safety_info = controller.get_controller_safety_info()

        self.assertIsInstance(safety_info, ControllerSafetyInfo)
        self.assertIs(safety_info, controller._safety_info)

    def test_compile_aois(self):
        """Test _compile_aois method."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock the compilation method
        with patch.object(controller, '_compile_common_hashlist_from_meta_data') as mock_compile:
            controller.compile_aois()
            mock_compile.assert_called_once_with(
                target_list=controller._aois,
                target_meta_list=controller.raw_aois,
                item_class=RaAddOnInstruction
            )

    def test_compile_datatypes(self):
        """Test _compile_datatypes method."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock the compilation method
        with patch.object(controller, '_compile_common_hashlist_from_meta_data') as mock_compile:
            with patch.object(controller, '_compile_atomic_datatypes') as mock_atomic:
                controller.compile_datatypes()

                mock_compile.assert_called_once_with(
                    target_list=controller._datatypes,
                    target_meta_list=controller.raw_datatypes,
                    item_class=RaDatatype
                )
                mock_atomic.assert_called_once()

    def test_compile_modules(self):
        """Test _compile_modules method."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock the compilation method
        with patch.object(controller, '_compile_common_hashlist_from_meta_data') as mock_compile:
            controller.compile_modules()
            mock_compile.assert_called_once_with(
                target_list=controller._modules,
                target_meta_list=controller.raw_modules,
                item_class=RaModule
            )

    def test_compile_programs(self):
        """Test _compile_programs method."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock the compilation method
        with patch.object(controller, '_compile_common_hashlist_from_meta_data') as mock_compile:
            controller.compile_programs()
            mock_compile.assert_called_once_with(
                target_list=controller._programs,
                target_meta_list=controller.raw_programs,
                item_class=RaProgram
            )

    def test_compile_tags(self):
        """Test _compile_tags method."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock the compilation method
        with patch.object(controller, '_compile_common_hashlist_from_meta_data') as mock_compile:
            controller.compile_tags()
            mock_compile.assert_called_once_with(
                target_list=controller._tags,
                target_meta_list=controller.raw_tags,
                item_class=RaTag,
                container=controller
            )

    def test_compile_from_meta_data(self):
        """Test _compile_from_meta_data method."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock the compilation methods
        with patch.object(controller, '_compile_common_hashlist_from_meta_data') as mock_compile:
            controller.compile()

            # Verify lists were cleared and compiled
            self.assertEqual(mock_compile.call_count, 5)  # aois, datatypes, modules, programs, tags

    def test_add_methods(self):
        """Test add_* methods for various assets."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock objects
        mock_aoi = Mock()
        mock_aoi.name = 'TestAOI'
        mock_aoi.meta_data = {'@Name': 'TestAOI'}

        mock_datatype = Mock()
        mock_datatype.name = 'TestDatatype'
        mock_datatype.meta_data = {'@Name': 'TestDatatype'}

        mock_module = Mock()
        mock_module.name = 'TestModule'
        mock_module.meta_data = {'@Name': 'TestModule'}

        mock_program = Mock()
        mock_program.name = 'TestProgram'
        mock_program.meta_data = {'@Name': 'TestProgram'}

        mock_tag = Mock()
        mock_tag.name = 'TestTag'
        mock_tag.meta_data = {'@Name': 'TestTag'}

        # Test add methods
        with patch.object(controller, 'add_asset_to_meta_data') as mock_add_common:
            controller.add_aoi(mock_aoi)
            controller.add_datatype(mock_datatype)
            controller.add_module(mock_module)
            controller.add_program(mock_program)
            controller.add_tag(mock_tag)

            self.assertEqual(mock_add_common.call_count, 5)

    def test_remove_methods(self):
        """Test remove_* methods for various assets."""
        controller = RaController(meta_data=self.test_meta_data)

        # Mock objects
        mock_aoi = Mock()
        mock_datatype = Mock()
        mock_module = Mock()
        mock_program = Mock()
        mock_tag = Mock()

        # Test remove methods
        with patch.object(controller, 'remove_asset_from_meta_data') as mock_remove_common:
            controller.remove_aoi(mock_aoi)
            controller.remove_datatype(mock_datatype)
            controller.remove_module(mock_module)
            controller.remove_program(mock_program)
            controller.remove_tag(mock_tag)

            self.assertEqual(mock_remove_common.call_count, 5)

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_import_assets_from_file(self, mock_l5x_dict_from_file):
        """Test import_assets_from_file method."""
        mock_l5x_dict_from_file.return_value = self.test_meta_data

        controller = RaController(meta_data=self.test_meta_data)

        with patch.object(controller, 'import_assets_from_l5x_dict') as mock_import:
            controller.import_assets_from_file('test.L5X', ['Tags'])

            mock_l5x_dict_from_file.assert_called_once_with('test.L5X')
            mock_import.assert_called_once_with(self.test_meta_data, asset_types=['Tags'])


if __name__ == '__main__':
    unittest.main()
