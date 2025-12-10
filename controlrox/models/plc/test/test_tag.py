"""Unit tests for controlrox.models.plc.tag module."""
import unittest
from unittest.mock import Mock, patch

from controlrox.interfaces import LogicTagScope
from controlrox.models.plc.tag import Tag


class TestTag(unittest.TestCase):
    """Test cases for Tag class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteTag(Tag):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._dimensions = ''
                self._external_access = 'Read/Write'
                self._opcua_access = '1'
                self._safety_class = 'Standard'
                self._tag_scope = LogicTagScope.CONTROLLER
                self._is_constant = False

            def get_dimensions(self):
                return self._dimensions

            def get_endpoint_operands(self):
                return []

            def get_external_access(self):
                return self._external_access

            def get_opcua_access(self):
                return self._opcua_access

            def get_safety_class(self):
                return self._safety_class

            def get_tag_scope(self):
                return self._tag_scope

            def is_constant(self):
                return self._is_constant

            def set_dimensions(self, value):
                self._dimensions = str(value)

            def set_external_access(self, value):
                self._external_access = value

            def set_opcua_access(self, value):
                self._opcua_access = value

            def set_safety_class(self, value):
                self._safety_class = value

            def set_is_constant(self, value):
                self._is_constant = value

            def get_alias_for_name(self):
                if not self._aliased_tag:
                    raise NotImplementedError()
                return self._aliased_tag.name

            def get_alias_for_tag(self):
                if not self._aliased_tag:
                    raise NotImplementedError()
                return self._aliased_tag

            def get_base_tag(self):
                if not self._base_tag:
                    raise NotImplementedError()
                return self._base_tag

            def get_datatype(self):
                if not self._datatype:
                    raise NotImplementedError()
                return self._datatype

            def set_datatype(self, datatype):
                self._datatype = datatype

        self.ConcreteClass = ConcreteTag

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        tag = self.ConcreteClass()

        self.assertIsNotNone(tag)
        self.assertIsNone(tag._aliased_tag)
        self.assertIsNone(tag._base_tag)
        self.assertIsNone(tag._datatype)

    def test_init_with_metadata(self):
        """Test initialization with metadata dict."""
        meta_data = {'@Name': 'TestTag', '@TagType': 'Base'}
        tag = self.ConcreteClass(meta_data=meta_data)

        self.assertEqual(tag.meta_data, meta_data)

    def test_init_with_name_and_description(self):
        """Test initialization with name and description."""
        tag = self.ConcreteClass(
            name='MyTag',
            description='My Tag Description'
        )

        self.assertEqual(tag.name, 'MyTag')
        self.assertEqual(tag.description, 'My Tag Description')

    def test_get_dimensions(self):
        """Test get_dimensions method."""
        tag = self.ConcreteClass()
        tag._dimensions = '[10,5]'

        self.assertEqual(tag.get_dimensions(), '[10,5]')

    def test_get_endpoint_operands(self):
        """Test get_endpoint_operands method."""
        tag = self.ConcreteClass()

        operands = tag.get_endpoint_operands()

        self.assertIsInstance(operands, list)

    def test_get_external_access(self):
        """Test get_external_access method."""
        tag = self.ConcreteClass()

        access = tag.get_external_access()

        self.assertEqual(access, 'Read/Write')

    def test_get_opcua_access(self):
        """Test get_opcua_access method."""
        tag = self.ConcreteClass()

        access = tag.get_opcua_access()

        self.assertEqual(access, '1')

    def test_get_safety_class(self):
        """Test get_safety_class method."""
        tag = self.ConcreteClass()

        safety_class = tag.get_safety_class()

        self.assertEqual(safety_class, 'Standard')

    def test_get_tag_scope(self):
        """Test get_tag_scope method."""
        tag = self.ConcreteClass()

        scope = tag.get_tag_scope()

        self.assertEqual(scope, LogicTagScope.CONTROLLER)

    def test_is_constant(self):
        """Test is_constant method."""
        tag = self.ConcreteClass()

        self.assertFalse(tag.is_constant())

    def test_set_dimensions_with_string(self):
        """Test set_dimensions with string value."""
        tag = self.ConcreteClass()

        tag.set_dimensions('[5,10]')

        self.assertEqual(tag._dimensions, '[5,10]')

    def test_set_dimensions_with_int(self):
        """Test set_dimensions with integer value."""
        tag = self.ConcreteClass()

        tag.set_dimensions(10)

        self.assertEqual(tag._dimensions, '10')

    def test_set_external_access(self):
        """Test set_external_access method."""
        tag = self.ConcreteClass()

        tag.set_external_access('None')

        self.assertEqual(tag._external_access, 'None')

    def test_set_opcua_access(self):
        """Test set_opcua_access method."""
        tag = self.ConcreteClass()

        tag.set_opcua_access('0')

        self.assertEqual(tag._opcua_access, '0')

    def test_set_safety_class(self):
        """Test set_safety_class method."""
        tag = self.ConcreteClass()

        tag.set_safety_class('Safety')

        self.assertEqual(tag._safety_class, 'Safety')

    def test_set_is_constant(self):
        """Test set_is_constant method."""
        tag = self.ConcreteClass()

        tag.set_is_constant(True)

        self.assertTrue(tag._is_constant)

    def test_set_datatype(self):
        """Test set_datatype method."""
        tag = self.ConcreteClass()
        mock_datatype = Mock()

        tag.set_datatype(mock_datatype)

        self.assertEqual(tag._datatype, mock_datatype)

    def test_get_datatype_with_datatype_set(self):
        """Test get_datatype when datatype is set."""
        tag = self.ConcreteClass()
        mock_datatype = Mock()
        tag._datatype = mock_datatype

        datatype = tag.get_datatype()

        self.assertEqual(datatype, mock_datatype)

    def test_get_alias_for_name_with_alias(self):
        """Test get_alias_for_name when aliased tag is set."""
        tag = self.ConcreteClass()
        aliased_tag = Mock()
        aliased_tag.name = 'AliasedTagName'
        tag._aliased_tag = aliased_tag

        name = tag.get_alias_for_name()

        self.assertEqual(name, 'AliasedTagName')

    def test_get_alias_for_tag_with_alias(self):
        """Test get_alias_for_tag when aliased tag is set."""
        tag = self.ConcreteClass()
        aliased_tag = Mock()
        tag._aliased_tag = aliased_tag

        result = tag.get_alias_for_tag()

        self.assertEqual(result, aliased_tag)

    def test_get_base_tag_with_base(self):
        """Test get_base_tag when base tag is set."""
        tag = self.ConcreteClass()
        base_tag = Mock()
        tag._base_tag = base_tag

        result = tag.get_base_tag()

        self.assertEqual(result, base_tag)


class TestTagNotImplemented(unittest.TestCase):
    """Test NotImplementedError cases for Tag."""

    def test_get_dimensions_not_implemented(self):
        """Test get_dimensions raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_dimensions()

    def test_get_endpoint_operands_not_implemented(self):
        """Test get_endpoint_operands raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_endpoint_operands()

    def test_get_external_access_not_implemented(self):
        """Test get_external_access raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_external_access()

    def test_get_opcua_access_not_implemented(self):
        """Test get_opcua_access raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_opcua_access()

    def test_get_safety_class_not_implemented(self):
        """Test get_safety_class raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_safety_class()

    def test_get_tag_scope_not_implemented(self):
        """Test get_tag_scope raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_tag_scope()

    def test_is_constant_not_implemented(self):
        """Test is_constant raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.is_constant()

    def test_set_datatype_not_implemented(self):
        """Test set_datatype raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.set_datatype(Mock())

    def test_set_dimensions_not_implemented(self):
        """Test set_dimensions raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.set_dimensions(10)

    def test_set_external_access_not_implemented(self):
        """Test set_external_access raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.set_external_access('None')

    def test_set_safety_class_not_implemented(self):
        """Test set_safety_class raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.set_safety_class('Standard')

    def test_set_opcua_access_not_implemented(self):
        """Test set_opcua_access raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.set_opcua_access('1')

    def test_set_is_constant_not_implemented(self):
        """Test set_is_constant raises NotImplementedError."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.set_is_constant(True)

    def test_get_alias_for_tag_not_implemented_when_no_alias(self):
        """Test get_alias_for_tag raises NotImplementedError when no alias."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_alias_for_tag()

    def test_get_base_tag_not_implemented_when_no_base(self):
        """Test get_base_tag raises NotImplementedError when no base."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_base_tag()

    def test_get_datatype_not_implemented_when_no_datatype(self):
        """Test get_datatype raises NotImplementedError when no datatype."""
        tag = Tag()

        with self.assertRaises(NotImplementedError):
            tag.get_datatype()


class TestTagInheritance(unittest.TestCase):
    """Test Tag inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test Tag inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        tag = Tag()

        self.assertIsInstance(tag, PlcObject)

    def test_implements_itag(self):
        """Test Tag implements ITag."""
        from controlrox.interfaces import ITag

        tag = Tag()

        self.assertIsInstance(tag, ITag)

    def test_has_name_property(self):
        """Test Tag has name property."""
        tag = Tag(name='TestTag')

        self.assertEqual(tag.name, 'TestTag')

    def test_has_description_property(self):
        """Test Tag has description property."""
        tag = Tag(description='Test Description')

        self.assertEqual(tag.description, 'Test Description')

    def test_initializes_with_none_values(self):
        """Test Tag initializes cached values as None."""
        tag = Tag()

        self.assertIsNone(tag._aliased_tag)
        self.assertIsNone(tag._base_tag)
        self.assertIsNone(tag._datatype)


class TestTagContainerIntegration(unittest.TestCase):
    """Test Tag with container integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IHasTags, IController

        self.mock_container = Mock(spec=IHasTags)
        self.mock_container.name = 'TestContainer'

        self.mock_controller = Mock(spec=IController)
        self.mock_controller.name = 'TestController'

        class TestableTag(Tag):
            def get_dimensions(self):
                return '0'

            def get_endpoint_operands(self):
                return ['']

            def get_external_access(self):
                return 'Read/Write'

            def get_opcua_access(self):
                return '1'

            def get_safety_class(self):
                return 'Standard'

            def get_tag_scope(self):
                return LogicTagScope.CONTROLLER

            def is_constant(self):
                return False

            def set_datatype(self, datatype):
                self._datatype = datatype

            def set_dimensions(self, value):
                pass

            def set_external_access(self, value):
                pass

            def set_opcua_access(self, value):
                pass

            def set_safety_class(self, value):
                pass

            def set_is_constant(self, value):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableTag = TestableTag

    def test_tag_with_container(self):
        """Test tag initialized with container."""
        tag = self.TestableTag(container=self.mock_container)

        self.assertEqual(tag.container, self.mock_container)

    def test_tag_get_container(self):
        """Test getting container from tag."""
        tag = self.TestableTag(container=self.mock_container)

        container = tag.get_container()

        self.assertEqual(container, self.mock_container)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_tag_container_defaults_to_controller(self, mock_get_controller):
        """Test container defaults to controller when not provided."""
        mock_get_controller.return_value = self.mock_controller
        tag = self.TestableTag()

        self.assertEqual(tag.container, self.mock_controller)


class TestTagAliasAndBaseTag(unittest.TestCase):
    """Test Tag alias and base tag functionality."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import ITag

        self.mock_alias_tag = Mock(spec=ITag)
        self.mock_alias_tag.name = 'AliasTag'

        self.mock_base_tag = Mock(spec=ITag)
        self.mock_base_tag.name = 'BaseTag'

        class TestableTag(Tag):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.compiled = False

            def get_dimensions(self):
                return '0'

            def get_endpoint_operands(self):
                return ['']

            def get_external_access(self):
                return 'Read/Write'

            def get_opcua_access(self):
                return '1'

            def get_safety_class(self):
                return 'Standard'

            def get_tag_scope(self):
                return LogicTagScope.CONTROLLER

            def is_constant(self):
                return False

            def set_datatype(self, datatype):
                self._datatype = datatype

            def set_dimensions(self, value):
                pass

            def set_external_access(self, value):
                pass

            def set_opcua_access(self, value):
                pass

            def set_safety_class(self, value):
                pass

            def set_is_constant(self, value):
                pass

            def compile(self):
                self.compiled = True
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableTag = TestableTag

    def test_get_alias_for_tag_returns_self_when_no_alias(self):
        """Test get_alias_for_tag returns self when no alias set."""
        tag = self.TestableTag()

        result = tag.get_alias_for_tag()

        self.assertEqual(result, tag)

    def test_get_alias_for_tag_with_alias_set(self):
        """Test get_alias_for_tag returns aliased tag when set."""
        tag = self.TestableTag()
        tag._aliased_tag = self.mock_alias_tag

        result = tag.get_alias_for_tag()

        self.assertEqual(result, self.mock_alias_tag)

    def test_get_alias_for_tag_triggers_compile(self):
        """Test get_alias_for_tag triggers compile when alias not set."""
        tag = self.TestableTag()

        tag.get_alias_for_tag()

        self.assertTrue(tag.compiled)

    def test_get_base_tag_returns_self_when_no_base(self):
        """Test get_base_tag returns self when no base set."""
        tag = self.TestableTag()

        result = tag.get_base_tag()

        self.assertEqual(result, tag)

    def test_get_base_tag_with_base_set(self):
        """Test get_base_tag returns base tag when set."""
        tag = self.TestableTag()
        tag._base_tag = self.mock_base_tag

        result = tag.get_base_tag()

        self.assertEqual(result, self.mock_base_tag)

    def test_get_base_tag_triggers_compile(self):
        """Test get_base_tag triggers compile when base not set."""
        tag = self.TestableTag()

        tag.get_base_tag()

        self.assertTrue(tag.compiled)


class TestTagDatatypeIntegration(unittest.TestCase):
    """Test Tag datatype integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IDatatype

        self.mock_datatype = Mock(spec=IDatatype)
        self.mock_datatype.name = 'DINT'

        class TestableTag(Tag):
            def get_dimensions(self):
                return '0'

            def get_endpoint_operands(self):
                if self._datatype:
                    return self._datatype.endpoint_operands
                return ['']

            def get_external_access(self):
                return 'Read/Write'

            def get_opcua_access(self):
                return '1'

            def get_safety_class(self):
                return 'Standard'

            def get_tag_scope(self):
                return LogicTagScope.CONTROLLER

            def is_constant(self):
                return False

            def set_datatype(self, datatype):
                if datatype is not None and not isinstance(datatype, IDatatype):
                    raise TypeError("datatype must be an IDatatype")
                self._datatype = datatype

            def set_dimensions(self, value):
                pass

            def set_external_access(self, value):
                pass

            def set_opcua_access(self, value):
                pass

            def set_safety_class(self, value):
                pass

            def set_is_constant(self, value):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableTag = TestableTag

    def test_set_and_get_datatype(self):
        """Test setting and getting datatype."""
        tag = self.TestableTag()

        tag.set_datatype(self.mock_datatype)

        self.assertEqual(tag.get_datatype(), self.mock_datatype)

    def test_get_datatype_raises_when_not_set(self):
        """Test get_datatype raises NotImplementedError when not set."""
        tag = self.TestableTag()

        with self.assertRaises(NotImplementedError):
            tag.get_datatype()

    def test_endpoint_operands_from_datatype(self):
        """Test endpoint operands can be derived from datatype."""
        self.mock_datatype.endpoint_operands = ['.PRE', '.ACC', '.DN']
        tag = self.TestableTag()
        tag.set_datatype(self.mock_datatype)

        operands = tag.get_endpoint_operands()

        self.assertEqual(operands, ['.PRE', '.ACC', '.DN'])


class TestTagMetaDataIntegration(unittest.TestCase):
    """Test Tag metadata integration."""

    def test_tag_metadata_as_dict(self):
        """Test tag metadata stored as dict."""
        meta_data = {'@Name': 'MyTag', '@TagType': 'Base', '@DataType': 'DINT'}
        tag = Tag(meta_data=meta_data)

        self.assertEqual(tag.meta_data, meta_data)
        self.assertIsInstance(tag.meta_data, dict)

    def test_tag_name_from_metadata(self):
        """Test tag name extracted from metadata."""
        meta_data = {'@Name': 'TagFromMeta'}
        tag = Tag(meta_data=meta_data)

        self.assertEqual(tag.name, 'TagFromMeta')

    def test_tag_description_from_metadata(self):
        """Test tag description extracted from metadata."""
        meta_data = {'@Name': 'MyTag', '@Description': 'Test Description'}
        tag = Tag(meta_data=meta_data)

        self.assertEqual(tag.description, 'Test Description')

    def test_tag_explicit_name_overrides_metadata(self):
        """Test explicit name parameter overrides metadata."""
        meta_data = {'@Name': 'MetaName'}
        tag = Tag(meta_data=meta_data, name='ExplicitName')

        self.assertEqual(tag.name, 'ExplicitName')


class TestTagScopeAndSafety(unittest.TestCase):
    """Test tag scope and safety functionality."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableTag(Tag):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._tag_scope = LogicTagScope.CONTROLLER
                self._safety_class = 'Standard'

            def get_dimensions(self):
                return '0'

            def get_endpoint_operands(self):
                return ['']

            def get_external_access(self):
                return 'Read/Write'

            def get_opcua_access(self):
                return '1'

            def get_safety_class(self):
                return self._safety_class

            def get_tag_scope(self):
                return self._tag_scope

            def is_constant(self):
                return False

            def set_datatype(self, datatype):
                self._datatype = datatype

            def set_dimensions(self, value):
                pass

            def set_external_access(self, value):
                pass

            def set_opcua_access(self, value):
                pass

            def set_safety_class(self, value):
                self._safety_class = value

            def set_is_constant(self, value):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableTag = TestableTag

    def test_tag_scope_controller(self):
        """Test tag with controller scope."""
        tag = self.TestableTag()

        self.assertEqual(tag.get_tag_scope(), LogicTagScope.CONTROLLER)

    def test_tag_scope_program(self):
        """Test tag with program scope."""
        tag = self.TestableTag()
        tag._tag_scope = LogicTagScope.PROGRAM

        self.assertEqual(tag.get_tag_scope(), LogicTagScope.PROGRAM)

    def test_safety_class_standard(self):
        """Test tag with standard safety class."""
        tag = self.TestableTag()

        self.assertEqual(tag.get_safety_class(), 'Standard')

    def test_safety_class_safety(self):
        """Test tag with safety class."""
        tag = self.TestableTag()
        tag.set_safety_class('Safety')

        self.assertEqual(tag.get_safety_class(), 'Safety')


class TestTagDimensionsAndAccess(unittest.TestCase):
    """Test tag dimensions and access settings."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableTag(Tag):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._dimensions = '0'
                self._external_access = 'Read/Write'
                self._opcua_access = '1'
                self._is_constant = False

            def get_dimensions(self):
                return self._dimensions

            def get_endpoint_operands(self):
                return ['']

            def get_external_access(self):
                return self._external_access

            def get_opcua_access(self):
                return self._opcua_access

            def get_safety_class(self):
                return 'Standard'

            def get_tag_scope(self):
                return LogicTagScope.CONTROLLER

            def is_constant(self):
                return self._is_constant

            def set_datatype(self, datatype):
                self._datatype = datatype

            def set_dimensions(self, value):
                self._dimensions = str(value)

            def set_external_access(self, value):
                self._external_access = value

            def set_opcua_access(self, value):
                self._opcua_access = value

            def set_safety_class(self, value):
                pass

            def set_is_constant(self, value):
                self._is_constant = value

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableTag = TestableTag

    def test_dimensions_single_value(self):
        """Test tag with single dimension."""
        tag = self.TestableTag()
        tag.set_dimensions('10')

        self.assertEqual(tag.get_dimensions(), '10')

    def test_dimensions_multi_dimensional(self):
        """Test tag with multiple dimensions."""
        tag = self.TestableTag()
        tag.set_dimensions('[10,5,3]')

        self.assertEqual(tag.get_dimensions(), '[10,5,3]')

    def test_external_access_read_write(self):
        """Test tag with read/write external access."""
        tag = self.TestableTag()

        self.assertEqual(tag.get_external_access(), 'Read/Write')

    def test_external_access_read_only(self):
        """Test tag with read-only external access."""
        tag = self.TestableTag()
        tag.set_external_access('Read Only')

        self.assertEqual(tag.get_external_access(), 'Read Only')

    def test_external_access_none(self):
        """Test tag with no external access."""
        tag = self.TestableTag()
        tag.set_external_access('None')

        self.assertEqual(tag.get_external_access(), 'None')

    def test_opcua_access_enabled(self):
        """Test tag with OPC UA access enabled."""
        tag = self.TestableTag()

        self.assertEqual(tag.get_opcua_access(), '1')

    def test_opcua_access_disabled(self):
        """Test tag with OPC UA access disabled."""
        tag = self.TestableTag()
        tag.set_opcua_access('0')

        self.assertEqual(tag.get_opcua_access(), '0')

    def test_is_constant_false(self):
        """Test non-constant tag."""
        tag = self.TestableTag()

        self.assertFalse(tag.is_constant())

    def test_is_constant_true(self):
        """Test constant tag."""
        tag = self.TestableTag()
        tag.set_is_constant(True)

        self.assertTrue(tag.is_constant())


class TestTagStringRepresentation(unittest.TestCase):
    """Test tag string representation."""

    def test_tag_str_returns_name(self):
        """Test __str__ returns tag name."""
        tag = Tag(name='MyTagName')

        self.assertEqual(str(tag), 'MyTagName')

    def test_tag_repr_returns_name(self):
        """Test __repr__ returns tag name."""
        tag = Tag(name='MyTagName')

        self.assertEqual(repr(tag), 'MyTagName')


class TestTagSpecialCases(unittest.TestCase):
    """Test special cases and edge conditions."""

    def test_tag_with_empty_metadata(self):
        """Test tag with empty metadata dict."""
        tag = Tag(meta_data={})

        self.assertEqual(tag.meta_data, {})

    def test_tag_multiple_property_access(self):
        """Test accessing tag properties multiple times."""
        tag = Tag(name='TestTag', description='Test Desc')

        name1 = tag.name
        name2 = tag.name
        desc1 = tag.description
        desc2 = tag.description

        self.assertEqual(name1, name2)
        self.assertEqual(desc1, desc2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
