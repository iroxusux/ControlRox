"""Test suite for tag module"""
import unittest
from unittest.mock import Mock
from controlrox.interfaces import ILogicTagScope
from controlrox.models.plc.rockwell.tag import RaTag, DataValueMember, TagEndpoint


class TestDataValueMember(unittest.TestCase):
    """Test class for DataValueMember"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_controller = Mock()
        self.mock_parent = Mock()
        self.valid_metadata = {'@Name': 'TestMember', '@DataType': 'BOOL'}

    def test_init_with_valid_params(self):
        """Test DataValueMember initialization with valid parameters"""
        member = DataValueMember(
            name="TestMember",
            meta_data=self.valid_metadata,

            parent=self.mock_parent
        )

        self.assertEqual(member.parent, self.mock_parent)
        self.assertEqual(member.name, "TestMember")

    def test_init_without_metadata_raises_error(self):
        """Test that missing metadata raises ValueError"""
        with self.assertRaises(ValueError) as context:
            DataValueMember(
                name="TestMember",
                meta_data=None,

                parent=self.mock_parent
            )

        self.assertEqual(str(context.exception), 'Cannot have an empty DataValueMember!')

    def test_init_without_parent_raises_error(self):
        """Test that missing parent raises ValueError"""
        with self.assertRaises(ValueError) as context:
            DataValueMember(
                name="TestMember",
                meta_data=self.valid_metadata,

                parent=None
            )

        self.assertEqual(str(context.exception), 'Cannot have a datavalue member without a parent!')

    def test_parent_property(self):
        """Test parent property returns correct parent"""
        member = DataValueMember(
            meta_data=self.valid_metadata,

            parent=self.mock_parent
        )

        self.assertEqual(member.parent, self.mock_parent)


class TestTagEndpoint(unittest.TestCase):
    """Test class for TagEndpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_controller = Mock()
        self.mock_parent_tag = Mock()
        self.test_meta_data = "TestTag.Endpoint"

    def test_init(self):
        """Test TagEndpoint initialization"""
        endpoint = TagEndpoint(
            meta_data=self.test_meta_data,

            parent_tag=self.mock_parent_tag
        )

        self.assertEqual(endpoint._parent_tag, self.mock_parent_tag)

    def test_name_property(self):
        """Test name property returns meta_data"""
        endpoint = TagEndpoint(
            meta_data=self.test_meta_data,

            parent_tag=self.mock_parent_tag
        )

        self.assertEqual(endpoint.name, self.test_meta_data)


class TestTag(unittest.TestCase):
    """Test class for Tag"""

    def setUp(self):
        """Set up test fixtures"""
        from controlrox.models.plc.rockwell.controller import RaController
        self.mock_controller = Mock(spec=RaController)
        self.mock_container = Mock()
        self.valid_metadata = {
            '@Name': 'TestTag',
            '@Class': 'Standard',
            '@TagType': 'Base',
            '@DataType': 'BOOL',
            '@Dimensions': '',
            '@Constant': 'false',
            '@ExternalAccess': 'ReadOnly',
            'Data': []
        }

    def test_init_with_minimal_params(self):
        """Test Tag initialization with minimal parameters"""
        _ = RaTag()

    def test_init_with_all_params(self):
        """Test Tag initialization with all parameters"""
        tag = RaTag(
            meta_data=self.valid_metadata,

            name="TestTag",
            description="Test Description",
            tag_klass="Standard",
            tag_type="Base",
            datatype="BOOL",
            dimensions="1",
            constant=True,
            external_access="ReadOnly",
            container=self.mock_container
        )

        self.assertEqual(tag.name, "TestTag")
        self.assertEqual(tag.description, "Test Description")
        self.assertEqual(tag.container, self.mock_container)

    def test_dict_key_order(self):
        """Test dict_key_order property returns correct order"""
        tag = RaTag(meta_data=self.valid_metadata, )

        expected_order = [
            '@Name', '@Class', '@TagType', '@DataType', '@Dimensions',
            '@Radix', '@AliasFor', '@Constant', '@ExternalAccess',
            'ConsumeInfo', 'ProduceInfo', 'Description', 'Data'
        ]

        self.assertEqual(tag.dict_key_order, expected_order)

    def test_alias_for_property(self):
        """Test alias_for property"""
        metadata_with_alias = self.valid_metadata.copy()
        metadata_with_alias['@AliasFor'] = 'OriginalTag.Member'

        tag = RaTag(meta_data=metadata_with_alias, )

        self.assertEqual(tag.alias_for, 'OriginalTag.Member')

    def test_alias_for_base_name(self):
        """Test alias_for_base_name property"""
        metadata_with_alias = self.valid_metadata.copy()
        metadata_with_alias['@AliasFor'] = 'OriginalTag.Member:Bit0'

        tag = RaTag(meta_data=metadata_with_alias, )

        self.assertEqual(tag.alias_for_base_name, 'OriginalTag')

    def test_alias_for_base_name_none(self):
        """Test alias_for_base_name returns None when no alias"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.alias_for_base_name, '')

    def test_class_property(self):
        """Test class_ property getter and setter"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.klass, 'Standard')

        tag.klass = 'Safety'
        self.assertEqual(tag.klass, 'Safety')

    def test_class_setter_invalid_type(self):
        """Test class_ setter with invalid type raises error"""
        tag = RaTag(meta_data=self.valid_metadata, )

        with self.assertRaises(ValueError) as context:
            tag.klass = 123  # type: ignore

        self.assertEqual(str(context.exception), "Class must be a string!")

    def test_class_setter_invalid_value(self):
        """Test class_ setter with invalid value raises error"""
        tag = RaTag(meta_data=self.valid_metadata, )

        with self.assertRaises(ValueError) as context:
            tag.klass = "Invalid"

        self.assertEqual(str(context.exception), "Class must be one of: Standard, Safety!")

    def test_constant_property(self):
        """Test constant property getter and setter"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.constant, 'false')

        tag.constant = True
        self.assertEqual(tag.constant, 'true')

        tag.constant = False
        self.assertEqual(tag.constant, 'false')

    def test_raw_datatype_property(self):
        """Test datatype property getter and setter"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.raw_datatype, 'BOOL')

        tag.raw_datatype = 'DINT'
        self.assertEqual(tag.raw_datatype, 'DINT')

    def test_dimensions_property(self):
        """Test dimensions property getter and setter"""
        tag = RaTag(meta_data=self.valid_metadata, )

        tag.dimensions = '10'
        self.assertEqual(tag.dimensions, '10')

        tag.dimensions = 5
        self.assertEqual(tag.dimensions, '5')

    def test_dimensions_setter_negative_int(self):
        """Test dimensions setter with negative integer raises error"""
        tag = RaTag(meta_data=self.valid_metadata, )

        with self.assertRaises(ValueError) as context:
            tag.dimensions = -1

        self.assertEqual(str(context.exception), "Dimensions must be a positive integer!")

    def test_external_access_property(self):
        """Test external_access property getter and setter"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.external_access, 'ReadOnly')

        tag.external_access = 'Read/Write'
        self.assertEqual(tag.external_access, 'Read/Write')

    def test_external_access_setter_invalid_value(self):
        """Test external_access setter with invalid value raises error"""
        tag = RaTag(meta_data=self.valid_metadata, )

        with self.assertRaises(ValueError) as context:
            tag.external_access = "Invalid"

        self.assertEqual(str(context.exception), "External access must be one of: None, ReadOnly, Read/Write!")

    def test_tag_type_property(self):
        """Test tag_type property getter and setter"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.tag_type, 'Base')

        tag.tag_type = 'Structure'
        self.assertEqual(tag.tag_type, 'Structure')

    def test_tag_type_setter_invalid_value(self):
        """Test tag_type setter with invalid value raises error"""
        tag = RaTag(meta_data=self.valid_metadata, )

        with self.assertRaises(ValueError) as context:
            tag.tag_type = "Invalid"

        self.assertEqual(str(context.exception), "Tag type must be one of: Atomic, Structure, Array!")

    def test_data_property_single_item(self):
        """Test data property with single data item"""
        metadata = self.valid_metadata.copy()
        metadata['Data'] = {'@Format': 'L5K', 'Value': '0'}

        tag = RaTag(meta_data=metadata, )

        self.assertEqual(len(tag.data), 1)
        self.assertEqual(tag.data[0]['@Format'], 'L5K')

    def test_data_property_list(self):
        """Test data property with list of data items"""
        metadata = self.valid_metadata.copy()
        metadata['Data'] = [{'@Format': 'L5K'}, {'@Format': 'Decorated'}]

        tag = RaTag(meta_data=metadata, )

        self.assertEqual(len(tag.data), 2)

    def test_decorated_data_property(self):
        """Test decorated_data property"""
        metadata = self.valid_metadata.copy()
        metadata['Data'] = [
            {'@Format': 'L5K', 'Value': '0'},
            {'@Format': 'Decorated', 'Structure': {}}
        ]

        tag = RaTag(meta_data=metadata, )

        decorated = tag.decorated_data
        self.assertEqual(decorated['@Format'], 'Decorated')  # type: ignore

    def test_l5k_data_property(self):
        """Test l5k_data property"""
        metadata = self.valid_metadata.copy()
        metadata['Data'] = [
            {'@Format': 'L5K', 'Value': '0'},
            {'@Format': 'Decorated', 'Structure': {}}
        ]

        tag = RaTag(meta_data=metadata, )

        l5k = tag.l5k_data
        self.assertEqual(l5k['@Format'], 'L5K')  # type: ignore

    def test_scope_property(self):
        """Test scope property for different container types"""
        # Test controller scope
        tag = RaTag(meta_data=self.valid_metadata, )
        tag._container = self.mock_controller
        self.assertEqual(tag.scope, ILogicTagScope.CONTROLLER)

    def test_get_alias_string_no_alias(self):
        """Test get_alias_string method without alias"""
        tag = RaTag(meta_data=self.valid_metadata, )
        tag.set_name('TestTag')

        result = tag.get_alias_string()
        self.assertEqual(result, 'TestTag')

    def test_get_alias_string_with_additional_elements(self):
        """Test get_alias_string method with additional elements"""
        tag = RaTag(meta_data=self.valid_metadata, )
        tag.set_name('TestTag')

        result = tag.get_alias_string('.Member')
        self.assertEqual(result, 'TestTag.Member')

    def test_get_base_tag_no_alias(self):
        """Test get_base_tag method without alias"""
        tag = RaTag(meta_data=self.valid_metadata, )

        result = tag.get_base_tag()
        self.assertEqual(result, tag)

    def test_get_parent_tag_no_alias(self):
        """Test get_parent_tag static method without alias"""
        tag = RaTag(meta_data=self.valid_metadata, )

        result = RaTag.get_parent_tag(tag)
        self.assertIsNone(result)

    def test_datavalue_members_property_empty(self):
        """Test datavalue_members property with no decorated data"""
        tag = RaTag(meta_data=self.valid_metadata, )

        self.assertEqual(tag.datavalue_members, [])

    def test_endpoint_operands_property_no_datatype(self):
        """Test endpoint_operands property with no datatype"""
        metadata = self.valid_metadata.copy()
        metadata['@DataType'] = ''

        tag = RaTag(meta_data=metadata, )

        self.assertEqual(tag.endpoint_operands, [])

    def test_init_with_container_program(self):
        """Test initialization with Program container"""
        from controlrox.models.plc.rockwell.program import RaProgram
        mock_program = Mock(spec=RaProgram)

        tag = RaTag(container=mock_program)

        self.assertEqual(tag.container, mock_program)
