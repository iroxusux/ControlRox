"""Unit tests for the module module."""

import unittest
from unittest.mock import Mock, patch
from enum import Enum

from controlrox.models.plc.rockwell.controller import RaController
from controlrox.models.plc.rockwell.module import (
    RaModule,
    RaModuleConnectionTag,
    RaModuleControlsType
)
from controlrox.models.plc.rockwell import meta as plc_meta


class TestModuleControlsType(unittest.TestCase):
    """Test cases for ModuleControlsType enum."""

    def test_enum_values(self):
        """Test that all enum values are correct."""
        expected_values = {
            'UNKOWN': 'Unknown',
            'PLC': 'PLC',
            'ETHERNET': 'Ethernet',
            'SERIAL': 'Serial',
            'BLOCK': 'Block',
            'SAFETY_BLOCK': 'SafetyBlock',
            'DRIVE': 'Drive',
            'POINT_IO': 'PointIO'
        }

        for attr_name, expected_value in expected_values.items():
            enum_member = getattr(RaModuleControlsType, attr_name)
            self.assertEqual(enum_member.value, expected_value)

    def test_enum_is_enum(self):
        """Test that ModuleControlsType is properly an Enum."""
        self.assertTrue(issubclass(RaModuleControlsType, Enum))
        self.assertGreaterEqual(len(RaModuleControlsType), 8)

    def test_enum_members_accessible(self):
        """Test that all enum members are accessible."""
        self.assertEqual(RaModuleControlsType.UNKOWN, RaModuleControlsType.UNKOWN)
        self.assertEqual(RaModuleControlsType.PLC, RaModuleControlsType.PLC)
        self.assertEqual(RaModuleControlsType.ETHERNET, RaModuleControlsType.ETHERNET)
        self.assertEqual(RaModuleControlsType.SERIAL, RaModuleControlsType.SERIAL)
        self.assertEqual(RaModuleControlsType.BLOCK, RaModuleControlsType.BLOCK)
        self.assertEqual(RaModuleControlsType.SAFETY_BLOCK, RaModuleControlsType.SAFETY_BLOCK)
        self.assertEqual(RaModuleControlsType.DRIVE, RaModuleControlsType.DRIVE)
        self.assertEqual(RaModuleControlsType.POINT_IO, RaModuleControlsType.POINT_IO)


class TestModuleConnectionTag(unittest.TestCase):
    """Test cases for ModuleConnectionTag class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_controller = Mock(spec=RaController)

        self.sample_tag_data = {
            '@ConfigSize': '128',
            'Data': [
                {
                    '@Format': 'L5X',
                    'SomeL5XData': 'value'
                },
                {
                    '@Format': 'Decorated',
                    'Structure': {
                        '@DataType': 'DINT',
                        'ArrayMember': {
                            '@Dimensions': '10'
                        }
                    }
                }
            ]
        }

    def test_initialization(self):
        """Test ModuleConnectionTag initialization."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,
        )

        self.assertEqual(tag['@ConfigSize'], '128')

    def test_config_size_property(self):
        """Test config_size property getter."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        self.assertEqual(tag.config_size, 128)

    def test_data_property_with_list(self):
        """Test data property when Data is a list."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        data = tag.data
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['@Format'] == 'L5X'
        assert data[1]['@Format'] == 'Decorated'

    def test_data_property_with_none(self):
        """Test data property when Data is None."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'] = None

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        data = tag.data
        assert data == [{}]

    def test_data_property_with_missing_data(self):
        """Test data property when Data key is missing."""
        tag_data = self.sample_tag_data.copy()
        del tag_data['Data']

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        data = tag.data
        assert data == [{}]

    def test_data_decorated_property(self):
        """Test data_decorated property finds Decorated format."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        decorated = tag.data_decorated
        assert decorated['@Format'] == 'Decorated'
        assert 'Structure' in decorated

    def test_data_decorated_property_not_found(self):
        """Test data_decorated property when Decorated format not found."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'] = [{'@Format': 'L5X'}]

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        decorated = tag.data_decorated
        assert decorated == {}

    def test_data_decorated_property_with_single_item(self):
        """Test data_decorated property when data is not a list."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'] = {'@Format': 'Decorated', 'Structure': {}}

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        decorated = tag.data_decorated
        assert decorated['@Format'] == 'Decorated'

    def test_data_decorated_structure_property(self):
        """Test data_decorated_structure property."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        structure = tag.data_decorated_structure
        expected = {
            '@DataType': 'DINT',
            'ArrayMember': {
                '@Dimensions': '10'
            }
        }
        assert structure == expected

    def test_data_decorated_structure_array_member_property(self):
        """Test data_decorated_structure_array_member property."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        array_member = tag.data_decorated_structure_array_member
        assert array_member == {'@Dimensions': '10'}

    def test_data_decorated_stucture_datatype_property(self):
        """Test data_decorated_stucture_datatype property."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        datatype = tag.data_decorated_stucture_datatype
        assert datatype == 'DINT'

    def test_data_decorated_stucture_size_property(self):
        """Test data_decorated_stucture_size property."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        size = tag.data_decorated_stucture_size
        assert size == '10'

    def test_data_l5x_property(self):
        """Test data_l5x property finds L5X format."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        l5x = tag.data_l5x
        assert l5x['@Format'] == 'L5X'
        assert l5x['SomeL5XData'] == 'value'

    def test_data_l5x_property_not_found(self):
        """Test data_l5x property when L5X format not found."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'] = [{'@Format': 'Decorated'}]

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        l5x = tag.data_l5x
        assert l5x == {}

    def test_get_data_multiplier_sint(self):
        """Test get_data_multiplier for SINT datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'SINT'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 1

    def test_get_data_multiplier_int(self):
        """Test get_data_multiplier for INT datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'INT'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 2

    def test_get_data_multiplier_dint(self):
        """Test get_data_multiplier for DINT datatype."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 4

    def test_get_data_multiplier_real(self):
        """Test get_data_multiplier for REAL datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'REAL'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 4

    def test_get_data_multiplier_dword(self):
        """Test get_data_multiplier for DWORD datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'DWORD'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 4

    def test_get_data_multiplier_lint(self):
        """Test get_data_multiplier for LINT datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'LINT'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 8

    def test_get_data_multiplier_lreal(self):
        """Test get_data_multiplier for LREAL datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'LREAL'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 8

    def test_get_data_multiplier_lword(self):
        """Test get_data_multiplier for LWORD datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'LWORD'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 8

    def test_get_data_multiplier_unsupported_datatype(self):
        """Test get_data_multiplier raises error for unsupported datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['@DataType'] = 'UNSUPPORTED'

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        with self.assertRaises(ValueError) as context:
            tag.get_data_multiplier()
        self.assertIn("Unsupported datatype: UNSUPPORTED", str(context.exception))

    def test_get_data_multiplier_no_datatype(self):
        """Test get_data_multiplier returns 0 when no datatype."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure'] = {}

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        multiplier = tag.get_data_multiplier()
        assert multiplier == 0

    def test_get_resolved_size(self):
        """Test get_resolved_size calculation."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        # Size is '10', multiplier for DINT is 4
        resolved_size = tag.get_resolved_size()
        assert resolved_size == 40  # 10 * 4

    def test_get_resolved_size_no_size(self):
        """Test get_resolved_size returns 0 when no size."""
        tag_data = self.sample_tag_data.copy()
        tag_data['Data'][1]['Structure']['ArrayMember'] = {}

        tag = RaModuleConnectionTag(
            meta_data=tag_data,

        )

        resolved_size = tag.get_resolved_size()
        assert resolved_size == 0

    def test_inheritance_from_plc_object(self):
        """Test that ModuleConnectionTag inherits from PlcObject."""
        tag = RaModuleConnectionTag(
            meta_data=self.sample_tag_data,

        )

        assert isinstance(tag, plc_meta.PlcObject)


class TestModule(unittest.TestCase):
    """Test cases for Module class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_controller = Mock(spec=RaController)

        self.sample_module_data = {
            '@Name': 'TestModule',
            '@CatalogNumber': '1756-L73',
            '@Vendor': '1',
            '@ProductType': '14',
            '@ProductCode': '166',
            '@Major': '33',
            '@Minor': '11',
            '@ParentModule': 'Local',
            '@ParentModPortId': '1',
            '@Inhibited': 'false',
            '@MajorFault': 'false',
            'Description': 'Test module description',
            'EKey': {
                '@State': 'ExactMatch'
            },
            'Ports': {
                'Port': [
                    {
                        '@Id': '1',
                        '@Type': 'ICP'
                    }
                ]
            },
            'Communications': {
                'ConfigTag': {
                    '@ConfigSize': '128',
                    'Data': []
                },
                'Connections': {
                    'Connection': [
                        {
                            '@Name': 'Connection1',
                            '@ConfigCxnPoint': '1',
                            '@InputCxnPoint': '2',
                            '@OutputCxnPoint': '3',
                            '@InputSize': '64',
                            '@OutputSize': '32',
                            'InputTag': {
                                '@ConfigSize': '64',
                                'Data': []
                            },
                            'OutputTag': {
                                '@ConfigSize': '32',
                                'Data': []
                            }
                        }
                    ]
                }
            }
        }

    def test_initialization_default_meta_data(self):
        """Test initialization with empty meta data."""
        module = RaModule()

        # When no meta_data is provided, name defaults to 'Module' as defined in the default L5X file
        self.assertEqual(module.name, 'Module')

    def test_initialization_with_meta_data(self):
        """Test initialization with provided meta data."""
        with patch('controlrox.models.plc.rockwell.module.RaModule.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.name == 'TestModule'

    def test_dict_key_order(self):
        """Test dict_key_order property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        expected_order = [
            '@Name',
            '@CatalogNumber',
            '@Vendor',
            '@ProductType',
            '@ProductCode',
            '@Major',
            '@Minor',
            '@ParentModule',
            '@ParentModPortId',
            '@Inhibited',
            '@MajorFault',
            'Description',
            'EKey',
            'Ports',
            'Communications',
        ]

        assert module.dict_key_order == expected_order

    def test_catalog_number_property_getter(self):
        """Test catalog_number property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.catalog_number == '1756-L73'

    def test_catalog_number_property_setter_valid(self):
        """Test catalog_number property setter with valid value."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_catalog_number('1756-L74')
        assert module.catalog_number == '1756-L74'
        assert module['@CatalogNumber'] == '1756-L74'

    def test_catalog_number_property_setter_invalid(self):
        """Test catalog_number property setter with invalid value."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with patch.object(module, 'is_valid_module_string', return_value=False):
            with self.assertRaises(module.InvalidNamingException):
                module.set_catalog_number('invalid-catalog')

    def test_communications_property_getter(self):
        """Test communications property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        communications = module.communications
        assert isinstance(communications, dict)
        assert 'ConfigTag' in communications
        assert 'Connections' in communications

    def test_communications_property_setter_valid(self):
        """Test communications property setter with valid dictionary."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        new_communications = {'NewKey': 'NewValue'}
        module.set_communications(new_communications)
        assert module.communications == new_communications

    def test_communications_property_setter_invalid(self):
        """Test communications property setter with invalid type."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with self.assertRaisesRegex(ValueError, "Communications must be a dictionary!"):
            module.set_communications("not a dictionary")  # type: ignore

    def test_controller_connection_property(self):
        """Test controller_connection property returns first connection."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        connection = module.controller_connection
        assert connection['@Name'] == 'Connection1'

    def test_controller_connection_property_empty_connections(self):
        """Test controller_connection property when no connections."""
        module_data = self.sample_module_data.copy()
        module_data['Communications']['Connections']['Connection'] = []

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        connection = module.controller_connection
        assert connection == {}

    def test_connections_property_with_list(self):
        """Test connections property when Connections contains a list."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        connections = module.connections
        assert isinstance(connections, list)
        assert len(connections) == 1
        assert connections[0]['@Name'] == 'Connection1'

    def test_connections_property_with_single_connection(self):
        """Test connections property when Connection is not a list."""
        module_data = self.sample_module_data.copy()
        module_data['Communications']['Connections']['Connection'] = {
            '@Name': 'SingleConnection'
        }

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        connections = module.connections
        assert isinstance(connections, list)
        assert len(connections) == 1
        assert connections[0]['@Name'] == 'SingleConnection'

    def test_connections_property_no_communications(self):
        """Test connections property when no communications."""
        module_data = self.sample_module_data.copy()
        module_data['Communications'] = None

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        connections = module.connections
        assert connections == []

    def test_connections_property_no_connections_key(self):
        """Test connections property when Connections key missing."""
        module_data = self.sample_module_data.copy()
        del module_data['Communications']['Connections']

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        connections = module.connections
        assert connections == []

    def test_config_connection_point_property(self):
        """Test config_connection_point property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        config_point = module.config_connection_point
        assert config_point == 1

    def test_config_connection_point_property_no_connections(self):
        """Test config_connection_point property when no connections."""
        module_data = self.sample_module_data.copy()
        module_data['Communications']['Connections']['Connection'] = []

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        config_point = module.config_connection_point
        assert config_point == -1

    def test_input_connection_point_property(self):
        """Test input_connection_point property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        input_point = module.input_connection_point
        assert input_point == 2

    def test_output_connection_point_property(self):
        """Test output_connection_point property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        output_point = module.output_connection_point
        assert output_point == 3

    def test_config_connection_size_property(self):
        """Test config_connection_size property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

            # Mock the config_tag
            mock_config_tag = Mock()
            mock_config_tag.config_size = '128'
            module._config_tag = mock_config_tag

        config_size = module.config_connection_size
        assert config_size == '128'

    def test_config_connection_size_property_no_config_tag(self):
        """Test config_connection_size property when no config tag."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )
            module['Communications'] = ''
            module._config_tag = None

        config_size = module.config_connection_size
        assert config_size == 0

    def test_input_connection_size_property(self):
        """Test input_connection_size property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        input_size = module.input_connection_size
        assert input_size == 64

    def test_output_connection_size_property(self):
        """Test output_connection_size property."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        output_size = module.output_connection_size
        assert output_size == 32

    def test_vendor_property_getter(self):
        """Test vendor property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.vendor == '1'

    def test_vendor_property_setter_valid(self):
        """Test vendor property setter with valid integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_vendor('2')
        assert module.vendor == '2'
        assert module['@Vendor'] == '2'

    def test_vendor_property_setter_invalid(self):
        """Test vendor property setter with non-integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with self.assertRaisesRegex(ValueError, "Vendor must be an integer!"):
            module.set_vendor('not_an_integer')

    def test_product_type_property_getter(self):
        """Test product_type property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.product_type == '14'

    def test_product_type_property_setter_valid(self):
        """Test product_type property setter with valid integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_product_type('15')
        assert module.product_type == '15'

    def test_product_type_property_setter_invalid(self):
        """Test product_type property setter with non-integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with self.assertRaisesRegex(ValueError, "@ProductType must be an integer!"):
            module.set_product_type('invalid')

    def test_product_code_property_getter(self):
        """Test product_code property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.product_code == '166'

    def test_product_code_property_setter_valid(self):
        """Test product_code property setter with valid integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_product_code('167')
        assert module.product_code == '167'

    def test_product_code_property_setter_invalid(self):
        """Test product_code property setter with non-integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with self.assertRaisesRegex(ValueError, "@ProductCode must be an integer!"):
            module.set_product_code('abc')

    def test_major_property_getter(self):
        """Test major property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.major_version == '33'

    def test_major_property_setter_valid(self):
        """Test major property setter with valid integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_major_version_number('34')
        assert module.major_version == '34'

    def test_major_property_setter_invalid(self):
        """Test major property setter with non-integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with self.assertRaisesRegex(ValueError, "@Major must be an integer!"):
            module.set_major_version_number('v33')

    def test_minor_property_getter(self):
        """Test minor property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.minor_version == '11'

    def test_minor_property_setter_valid(self):
        """Test minor property setter with valid integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_minor_version_number('12')
        assert module.minor_version == '12'

    def test_minor_property_setter_invalid(self):
        """Test minor property setter with non-integer string."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        with self.assertRaisesRegex(ValueError, "@Minor must be an integer!"):
            module.set_minor_version_number('beta')

    @patch('controlrox.models.plc.rockwell.module.ControllerInstanceManager.get_controller', return_value=Mock())
    def test_parent_module_property(self, mock_get_controller):
        """Test parent_module property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert module.parent_module is not None

    def test_inhibited_property_getter(self):
        """Test inhibited property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert not module.inhibited

    def test_inhibited_property_setter(self):
        """Test inhibited property setter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_is_inhibited(True)
        assert module.inhibited

        module.set_is_inhibited(False)
        assert not module.inhibited

    def test_major_fault_property_getter(self):
        """Test major_fault property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert not module.major_fault

    def test_major_fault_property_setter(self):
        """Test major_fault property setter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        module.set_major_fault(True)
        assert module.major_fault

    def test_ekey_property(self):
        """Test ekey property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        ekey = module.ekey
        assert ekey['@State'] == 'ExactMatch'

    def test_ports_property_with_list(self):
        """Test ports property when Ports contains a list."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        ports = module.ports
        assert isinstance(ports, list)
        assert len(ports) == 1
        assert ports[0]['@Id'] == '1'

    def test_ports_property_with_single_port(self):
        """Test ports property when Port is not a list."""
        module_data = self.sample_module_data.copy()
        module_data['Ports']['Port'] = {'@Id': '2', '@Type': 'ICP'}

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        ports = module.ports
        assert isinstance(ports, list)
        assert len(ports) == 1
        assert ports[0]['@Id'] == '2'

    def test_ports_property_no_ports(self):
        """Test ports property when no Ports."""
        module_data = self.sample_module_data.copy()
        module_data['Ports'] = None

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        ports = module.ports
        assert ports == []

    def test_config_tag_property(self):
        """Test config_tag property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

            mock_config_tag = Mock()
            module._config_tag = mock_config_tag

        assert module.config_tag is mock_config_tag

    def test_input_tag_property(self):
        """Test input_tag property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

            mock_input_tag = Mock()
            module._input_tag = mock_input_tag

        assert module.input_tag is mock_input_tag

    def test_output_tag_property(self):
        """Test output_tag property getter."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

            mock_output_tag = Mock()
            module._output_tag = mock_output_tag

        assert module.output_tag is mock_output_tag

    def test_inheritance_from_plc_object(self):
        """Test that Module inherits from NamedPlcObject."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.sample_module_data,

            )

        assert isinstance(module, plc_meta.PlcObject)


class TestModuleEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for Module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock()

        self.minimal_module_data = {
            '@Name': 'MinimalModule',
            '@CatalogNumber': '1756-L73',
            '@Vendor': '1',
            '@ProductType': '14',
            '@ProductCode': '166',
            '@Major': '33',
            '@Minor': '11',
            '@ParentModule': 'Local',
            '@ParentModPortId': '1',
            '@Inhibited': 'false',
            '@MajorFault': 'false'
        }

    def test_module_with_missing_optional_fields(self):
        """Test module with missing optional fields."""
        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=self.minimal_module_data,

            )

        self.assertEqual(module.name, 'MinimalModule')
        self.assertEqual(module.catalog_number, '1756-L73')

        # These should NOT raise KeyError for missing keys
        _ = module.description
        _ = module.ekey

    def test_empty_structures_handling(self):
        """Test handling of empty or None structures."""
        module_data = self.minimal_module_data.copy()
        module_data['Ports'] = ''
        module_data['Communications'] = {}  # type: ignore

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        self.assertEqual(module.ports, [])
        self.assertEqual(module.connections, [])
        self.assertEqual(module.controller_connection, {})

    def test_connections_structure_normalization(self):
        """Test that connections structure gets normalized properly."""
        module_data = self.minimal_module_data.copy()
        module_data['Communications'] = {  # type: ignore
            'Connections': 'not_a_dict'  # Invalid structure
        }

        with patch('controlrox.models.plc.rockwell.module.compile'):
            module = RaModule(
                meta_data=module_data,

            )

        # Should normalize to proper structure
        connections = module.connections
        self.assertEqual(connections, [])

        # Check that the structure was normalized
        self.assertEqual(module.communications['Connections'], {'Connection': []})


class TestModuleIntegration(unittest.TestCase):
    """Integration tests for Module class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)

        self.complex_module_data = {
            '@Name': 'ComplexModule',
            '@CatalogNumber': '1756-L73',
            '@Vendor': '1',
            '@ProductType': '14',
            '@ProductCode': '166',
            '@Major': '33',
            '@Minor': '11',
            '@ParentModule': 'Local',
            '@ParentModPortId': '1',
            '@Inhibited': 'false',
            '@MajorFault': 'false',
            'Description': 'Complex test module',
            'EKey': {'@State': 'ExactMatch'},
            'Ports': {
                'Port': [
                    {'@Id': '1', '@Type': 'ICP'},
                    {'@Id': '2', '@Type': 'Ethernet'}
                ]
            },
            'Communications': {
                'ConfigTag': {
                    '@ConfigSize': '256',
                    'Data': [
                        {'@Format': 'L5X'},
                        {
                            '@Format': 'Decorated',
                            'Structure': {
                                '@DataType': 'DINT',
                                'ArrayMember': {'@Dimensions': '20'}
                            }
                        }
                    ]
                },
                'Connections': {
                    'Connection': [
                        {
                            '@Name': 'Connection1',
                            '@ConfigCxnPoint': '1',
                            '@InputCxnPoint': '2',
                            '@OutputCxnPoint': '3',
                            '@InputSize': '128',
                            '@OutputSize': '64',
                            'InputTag': {
                                '@ConfigSize': '128',
                                'Data': [
                                    {
                                        '@Format': 'Decorated',
                                        'Structure': {
                                            '@DataType': 'REAL',
                                            'ArrayMember': {'@Dimensions': '32'}
                                        }
                                    }
                                ]
                            },
                            'OutputTag': {
                                '@ConfigSize': '64',
                                'Data': [
                                    {
                                        '@Format': 'Decorated',
                                        'Structure': {
                                            '@DataType': 'INT',
                                            'ArrayMember': {'@Dimensions': '512'}
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

    def test_complex_module_creation(self):
        """Test creating a complex module with all features."""

        module = RaModule(
            meta_data=self.complex_module_data,

        )

        # Test basic properties
        self.assertEqual(module.name, 'ComplexModule')
        self.assertEqual(module.catalog_number, '1756-L73')
        self.assertEqual(module.vendor, '1')

        # Test complex structures
        self.assertEqual(len(module.ports), 2)
        self.assertEqual(module.ports[0]['@Id'], '1')
        self.assertEqual(module.ports[1]['@Id'], '2')

        # Test connection properties
        self.assertEqual(module.config_connection_point, 1)
        self.assertEqual(module.input_connection_point, 2)
        self.assertEqual(module.output_connection_point, 3)
        self.assertEqual(module.input_connection_size, 128)
        self.assertEqual(module.output_connection_size, 64)

        # Test connection tags
        self.assertIsInstance(module.config_tag, RaModuleConnectionTag)
        self.assertIsInstance(module.input_tag, RaModuleConnectionTag)
        self.assertIsInstance(module.output_tag, RaModuleConnectionTag)

        # Test connection tag functionality
        self.assertEqual(module.config_tag.config_size, 256)  # type: ignore
        self.assertEqual(module.input_tag.config_size, 128)  # type: ignore
        self.assertEqual(module.output_tag.config_size, 64)  # type: ignore

        # Test resolved sizes
        config_resolved = module.config_tag.get_resolved_size()  # 20 * 4 (DINT)  # type: ignore
        self.assertEqual(config_resolved, 80)

        input_resolved = module.input_tag.get_resolved_size()  # 32 * 4 (REAL)  # type: ignore
        self.assertEqual(input_resolved, 128)

        output_resolved = module.output_tag.get_resolved_size()  # 512 * 2 (INT)  # type: ignore
        self.assertEqual(output_resolved, 1024)

    def test_module_property_modifications(self):
        """Test modifying various module properties."""

        module = RaModule(
            meta_data=self.complex_module_data,

        )

        # Test catalog number modification
        module.set_catalog_number('1756-L74')
        self.assertEqual(module.catalog_number, '1756-L74')

        # Test numeric property modifications
        module.set_vendor('2')
        self.assertEqual(module.vendor, '2')

        module.set_product_type('15')
        self.assertEqual(module.product_type, '15')

        module.set_product_code('167')
        self.assertEqual(module.product_code, '167')

        module.set_major_version_number('34')
        self.assertEqual(module.major_version, '34')

        module.set_minor_version_number('12')
        self.assertEqual(module.minor_version, '12')

        # Test boolean property modifications
        module.set_is_inhibited(True)
        self.assertTrue(module.inhibited)

        module.set_major_fault(True)
        self.assertTrue(module.major_fault)

        # Test communications modification
        new_communications = {'NewKey': 'NewValue'}
        module.set_communications(new_communications)
        self.assertEqual(module.communications, new_communications)

    @patch('controlrox.models.plc.rockwell.meta.l5x_dict_from_file')
    def test_default_file_loading_integration(self, mock_l5x_dict):
        """Test complete integration with default file loading."""
        mock_l5x_dict.return_value = {'Module': self.complex_module_data}

        module = RaModule(

        )

        mock_l5x_dict.assert_called_once_with(plc_meta.PLC_MOD_FILE)
        assert module.name == 'ComplexModule'
        assert isinstance(module.config_tag, RaModuleConnectionTag)
        assert isinstance(module.input_tag, RaModuleConnectionTag)
        assert isinstance(module.output_tag, RaModuleConnectionTag)


if __name__ == '__main__':
    unittest.main()
