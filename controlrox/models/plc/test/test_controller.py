"""Unit tests for controlrox.models.plc.controller module."""
import unittest
from unittest.mock import Mock, patch

from pyrox.models.list import HashList
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


class TestControllerCreateMethods(unittest.TestCase):
    """Test Controller create methods for PLC assets."""

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

    def test_create_aoi(self):
        """Test create_aoi method creates an AOI."""
        controller = self.ConcreteClass()

        aoi = controller.create_aoi(
            name='TestAOI',
            description='Test AOI description'
        )

        self.assertIsNotNone(aoi)
        self.assertEqual(aoi.name, 'TestAOI')
        self.assertEqual(aoi.description, 'Test AOI description')

    def test_create_aoi_with_metadata(self):
        """Test create_aoi with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Name': 'MetaAOI', '@Revision': '1.0'}

        aoi = controller.create_aoi(meta_data=meta_data)

        self.assertIsNotNone(aoi)
        self.assertEqual(aoi.meta_data, meta_data)

    def test_create_datatype(self):
        """Test create_datatype method creates a datatype."""
        controller = self.ConcreteClass()

        datatype = controller.create_datatype(
            name='TestDatatype',
            description='Test datatype description'
        )

        self.assertIsNotNone(datatype)
        self.assertEqual(datatype.name, 'TestDatatype')
        self.assertEqual(datatype.description, 'Test datatype description')

    def test_create_datatype_with_metadata(self):
        """Test create_datatype with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Name': 'CustomType', '@Family': 'NoFamily'}

        datatype = controller.create_datatype(meta_data=meta_data)

        self.assertIsNotNone(datatype)
        self.assertEqual(datatype.meta_data, meta_data)

    def test_create_instruction(self):
        """Test create_instruction method creates an instruction."""
        controller = self.ConcreteClass()

        instruction = controller.create_instruction(
            name='XIC',
            description='Examine If Closed'
        )

        self.assertIsNotNone(instruction)
        self.assertEqual(instruction.name, 'XIC')
        self.assertEqual(instruction.description, 'Examine If Closed')

    def test_create_instruction_with_rung(self):
        """Test create_instruction with rung parameter."""
        controller = self.ConcreteClass()
        mock_rung = Mock()

        instruction = controller.create_instruction(
            name='OTE',
            rung=mock_rung
        )

        self.assertIsNotNone(instruction)
        self.assertEqual(instruction.name, 'OTE')

    def test_create_instruction_with_metadata(self):
        """Test create_instruction with metadata."""
        controller = self.ConcreteClass()
        meta_data = '<XIC Name="MyTag" />'

        instruction = controller.create_instruction(meta_data=meta_data)

        self.assertIsNotNone(instruction)

    def test_create_module(self):
        """Test create_module method creates a module."""
        controller = self.ConcreteClass()

        module = controller.create_module(
            name='TestModule',
            description='Test module description'
        )

        self.assertIsNotNone(module)
        self.assertEqual(module.name, 'TestModule')
        self.assertEqual(module.description, 'Test module description')

    def test_create_module_with_metadata(self):
        """Test create_module with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Name': 'IO_Module', '@CatalogNumber': '1756-IB16'}

        module = controller.create_module(meta_data=meta_data)

        self.assertIsNotNone(module)
        self.assertEqual(module.meta_data, meta_data)

    def test_create_operand(self):
        """Test create_operand method creates an operand."""
        controller = self.ConcreteClass()

        operand = controller.create_operand(
            name='MyTag',
            description='Test operand',
        )

        self.assertIsNotNone(operand)
        self.assertEqual(operand.name, 'MyTag')
        self.assertEqual(operand.description, 'Test operand')

    def test_create_operand_with_instruction(self):
        """Test create_operand with instruction parameter."""
        controller = self.ConcreteClass()
        mock_instruction = Mock()

        operand = controller.create_operand(
            name='InputTag',
            instruction=mock_instruction
        )

        self.assertIsNotNone(operand)
        self.assertEqual(operand.name, 'InputTag')

    def test_create_operand_with_metadata(self):
        """Test create_operand with metadata."""
        controller = self.ConcreteClass()
        meta_data = '<Operand Name="Tag1" Type="BOOL" />'

        operand = controller.create_operand(meta_data=meta_data)

        self.assertIsNotNone(operand)

    def test_create_program(self):
        """Test create_program method creates a program."""
        controller = self.ConcreteClass()

        program = controller.create_program(
            name='MainProgram',
            description='Main program description'
        )

        self.assertIsNotNone(program)
        self.assertEqual(program.name, 'MainProgram')
        self.assertEqual(program.description, 'Main program description')

    def test_create_program_with_metadata(self):
        """Test create_program with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Name': 'AlarmProgram', '@Type': 'Normal'}

        program = controller.create_program(meta_data=meta_data)

        self.assertIsNotNone(program)
        self.assertEqual(program.meta_data, meta_data)

    def test_create_routine(self):
        """Test create_routine method creates a routine."""
        controller = self.ConcreteClass()

        routine = controller.create_routine(
            name='MainRoutine',
            description='Main routine description'
        )

        self.assertIsNotNone(routine)
        self.assertEqual(routine.name, 'MainRoutine')
        self.assertEqual(routine.description, 'Main routine description')

    def test_create_routine_with_container(self):
        """Test create_routine with container parameter."""
        controller = self.ConcreteClass()
        mock_container = Mock()

        routine = controller.create_routine(
            name='Subroutine',
            container=mock_container
        )

        self.assertIsNotNone(routine)
        self.assertEqual(routine.name, 'Subroutine')

    def test_create_routine_with_metadata(self):
        """Test create_routine with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Name': 'InitRoutine', '@Type': 'RLL'}

        routine = controller.create_routine(meta_data=meta_data)

        self.assertIsNotNone(routine)
        self.assertEqual(routine.meta_data, meta_data)

    def test_create_rung(self):
        """Test create_rung method creates a rung."""
        controller = self.ConcreteClass()

        rung = controller.create_rung(
            name='Rung0',
            comment='Test rung',
            rung_text='XIC(Input)OTE(Output);',
            rung_number=0
        )

        self.assertIsNotNone(rung)
        self.assertEqual(rung.name, 'Rung0')
        self.assertEqual(rung.comment, 'Test rung')

    def test_create_rung_with_routine(self):
        """Test create_rung with routine parameter."""
        controller = self.ConcreteClass()
        mock_routine = Mock()

        rung = controller.create_rung(
            rung_number=5,
            routine=mock_routine
        )

        self.assertIsNotNone(rung)

    def test_create_rung_with_metadata(self):
        """Test create_rung with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Number': '0', '@Type': 'N'}

        rung = controller.create_rung(meta_data=meta_data)

        self.assertIsNotNone(rung)
        self.assertEqual(rung.meta_data, meta_data)

    def test_create_rung_with_all_parameters(self):
        """Test create_rung with all parameters."""
        controller = self.ConcreteClass()
        mock_routine = Mock()

        rung = controller.create_rung(
            meta_data={'@Number': '1'},
            name='Rung1',
            description='Detailed rung',
            routine=mock_routine,
            comment='Start sequence',
            rung_text='XIC(Start)OTE(Running);',
            rung_number=1
        )

        self.assertIsNotNone(rung)
        self.assertEqual(rung.name, 'Rung1')
        self.assertEqual(rung.description, 'Detailed rung')
        self.assertEqual(rung.comment, 'Start sequence')

    def test_create_tag(self):
        """Test create_tag method creates a tag."""
        controller = self.ConcreteClass()

        tag = controller.create_tag(
            name='TestTag',
            datatype='BOOL',
            description='Test tag description'
        )

        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'TestTag')
        self.assertEqual(tag.description, 'Test tag description')

    def test_create_tag_with_container(self):
        """Test create_tag with container parameter."""
        controller = self.ConcreteClass()
        mock_container = Mock()

        tag = controller.create_tag(
            name='ProgramTag',
            datatype='DINT',
            container=mock_container
        )

        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'ProgramTag')

    def test_create_tag_with_metadata(self):
        """Test create_tag with metadata."""
        controller = self.ConcreteClass()
        meta_data = {'@Name': 'ConfigTag', '@DataType': 'REAL'}

        tag = controller.create_tag(meta_data=meta_data)

        self.assertIsNotNone(tag)
        self.assertEqual(tag.meta_data, meta_data)

    def test_create_tag_with_all_parameters(self):
        """Test create_tag with all parameters."""
        controller = self.ConcreteClass()
        mock_container = Mock()

        tag = controller.create_tag(
            name='ComplexTag',
            datatype='TIMER',
            description='Complex tag with all params',
            container=mock_container,
            meta_data={'@Name': 'Timer1'},
            tag_klass='Standard',
            tag_type='Base',
            dimensions='',
            constant=False,
            external_access='Read/Write'
        )

        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'ComplexTag')
        self.assertEqual(tag.description, 'Complex tag with all params')

    def test_create_tag_array(self):
        """Test create_tag with array dimensions."""
        controller = self.ConcreteClass()

        tag = controller.create_tag(
            name='ArrayTag',
            datatype='DINT',
            dimensions='[10]'
        )

        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'ArrayTag')

    def test_create_tag_constant(self):
        """Test create_tag with constant parameter."""
        controller = self.ConcreteClass()

        tag = controller.create_tag(
            name='ConstantTag',
            datatype='REAL',
            constant=True
        )

        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'ConstantTag')

    def test_create_tag_external_access(self):
        """Test create_tag with external_access parameter."""
        controller = self.ConcreteClass()

        tag = controller.create_tag(
            name='ReadOnlyTag',
            datatype='INT',
            external_access='Read Only'
        )

        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'ReadOnlyTag')

    @patch('controlrox.models.plc.controller.AOIFactory')
    def test_create_common_object_calls_factory(self, mock_factory):
        """Test create_common_object uses factory to get registered type."""
        controller = self.ConcreteClass()
        mock_constructor = Mock(return_value=Mock())
        mock_factory.get_registered_type_by_supporting_class.return_value = mock_constructor

        result = controller.create_common_object(
            factory=mock_factory,
            name='TestObject',
            description='Test description'
        )

        mock_factory.get_registered_type_by_supporting_class.assert_called_once_with(self.ConcreteClass)
        mock_constructor.assert_called_once_with(
            name='TestObject',
            description='Test description',
            meta_data=None
        )
        self.assertIsNotNone(result)

    @patch('controlrox.models.plc.controller.AOIFactory')
    def test_create_common_object_uses_default_type(self, mock_factory):
        """Test create_common_object falls back to default_type when no registered type."""
        controller = self.ConcreteClass()
        mock_factory.get_registered_type_by_supporting_class.return_value = None
        mock_default = Mock(return_value=Mock())

        result = controller.create_common_object(
            factory=mock_factory,
            name='TestObject',
            default_type=mock_default
        )

        mock_default.assert_called_once()
        self.assertIsNotNone(result)

    @patch('controlrox.models.plc.controller.AOIFactory')
    def test_create_common_object_raises_error_without_constructor(self, mock_factory):
        """Test create_common_object raises RuntimeError when no constructor found."""
        controller = self.ConcreteClass()
        mock_factory.get_registered_type_by_supporting_class.return_value = None
        mock_factory.__name__ = 'TestFactory'

        with self.assertRaises(RuntimeError) as context:
            controller.create_common_object(
                factory=mock_factory,
                name='TestObject'
            )

        self.assertIn('No constructor or default constructor found', str(context.exception))
        self.assertIn('TestFactory', str(context.exception))




if __name__ == '__main__':
    unittest.main(verbosity=2)
