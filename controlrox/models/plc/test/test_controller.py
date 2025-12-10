"""Unit tests for controlrox.models.plc.controller module."""
import unittest
from unittest.mock import Mock, patch

from pyrox.models.abc.list import HashList
from controlrox.interfaces import (
    IDatatype,
    IProgram
)
from controlrox.models.plc.controller import Controller


class TestController(unittest.TestCase):
    """Test cases for Controller class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteController(Controller):
            @classmethod
            def from_file(cls, file_location, meta_data=None):
                return cls(
                    meta_data=meta_data,
                    file_location=file_location
                )

            @classmethod
            def from_meta_data(cls, meta_data, file_location='', comms_path='', slot=0):
                return cls(
                    meta_data=meta_data,
                    file_location=file_location,
                    comms_path=comms_path,
                    slot=slot
                )

            def compile_aois(self):
                pass

            def compile_datatypes(self):
                pass

            def compile_modules(self):
                pass

            def compile_programs(self):
                pass

            def compile_tags(self):
                pass

            def get_safety_programs(self) -> HashList[IProgram]:
                return HashList('name')

            def get_standard_programs(self) -> HashList[IProgram]:
                return HashList('name')

            def import_assets_from_file(self, file_location, asset_types=None):
                pass

        self.ConcreteClass = ConcreteController

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        controller = self.ConcreteClass()

        self.assertIsNotNone(controller)
        self.assertEqual(controller._file_location, '')
        self.assertEqual(controller._comms_path, '')
        self.assertEqual(controller._slot, 0)

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        meta_data = {'@Name': 'TestController'}
        controller = self.ConcreteClass(
            meta_data=meta_data,
            file_location='/path/to/file.ACD',
            comms_path='1,0',
            slot=2
        )

        self.assertEqual(controller._file_location, '/path/to/file.ACD')
        self.assertEqual(controller._comms_path, '1,0')
        self.assertEqual(controller._slot, 2)
        self.assertEqual(controller.name, 'TestController')

    def test_init_creates_hash_lists(self):
        """Test initialization creates HashList instances."""
        controller = self.ConcreteClass()

        self.assertIsInstance(controller._aois, HashList)
        self.assertIsInstance(controller._datatypes, HashList)
        self.assertIsInstance(controller._modules, HashList)
        self.assertIsInstance(controller._programs, HashList)
        self.assertIsInstance(controller._tags, HashList)

    def test_aois_property(self):
        """Test aois property."""
        controller = self.ConcreteClass()

        aois = controller.aois

        self.assertIsInstance(aois, HashList)

    def test_comms_path_property(self):
        """Test comms_path property."""
        controller = self.ConcreteClass(comms_path='1,0')

        self.assertEqual(controller.comms_path, '1,0')

    def test_datatypes_property(self):
        """Test datatypes property."""
        controller = self.ConcreteClass()

        datatypes = controller.datatypes

        self.assertIsInstance(datatypes, HashList)

    def test_file_location_property(self):
        """Test file_location property."""
        controller = self.ConcreteClass(file_location='/test/path.ACD')

        self.assertEqual(controller.file_location, '/test/path.ACD')

    def test_modules_property(self):
        """Test modules property."""
        controller = self.ConcreteClass()

        modules = controller.modules

        self.assertIsInstance(modules, HashList)

    def test_programs_property(self):
        """Test programs property."""
        controller = self.ConcreteClass()

        programs = controller.programs

        self.assertIsInstance(programs, HashList)

    def test_safety_programs_property(self):
        """Test safety_programs property."""
        controller = self.ConcreteClass()

        safety_programs = controller.safety_programs

        self.assertIsInstance(safety_programs, HashList)

    def test_slot_property(self):
        """Test slot property."""
        controller = self.ConcreteClass(slot=5)

        self.assertEqual(controller.slot, 5)

    def test_standard_programs_property(self):
        """Test standard_programs property."""
        controller = self.ConcreteClass()

        standard_programs = controller.standard_programs

        self.assertIsInstance(standard_programs, HashList)

    def test_tags_property(self):
        """Test tags property."""
        controller = self.ConcreteClass()

        tags = controller.tags

        self.assertIsInstance(tags, HashList)

    def test_controller_invalidation_method(self):
        """Test _invalidate_controller method."""
        controller = self.ConcreteClass()

        with patch.object(
            controller,
            'invalidate_aois'
        ) as mock_invalidate_aois, patch.object(
            controller,
            'invalidate_datatypes'
        ) as mock_invalidate_datatypes, patch.object(
            controller,
            'invalidate_modules'
        ) as mock_invalidate_modules, patch.object(
            controller,
            'invalidate_programs'
        ) as mock_invalidate_programs, patch.object(
            controller,
            'invalidate_tags'
        ) as mock_invalidate_tags:
            controller.invalidate()
            mock_invalidate_aois.assert_called_once()
            mock_invalidate_datatypes.assert_called_once()
            mock_invalidate_modules.assert_called_once()
            mock_invalidate_programs.assert_called_once()
            mock_invalidate_tags.assert_called_once()


class TestControllerClassMethods(unittest.TestCase):
    """Test Controller class methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteController(Controller):
            @classmethod
            def from_file(cls, file_location, meta_data=None):
                return cls(
                    meta_data=meta_data,
                    file_location=file_location
                )

            @classmethod
            def from_meta_data(cls, meta_data, file_location='', comms_path='', slot=0):
                return cls(
                    meta_data=meta_data,
                    file_location=file_location,
                    comms_path=comms_path,
                    slot=slot
                )

            def compile_aois(self):
                pass

            def compile_datatypes(self):
                pass

            def compile_modules(self):
                pass

            def compile_programs(self):
                pass

            def compile_tags(self):
                pass

            def get_safety_programs(self):
                return HashList('name')

            def get_standard_programs(self):
                return HashList('name')

            def import_assets_from_file(self, file_location, asset_types=None):
                pass

        self.ConcreteClass = ConcreteController

    def test_from_file_creates_controller(self):
        """Test from_file class method creates controller."""
        controller = self.ConcreteClass.from_file('/path/to/file.ACD')

        self.assertIsInstance(controller, Controller)
        self.assertEqual(controller.file_location, '/path/to/file.ACD')

    def test_from_file_with_metadata(self):
        """Test from_file with metadata parameter."""
        meta_data = {'@Name': 'TestController'}
        controller = self.ConcreteClass.from_file('/path/file.ACD', meta_data)

        self.assertEqual(controller.meta_data, meta_data)

    def test_from_meta_data_creates_controller(self):
        """Test from_meta_data class method creates controller."""
        meta_data = {'@Name': 'MyController'}
        controller = self.ConcreteClass.from_meta_data(meta_data)

        self.assertIsInstance(controller, Controller)
        self.assertEqual(controller.meta_data, meta_data)

    def test_from_meta_data_with_all_params(self):
        """Test from_meta_data with all parameters."""
        meta_data = {'@Name': 'MyController'}
        controller = self.ConcreteClass.from_meta_data(
            meta_data=meta_data,
            file_location='/test.ACD',
            comms_path='1,0',
            slot=3
        )

        self.assertEqual(controller.file_location, '/test.ACD')
        self.assertEqual(controller.comms_path, '1,0')
        self.assertEqual(controller.slot, 3)

    def test_from_file_not_implemented_in_base(self):
        """Test from_file raises NotImplementedError in base class."""
        with self.assertRaises(NotImplementedError):
            Controller.from_file('/test.ACD')

    def test_from_meta_data_not_implemented_in_base(self):
        """Test from_meta_data raises NotImplementedError in base class."""
        with self.assertRaises(NotImplementedError):
            Controller.from_meta_data({})


class TestControllerAddMethods(unittest.TestCase):
    """Test Controller add methods for assets."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteController(Controller):
            def compile_aois(self):
                pass

            def compile_datatypes(self):
                pass

            def compile_modules(self):
                pass

            def compile_programs(self):
                pass

            def compile_tags(self):
                pass

            def get_raw_aois(self):
                return []

            def get_raw_datatypes(self):
                return []

            def get_raw_modules(self):
                return []

            def get_raw_programs(self):
                return []

            def get_raw_tags(self):
                return []

            def get_safety_programs(self):
                return HashList('name')

            def get_standard_programs(self):
                return HashList('name')

            def import_assets_from_file(self, file_location, asset_types=None):
                pass

        self.ConcreteClass = ConcreteController

    def test_add_aoi(self):
        """Test add_aoi method."""
        controller = self.ConcreteClass()
        mock_aoi = Mock()
        mock_aoi.name = 'TestAOI'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_aoi(mock_aoi)

            mock_add.assert_called_once_with(
                asset=mock_aoi,
                asset_list=controller.aois,
                raw_asset_list=controller.raw_aois,
                inhibit_invalidate=False,
                invalidate_method=controller.invalidate_aois,
            )

    def test_add_datatype(self):
        """Test add_datatype method."""
        controller = self.ConcreteClass()
        mock_datatype = Mock(spec=IDatatype)
        mock_datatype.name = 'TestType'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_datatype(mock_datatype)

            mock_add.assert_called_once_with(
                asset=mock_datatype,
                asset_list=controller.datatypes,
                raw_asset_list=controller.raw_datatypes,
                inhibit_invalidate=False,
                invalidate_method=controller.invalidate_datatypes,
            )

    def test_add_module(self):
        """Test add_module method."""
        controller = self.ConcreteClass()
        mock_module = Mock()
        mock_module.name = 'TestModule'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_module(mock_module)

            mock_add.assert_called_once_with(
                asset=mock_module,
                asset_list=controller.modules,
                raw_asset_list=controller.raw_modules,
                inhibit_invalidate=False,
                invalidate_method=controller.invalidate_modules,
            )

    def test_add_program(self):
        """Test add_program method."""
        controller = self.ConcreteClass()
        mock_program = Mock()
        mock_program.name = 'TestProgram'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_program(mock_program)

            mock_add.assert_called_once_with(
                asset=mock_program,
                asset_list=controller.programs,
                raw_asset_list=controller.raw_programs,
                inhibit_invalidate=False,
                invalidate_method=controller.invalidate_programs,
            )

    def test_add_tag(self):
        """Test add_tag method."""
        controller = self.ConcreteClass()
        mock_tag = Mock()
        mock_tag.name = 'TestTag'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_tag(mock_tag)

            mock_add.assert_called_once_with(
                asset=mock_tag,
                asset_list=controller.tags,
                raw_asset_list=controller.raw_tags,
                inhibit_invalidate=False,
                invalidate_method=controller.invalidate_tags,
            )

    def test_add_aoi_with_inhibit_invalidate(self):
        """Test add_aoi method with inhibit_invalidate=True."""
        controller = self.ConcreteClass()
        mock_aoi = Mock()
        mock_aoi.name = 'TestAOI'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_aoi(mock_aoi, inhibit_invalidate=True)

            mock_add.assert_called_once_with(
                asset=mock_aoi,
                asset_list=controller.aois,
                raw_asset_list=controller.raw_aois,
                inhibit_invalidate=True,
                invalidate_method=controller.invalidate_aois,
            )

    def test_add_datatype_with_inhibit_invalidate(self):
        """Test add_datatype method with inhibit_invalidate=True."""
        controller = self.ConcreteClass()
        mock_datatype = Mock(spec=IDatatype)
        mock_datatype.name = 'TestType'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_datatype(mock_datatype, inhibit_invalidate=True)

            mock_add.assert_called_once_with(
                asset=mock_datatype,
                asset_list=controller.datatypes,
                raw_asset_list=controller.raw_datatypes,
                inhibit_invalidate=True,
                invalidate_method=controller.invalidate_datatypes,
            )

    def test_add_module_with_inhibit_invalidate(self):
        """Test add_module method with inhibit_invalidate=True."""
        controller = self.ConcreteClass()
        mock_module = Mock()
        mock_module.name = 'TestModule'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_module(mock_module, inhibit_invalidate=True)

            mock_add.assert_called_once_with(
                asset=mock_module,
                asset_list=controller.modules,
                raw_asset_list=controller.raw_modules,
                inhibit_invalidate=True,
                invalidate_method=controller.invalidate_modules,
            )

    def test_add_program_with_inhibit_invalidate(self):
        """Test add_program method with inhibit_invalidate=True."""
        controller = self.ConcreteClass()
        mock_program = Mock()
        mock_program.name = 'TestProgram'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_program(mock_program, inhibit_invalidate=True)

            mock_add.assert_called_once_with(
                asset=mock_program,
                asset_list=controller.programs,
                raw_asset_list=controller.raw_programs,
                inhibit_invalidate=True,
                invalidate_method=controller.invalidate_programs,
            )

    def test_add_tag_with_inhibit_invalidate(self):
        """Test add_tag method with inhibit_invalidate=True."""
        controller = self.ConcreteClass()
        mock_tag = Mock()
        mock_tag.name = 'TestTag'

        with patch.object(controller, 'add_asset_to_meta_data') as mock_add:
            controller.add_tag(mock_tag, inhibit_invalidate=True)

            mock_add.assert_called_once_with(
                asset=mock_tag,
                asset_list=controller.tags,
                raw_asset_list=controller.raw_tags,
                inhibit_invalidate=True,
                invalidate_method=controller.invalidate_tags,
            )


class TestControllerSetters(unittest.TestCase):
    """Test Controller setter methods."""

    def setUp(self):
        """Set up test fixtures."""
        class ConcreteController(Controller):
            def compile_aois(self):
                pass

            def compile_datatypes(self):
                pass

            def compile_modules(self):
                pass

            def compile_programs(self):
                pass

            def compile_tags(self):
                pass

            def get_raw_aois(self):
                return []

            def get_raw_datatypes(self):
                return []

            def get_raw_modules(self):
                return []

            def get_raw_programs(self):
                return []

            def get_raw_tags(self):
                return []

            def get_safety_programs(self):
                return HashList('name')

            def get_standard_programs(self):
                return HashList('name')

            def import_assets_from_file(self, file_location, asset_types=None):
                pass

        self.ConcreteClass = ConcreteController

    def test_set_comms_path(self):
        """Test set_comms_path method."""
        controller = self.ConcreteClass()

        controller.set_comms_path('1,0,2')

        self.assertEqual(controller._comms_path, '1,0,2')

    def test_set_comms_path_with_none(self):
        """Test set_comms_path with None."""
        controller = self.ConcreteClass(comms_path='1,0')

        controller.set_comms_path(None)  # type: ignore

        self.assertIsNone(controller._comms_path)

    def test_set_comms_path_invalid_type_raises_error(self):
        """Test set_comms_path with invalid type raises ValueError."""
        controller = self.ConcreteClass()

        with self.assertRaises(ValueError) as context:
            controller.set_comms_path(123)  # type: ignore

        self.assertIn('must be a string or None', str(context.exception))

    def test_set_file_location(self):
        """Test set_file_location method."""
        controller = self.ConcreteClass()

        controller.set_file_location('/new/path.ACD')

        self.assertEqual(controller._file_location, '/new/path.ACD')

    def test_set_file_location_with_none(self):
        """Test set_file_location with None."""
        controller = self.ConcreteClass(file_location='/old/path.ACD')

        controller.set_file_location(None)

        self.assertIsNone(controller._file_location)

    def test_set_file_location_invalid_type_raises_error(self):
        """Test set_file_location with invalid type raises ValueError."""
        controller = self.ConcreteClass()

        with self.assertRaises(ValueError) as context:
            controller.set_file_location(123)  # type: ignore

        self.assertIn('must be a string or None', str(context.exception))

    def test_set_slot(self):
        """Test set_slot method."""
        controller = self.ConcreteClass()

        controller.set_slot(7)

        self.assertEqual(controller._slot, 7)

    def test_set_slot_zero(self):
        """Test set_slot with zero."""
        controller = self.ConcreteClass(slot=5)

        controller.set_slot(0)

        self.assertEqual(controller._slot, 0)


class TestControllerInheritance(unittest.TestCase):
    """Test Controller inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test Controller inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        controller = Controller()

        self.assertIsInstance(controller, PlcObject)

    def test_implements_icontroller(self):
        """Test Controller implements IController."""
        from controlrox.interfaces import IController

        controller = Controller()

        self.assertIsInstance(controller, IController)


if __name__ == '__main__':
    unittest.main(verbosity=2)
