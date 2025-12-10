"""Unit tests for controlrox.models.plc.module module."""
import unittest
from unittest.mock import Mock

from controlrox.models.plc.module import Module


class TestModule(unittest.TestCase):
    """Test cases for Module class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteModule(Module):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._catalog_number = '1756-L85E'
                self._ip_address = '192.168.1.1'
                self._is_inhibited = False
                self._major_version = '32'
                self._minor_version = '11'
                self._parent_module = None
                self._product_code = '123'
                self._product_type = '14'
                self._rpi = '20'
                self._vendor = '1'

            def get_catalog_number(self):
                return self._catalog_number

            def get_ip_address(self):
                return self._ip_address

            def get_is_inhibited(self):
                return self._is_inhibited

            def get_major_version_number(self):
                return self._major_version

            def get_minor_version_number(self):
                return self._minor_version

            def get_parent_module(self):
                if self._parent_module is None:
                    raise NotImplementedError()
                return self._parent_module

            def get_product_code(self):
                return self._product_code

            def get_product_type(self):
                return self._product_type

            def get_rpi(self):
                return self._rpi

            def get_vendor(self):
                return self._vendor

            def set_catalog_number(self, catalog_number):
                self._catalog_number = catalog_number

            def set_is_inhibited(self, inhibited):
                self._is_inhibited = inhibited

            def set_ip_address(self, ip_address):
                self._ip_address = ip_address

            def set_major_version_number(self, major_version_number):
                self._major_version = major_version_number

            def set_minor_version_number(self, minor_version_number):
                self._minor_version = minor_version_number

            def set_parent_module(self, parent_module):
                self._parent_module = parent_module

            def set_product_code(self, product_code):
                self._product_code = product_code

            def set_product_type(self, product_type):
                self._product_type = product_type

            def set_rpi(self, rpi):
                self._rpi = rpi

            def set_vendor(self, vendor):
                self._vendor = vendor

        self.ConcreteClass = ConcreteModule

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        module = self.ConcreteClass()

        self.assertIsNotNone(module)

    def test_init_with_metadata(self):
        """Test initialization with metadata dict."""
        meta_data = {'@Name': 'LocalModule', '@CatalogNumber': '1756-L85E'}
        module = self.ConcreteClass(meta_data=meta_data)

        self.assertEqual(module.meta_data, meta_data)

    def test_catalog_number_property(self):
        """Test catalog_number property."""
        module = self.ConcreteClass()

        self.assertEqual(module.catalog_number, '1756-L85E')

    def test_inhibited_property(self):
        """Test inhibited property."""
        module = self.ConcreteClass()

        self.assertFalse(module.inhibited)

    def test_ip_address_property(self):
        """Test ip_address property."""
        module = self.ConcreteClass()

        self.assertEqual(module.ip_address, '192.168.1.1')

    def test_vendor_property(self):
        """Test vendor property."""
        module = self.ConcreteClass()

        self.assertEqual(module.vendor, '1')

    def test_product_type_property(self):
        """Test product_type property."""
        module = self.ConcreteClass()

        self.assertEqual(module.product_type, '14')

    def test_product_code_property(self):
        """Test product_code property."""
        module = self.ConcreteClass()

        self.assertEqual(module.product_code, '123')

    def test_major_version_property(self):
        """Test major_version property."""
        module = self.ConcreteClass()

        self.assertEqual(module.major_version, '32')

    def test_minor_version_property(self):
        """Test minor_version property."""
        module = self.ConcreteClass()

        self.assertEqual(module.minor_version, '11')

    def test_rpi_property(self):
        """Test rpi property."""
        module = self.ConcreteClass()

        self.assertEqual(module.rpi, '20')

    def test_parent_module_property(self):
        """Test parent_module property."""
        module = self.ConcreteClass()
        mock_parent = Mock()
        module._parent_module = mock_parent

        self.assertEqual(module.parent_module, mock_parent)

    def test_set_catalog_number(self):
        """Test set_catalog_number method."""
        module = self.ConcreteClass()

        module.set_catalog_number('1756-L83E')

        self.assertEqual(module._catalog_number, '1756-L83E')

    def test_set_is_inhibited(self):
        """Test set_is_inhibited method."""
        module = self.ConcreteClass()

        module.set_is_inhibited(True)

        self.assertTrue(module._is_inhibited)

    def test_set_ip_address(self):
        """Test set_ip_address method."""
        module = self.ConcreteClass()

        module.set_ip_address('10.0.0.1')

        self.assertEqual(module._ip_address, '10.0.0.1')

    def test_set_major_version_number(self):
        """Test set_major_version_number method."""
        module = self.ConcreteClass()

        module.set_major_version_number('33')

        self.assertEqual(module._major_version, '33')

    def test_set_minor_version_number(self):
        """Test set_minor_version_number method."""
        module = self.ConcreteClass()

        module.set_minor_version_number('12')

        self.assertEqual(module._minor_version, '12')

    def test_set_parent_module(self):
        """Test set_parent_module method."""
        module = self.ConcreteClass()
        mock_parent = Mock()

        module.set_parent_module(mock_parent)

        self.assertEqual(module._parent_module, mock_parent)

    def test_set_product_code(self):
        """Test set_product_code method."""
        module = self.ConcreteClass()

        module.set_product_code('456')

        self.assertEqual(module._product_code, '456')

    def test_set_product_type(self):
        """Test set_product_type method."""
        module = self.ConcreteClass()

        module.set_product_type('20')

        self.assertEqual(module._product_type, '20')

    def test_set_rpi(self):
        """Test set_rpi method."""
        module = self.ConcreteClass()

        module.set_rpi('100')

        self.assertEqual(module._rpi, '100')

    def test_set_vendor(self):
        """Test set_vendor method."""
        module = self.ConcreteClass()

        module.set_vendor('2')

        self.assertEqual(module._vendor, '2')


class TestModuleNotImplemented(unittest.TestCase):
    """Test NotImplementedError cases for Module."""

    def test_get_catalog_number_not_implemented(self):
        """Test get_catalog_number raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError) as context:
            module.get_catalog_number()

        self.assertIn('should be overridden by subclasses', str(context.exception))

    def test_get_ip_address_not_implemented(self):
        """Test get_ip_address raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_ip_address()

    def test_get_is_inhibited_not_implemented(self):
        """Test get_is_inhibited raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_is_inhibited()

    def test_get_major_version_number_not_implemented(self):
        """Test get_major_version_number raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_major_version_number()

    def test_get_minor_version_number_not_implemented(self):
        """Test get_minor_version_number raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_minor_version_number()

    def test_get_parent_module_not_implemented(self):
        """Test get_parent_module raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_parent_module()

    def test_get_product_code_not_implemented(self):
        """Test get_product_code raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_product_code()

    def test_get_product_type_not_implemented(self):
        """Test get_product_type raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_product_type()

    def test_get_rpi_not_implemented(self):
        """Test get_rpi raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_rpi()

    def test_get_vendor_not_implemented(self):
        """Test get_vendor raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.get_vendor()

    def test_set_catalog_number_not_implemented(self):
        """Test set_catalog_number raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_catalog_number('1756-L85E')

    def test_set_is_inhibited_not_implemented(self):
        """Test set_is_inhibited raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_is_inhibited(True)

    def test_set_ip_address_not_implemented(self):
        """Test set_ip_address raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_ip_address('192.168.1.1')

    def test_set_major_version_number_not_implemented(self):
        """Test set_major_version_number raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_major_version_number('32')

    def test_set_minor_version_number_not_implemented(self):
        """Test set_minor_version_number raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_minor_version_number('11')

    def test_set_parent_module_not_implemented(self):
        """Test set_parent_module raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_parent_module(Mock())

    def test_set_product_code_not_implemented(self):
        """Test set_product_code raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_product_code('123')

    def test_set_product_type_not_implemented(self):
        """Test set_product_type raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_product_type('14')

    def test_set_rpi_not_implemented(self):
        """Test set_rpi raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_rpi('20')

    def test_set_vendor_not_implemented(self):
        """Test set_vendor raises NotImplementedError."""
        module = Module()

        with self.assertRaises(NotImplementedError):
            module.set_vendor('1')


class TestModuleInheritance(unittest.TestCase):
    """Test Module inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test Module inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        module = Module()

        self.assertIsInstance(module, PlcObject)

    def test_implements_imodule(self):
        """Test Module implements IModule."""
        from controlrox.interfaces import IModule

        module = Module()

        self.assertIsInstance(module, IModule)


class TestModuleWithController(unittest.TestCase):
    """Test Module with controller integration."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IController

        self.mock_controller = Mock(spec=IController)
        self.mock_controller.name = 'TestController'

        class TestableModule(Module):
            def get_catalog_number(self):
                return '1756-L85E'

            def get_ip_address(self):
                return '192.168.1.1'

            def get_is_inhibited(self):
                return False

            def get_major_version_number(self):
                return '32'

            def get_minor_version_number(self):
                return '11'

            def get_parent_module(self):  # type: ignore
                return None

            def get_product_code(self):
                return '123'

            def get_product_type(self):
                return '14'

            def get_rpi(self):
                return '20'

            def get_vendor(self):
                return '1'

            def set_catalog_number(self, catalog_number):
                pass

            def set_is_inhibited(self, inhibited):
                pass

            def set_ip_address(self, ip_address):
                pass

            def set_major_version_number(self, major_version_number):
                pass

            def set_minor_version_number(self, minor_version_number):
                pass

            def set_parent_module(self, parent_module):
                pass

            def set_product_code(self, product_code):
                pass

            def set_product_type(self, product_type):
                pass

            def set_rpi(self, rpi):
                pass

            def set_vendor(self, vendor):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableModule = TestableModule

    def test_module_with_controller(self):
        """Test module initialized with controller."""
        module = self.TestableModule(controller=self.mock_controller)

        self.assertEqual(module.controller, self.mock_controller)

    def test_module_controller_access(self):
        """Test accessing controller from module."""
        module = self.TestableModule(controller=self.mock_controller)

        controller = module.get_controller()

        self.assertEqual(controller, self.mock_controller)

    def test_module_set_controller(self):
        """Test setting controller after initialization."""
        module = self.TestableModule()

        module.set_controller(self.mock_controller)

        self.assertEqual(module.controller, self.mock_controller)

    def test_module_without_controller(self):
        """Test module without controller."""
        module = self.TestableModule()

        self.assertIsNone(module.controller)


class TestModuleMetaDataIntegration(unittest.TestCase):
    """Test Module metadata integration."""

    def test_module_metadata_as_dict(self):
        """Test module metadata stored as dict."""
        meta_data = {'@Name': 'LocalModule', '@CatalogNumber': '1756-L85E'}
        module = Module(meta_data=meta_data)

        self.assertEqual(module.meta_data, meta_data)
        self.assertIsInstance(module.meta_data, dict)

    def test_module_name_from_metadata(self):
        """Test module name extracted from metadata."""
        meta_data = {'@Name': 'ModuleFromMeta'}
        module = Module(meta_data=meta_data)

        self.assertEqual(module.name, 'ModuleFromMeta')

    def test_module_description_from_metadata(self):
        """Test module description extracted from metadata."""
        meta_data = {'@Name': 'MyModule', '@Description': 'Test Module Description'}
        module = Module(meta_data=meta_data)

        self.assertEqual(module.description, 'Test Module Description')

    def test_module_explicit_name_overrides_metadata(self):
        """Test explicit name parameter overrides metadata."""
        meta_data = {'@Name': 'MetaName'}
        module = Module(meta_data=meta_data, name='ExplicitName')

        self.assertEqual(module.name, 'ExplicitName')

    def test_module_with_empty_metadata(self):
        """Test module with empty metadata dict."""
        module = Module(meta_data={})

        self.assertEqual(module.meta_data, {})


class TestModuleVersionManagement(unittest.TestCase):
    """Test module version management."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableModule(Module):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._major_version = '32'
                self._minor_version = '11'

            def get_catalog_number(self):
                return '1756-L85E'

            def get_ip_address(self):
                return '192.168.1.1'

            def get_is_inhibited(self):
                return False

            def get_major_version_number(self):
                return self._major_version

            def get_minor_version_number(self):
                return self._minor_version

            def get_parent_module(self):  # type: ignore
                return None

            def get_product_code(self):
                return '123'

            def get_product_type(self):
                return '14'

            def get_rpi(self):
                return '20'

            def get_vendor(self):
                return '1'

            def set_catalog_number(self, catalog_number):
                pass

            def set_is_inhibited(self, inhibited):
                pass

            def set_ip_address(self, ip_address):
                pass

            def set_major_version_number(self, major_version_number):
                self._major_version = major_version_number

            def set_minor_version_number(self, minor_version_number):
                self._minor_version = minor_version_number

            def set_parent_module(self, parent_module):
                pass

            def set_product_code(self, product_code):
                pass

            def set_product_type(self, product_type):
                pass

            def set_rpi(self, rpi):
                pass

            def set_vendor(self, vendor):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableModule = TestableModule

    def test_default_major_version(self):
        """Test default major version."""
        module = self.TestableModule()

        self.assertEqual(module.get_major_version_number(), '32')

    def test_default_minor_version(self):
        """Test default minor version."""
        module = self.TestableModule()

        self.assertEqual(module.get_minor_version_number(), '11')

    def test_set_major_version(self):
        """Test setting major version."""
        module = self.TestableModule()

        module.set_major_version_number('33')

        self.assertEqual(module.get_major_version_number(), '33')

    def test_set_minor_version(self):
        """Test setting minor version."""
        module = self.TestableModule()

        module.set_minor_version_number('12')

        self.assertEqual(module.get_minor_version_number(), '12')

    def test_version_as_strings(self):
        """Test versions stored as strings."""
        module = self.TestableModule()

        self.assertIsInstance(module.get_major_version_number(), str)
        self.assertIsInstance(module.get_minor_version_number(), str)


class TestModuleNetworkConfiguration(unittest.TestCase):
    """Test module network configuration."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableModule(Module):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._ip_address = '192.168.1.1'
                self._is_inhibited = False

            def get_catalog_number(self):
                return '1756-L85E'

            def get_ip_address(self):
                return self._ip_address

            def get_is_inhibited(self):
                return self._is_inhibited

            def get_major_version_number(self):
                return '32'

            def get_minor_version_number(self):
                return '11'

            def get_parent_module(self):  # type: ignore
                return None

            def get_product_code(self):
                return '123'

            def get_product_type(self):
                return '14'

            def get_rpi(self):
                return '20'

            def get_vendor(self):
                return '1'

            def set_catalog_number(self, catalog_number):
                pass

            def set_is_inhibited(self, inhibited):
                self._is_inhibited = inhibited

            def set_ip_address(self, ip_address):
                self._ip_address = ip_address

            def set_major_version_number(self, major_version_number):
                pass

            def set_minor_version_number(self, minor_version_number):
                pass

            def set_parent_module(self, parent_module):
                pass

            def set_product_code(self, product_code):
                pass

            def set_product_type(self, product_type):
                pass

            def set_rpi(self, rpi):
                pass

            def set_vendor(self, vendor):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableModule = TestableModule

    def test_default_ip_address(self):
        """Test default IP address."""
        module = self.TestableModule()

        self.assertEqual(module.get_ip_address(), '192.168.1.1')

    def test_set_ip_address(self):
        """Test setting IP address."""
        module = self.TestableModule()

        module.set_ip_address('10.0.0.100')

        self.assertEqual(module.get_ip_address(), '10.0.0.100')

    def test_ip_address_validation_format(self):
        """Test IP address stored as string."""
        module = self.TestableModule()

        self.assertIsInstance(module.get_ip_address(), str)

    def test_module_not_inhibited_by_default(self):
        """Test module not inhibited by default."""
        module = self.TestableModule()

        self.assertFalse(module.get_is_inhibited())

    def test_set_module_inhibited(self):
        """Test setting module as inhibited."""
        module = self.TestableModule()

        module.set_is_inhibited(True)

        self.assertTrue(module.get_is_inhibited())

    def test_set_module_not_inhibited(self):
        """Test setting module as not inhibited."""
        module = self.TestableModule()
        module.set_is_inhibited(True)

        module.set_is_inhibited(False)

        self.assertFalse(module.get_is_inhibited())


class TestModuleProductInformation(unittest.TestCase):
    """Test module product information."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableModule(Module):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._catalog_number = '1756-L85E'
                self._product_code = '123'
                self._product_type = '14'
                self._vendor = '1'

            def get_catalog_number(self):
                return self._catalog_number

            def get_ip_address(self):
                return '192.168.1.1'

            def get_is_inhibited(self):
                return False

            def get_major_version_number(self):
                return '32'

            def get_minor_version_number(self):
                return '11'

            def get_parent_module(self):  # type: ignore
                return None

            def get_product_code(self):
                return self._product_code

            def get_product_type(self):
                return self._product_type

            def get_rpi(self):
                return '20'

            def get_vendor(self):
                return self._vendor

            def set_catalog_number(self, catalog_number):
                self._catalog_number = catalog_number

            def set_is_inhibited(self, inhibited):
                pass

            def set_ip_address(self, ip_address):
                pass

            def set_major_version_number(self, major_version_number):
                pass

            def set_minor_version_number(self, minor_version_number):
                pass

            def set_parent_module(self, parent_module):
                pass

            def set_product_code(self, product_code):
                self._product_code = product_code

            def set_product_type(self, product_type):
                self._product_type = product_type

            def set_rpi(self, rpi):
                pass

            def set_vendor(self, vendor):
                self._vendor = vendor

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableModule = TestableModule

    def test_catalog_number(self):
        """Test catalog number."""
        module = self.TestableModule()

        self.assertEqual(module.get_catalog_number(), '1756-L85E')

    def test_set_catalog_number(self):
        """Test setting catalog number."""
        module = self.TestableModule()

        module.set_catalog_number('1756-L83E')

        self.assertEqual(module.get_catalog_number(), '1756-L83E')

    def test_product_code(self):
        """Test product code."""
        module = self.TestableModule()

        self.assertEqual(module.get_product_code(), '123')

    def test_set_product_code(self):
        """Test setting product code."""
        module = self.TestableModule()

        module.set_product_code('456')

        self.assertEqual(module.get_product_code(), '456')

    def test_product_type(self):
        """Test product type."""
        module = self.TestableModule()

        self.assertEqual(module.get_product_type(), '14')

    def test_set_product_type(self):
        """Test setting product type."""
        module = self.TestableModule()

        module.set_product_type('20')

        self.assertEqual(module.get_product_type(), '20')

    def test_vendor(self):
        """Test vendor."""
        module = self.TestableModule()

        self.assertEqual(module.get_vendor(), '1')

    def test_set_vendor(self):
        """Test setting vendor."""
        module = self.TestableModule()

        module.set_vendor('2')

        self.assertEqual(module.get_vendor(), '2')

    def test_rockwell_vendor_id(self):
        """Test Rockwell Automation vendor ID is '1'."""
        module = self.TestableModule()

        # Rockwell Automation vendor ID
        self.assertEqual(module.get_vendor(), '1')


class TestModuleRPIConfiguration(unittest.TestCase):
    """Test module RPI (Requested Packet Interval) configuration."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableModule(Module):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._rpi = '20'

            def get_catalog_number(self):
                return '1756-L85E'

            def get_ip_address(self):
                return '192.168.1.1'

            def get_is_inhibited(self):
                return False

            def get_major_version_number(self):
                return '32'

            def get_minor_version_number(self):
                return '11'

            def get_parent_module(self):  # type: ignore
                return None

            def get_product_code(self):
                return '123'

            def get_product_type(self):
                return '14'

            def get_rpi(self):
                return self._rpi

            def get_vendor(self):
                return '1'

            def set_catalog_number(self, catalog_number):
                pass

            def set_is_inhibited(self, inhibited):
                pass

            def set_ip_address(self, ip_address):
                pass

            def set_major_version_number(self, major_version_number):
                pass

            def set_minor_version_number(self, minor_version_number):
                pass

            def set_parent_module(self, parent_module):
                pass

            def set_product_code(self, product_code):
                pass

            def set_product_type(self, product_type):
                pass

            def set_rpi(self, rpi):
                self._rpi = rpi

            def set_vendor(self, vendor):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableModule = TestableModule

    def test_default_rpi(self):
        """Test default RPI value."""
        module = self.TestableModule()

        self.assertEqual(module.get_rpi(), '20')

    def test_set_rpi(self):
        """Test setting RPI."""
        module = self.TestableModule()

        module.set_rpi('100')

        self.assertEqual(module.get_rpi(), '100')

    def test_rpi_as_string(self):
        """Test RPI stored as string."""
        module = self.TestableModule()

        self.assertIsInstance(module.get_rpi(), str)


class TestModuleParentChildRelationship(unittest.TestCase):
    """Test module parent-child relationship."""

    def setUp(self):
        """Set up test fixtures."""
        from controlrox.interfaces import IModule

        self.mock_parent = Mock(spec=IModule)
        self.mock_parent.name = 'ParentModule'

        class TestableModule(Module):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._parent_module = None

            def get_catalog_number(self):
                return '1756-L85E'

            def get_ip_address(self):
                return '192.168.1.1'

            def get_is_inhibited(self):
                return False

            def get_major_version_number(self):
                return '32'

            def get_minor_version_number(self):
                return '11'

            def get_parent_module(self):  # type: ignore
                return self._parent_module

            def get_product_code(self):
                return '123'

            def get_product_type(self):
                return '14'

            def get_rpi(self):
                return '20'

            def get_vendor(self):
                return '1'

            def set_catalog_number(self, catalog_number):
                pass

            def set_is_inhibited(self, inhibited):
                pass

            def set_ip_address(self, ip_address):
                pass

            def set_major_version_number(self, major_version_number):
                pass

            def set_minor_version_number(self, minor_version_number):
                pass

            def set_parent_module(self, parent_module):
                if parent_module is not None and not isinstance(parent_module, IModule):
                    raise TypeError("parent_module must be an IModule")
                self._parent_module = parent_module

            def set_product_code(self, product_code):
                pass

            def set_product_type(self, product_type):
                pass

            def set_rpi(self, rpi):
                pass

            def set_vendor(self, vendor):
                pass

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return 'TestProcess'

        self.TestableModule = TestableModule

    def test_module_without_parent(self):
        """Test module without parent."""
        module = self.TestableModule()

        self.assertIsNone(module.get_parent_module())

    def test_set_parent_module(self):
        """Test setting parent module."""
        module = self.TestableModule()

        module.set_parent_module(self.mock_parent)

        self.assertEqual(module.get_parent_module(), self.mock_parent)

    def test_parent_module_type_validation(self):
        """Test parent module must be IModule."""
        module = self.TestableModule()

        with self.assertRaises(TypeError):
            module.set_parent_module("not a module")  # type: ignore


class TestModuleStringRepresentation(unittest.TestCase):
    """Test module string representation."""

    def test_module_str_returns_name(self):
        """Test __str__ returns module name."""
        module = Module(name='MyModuleName')

        self.assertEqual(str(module), 'MyModuleName')

    def test_module_repr_returns_name(self):
        """Test __repr__ returns module name."""
        module = Module(name='MyModuleName')

        self.assertEqual(repr(module), 'MyModuleName')


class TestModuleSpecialCases(unittest.TestCase):
    """Test special cases and edge conditions."""

    def test_module_with_none_values(self):
        """Test module with None for optional parameters."""
        module = Module(
            meta_data=None,
            controller=None,
            name=None,
            description=None
        )

        self.assertIsNotNone(module)

    def test_module_multiple_property_access(self):
        """Test accessing module properties multiple times."""
        module = Module(name='TestModule', description='Test Desc')

        name1 = module.name
        name2 = module.name
        desc1 = module.description
        desc2 = module.description

        self.assertEqual(name1, name2)
        self.assertEqual(desc1, desc2)

    def test_module_initialization_order(self):
        """Test module initializes properly with various parameter orders."""
        module1 = Module(name='Mod1', description='Desc1')
        module2 = Module(description='Desc2', name='Mod2')

        self.assertEqual(module1.name, 'Mod1')
        self.assertEqual(module2.name, 'Mod2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
