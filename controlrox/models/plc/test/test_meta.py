"""Unit tests for controlrox.models.plc.meta module."""
import unittest
from typing import Self
from unittest.mock import Mock, patch

from controlrox.models.plc.meta import PlcObject
from controlrox.interfaces import IController


class TestPlcObject(unittest.TestCase):
    """Test cases for PlcObject class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing since PlcObject has abstract methods
        class ConcreteTestPlcObject(PlcObject):
            """Concrete implementation for testing."""

            def compile(self) -> Self:
                """Implement compile method."""
                self.compiled = True
                return self

            def invalidate(self) -> None:
                """Implement invalidate method."""
                self.invalidated = True

            @property
            def process_name(self) -> str:
                """Implement process_name property."""
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_init_with_defaults(self):
        """Test PlcObject initialization with default values."""
        obj = self.ConcreteTestPlcObject()

        self.assertEqual(obj.name, '')
        self.assertEqual(obj.description, '')
        self.assertIsInstance(obj.meta_data, dict)

    def test_init_with_name(self):
        """Test PlcObject initialization with name parameter."""
        obj = self.ConcreteTestPlcObject(name='TestName')

        self.assertEqual(obj.name, 'TestName')
        self.assertEqual(obj.description, '')

    def test_init_with_description(self):
        """Test PlcObject initialization with description parameter."""
        obj = self.ConcreteTestPlcObject(description='Test Description')

        self.assertEqual(obj.description, 'Test Description')

    def test_init_with_name_and_description(self):
        """Test PlcObject initialization with both name and description."""
        obj = self.ConcreteTestPlcObject(
            name='TestName',
            description='Test Description'
        )

        self.assertEqual(obj.name, 'TestName')
        self.assertEqual(obj.description, 'Test Description')

    def test_init_with_dict_meta_data(self):
        """Test PlcObject initialization with dictionary metadata."""
        meta_data = {
            '@Name': 'MetaName',
            '@Description': 'Meta Description',
            'SomeKey': 'SomeValue'
        }
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'MetaName')
        self.assertEqual(obj.description, 'Meta Description')
        self.assertEqual(obj.meta_data, meta_data)

    def test_init_with_dict_meta_data_name_key(self):
        """Test PlcObject initialization with 'Name' key (without @)."""
        meta_data = {
            'Name': 'NameWithoutAt',
            'Description': 'DescWithoutAt'
        }
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'NameWithoutAt')
        self.assertEqual(obj.description, 'DescWithoutAt')

    def test_init_name_parameter_overrides_metadata(self):
        """Test that name parameter overrides metadata name."""
        meta_data = {'@Name': 'MetaName'}
        obj = self.ConcreteTestPlcObject(meta_data=meta_data, name='OverrideName')

        self.assertEqual(obj.name, 'OverrideName')

    def test_init_description_parameter_overrides_metadata(self):
        """Test that description parameter overrides metadata description."""
        meta_data = {'@Description': 'MetaDesc'}
        obj = self.ConcreteTestPlcObject(
            meta_data=meta_data,
            description='OverrideDesc'
        )

        self.assertEqual(obj.description, 'OverrideDesc')

    def test_init_with_string_meta_data(self):
        """Test PlcObject initialization with string metadata."""
        obj = self.ConcreteTestPlcObject(meta_data="String metadata")

        self.assertEqual(obj.meta_data, "String metadata")
        self.assertEqual(obj.name, '')
        self.assertEqual(obj.description, '')

    def test_init_with_none_meta_data(self):
        """Test PlcObject initialization with None metadata."""
        obj = self.ConcreteTestPlcObject(meta_data=None)

        self.assertIsInstance(obj.meta_data, dict)

    def test_str_with_name(self):
        """Test __str__ method returns name when available."""
        obj = self.ConcreteTestPlcObject(name='TestName')

        self.assertEqual(str(obj), 'TestName')

    def test_str_without_name(self):
        """Test __str__ method returns metadata when name is None."""
        obj = self.ConcreteTestPlcObject(name='')
        obj._name = None

        result = str(obj)
        self.assertIsNotNone(result)

    def test_repr(self):
        """Test __repr__ method."""
        obj = self.ConcreteTestPlcObject(name='TestName')

        self.assertEqual(repr(obj), 'TestName')

    def test_name_property_getter(self):
        """Test name property getter."""
        obj = self.ConcreteTestPlcObject(name='PropertyTest')

        self.assertEqual(obj.name, 'PropertyTest')

    def test_description_property_getter(self):
        """Test description property getter."""
        obj = self.ConcreteTestPlcObject(description='Test Description')

        self.assertEqual(obj.description, 'Test Description')

    def test_process_name_property(self):
        """Test process_name property (implemented in concrete class)."""
        obj = self.ConcreteTestPlcObject()

        self.assertEqual(obj.process_name, 'TestProcess')

    def test_set_name_with_valid_string(self):
        """Test set_name with valid string."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('NewName')
        self.assertEqual(obj.name, 'NewName')

    def test_set_name_with_underscores(self):
        """Test set_name with underscores (valid)."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('Valid_Name_123')
        self.assertEqual(obj.name, 'Valid_Name_123')

    def test_set_name_with_brackets(self):
        """Test set_name with brackets (valid for array notation)."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('Array[0]')
        self.assertEqual(obj.name, 'Array[0]')

    def test_set_name_with_invalid_string_spaces(self):
        """Test set_name with invalid string containing spaces."""
        obj = self.ConcreteTestPlcObject()

        with self.assertRaises(obj.InvalidNamingException) as context:
            obj.set_name('Invalid Name With Spaces')

        self.assertIn('valid', str(context.exception).lower())

    def test_set_name_with_invalid_string_special_chars(self):
        """Test set_name with invalid string containing special characters."""
        obj = self.ConcreteTestPlcObject()

        with self.assertRaises(obj.InvalidNamingException) as context:
            obj.set_name('Invalid@Name!')

        self.assertIn('valid', str(context.exception).lower())

    def test_set_description(self):
        """Test set_description method."""
        obj = self.ConcreteTestPlcObject()

        obj.set_description('New Description')
        self.assertEqual(obj.description, 'New Description')

    def test_set_description_with_empty_string(self):
        """Test set_description with empty string."""
        obj = self.ConcreteTestPlcObject(description='Old Description')

        obj.set_description('')
        self.assertEqual(obj.description, '')

    def test_compile_method(self):
        """Test compile method implementation."""
        obj = self.ConcreteTestPlcObject()

        result = obj.compile()

        self.assertTrue(obj.compiled)
        self.assertEqual(result, obj)  # Should return self for chaining

    def test_compile_method_chaining(self):
        """Test compile method returns self for method chaining."""
        obj = self.ConcreteTestPlcObject()

        result = obj.compile()

        self.assertIs(result, obj)

    def test_invalidate_method(self):
        """Test invalidate method implementation."""
        obj = self.ConcreteTestPlcObject()

        obj.invalidate()

        self.assertTrue(obj.invalidated)

    def test_inheritance_from_pyrox_object(self):
        """Test that PlcObject inherits from PyroxObject."""
        obj = self.ConcreteTestPlcObject()

        # Should have PyroxObject attributes
        self.assertTrue(hasattr(obj, 'id'))

    def test_inheritance_from_enforces_naming(self):
        """Test that PlcObject inherits from EnforcesNaming."""
        obj = self.ConcreteTestPlcObject()

        # Should have EnforcesNaming methods
        self.assertTrue(hasattr(obj, 'is_valid_string'))
        self.assertTrue(hasattr(obj, 'InvalidNamingException'))

    def test_inheritance_from_supports_metadata(self):
        """Test that PlcObject inherits from SupportsMetaData."""
        obj = self.ConcreteTestPlcObject()

        # Should have SupportsMetaData attributes
        self.assertTrue(hasattr(obj, 'meta_data'))

    def test_enforces_naming_validation(self):
        """Test that EnforcesNaming validation works."""
        obj = self.ConcreteTestPlcObject()

        # Test validation methods
        self.assertTrue(obj.is_valid_string('ValidName'))
        self.assertFalse(obj.is_valid_string('Invalid Name'))

    def test_metadata_attribute_exists(self):
        """Test that meta_data attribute exists and is accessible."""
        obj = self.ConcreteTestPlcObject(meta_data={'key': 'value'})

        self.assertEqual(obj.meta_data, {'key': 'value'})

    def test_multiple_instances_independent(self):
        """Test that multiple instances are independent."""
        obj1 = self.ConcreteTestPlcObject(name='Object1')
        obj2 = self.ConcreteTestPlcObject(name='Object2')

        self.assertEqual(obj1.name, 'Object1')
        self.assertEqual(obj2.name, 'Object2')

        obj1.set_name('Modified1')
        self.assertEqual(obj1.name, 'Modified1')
        self.assertEqual(obj2.name, 'Object2')  # Should not be affected


class TestPlcObjectEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for PlcObject."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_init_with_empty_dict_metadata(self):
        """Test initialization with empty dictionary metadata."""
        obj = self.ConcreteTestPlcObject(meta_data={})

        self.assertEqual(obj.name, '')
        self.assertEqual(obj.description, '')

    def test_init_with_partial_metadata(self):
        """Test initialization with partial metadata."""
        obj1 = self.ConcreteTestPlcObject(meta_data={'@Name': 'OnlyName'})
        self.assertEqual(obj1.name, 'OnlyName')
        self.assertEqual(obj1.description, '')

        obj2 = self.ConcreteTestPlcObject(meta_data={'@Description': 'OnlyDesc'})
        self.assertEqual(obj2.name, '')
        self.assertEqual(obj2.description, 'OnlyDesc')

    def test_set_name_multiple_times(self):
        """Test setting name multiple times."""
        obj = self.ConcreteTestPlcObject(name='Initial')

        obj.set_name('Second')
        self.assertEqual(obj.name, 'Second')

        obj.set_name('Third')
        self.assertEqual(obj.name, 'Third')

    def test_set_description_multiple_times(self):
        """Test setting description multiple times."""
        obj = self.ConcreteTestPlcObject(description='Initial')

        obj.set_description('Second')
        self.assertEqual(obj.description, 'Second')

        obj.set_description('Third')
        self.assertEqual(obj.description, 'Third')

    def test_compile_multiple_times(self):
        """Test calling compile multiple times."""
        obj = self.ConcreteTestPlcObject()

        result1 = obj.compile()
        result2 = obj.compile()

        self.assertIs(result1, obj)
        self.assertIs(result2, obj)

    def test_invalidate_multiple_times(self):
        """Test calling invalidate multiple times."""
        obj = self.ConcreteTestPlcObject()

        # Should not raise exception
        obj.invalidate()
        obj.invalidate()

    def test_unicode_characters_in_description(self):
        """Test description with unicode characters."""
        obj = self.ConcreteTestPlcObject()

        obj.set_description('Test with émojis 🚀 and spëcial çhars')
        self.assertEqual(obj.description, 'Test with émojis 🚀 and spëcial çhars')

    def test_long_name(self):
        """Test with a very long valid name."""
        long_name = 'A' * 200  # Long but valid name
        obj = self.ConcreteTestPlcObject()

        obj.set_name(long_name)
        self.assertEqual(obj.name, long_name)

    def test_long_description(self):
        """Test with a very long description."""
        long_description = 'A' * 1000
        obj = self.ConcreteTestPlcObject()

        obj.set_description(long_description)
        self.assertEqual(obj.description, long_description)


class TestPlcObjectInterfaceCompliance(unittest.TestCase):
    """Test that PlcObject properly implements IPlcObject interface."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_has_compile_method(self):
        """Test that PlcObject has compile method."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'compile'))
        self.assertTrue(callable(obj.compile))

    def test_has_invalidate_method(self):
        """Test that PlcObject has invalidate method."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'invalidate'))
        self.assertTrue(callable(obj.invalidate))

    def test_has_set_name_method(self):
        """Test that PlcObject has set_name method."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'set_name'))
        self.assertTrue(callable(obj.set_name))

    def test_has_set_description_method(self):
        """Test that PlcObject has set_description method."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'set_description'))
        self.assertTrue(callable(obj.set_description))

    def test_has_name_property(self):
        """Test that PlcObject has name property."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'name'))

    def test_has_description_property(self):
        """Test that PlcObject has description property."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'description'))

    def test_has_process_name_property(self):
        """Test that PlcObject has process_name property."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'process_name'))

    def test_compile_returns_self_type(self):
        """Test that compile returns Self type."""
        obj = self.ConcreteTestPlcObject()

        result = obj.compile()

        self.assertIsInstance(result, self.ConcreteTestPlcObject)
        self.assertIs(result, obj)


class TestPlcObjectAbstractMethods(unittest.TestCase):
    """Test that abstract methods must be implemented."""

    def test_compile_raises_error_without_implimentation(self):
        """Test that PlcObject cannot be instantiated without compile implementation."""
        class IncompleteObject1(PlcObject):
            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "Test"

        with self.assertRaises(NotImplementedError):
            IncompleteObject1().compile()

    def test_invalidate_raises_error_without_implimentation(self):
        """Test that PlcObject cannot be instantiated without invalidate implementation."""
        class IncompleteObject2(PlcObject):
            def compile(self) -> Self:
                return self

            @property
            def process_name(self) -> str:
                return "Test"

        with self.assertRaises(NotImplementedError):
            IncompleteObject2().invalidate()


class TestPlcObjectWithController(unittest.TestCase):
    """Test PlcObject with controller functionality."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject
        self.mock_controller = Mock(spec=IController)
        self.mock_controller.name = "TestController"

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_get_controller(self, mock_get_controller):
        """Test get_controller method."""
        obj = self.ConcreteTestPlcObject()
        mock_get_controller.return_value = self.mock_controller
        self.assertEqual(obj.get_controller(), self.mock_controller)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_set_controller(self, mock_get_controller):
        """Test set_controller method."""
        mock_get_controller.return_value = None
        obj = self.ConcreteTestPlcObject()
        self.assertIsNone(obj.controller)

        mock_get_controller.return_value = self.mock_controller
        obj.set_controller(self.mock_controller)
        self.assertEqual(obj.controller, self.mock_controller)


class TestPlcObjectMetaDataVariations(unittest.TestCase):
    """Test PlcObject with various metadata formats."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_metadata_with_lowercase_name(self):
        """Test metadata with lowercase 'name' key."""
        meta_data = {'name': 'LowercaseName'}
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'LowercaseName')

    def test_metadata_with_at_lowercase_name(self):
        """Test metadata with '@name' key."""
        meta_data = {'@name': 'AtLowercaseName'}
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'AtLowercaseName')

    def test_metadata_with_lowercase_description(self):
        """Test metadata with lowercase 'description' key."""
        meta_data = {'description': 'Lowercase description'}
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.description, 'Lowercase description')

    def test_metadata_with_at_lowercase_description(self):
        """Test metadata with '@description' key."""
        meta_data = {'@description': 'At lowercase description'}
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.description, 'At lowercase description')

    def test_metadata_with_complex_structure(self):
        """Test metadata with complex nested structure."""
        meta_data = {
            '@Name': 'ComplexObject',
            '@Description': 'Complex description',
            'Properties': {
                'SubProperty': 'Value',
                'NestedDict': {'Key': 'NestedValue'}
            },
            'Array': [1, 2, 3]
        }
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'ComplexObject')
        self.assertEqual(obj.description, 'Complex description')
        self.assertEqual(obj.meta_data, meta_data)

    def test_set_meta_data(self):
        """Test set_meta_data method."""
        obj = self.ConcreteTestPlcObject()
        new_meta = {'@Name': 'NewName', 'SomeKey': 'SomeValue'}

        obj.set_meta_data(new_meta)

        self.assertEqual(obj.meta_data, new_meta)

    def test_get_meta_data(self):
        """Test get_meta_data method."""
        meta_data = {'@Name': 'TestName'}
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        result = obj.get_meta_data()

        self.assertEqual(result, meta_data)

    def test_meta_data_property_setter(self):
        """Test meta_data property setter."""
        obj = self.ConcreteTestPlcObject()
        new_meta = {'@Name': 'PropertySetter'}

        obj.meta_data = new_meta

        self.assertEqual(obj.meta_data, new_meta)


class TestPlcObjectNameValidation(unittest.TestCase):
    """Test PlcObject name validation in detail."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_valid_name_alphanumeric(self):
        """Test valid alphanumeric name."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('ValidName123')
        self.assertEqual(obj.name, 'ValidName123')

    def test_valid_name_with_underscores(self):
        """Test valid name with underscores."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('Valid_Name_123')
        self.assertEqual(obj.name, 'Valid_Name_123')

    def test_valid_name_starting_with_underscore(self):
        """Test valid name starting with underscore."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('_PrivateName')
        self.assertEqual(obj.name, '_PrivateName')

    def test_valid_name_with_numbers(self):
        """Test valid name with numbers."""
        obj = self.ConcreteTestPlcObject()

        obj.set_name('Name123')
        self.assertEqual(obj.name, 'Name123')

    def test_invalid_name_with_space(self):
        """Test invalid name with space."""
        obj = self.ConcreteTestPlcObject()

        with self.assertRaises(obj.InvalidNamingException):
            obj.set_name('Invalid Name')

    def test_invalid_name_with_special_chars(self):
        """Test invalid name with special characters."""
        obj = self.ConcreteTestPlcObject()

        invalid_names = ['Name@Test', 'Name!', 'Name#', 'Name$', 'Name%']
        for invalid_name in invalid_names:
            with self.assertRaises(obj.InvalidNamingException):
                obj.set_name(invalid_name)

    def test_invalid_name_with_hyphen(self):
        """Test invalid name with hyphen."""
        obj = self.ConcreteTestPlcObject()

        with self.assertRaises(obj.InvalidNamingException):
            obj.set_name('Invalid-Name')

    def test_is_valid_string_method(self):
        """Test is_valid_string method directly."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(obj.is_valid_string('ValidName'))
        self.assertTrue(obj.is_valid_string('Valid_Name'))
        self.assertTrue(obj.is_valid_string('_Name'))
        self.assertTrue(obj.is_valid_string('Name123'))
        self.assertTrue(obj.is_valid_string('Array[0]'))

        self.assertFalse(obj.is_valid_string('Invalid Name'))
        self.assertFalse(obj.is_valid_string('Invalid@Name'))
        self.assertFalse(obj.is_valid_string('Invalid-Name'))


class TestPlcObjectInheritanceChain(unittest.TestCase):
    """Test PlcObject's inheritance and mixin integration."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_has_pyrox_object_id(self):
        """Test that object has id from PyroxObject."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'id'))
        self.assertIsNotNone(obj.id)

    def test_has_controller_methods(self):
        """Test that object has HasController methods."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'get_controller'))
        self.assertTrue(hasattr(obj, 'set_controller'))
        self.assertTrue(hasattr(obj, 'controller'))

    def test_has_metadata_methods(self):
        """Test that object has HasMetaData methods."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'get_meta_data'))
        self.assertTrue(hasattr(obj, 'set_meta_data'))
        self.assertTrue(hasattr(obj, 'meta_data'))

    def test_has_naming_methods(self):
        """Test that object has EnforcesNaming methods."""
        obj = self.ConcreteTestPlcObject()

        self.assertTrue(hasattr(obj, 'is_valid_string'))
        self.assertTrue(hasattr(obj, 'InvalidNamingException'))

    def test_multiple_inheritance_resolution(self):
        """Test that multiple inheritance is properly resolved."""
        obj = self.ConcreteTestPlcObject(
            meta_data={'@Name': 'Test'},
        )

        # Should have attributes from all parent classes
        self.assertIsNotNone(obj.id)  # From PyroxObject
        self.assertIsNotNone(obj.meta_data)  # From HasMetaData
        self.assertIsNotNone(obj.name)  # From EnforcesNaming
        self.assertTrue(callable(obj.compile))  # From PlcObject
        self.assertTrue(callable(obj.invalidate))  # From PlcObject


class TestPlcObjectMethodChaining(unittest.TestCase):
    """Test method chaining capabilities."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                self.compiled = True
                return self

            def invalidate(self) -> None:
                self.invalidated = True

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_compile_returns_self(self):
        """Test that compile returns self for chaining."""
        obj = self.ConcreteTestPlcObject()

        result = obj.compile()

        self.assertIs(result, obj)
        self.assertTrue(obj.compiled)

    def test_compile_chaining(self):
        """Test actual method chaining with compile."""
        obj = self.ConcreteTestPlcObject(name='ChainTest')

        # Compile should return self, allowing further method calls
        result = obj.compile()
        self.assertEqual(result.name, 'ChainTest')
        self.assertTrue(result.compiled)


class TestPlcObjectStateManagement(unittest.TestCase):
    """Test state management and lifecycle."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.compile_count = 0
                self.invalidate_count = 0

            def compile(self) -> Self:
                self.compile_count += 1
                return self

            def invalidate(self) -> None:
                self.invalidate_count += 1

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_compile_state_tracking(self):
        """Test that compile state can be tracked."""
        obj = self.ConcreteTestPlcObject()

        self.assertEqual(obj.compile_count, 0)
        obj.compile()
        self.assertEqual(obj.compile_count, 1)
        obj.compile()
        self.assertEqual(obj.compile_count, 2)

    def test_invalidate_state_tracking(self):
        """Test that invalidate state can be tracked."""
        obj = self.ConcreteTestPlcObject()

        self.assertEqual(obj.invalidate_count, 0)
        obj.invalidate()
        self.assertEqual(obj.invalidate_count, 1)
        obj.invalidate()
        self.assertEqual(obj.invalidate_count, 2)

    def test_state_independence_between_instances(self):
        """Test that state is independent between instances."""
        obj1 = self.ConcreteTestPlcObject()
        obj2 = self.ConcreteTestPlcObject()

        obj1.compile()
        obj1.compile()
        obj2.compile()

        self.assertEqual(obj1.compile_count, 2)
        self.assertEqual(obj2.compile_count, 1)


class TestPlcObjectSpecialCases(unittest.TestCase):
    """Test special cases and boundary conditions."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_empty_string_name(self):
        """Test with empty string name."""
        obj = self.ConcreteTestPlcObject(name='')

        self.assertEqual(obj.name, '')

    def test_empty_string_description(self):
        """Test with empty string description."""
        obj = self.ConcreteTestPlcObject(description='')

        self.assertEqual(obj.description, '')

    def test_none_converted_to_empty_string(self):
        """Test that None values are converted to empty strings."""
        obj = self.ConcreteTestPlcObject()

        self.assertEqual(obj.name, '')
        self.assertEqual(obj.description, '')

    def test_numeric_values_in_metadata(self):
        """Test metadata with numeric values."""
        meta_data = {
            '@Name': 'Test',
            'NumericValue': 123,
            'FloatValue': 45.67,
            'BoolValue': True
        }
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.meta_data, meta_data)

    def test_none_values_in_metadata(self):
        """Test metadata with None values."""
        meta_data = {
            '@Name': 'Test',
            'NullValue': None
        }
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.meta_data, meta_data)

    def test_list_values_in_metadata(self):
        """Test metadata with list values."""
        meta_data = {
            '@Name': 'Test',
            'ListValue': [1, 2, 3, 'four']
        }
        obj = self.ConcreteTestPlcObject(meta_data=meta_data)

        self.assertEqual(obj.meta_data, meta_data)

    def test_very_long_description(self):
        """Test with very long description."""
        long_desc = 'A' * 10000
        obj = self.ConcreteTestPlcObject()

        obj.set_description(long_desc)
        self.assertEqual(obj.description, long_desc)
        self.assertEqual(len(obj.description), 10000)


class TestPlcObjectCombinedFeatures(unittest.TestCase):
    """Test combinations of features working together."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteTestPlcObject(PlcObject):
            def compile(self) -> Self:
                return self

            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

        self.ConcreteTestPlcObject = ConcreteTestPlcObject

    def test_full_initialization(self):
        """Test initialization with all parameters."""
        meta_data = {'@Name': 'MetaName', 'Extra': 'Data'}

        obj = self.ConcreteTestPlcObject(
            meta_data=meta_data,
            name='ExplicitName',
            description='Test Description',
        )

        self.assertEqual(obj.name, 'ExplicitName')
        self.assertEqual(obj.description, 'Test Description')
        self.assertEqual(obj.meta_data, meta_data)

    def test_metadata_extraction_with_controller(self):
        """Test metadata extraction works with controller."""
        meta_data = {'@Name': 'MetaName', '@Description': 'Meta Desc'}

        obj = self.ConcreteTestPlcObject(
            meta_data=meta_data,
        )

        self.assertEqual(obj.name, 'MetaName')
        self.assertEqual(obj.description, 'Meta Desc')

    def test_modify_after_initialization(self):
        """Test modifying object after initialization."""
        obj = self.ConcreteTestPlcObject(name='Initial')

        obj.set_name('Modified')
        obj.set_description('New Description')
        obj.set_controller(Mock(spec=IController))
        obj.set_meta_data({'New': 'Data'})

        self.assertEqual(obj.name, 'Modified')
        self.assertEqual(obj.description, 'New Description')
        self.assertIsNotNone(obj.controller)
        self.assertEqual(obj.meta_data, {'New': 'Data'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
