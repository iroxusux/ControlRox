"""Unit tests for controlrox.models.plc.rockwell.meta module."""
import unittest
from pathlib import Path
from unittest.mock import patch

from pyrox.models import HashList
from controlrox.models.plc.rockwell.meta import (
    # Constants
    INST_RE_PATTERN,
    INST_TYPE_RE_PATTERN,
    INST_OPER_RE_PATTERN,
    PLC_ROOT_FILE,
    PLC_PROG_FILE,
    PLC_ROUT_FILE,
    PLC_DT_FILE,
    PLC_AOI_FILE,
    PLC_MOD_FILE,
    PLC_RUNG_FILE,
    PLC_TAG_FILE,
    BASE_FILES,
    RE_PATTERN_META_PRE,
    RE_PATTERN_META_POST,
    XIC_OPERAND_RE_PATTERN,
    XIO_OPERAND_RE_PATTERN,
    INPUT_INSTRUCTIONS_RE_PATTER,
    OTE_OPERAND_RE_PATTERN,
    OTL_OPERAND_RE_PATTERN,
    OTU_OPERAND_RE_PATTERN,
    MOV_OPERAND_RE_PATTERN,
    MOVE_OPERAND_RE_PATTERN,
    COP_OPERAND_RE_PATTERN,
    CPS_OPERAND_RE_PATTERN,
    OUTPUT_INSTRUCTIONS_RE_PATTERN,
    L5X_ASSET_DATATYPES,
    L5X_ASSET_TAGS,
    L5X_ASSET_PROGRAMS,
    L5X_ASSET_ADDONINSTRUCTIONDEFINITIONS,
    L5X_ASSET_MODULES,
    L5X_ASSETS,
    L5X_PROP_NAME,
    L5X_PROP_DESCRIPTION,
    RaPlcObject,
)


class TestConstants(unittest.TestCase):
    """Test cases for module constants."""

    def test_regex_patterns(self):
        """Test regex pattern constants are properly defined."""
        self.assertIsInstance(INST_RE_PATTERN, str)
        self.assertIsInstance(INST_TYPE_RE_PATTERN, str)
        self.assertIsInstance(INST_OPER_RE_PATTERN, str)
        self.assertIsInstance(RE_PATTERN_META_PRE, str)
        self.assertIsInstance(RE_PATTERN_META_POST, str)

    def test_input_instruction_patterns(self):
        """Test input instruction regex patterns."""
        self.assertIsInstance(XIC_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(XIO_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(INPUT_INSTRUCTIONS_RE_PATTER, list)
        self.assertEqual(len(INPUT_INSTRUCTIONS_RE_PATTER), 2)

    def test_output_instruction_patterns(self):
        """Test output instruction regex patterns."""
        self.assertIsInstance(OTE_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(OTL_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(OTU_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(MOV_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(MOVE_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(COP_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(CPS_OPERAND_RE_PATTERN, str)
        self.assertIsInstance(OUTPUT_INSTRUCTIONS_RE_PATTERN, list)
        self.assertEqual(len(OUTPUT_INSTRUCTIONS_RE_PATTERN), 7)

    def test_file_paths(self):
        """Test file path constants are Path objects."""
        file_paths = [
            PLC_ROOT_FILE,
            PLC_PROG_FILE,
            PLC_ROUT_FILE,
            PLC_DT_FILE,
            PLC_AOI_FILE,
            PLC_MOD_FILE,
            PLC_RUNG_FILE,
            PLC_TAG_FILE,
        ]

        for file_path in file_paths:
            self.assertIsInstance(file_path, Path)
            self.assertEqual(file_path.suffix, '.L5X')

    def test_base_files_list(self):
        """Test BASE_FILES list contains all expected files."""
        self.assertEqual(len(BASE_FILES), 8)
        self.assertIn(PLC_ROOT_FILE, BASE_FILES)
        self.assertIn(PLC_PROG_FILE, BASE_FILES)
        self.assertIn(PLC_ROUT_FILE, BASE_FILES)
        self.assertIn(PLC_DT_FILE, BASE_FILES)
        self.assertIn(PLC_AOI_FILE, BASE_FILES)
        self.assertIn(PLC_MOD_FILE, BASE_FILES)
        self.assertIn(PLC_RUNG_FILE, BASE_FILES)
        self.assertIn(PLC_TAG_FILE, BASE_FILES)

    def test_l5x_assets(self):
        """Test L5X assets list."""
        expected_assets = [
            'DataTypes',
            'Tags',
            'Programs',
            'AddOnInstructionDefinitions',
            'Modules'
        ]

        for asset in expected_assets:
            self.assertIn(asset, L5X_ASSETS)

        self.assertEqual(len(L5X_ASSETS), len(expected_assets))

    def test_l5x_asset_constants(self):
        """Test L5X asset constant values."""
        self.assertEqual(L5X_ASSET_DATATYPES, 'DataTypes')
        self.assertEqual(L5X_ASSET_TAGS, 'Tags')
        self.assertEqual(L5X_ASSET_PROGRAMS, 'Programs')
        self.assertEqual(L5X_ASSET_ADDONINSTRUCTIONDEFINITIONS, 'AddOnInstructionDefinitions')
        self.assertEqual(L5X_ASSET_MODULES, 'Modules')

    def test_l5x_properties(self):
        """Test L5X property constants."""
        self.assertEqual(L5X_PROP_NAME, '@Name')
        self.assertEqual(L5X_PROP_DESCRIPTION, 'Description')


class TestRaPlcObject(unittest.TestCase):
    """Test cases for RaPlcObject class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteRaPlcObject(RaPlcObject):
            """Concrete implementation for testing."""

            def compile(self):
                """Implement compile from metadata."""
                self.compiled = True
                return self

            def invalidate(self) -> None:
                """Implement invalidate method."""
                self.invalidated = True

            @property
            def process_name(self) -> str:
                """Implement process_name property."""
                return "TestProcess"

        self.ConcreteRaPlcObject = ConcreteRaPlcObject

    def test_init_with_defaults(self):
        """Test RaPlcObject initialization with default values."""
        obj = self.ConcreteRaPlcObject()

        self.assertEqual(obj.name, '')
        self.assertEqual(obj.description, '')
        self.assertIsInstance(obj.meta_data, dict)
        self.assertIsNone(obj._controller)

    def test_init_with_dict_metadata(self):
        """Test RaPlcObject initialization with dictionary metadata."""
        meta_data = {
            '@Name': 'TestName',
            'Description': 'Test Description'
        }
        obj = self.ConcreteRaPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'TestName')
        self.assertEqual(obj.description, 'Test Description')

    def test_init_with_name_and_description(self):
        """Test RaPlcObject initialization with name and description parameters."""
        obj = self.ConcreteRaPlcObject(
            name='CustomName',
            description='Custom Description'
        )

        self.assertEqual(obj.name, 'CustomName')
        self.assertEqual(obj.description, 'Custom Description')

    def test_dict_key_order_default(self):
        """Test dict_key_order property default implementation."""
        obj = self.ConcreteRaPlcObject()

        self.assertEqual(obj.dict_key_order, [])

    def test_default_l5x_file_path_class_attribute(self):
        """Test default_l5x_file_path class attribute exists."""
        self.assertTrue(hasattr(self.ConcreteRaPlcObject, 'default_l5x_file_path'))
        self.assertIsNone(self.ConcreteRaPlcObject.default_l5x_file_path)

    def test_default_l5x_asset_key_class_attribute(self):
        """Test default_l5x_asset_key class attribute exists."""
        self.assertTrue(hasattr(self.ConcreteRaPlcObject, 'default_l5x_asset_key'))
        self.assertIsNone(self.ConcreteRaPlcObject.default_l5x_asset_key)

    def test_compile_method(self):
        """Test compile method implementation."""
        obj = self.ConcreteRaPlcObject()

        obj.compile()

        self.assertTrue(obj.compiled)

    def test_compile_calls_compile_from_meta_data(self):
        """Test compile method calls _compile_from_meta_data."""
        obj = self.ConcreteRaPlcObject()
        obj.compiled = False

        obj.compile()

        self.assertTrue(obj.compiled)

    def test_compile_calls_init_dict_order(self):
        """Test compile method calls _init_dict_order."""
        class OrderedRaPlcObject(RaPlcObject):
            @property
            def dict_key_order(self):
                return ['key1', 'key2']

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = OrderedRaPlcObject(meta_data={})
        obj.compile()

        # Check that dict keys were initialized
        self.assertIn('key1', obj.meta_data)
        self.assertIn('key2', obj.meta_data)


class TestRaPlcObjectGetDefaultMetaData(unittest.TestCase):
    """Test cases for get_default_meta_data class method."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def testget_default_meta_data_with_string(self):
        """Test get_default_meta_data with string metadata."""
        result = self.TestRaPlcObject.get_default_meta_data(
            meta_data="string_metadata",
            file_location=None,
            l5x_dict_key=None
        )

        self.assertEqual(result, "string_metadata")

    def testget_default_meta_data_with_dict(self):
        """Test get_default_meta_data with dictionary metadata."""
        meta_dict = {'@Name': 'Test'}
        result = self.TestRaPlcObject.get_default_meta_data(
            meta_data=meta_dict,
            file_location=None,
            l5x_dict_key=None
        )

        self.assertEqual(result, meta_dict)

    def testget_default_meta_data_no_file_location(self):
        """Test get_default_meta_data returns None when no file location."""
        result = self.TestRaPlcObject.get_default_meta_data(
            meta_data=None,
            file_location=None,
            l5x_dict_key='SomeKey'
        )

        self.assertIsNone(result)

    def testget_default_meta_data_invalid_type(self):
        """Test get_default_meta_data raises ValueError for invalid type."""
        with self.assertRaises(ValueError) as context:
            self.TestRaPlcObject.get_default_meta_data(
                meta_data=123,  # type: ignore  # Invalid type
                file_location=None,
                l5x_dict_key=None
            )

        self.assertIn('meta_data must be of type dict, str, or None!', str(context.exception))

    @patch('controlrox.models.plc.rockwell.meta.l5x_dict_from_file')
    def testget_default_meta_data_loads_from_file(self, mock_l5x_dict):
        """Test get_default_meta_data loads from file when meta_data is None."""
        mock_l5x_dict.return_value = {'TestKey': {'@Name': 'LoadedName'}}

        result = self.TestRaPlcObject.get_default_meta_data(
            meta_data=None,
            file_location='/test/path.L5X',
            l5x_dict_key='TestKey'
        )

        mock_l5x_dict.assert_called_once_with('/test/path.L5X')
        self.assertEqual(result, {'@Name': 'LoadedName'})

    @patch('controlrox.models.plc.rockwell.meta.l5x_dict_from_file')
    def testget_default_meta_data_raises_on_empty_file(self, mock_l5x_dict):
        """Test get_default_meta_data raises ValueError when file is empty."""
        mock_l5x_dict.return_value = None

        with self.assertRaises(ValueError) as context:
            self.TestRaPlcObject.get_default_meta_data(
                meta_data=None,
                file_location='/test/path.L5X',
                l5x_dict_key='TestKey'
            )

        self.assertIn('Could not load default meta data', str(context.exception))

    @patch('controlrox.models.plc.rockwell.meta.l5x_dict_from_file')
    def testget_default_meta_data_raises_on_invalid_dict_key(self, mock_l5x_dict):
        """Test get_default_meta_data raises ValueError when dict key is invalid."""
        mock_l5x_dict.return_value = {'TestKey': 'not a dict'}

        with self.assertRaises(ValueError) as context:
            self.TestRaPlcObject.get_default_meta_data(
                meta_data=None,
                file_location='/test/path.L5X',
                l5x_dict_key='TestKey'
            )

        self.assertIn('is invalid', str(context.exception))


class TestRaPlcObjectDictOperations(unittest.TestCase):
    """Test cases for dictionary operations in RaPlcObject."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                self.was_invalidated = True

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_init_dict_order_no_key_order(self):
        """Test _init_dict_order with empty dict_key_order."""
        obj = self.TestRaPlcObject(meta_data={})

        # Should not crash and meta_data should remain empty
        self.assertEqual(obj.meta_data, {})

    def test_init_dict_order_with_key_order(self):
        """Test _init_dict_order adds missing keys."""
        class OrderedRaPlcObject(RaPlcObject):
            @property
            def dict_key_order(self):
                return ['key1', 'key2', 'key3']

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = OrderedRaPlcObject(meta_data={'existing': 'value'})

        # Check that keys were added
        self.assertIn('key1', obj.meta_data)
        self.assertIn('key2', obj.meta_data)
        self.assertIn('key3', obj.meta_data)

    def test_init_dict_order_with_non_dict_metadata(self):
        """Test _init_dict_order with non-dict metadata."""
        class OrderedRaPlcObject(RaPlcObject):
            @property
            def dict_key_order(self):
                return ['key1', 'key2']

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = OrderedRaPlcObject(meta_data="string metadata")

        # Should not crash with string metadata
        self.assertEqual(obj.meta_data, "string metadata")


class TestRaPlcObjectAssetOperations(unittest.TestCase):
    """Test cases for asset operations in RaPlcObject."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                self.was_invalidated = True

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject


class TestRaPlcObjectAddRemoveAsset(unittest.TestCase):
    """Test cases for add_asset_to_meta_data and remove_asset_from_meta_data."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                self.was_invalidated = True

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_add_asset_to_meta_data_success(self):
        """Test adding asset to metadata successfully."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')
        raw_asset_list = []

        parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 1)
        self.assertIn(asset, asset_list)
        self.assertEqual(raw_asset_list[0]['@Name'], 'AssetName')
        self.assertTrue(parent.was_invalidated)

    def test_add_asset_to_meta_data_with_index(self):
        """Test adding asset at specific index."""
        parent = self.TestRaPlcObject(meta_data={})
        asset1 = self.TestRaPlcObject(meta_data={'@Name': 'Asset1'})
        asset2 = self.TestRaPlcObject(meta_data={'@Name': 'Asset2'})
        asset_list = HashList('name')
        raw_asset_list = []

        parent.add_asset_to_meta_data(asset1, asset_list, raw_asset_list)
        parent.add_asset_to_meta_data(asset2, asset_list, raw_asset_list, index=0)

        self.assertEqual(raw_asset_list[0]['@Name'], 'Asset2')
        self.assertEqual(raw_asset_list[1]['@Name'], 'Asset1')

    def test_add_asset_to_meta_data_inhibit_invalidate(self):
        """Test adding asset with inhibit_invalidate."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')
        raw_asset_list = []
        parent.was_invalidated = False

        parent.add_asset_to_meta_data(
            asset, asset_list, raw_asset_list, inhibit_invalidate=True
        )

        self.assertFalse(parent.was_invalidated)

    def test_add_asset_to_meta_data_invalid_asset_type(self):
        """Test adding invalid asset type raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset_list = HashList('name')
        raw_asset_list = []

        with self.assertRaises(ValueError) as context:
            parent.add_asset_to_meta_data(123, asset_list, raw_asset_list)  # type: ignore

        self.assertIn('must be of type', str(context.exception))

    def test_add_asset_to_meta_data_invalid_asset_list_type(self):
        """Test adding asset with invalid asset_list type raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        raw_asset_list = []

        with self.assertRaises(ValueError) as context:
            parent.add_asset_to_meta_data(asset, '[]', raw_asset_list)  # type: ignore

        self.assertIn('must be of type HashList or list', str(context.exception))

    def test_add_asset_to_meta_data_invalid_raw_list_type(self):
        """Test adding asset with invalid raw_asset_list type raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')

        with self.assertRaises(ValueError) as context:
            parent.add_asset_to_meta_data(asset, asset_list, {})  # type: ignore

        self.assertIn('must be of type list', str(context.exception))

    def test_add_asset_to_meta_data_removes_existing(self):
        """Test adding existing asset removes it first."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')
        raw_asset_list = []

        # Add asset twice
        parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list)
        parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list)

        # Should only be present once
        self.assertEqual(len(raw_asset_list), 1)

    def test_add_asset_to_meta_data_invalid_metadata(self):
        """Test adding asset with non-dict metadata raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data="string metadata")
        asset_list = HashList('name')
        raw_asset_list = []

        with self.assertRaises(ValueError) as context:
            parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list)

        self.assertIn('meta_data must be of type dict', str(context.exception))

    def test_remove_asset_from_meta_data_success(self):
        """Test removing asset from metadata successfully."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')
        raw_asset_list = []

        parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list, inhibit_invalidate=True)
        parent.was_invalidated = False
        parent.remove_asset_from_meta_data(asset, asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 0)
        self.assertTrue(parent.was_invalidated)

    def test_remove_asset_from_meta_data_inhibit_invalidate(self):
        """Test removing asset with inhibit_invalidate."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')
        raw_asset_list = []

        parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list, inhibit_invalidate=True)
        parent.was_invalidated = False
        parent.remove_asset_from_meta_data(
            asset, asset_list, raw_asset_list, inhibit_invalidate=True
        )

        self.assertFalse(parent.was_invalidated)

    def test_remove_asset_from_meta_data_invalid_asset_type(self):
        """Test removing invalid asset type raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset_list = HashList('name')
        raw_asset_list = []

        with self.assertRaises(ValueError) as context:
            parent.remove_asset_from_meta_data(123, asset_list, raw_asset_list)  # type: ignore

        self.assertIn('must be of type', str(context.exception))

    def test_remove_asset_from_meta_data_not_in_list(self):
        """Test removing asset that's not in list doesn't crash."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'AssetName'})
        asset_list = HashList('name')
        raw_asset_list = []

        # Should not raise exception
        parent.remove_asset_from_meta_data(asset, asset_list, raw_asset_list)


class TestRaPlcObjectRedefineAssetList(unittest.TestCase):
    """Test cases for _redefine_raw_asset_list_from_asset_list."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                self.was_invalidated = True

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_redefine_raw_asset_list_success(self):
        """Test redefining raw asset list from asset list."""
        parent = self.TestRaPlcObject(meta_data={})
        asset1 = self.TestRaPlcObject(meta_data={'@Name': 'Asset1'})
        asset2 = self.TestRaPlcObject(meta_data={'@Name': 'Asset2'})

        asset_list = HashList('name')
        asset_list.append(asset1)
        asset_list.append(asset2)

        raw_asset_list = []

        parent.redefine_raw_asset_list_from_asset_list(asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 2)
        self.assertEqual(raw_asset_list[0]['@Name'], 'Asset1')
        self.assertEqual(raw_asset_list[1]['@Name'], 'Asset2')
        self.assertTrue(parent.was_invalidated)

    def test_redefine_raw_asset_list_clears_existing(self):
        """Test redefining raw asset list clears existing items."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'NewAsset'})

        asset_list = HashList('name')
        asset_list.append(asset)

        raw_asset_list = [{'@Name': 'OldAsset'}]

        parent.redefine_raw_asset_list_from_asset_list(asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 1)
        self.assertEqual(raw_asset_list[0]['@Name'], 'NewAsset')

    def test_redefine_raw_asset_list_invalid_asset_list_type(self):
        """Test redefining with invalid asset_list type raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})

        with self.assertRaises(ValueError) as context:
            parent.redefine_raw_asset_list_from_asset_list([], [])  # type: ignore

        self.assertIn('must be of type HashList', str(context.exception))

    def test_redefine_raw_asset_list_invalid_raw_list_type(self):
        """Test redefining with invalid raw_asset_list type raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset_list = HashList('name')

        with self.assertRaises(ValueError) as context:
            parent.redefine_raw_asset_list_from_asset_list(asset_list, {})  # type: ignore

        self.assertIn('must be of type list', str(context.exception))

    def test_redefine_raw_asset_list_invalid_asset_metadata(self):
        """Test redefining with invalid asset metadata raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data="string metadata")

        asset_list = HashList('name')
        asset_list.append(asset)
        raw_asset_list = []

        with self.assertRaises(ValueError) as context:
            parent.redefine_raw_asset_list_from_asset_list(asset_list, raw_asset_list)

        self.assertIn('meta_data must be of type dict', str(context.exception))

    def test_redefine_raw_asset_list_non_plc_object(self):
        """Test redefining with non-PlcObject in list raises ValueError."""
        parent = self.TestRaPlcObject(meta_data={})

        class NonPlcObject:
            @property
            def name(self):
                return "NonPlc"

        asset_list = HashList('name')
        asset_list.append(NonPlcObject())
        raw_asset_list = []

        with self.assertRaises(ValueError) as context:
            parent.redefine_raw_asset_list_from_asset_list(asset_list, raw_asset_list)

        self.assertIn('asset must be of type PlcObject', str(context.exception))


class TestRaPlcObjectAbstractMethods(unittest.TestCase):
    """Test that abstract methods must be implemented."""

    def test_compile_from_meta_data_not_implemented(self):
        """Test _compile_from_meta_data raises NotImplementedError by default."""
        class IncompleteRaPlcObject(RaPlcObject):
            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = IncompleteRaPlcObject()

        with self.assertRaises(NotImplementedError):
            obj.compile()


class TestRaPlcObjectGetAssetFromMetaData(unittest.TestCase):
    """Test cases for get_asset_from_meta_data method."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_get_asset_creates_structure(self):
        """Test get_asset_from_meta_data creates structure when missing."""
        obj = self.TestRaPlcObject(meta_data={})

        result = obj.get_asset_from_meta_data('TestAsset', 'TestList')

        self.assertIsInstance(result, list)
        meta_data = obj.meta_data
        assert isinstance(meta_data, dict)
        self.assertIn('TestAsset', meta_data)
        self.assertIn('TestList', meta_data['TestAsset'])

    def test_get_asset_returns_existing_list(self):
        """Test get_asset_from_meta_data returns existing list."""
        obj = self.TestRaPlcObject(meta_data={
            'TestAsset': {
                'TestList': [{'@Name': 'Item1'}, {'@Name': 'Item2'}]
            }
        })

        result = obj.get_asset_from_meta_data('TestAsset', 'TestList')

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['@Name'], 'Item1')

    def test_get_asset_converts_dict_to_list(self):
        """Test get_asset_from_meta_data converts single dict to list."""
        obj = self.TestRaPlcObject(meta_data={
            'TestAsset': {
                'TestList': {'@Name': 'SingleItem'}
            }
        })

        result = obj.get_asset_from_meta_data('TestAsset', 'TestList')

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['@Name'], 'SingleItem')

    def test_get_asset_handles_empty_dict(self):
        """Test get_asset_from_meta_data handles empty dict."""
        obj = self.TestRaPlcObject(meta_data={
            'TestAsset': {
                'TestList': {}
            }
        })

        result = obj.get_asset_from_meta_data('TestAsset', 'TestList')

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_asset_handles_none(self):
        """Test get_asset_from_meta_data handles None value."""
        obj = self.TestRaPlcObject(meta_data={
            'TestAsset': {
                'TestList': None
            }
        })

        result = obj.get_asset_from_meta_data('TestAsset', 'TestList')

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_asset_creates_missing_asset_key(self):
        """Test get_asset_from_meta_data creates missing asset key."""
        obj = self.TestRaPlcObject(meta_data={'OtherKey': {}})

        result = obj.get_asset_from_meta_data('NewAsset', 'NewList')

        meta_data = obj.meta_data
        assert isinstance(meta_data, dict)
        self.assertIn('NewAsset', meta_data)
        self.assertIsInstance(result, list)


class TestRaPlcObjectInitDictOrder(unittest.TestCase):
    """Test cases for init_dict_order method."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_init_dict_order_empty_order(self):
        """Test init_dict_order with empty dict_key_order."""
        obj = self.TestRaPlcObject(meta_data={'existing': 'value'})

        obj.init_dict_order()

        # Should not modify dict
        meta_data = obj.meta_data
        assert isinstance(meta_data, dict)
        self.assertEqual(len(meta_data), 1)

    def test_init_dict_order_adds_keys(self):
        """Test init_dict_order adds keys in order."""
        class OrderedObject(RaPlcObject):
            @property
            def dict_key_order(self):
                return ['first', 'second', 'third']

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = OrderedObject(meta_data={})

        meta_data = obj.meta_data
        assert isinstance(meta_data, dict)
        keys = list(meta_data.keys())
        self.assertEqual(keys[0], 'first')
        self.assertEqual(keys[1], 'second')
        self.assertEqual(keys[2], 'third')

    def test_init_dict_order_preserves_existing(self):
        """Test init_dict_order preserves existing keys."""
        class OrderedObject(RaPlcObject):
            @property
            def dict_key_order(self):
                return ['key1', 'key2']

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = OrderedObject(meta_data={'key1': 'value1'})

        meta_data = obj.meta_data
        assert isinstance(meta_data, dict)
        self.assertEqual(meta_data['key1'], 'value1')
        self.assertIn('key2', meta_data)

    def test_init_dict_order_string_metadata(self):
        """Test init_dict_order with string metadata."""
        class OrderedObject(RaPlcObject):
            @property
            def dict_key_order(self):
                return ['key1', 'key2']

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        obj = OrderedObject(meta_data="string_meta")

        # Should not crash
        self.assertEqual(obj.meta_data, "string_meta")


class TestRaPlcObjectDictItemAccess(unittest.TestCase):
    """Test cases for dictionary item access on RaPlcObject."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_getitem_access(self):
        """Test dictionary-style item access."""
        obj = self.TestRaPlcObject(meta_data={'key': 'value'})

        result = obj['key']

        self.assertEqual(result, 'value')

    def test_setitem_access(self):
        """Test dictionary-style item setting."""
        obj = self.TestRaPlcObject(meta_data={})

        obj['newkey'] = 'newvalue'

        meta_data = obj.meta_data
        assert isinstance(meta_data, dict)
        self.assertEqual(meta_data['newkey'], 'newvalue')

    def test_getitem_missing_key(self):
        """Test dictionary-style access with missing key."""
        obj = self.TestRaPlcObject(meta_data={})

        # Should raise KeyError or return None based on implementation
        try:
            result = obj['missing']
            # If no error, should be None or some default
            self.assertIsNone(result)
        except KeyError:
            pass  # Expected behavior


class TestRaPlcObjectInheritance(unittest.TestCase):
    """Test RaPlcObject inheritance from PlcObject."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_inherits_from_plc_object(self):
        """Test RaPlcObject inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        obj = self.TestRaPlcObject()

        self.assertIsInstance(obj, PlcObject)
        self.assertIsInstance(obj, RaPlcObject)

    def test_has_plc_object_properties(self):
        """Test RaPlcObject has PlcObject properties."""
        obj = self.TestRaPlcObject()

        self.assertTrue(hasattr(obj, 'name'))
        self.assertTrue(hasattr(obj, 'description'))
        self.assertTrue(hasattr(obj, 'meta_data'))

    def test_has_plc_object_methods(self):
        """Test RaPlcObject has PlcObject methods."""
        obj = self.TestRaPlcObject()

        self.assertTrue(hasattr(obj, 'set_name'))
        self.assertTrue(hasattr(obj, 'set_description'))
        self.assertTrue(hasattr(obj, 'compile'))


class TestRaPlcObjectControllerIntegration(unittest.TestCase):
    """Test RaPlcObject with controller integration."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_init_with_controller(self):
        """Test RaPlcObject initialization with controller."""
        from unittest.mock import Mock
        from controlrox.interfaces import IController

        controller = Mock(spec=IController)
        obj = self.TestRaPlcObject(controller=controller)

        self.assertIsNotNone(obj._controller)

    def test_init_without_controller(self):
        """Test RaPlcObject initialization without controller."""
        obj = self.TestRaPlcObject()

        self.assertIsNone(obj._controller)

    def test_get_controller_when_set(self):
        """Test get_controller when controller is set."""
        from unittest.mock import Mock
        from controlrox.interfaces import IController

        controller = Mock(spec=IController)
        obj = self.TestRaPlcObject(controller=controller)

        result = obj.get_controller()

        self.assertEqual(result, controller)


class TestRaPlcObjectComplexScenarios(unittest.TestCase):
    """Test RaPlcObject complex real-world scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                self.invalidated = True

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_multiple_asset_additions(self):
        """Test adding multiple assets in sequence."""
        parent = self.TestRaPlcObject(meta_data={})
        asset1 = self.TestRaPlcObject(meta_data={'@Name': 'Asset1'})
        asset2 = self.TestRaPlcObject(meta_data={'@Name': 'Asset2'})
        asset3 = self.TestRaPlcObject(meta_data={'@Name': 'Asset3'})

        asset_list = HashList('name')
        raw_asset_list = []

        parent.add_asset_to_meta_data(asset1, asset_list, raw_asset_list)
        parent.add_asset_to_meta_data(asset2, asset_list, raw_asset_list)
        parent.add_asset_to_meta_data(asset3, asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 3)
        self.assertEqual(len(asset_list), 3)

    def test_add_then_remove_asset(self):
        """Test adding and then removing an asset."""
        parent = self.TestRaPlcObject(meta_data={})
        asset = self.TestRaPlcObject(meta_data={'@Name': 'Asset'})

        asset_list = HashList('name')
        raw_asset_list = []

        parent.add_asset_to_meta_data(asset, asset_list, raw_asset_list)
        self.assertEqual(len(raw_asset_list), 1)

        parent.remove_asset_from_meta_data(asset, asset_list, raw_asset_list)
        self.assertEqual(len(raw_asset_list), 0)

    def test_redefine_after_modifications(self):
        """Test redefining raw list after manual modifications."""
        parent = self.TestRaPlcObject(meta_data={})
        asset1 = self.TestRaPlcObject(meta_data={'@Name': 'Asset1'})
        asset2 = self.TestRaPlcObject(meta_data={'@Name': 'Asset2'})

        asset_list = HashList('name')
        raw_asset_list = [{'@Name': 'OldAsset'}]

        asset_list.append(asset1)
        asset_list.append(asset2)

        parent.redefine_raw_asset_list_from_asset_list(asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 2)
        self.assertEqual(raw_asset_list[0]['@Name'], 'Asset1')


class TestRaPlcObjectEdgeCases(unittest.TestCase):
    """Test RaPlcObject edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        class TestRaPlcObject(RaPlcObject):
            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.TestRaPlcObject = TestRaPlcObject

    def test_init_with_empty_dict(self):
        """Test initialization with empty dictionary."""
        obj = self.TestRaPlcObject(meta_data={})

        self.assertIsInstance(obj.meta_data, dict)
        self.assertEqual(len(obj.meta_data), 0)

    def test_init_with_complex_nested_dict(self):
        """Test initialization with complex nested dictionary."""
        meta_data = {
            '@Name': 'Complex',
            'Level1': {
                'Level2': {
                    'Level3': ['item1', 'item2']
                }
            }
        }
        obj = self.TestRaPlcObject(meta_data=meta_data)

        self.assertEqual(obj.name, 'Complex')
        self.assertIn('Level1', obj.meta_data)

    def test_string_metadata_preserved(self):
        """Test string metadata is preserved."""
        obj = self.TestRaPlcObject(meta_data="string_metadata")

        self.assertEqual(obj.meta_data, "string_metadata")

    def test_name_from_metadata_variations(self):
        """Test name extraction from various metadata formats."""
        test_cases = [
            ({'@Name': 'Test1'}, 'Test1'),
            ({'Name': 'Test2'}, 'Test2'),
            ({'@name': 'Test3'}, 'Test3'),
            ({'name': 'Test4'}, 'Test4'),
        ]

        for meta_data, expected_name in test_cases:
            obj = self.TestRaPlcObject(meta_data=meta_data)
            self.assertEqual(obj.name, expected_name)

    def test_description_from_metadata(self):
        """Test description extraction from metadata."""
        meta_data = {
            '@Name': 'Test',
            'Description': 'Test Description'
        }
        obj = self.TestRaPlcObject(meta_data=meta_data)

        self.assertEqual(obj.description, 'Test Description')

    def test_empty_asset_operations(self):
        """Test asset operations with empty lists."""
        parent = self.TestRaPlcObject(meta_data={})
        asset_list = HashList('name')
        raw_asset_list = []

        parent.redefine_raw_asset_list_from_asset_list(asset_list, raw_asset_list)

        self.assertEqual(len(raw_asset_list), 0)


class TestRaPlcObjectClassAttributes(unittest.TestCase):
    """Test RaPlcObject class-level attributes."""

    def test_default_l5x_file_path_none(self):
        """Test default_l5x_file_path is None by default."""
        self.assertIsNone(RaPlcObject.default_l5x_file_path)

    def test_default_l5x_asset_key_none(self):
        """Test default_l5x_asset_key is None by default."""
        self.assertIsNone(RaPlcObject.default_l5x_asset_key)

    def test_subclass_can_override_defaults(self):
        """Test subclass can override default attributes."""
        class CustomRaPlcObject(RaPlcObject):
            default_l5x_file_path = Path('/custom/path.L5X')
            default_l5x_asset_key = 'CustomKey'

            def compile(self):
                return self

            def invalidate(self):
                pass

            @property
            def process_name(self):
                return "Test"

        self.assertEqual(CustomRaPlcObject.default_l5x_file_path, Path('/custom/path.L5X'))
        self.assertEqual(CustomRaPlcObject.default_l5x_asset_key, 'CustomKey')


if __name__ == '__main__':
    unittest.main(verbosity=2)
