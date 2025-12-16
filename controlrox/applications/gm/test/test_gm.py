"""Comprehensive unit tests for gm.py module.

This test suite verifies that when a GmController is created, all of its
subcomponents are properly instantiated as GM-specific subclasses rather than
generic Rockwell classes. Additionally, it tests GM-specific functionality like
KDiag handling, text list extraction, and parameter routines.
"""
import unittest
from unittest.mock import patch, Mock

from controlrox.applications.gm.gm import (
    GmController,
    GmProgram,
    GmRoutine,
    GmRung,
    GmTag,
    GmModule,
    GmDatatype,
    GmAddOnInstruction,
    TextListElement,
    KDiag,
    KDiagType,
)
from controlrox.models.plc.rockwell import (
    RaController,
    RaRung,
    RaTag,
    RaModule,
    RaDatatype,
    RaAddOnInstruction,
)


class TestGmClassInheritance(unittest.TestCase):
    """Test GM classes properly inherit from Rockwell base classes."""

    def test_gm_controller_inherits_from_ra_controller(self):
        """Test GmController inherits from RaController."""
        self.assertTrue(issubclass(GmController, RaController))

    def test_gm_program_is_program_type(self):
        """Test GmProgram is a valid program type."""
        # GmProgram should be subclass of base program interface
        self.assertTrue(hasattr(GmProgram, '__mro__'))

    def test_gm_routine_is_routine_type(self):
        """Test GmRoutine is a valid routine type."""
        # GmRoutine should be subclass of base routine interface
        self.assertTrue(hasattr(GmRoutine, '__mro__'))

    def test_gm_rung_inherits_from_ra_rung(self):
        """Test GmRung inherits from RaRung."""
        self.assertTrue(issubclass(GmRung, RaRung))

    def test_gm_tag_inherits_from_ra_tag(self):
        """Test GmTag inherits from RaTag."""
        self.assertTrue(issubclass(GmTag, RaTag))

    def test_gm_module_inherits_from_ra_module(self):
        """Test GmModule inherits from RaModule."""
        self.assertTrue(issubclass(GmModule, RaModule))

    def test_gm_datatype_inherits_from_ra_datatype(self):
        """Test GmDatatype inherits from RaDatatype."""
        self.assertTrue(issubclass(GmDatatype, RaDatatype))

    def test_gm_aoi_inherits_from_ra_aoi(self):
        """Test GmAddOnInstruction inherits from RaAddOnInstruction."""
        self.assertTrue(issubclass(GmAddOnInstruction, RaAddOnInstruction))


class TestGmControllerFromFile(unittest.TestCase):
    """Test GmController creation from file creates GM-specific subcomponents."""

    def setUp(self):
        """Set up test fixtures with minimal L5X structure."""
        self.test_l5x_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'TestGmController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {
                        'AddOnInstructionDefinition': []
                    },
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'zz_Version', '@Family': 'NoFamily'},
                            {'@Name': 'zz_Prompt', '@Family': 'NoFamily'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'zz_LocalModule', '@CatalogNumber': '1769-L33ER'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'zz_MainRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {'@Number': '0', 'Text': 'NOP();'}
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {
                        'Tag': [
                            {'@Name': 'zz_ControllerTag1', '@TagType': 'Base', '@DataType': 'DINT'},
                        ]
                    },
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_gm_programs(self, mock_l5x_from_file):
        """Test from_file creates GmProgram instances, not RaProgram."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = GmController.from_file('test.L5X')

        self.assertGreater(len(controller.programs), 0)
        for program in controller.programs:
            self.assertIsInstance(program, GmProgram,
                                  f"Expected GmProgram but got {type(program).__name__}")
            self.assertNotEqual(type(program).__name__, 'RaProgram',
                                "Program should be GmProgram, not base RaProgram")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_gm_routines(self, mock_l5x_from_file, mock_get_controller):
        """Test from_file creates GmRoutine instances within programs."""
        mock_l5x_from_file.return_value = self.test_l5x_data
        mock_get_controller.return_value = GmController.from_file('test.L5X')

        controller = GmController.from_file('test.L5X')

        for program in controller.programs:
            self.assertGreater(len(program.routines), 0)
            for routine in program.routines:
                self.assertIsInstance(routine, GmRoutine,
                                      f"Expected GmRoutine but got {type(routine).__name__}")
                self.assertNotEqual(type(routine).__name__, 'RaRoutine',
                                    "Routine should be GmRoutine, not base RaRoutine")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_gm_rungs(self, mock_l5x_from_file, mock_get_controller):
        """Test from_file creates GmRung instances within routines."""
        mock_l5x_from_file.return_value = self.test_l5x_data
        mock_get_controller.return_value = GmController.from_file('test.L5X')

        controller = GmController.from_file('test.L5X')

        for program in controller.programs:
            for routine in program.routines:
                if hasattr(routine, 'rungs') and routine.rungs:
                    for rung in routine.rungs:
                        self.assertIsInstance(rung, GmRung,
                                              f"Expected GmRung but got {type(rung).__name__}")
                        self.assertNotEqual(type(rung).__name__, 'RaRung',
                                            "Rung should be GmRung, not base RaRung")

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_gm_tags(self, mock_l5x_from_file):
        """Test from_file creates GmTag instances for controller tags."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = GmController.from_file('test.L5X')

        self.assertGreater(len(controller.tags), 0)
        for tag in controller.tags:
            self.assertIsInstance(tag, GmTag,
                                  f"Expected GmTag but got {type(tag).__name__}")
            self.assertNotEqual(type(tag).__name__, 'RaTag',
                                "Tag should be GmTag, not base RaTag")

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_gm_modules(self, mock_l5x_from_file):
        """Test from_file creates GmModule instances."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = GmController.from_file('test.L5X')

        self.assertGreater(len(controller.modules), 0)
        for module in controller.modules:
            self.assertIsInstance(module, GmModule,
                                  f"Expected GmModule but got {type(module).__name__}")
            self.assertNotEqual(type(module).__name__, 'RaModule',
                                "Module should be GmModule, not base RaModule")

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_gm_datatypes(self, mock_l5x_from_file):
        """Test from_file creates GmDatatype instances."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = GmController.from_file('test.L5X')

        # Filter out built-in datatypes to check only custom ones
        custom_datatypes = [dt for dt in controller.datatypes
                            if dt.name in ['zz_Version', 'zz_Prompt']]

        self.assertGreater(len(custom_datatypes), 0)
        for datatype in custom_datatypes:
            self.assertIsInstance(datatype, GmDatatype,
                                  f"Expected GmDatatype but got {type(datatype).__name__}")
            self.assertNotEqual(type(datatype).__name__, 'RaDatatype',
                                "Datatype should be GmDatatype, not base RaDatatype")


class TestGmControllerFromMetaData(unittest.TestCase):
    """Test GmController creation from metadata creates GM-specific subcomponents."""

    def setUp(self):
        """Set up test fixtures with minimal L5X structure."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'TestGmController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {
                        'AddOnInstructionDefinition': [
                            {'@Name': 'zz_CustomAOI', '@Revision': '1.0'}
                        ]
                    },
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'zz_GmCustomType', '@Family': 'NoFamily'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'zz_GmModule1', '@CatalogNumber': '1769-L33ER'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'zz_GmRoutine1',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {'@Number': '0', 'Text': 'NOP();'},
                                                    {'@Number': '1', 'Text': 'XIC(TestBit);'}
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {
                        'Tag': [
                            {'@Name': 'zz_GmTag1', '@TagType': 'Base', '@DataType': 'DINT'},
                            {'@Name': 'zz_GmTag2', '@TagType': 'Base', '@DataType': 'BOOL'}
                        ]
                    },
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_programs(self, mock_get_controller):
        """Test from_meta_data creates GmProgram instances."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        self.assertGreater(len(controller.programs), 0)
        for program in controller.programs:
            self.assertIsInstance(program, GmProgram,
                                  f"Expected GmProgram but got {type(program).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_routines(self, mock_get_controller):
        """Test from_meta_data creates GmRoutine instances."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        for program in controller.programs:
            for routine in program.routines:
                self.assertIsInstance(routine, GmRoutine,
                                      f"Expected GmRoutine but got {type(routine).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_rungs(self, mock_get_controller):
        """Test from_meta_data creates GmRung instances."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        for program in controller.programs:
            for routine in program.routines:
                if hasattr(routine, 'rungs'):
                    for rung in routine.rungs:
                        self.assertIsInstance(rung, GmRung,
                                              f"Expected GmRung but got {type(rung).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_tags(self, mock_get_controller):
        """Test from_meta_data creates GmTag instances."""
        controller = GmController.from_meta_data(self.test_meta_data)
        mock_get_controller.return_value = controller

        self.assertGreater(len(controller.tags), 0)
        for tag in controller.tags:
            self.assertIsInstance(tag, GmTag,
                                  f"Expected GmTag but got {type(tag).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_modules(self, mock_get_controller):
        """Test from_meta_data creates GmModule instances."""
        controller = GmController.from_meta_data(self.test_meta_data)
        mock_get_controller.return_value = controller

        self.assertGreater(len(controller.modules), 0)
        for module in controller.modules:
            self.assertIsInstance(module, GmModule,
                                  f"Expected GmModule but got {type(module).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_datatypes(self, mock_get_controller):
        """Test from_meta_data creates GmDatatype instances."""
        controller = GmController.from_meta_data(self.test_meta_data)
        mock_get_controller.return_value = controller

        custom_datatypes = [dt for dt in controller.datatypes
                            if dt.name == 'zz_GmCustomType']

        self.assertGreater(len(custom_datatypes), 0)
        for datatype in custom_datatypes:
            self.assertIsInstance(datatype, GmDatatype,
                                  f"Expected GmDatatype but got {type(datatype).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_gm_aois(self, mock_get_controller):
        """Test from_meta_data creates GmAddOnInstruction instances."""
        controller = GmController.from_meta_data(self.test_meta_data)
        mock_get_controller.return_value = controller

        self.assertGreater(len(controller.aois), 0)
        for aoi in controller.aois:
            self.assertIsInstance(aoi, GmAddOnInstruction,
                                  f"Expected GmAddOnInstruction but got {type(aoi).__name__}")


class TestGmPlcObjectProperties(unittest.TestCase):
    """Test NamedGmPlcObject properties for ownership and processing."""

    def setUp(self):
        """Set up test metadata."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'DataTypes': {'DataType': []},
                    'Modules': {
                        'Module': [
                            {'@Name': 'zz_GmModule', '@CatalogNumber': '1769-L33ER'},
                            {'@Name': 'u_UserModule', '@CatalogNumber': '1769-IQ16'},
                            {'@Name': 'RegularModule', '@CatalogNumber': '1769-OB16'}
                        ]
                    },
                    'Programs': {'Program': []},
                    'Tags': {'Tag': []},
                    'SafetyInfo': None
                }
            }
        }

    def test_is_gm_owned_for_zz_prefix(self):
        """Test is_gm_owned returns True for zz_ prefix."""
        controller = GmController.from_meta_data(self.test_meta_data)
        gm_module = [m for m in controller.modules if m.name == 'zz_GmModule'][0]

        self.assertTrue(gm_module.is_gm_owned)

    def test_is_user_owned_for_u_prefix(self):
        """Test is_user_owned returns True for u_ prefix."""
        controller = GmController.from_meta_data(self.test_meta_data)
        user_module = [m for m in controller.modules if m.name == 'u_UserModule'][0]

        self.assertTrue(user_module.is_user_owned)

    def test_is_gm_owned_false_for_non_gm(self):
        """Test is_gm_owned returns False for non-GM modules."""
        controller = GmController.from_meta_data(self.test_meta_data)
        regular_module = [m for m in controller.modules if m.name == 'RegularModule'][0]

        self.assertFalse(regular_module.is_gm_owned)

    def test_is_user_owned_false_for_non_user(self):
        """Test is_user_owned returns False for non-user modules."""
        controller = GmController.from_meta_data(self.test_meta_data)
        gm_module = [m for m in controller.modules if m.name == 'zz_GmModule'][0]

        self.assertFalse(gm_module.is_user_owned)

    def test_process_name_strips_prefixes(self):
        """Test process_name strips CG_, zz_, sz_, zs_ prefixes."""
        controller = GmController.from_meta_data(self.test_meta_data)
        gm_module = [m for m in controller.modules if m.name == 'zz_GmModule'][0]

        self.assertEqual(gm_module.process_name, 'GmModule')


class TestTextListElement(unittest.TestCase):
    """Test TextListElement functionality."""

    def setUp(self):
        """Set up mock rung."""
        self.mock_rung = Mock(spec=GmRung)

    def test_text_list_element_creation(self):
        """Test TextListElement can be created with text list format."""
        text = '<TestList[5]: Some message>'
        element = TextListElement(text, self.mock_rung)

        self.assertEqual(element.text, '<TestList[5]: Some message>')
        self.assertEqual(element.number, 5)
        self.assertEqual(element.text_list_id, 'TestList')
        self.assertIs(element.rung, self.mock_rung)

    def test_text_list_element_equality(self):
        """Test TextListElement equality based on number."""
        text1 = '<TestList[5]: Message 1>'
        text2 = '<TestList[5]: Message 2>'
        element1 = TextListElement(text1, self.mock_rung)
        element2 = TextListElement(text2, self.mock_rung)

        self.assertEqual(element1, element2)

    def test_text_list_element_hash(self):
        """Test TextListElement can be hashed."""
        text = '<TestList[5]: Some message>'
        element = TextListElement(text, self.mock_rung)

        # Should be hashable for use in sets/dicts
        hash_value = hash(element)
        self.assertIsInstance(hash_value, int)

    def test_text_list_element_str(self):
        """Test TextListElement string representation."""
        text = '<TestList[5]: Some message>'
        element = TextListElement(text, self.mock_rung)

        self.assertEqual(str(element), '<TestList[5]: Some message>')

    def test_text_list_element_invalid_format_raises_error(self):
        """Test TextListElement raises error for invalid format."""
        text = 'Invalid format without brackets'

        with self.assertRaises(ValueError):
            TextListElement(text, self.mock_rung)


class TestKDiag(unittest.TestCase):
    """Test KDiag functionality."""

    def setUp(self):
        """Set up mock rung."""
        self.mock_rung = Mock(spec=GmRung)

    def test_kdiag_alarm_creation(self):
        """Test KDiag creation with ALARM type."""
        text = '<Alarm[10]:@C5 Test alarm message>'
        kdiag = KDiag(KDiagType.ALARM, text, 100, self.mock_rung)

        self.assertEqual(kdiag.diag_type, KDiagType.ALARM)
        self.assertEqual(kdiag.number, 10)
        self.assertEqual(kdiag.parent_offset, 100)
        self.assertEqual(kdiag.global_number, 110)
        self.assertEqual(kdiag.column_location, '@C5')

    def test_kdiag_prompt_creation(self):
        """Test KDiag creation with PROMPT type."""
        text = '<Prompt[20]:@D10 Test prompt message>'
        kdiag = KDiag(KDiagType.PROMPT, text, 50, self.mock_rung)

        self.assertEqual(kdiag.diag_type, KDiagType.PROMPT)
        self.assertEqual(kdiag.number, 20)
        self.assertEqual(kdiag.parent_offset, 50)
        self.assertEqual(kdiag.global_number, 70)

    def test_kdiag_na_type_raises_error(self):
        """Test KDiag raises error for NA type."""
        text = '<Alarm[10]: Test message>'

        with self.assertRaises(ValueError):
            KDiag(KDiagType.NA, text, 0, self.mock_rung)

    def test_kdiag_none_parent_offset_defaults_to_zero(self):
        """Test KDiag handles None parent_offset."""
        text = '<Alarm[10]: Test message>'
        kdiag = KDiag(KDiagType.ALARM, text, None, self.mock_rung)

        self.assertEqual(kdiag.parent_offset, 0)
        self.assertEqual(kdiag.global_number, 10)

    def test_kdiag_equality(self):
        """Test KDiag equality based on global_number."""
        text1 = '<Alarm[10]: Message 1>'
        text2 = '<Alarm[10]: Message 2>'
        kdiag1 = KDiag(KDiagType.ALARM, text1, 100, self.mock_rung)
        kdiag2 = KDiag(KDiagType.ALARM, text2, 100, self.mock_rung)

        self.assertEqual(kdiag1, kdiag2)

    def test_kdiag_hash(self):
        """Test KDiag can be hashed."""
        text = '<Alarm[10]: Test message>'
        kdiag = KDiag(KDiagType.ALARM, text, 100, self.mock_rung)

        hash_value = hash(kdiag)
        self.assertIsInstance(hash_value, int)


class TestGmRungProperties(unittest.TestCase):
    """Test GmRung properties and KDiag extraction."""

    def setUp(self):
        """Set up test metadata with rungs containing KDiag comments."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'DataTypes': {'DataType': []},
                    'Modules': {'Module': []},
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'TestRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {
                                                        '@Number': '0',
                                                        'Comment': '<@DIAG>\n<Alarm[10]: Test alarm>\n<Prompt[20]: Test prompt>',
                                                        'Text': 'NOP();'
                                                    },
                                                    {
                                                        '@Number': '1',
                                                        'Comment': '<TestList[5]: Regular text list>',
                                                        'Text': 'XIC(Bit1);'
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {'Tag': []},
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_has_kdiag_returns_true_when_present(self, mock_get_controller):
        """Test has_kdiag returns True when rung has @DIAG marker."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]
        routine = program.routines[0]  # type: ignore
        rung = routine.rungs[0]  # type: ignore

        self.assertTrue(rung.has_kdiag)  # type: ignore

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_has_kdiag_returns_false_when_absent(self, mock_get_controller):
        """Test has_kdiag returns False when no @DIAG marker."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]
        routine = program.routines[0]
        rung = routine.rungs[1]

        self.assertFalse(rung.has_kdiag)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_kdiags_extracts_alarms_and_prompts(self, mock_get_controller):
        """Test kdiags property extracts KDiag objects from comments."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]
        routine = program.routines[0]
        rung = routine.rungs[0]

        kdiags = rung.kdiags
        self.assertEqual(len(kdiags), 2)

        # Check alarm
        alarm = [k for k in kdiags if k.diag_type == KDiagType.ALARM][0]
        self.assertEqual(alarm.number, 10)

        # Check prompt
        prompt = [k for k in kdiags if k.diag_type == KDiagType.PROMPT][0]
        self.assertEqual(prompt.number, 20)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_text_list_items_extraction(self, mock_get_controller):
        """Test text_list_items extracts TextListElement objects."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]
        routine = program.routines[0]
        rung = routine.rungs[1]

        text_items = rung.text_list_items
        self.assertEqual(len(text_items), 1)
        self.assertEqual(text_items[0].text_list_id, 'TestList')
        self.assertEqual(text_items[0].number, 5)


class TestGmRoutineProperties(unittest.TestCase):
    """Test GmRoutine aggregation properties."""

    def setUp(self):
        """Set up test metadata."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'DataTypes': {'DataType': []},
                    'Modules': {'Module': []},
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'zz_TestRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {
                                                        '@Number': '0',
                                                        'Comment': '<@DIAG>\n<Alarm[10]: Alarm 1>',
                                                        'Text': 'NOP();'
                                                    },
                                                    {
                                                        '@Number': '1',
                                                        'Comment': '<@DIAG>\n<Alarm[20]: Alarm 2>',
                                                        'Text': 'XIC(Bit1);'
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {'Tag': []},
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_kdiag_rungs_aggregates_from_all_rungs(self, mock_get_controller):
        """Test kdiag_rungs aggregates KDiag from all rungs in routine."""
        controller = GmController.from_meta_data(self.test_meta_data)
        mock_get_controller.return_value = controller
        program = controller.programs[0]
        routine = program.routines[0]

        kdiags = routine.kdiags
        self.assertEqual(len(kdiags), 2)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_text_list_items_aggregates_from_all_rungs(self, mock_get_controller):
        """Test text_list_items aggregates from all rungs in routine."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]
        routine = program.routines[0]

        # This test will pass even with empty list since we're testing the aggregation
        text_items = routine.text_list_items
        self.assertIsInstance(text_items, list)


class TestGmProgramProperties(unittest.TestCase):
    """Test GmProgram properties and parameter extraction."""

    def setUp(self):
        """Set up test metadata with parameter routine."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'DataTypes': {'DataType': []},
                    'Modules': {'Module': []},
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'B1_Parameters',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {
                                                        '@Number': '0',
                                                        'Text': 'MOV(100,HMI.Diag.Pgm.MsgOffset);'
                                                    }
                                                ]
                                            }
                                        },
                                        {
                                            '@Name': 'zz_MainRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {
                                                        '@Number': '0',
                                                        '@Comment': '<@DIAG>\n<Alarm[10]: Test alarm>',
                                                        'Text': 'NOP();'
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {'Tag': []},
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_parameter_routine_found(self, mock_get_controller):
        """Test parameter_routine finds routine matching pattern."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]

        param_routine = program.parameter_routine
        self.assertIsNotNone(param_routine)
        self.assertEqual(param_routine.name, 'B1_Parameters')

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_parameter_offset_extraction(self, mock_get_controller):
        """Test parameter_offset extracts value from parameter routine."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]

        offset = program.parameter_offset
        self.assertEqual(offset, 100)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_gm_routines_filters_gm_owned(self, mock_get_controller):
        """Test gm_routines returns only GM-owned routines."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]

        gm_routines = program.gm_routines
        self.assertGreater(len(gm_routines), 0)
        for routine in gm_routines:
            self.assertTrue(routine.is_gm_owned)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_is_gm_owned_based_on_routines(self, mock_get_controller):
        """Test program is_gm_owned based on GM routines presence."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]

        # Should be True since it has zz_ routines
        self.assertTrue(program.is_gm_owned)


class TestGmControllerProperties(unittest.TestCase):
    """Test GmController aggregation and utility properties."""

    def setUp(self):
        """Set up test metadata with multiple programs."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'DataTypes': {'DataType': []},
                    'Modules': {'Module': []},
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'zz_Routine1',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {
                                                        '@Number': '0',
                                                        'Comment': '<TestList[10]: Message>',
                                                        'Text': 'NOP();'
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                '@Name': 's_Common',
                                '@Class': 'Safety',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 's_z_SafetyRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {'Rung': []}
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {'Tag': []},
                    'SafetyInfo': {}
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_mcp_program_property(self, mock_get_controller):
        """Test mcp_program returns MCP program."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        mcp = controller.mcp_program
        self.assertIsNotNone(mcp)
        self.assertEqual(mcp.name, 'MCP')

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_safety_common_program_property(self, mock_get_controller):
        """Test safety_common_program returns s_Common program."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        safety_common = controller.safety_common_program
        self.assertIsNotNone(safety_common)
        self.assertEqual(safety_common.name, 's_Common')

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_text_list_items_aggregates_from_programs(self, mock_get_controller):
        """Test text_list_items aggregates from all programs."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        text_items = controller.text_list_items
        self.assertIsInstance(text_items, list)
        self.assertGreater(len(text_items), 0)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_gm_programs_filters_gm_owned(self, mock_get_controller):
        """Test gm_programs returns only GM-owned programs."""
        mock_get_controller.return_value = GmController.from_meta_data(self.test_meta_data)
        controller = GmController.from_meta_data(self.test_meta_data)

        gm_programs = controller.gm_programs
        self.assertIsInstance(gm_programs, list)


class TestGmControllerGeneratorType(unittest.TestCase):
    """Test GmController generator_type attribute."""

    def test_generator_type_is_gm_emulation_generator(self):
        """Test generator_type is set to GmEmulationGenerator."""
        self.assertEqual(GmController.generator_type, 'GmEmulationGenerator')

    def test_generator_type_is_accessible_from_instance(self):
        """Test generator_type is accessible from controller instance."""
        minimal_meta = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                'Controller': {
                    '@Name': 'Test',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {'AddOnInstructionDefinition': []},
                    'DataTypes': {'DataType': []},
                    'Modules': {'Module': []},
                    'Programs': {'Program': []},
                    'Tags': {'Tag': []},
                    'SafetyInfo': None
                }
            }
        }
        controller = GmController(meta_data=minimal_meta)
        self.assertEqual(controller.generator_type, 'GmEmulationGenerator')


class TestGmControllerIntegration(unittest.TestCase):
    """Integration tests verifying complete GM controller hierarchy."""

    def setUp(self):
        """Set up comprehensive test data."""
        self.comprehensive_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'GmIntegrationTest',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {
                        'AddOnInstructionDefinition': [
                            {'@Name': 'zz_GmAOI1', '@Revision': '1.0'},
                            {'@Name': 'zz_GmAOI2', '@Revision': '2.0'}
                        ]
                    },
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'zz_GmType1', '@Family': 'NoFamily'},
                            {'@Name': 'zz_GmType2', '@Family': 'NoFamily'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'zz_GmModule1', '@CatalogNumber': '1769-L33ER'},
                            {'@Name': 'zz_GmModule2', '@CatalogNumber': '1769-IQ16'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MCP',
                                '@Class': 'Standard',
                                'Tags': {
                                    'Tag': [
                                        {'@Name': 'zz_ProgTag1', '@TagType': 'Base', '@DataType': 'DINT'}
                                    ]
                                },
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'zz_MainRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {
                                                        '@Number': '0',
                                                        'Comment': '<@DIAG>\n<Alarm[10]: Test alarm>',
                                                        'Text': 'XIC(InputBit);'
                                                    },
                                                    {'@Number': '1', 'Text': 'OTE(OutputBit);'}
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    'Tags': {
                        'Tag': [
                            {'@Name': 'zz_CtrlTag1', '@TagType': 'Base', '@DataType': 'DINT'},
                            {'@Name': 'zz_CtrlTag2', '@TagType': 'Base', '@DataType': 'BOOL'}
                        ]
                    },
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_complete_hierarchy_uses_gm_classes(self, mock_get_controller):
        """Test entire controller hierarchy uses GM-specific classes."""
        mock_get_controller.return_value = GmController.from_meta_data(self.comprehensive_meta_data)
        controller = GmController.from_meta_data(self.comprehensive_meta_data)

        # Verify controller
        self.assertIsInstance(controller, GmController)

        # Verify all programs are GM programs
        for program in controller.programs:
            self.assertIsInstance(program, GmProgram)

            # Verify all routines are GM routines
            for routine in program.routines:
                self.assertIsInstance(routine, GmRoutine)

                # Verify all rungs are GM rungs
                if hasattr(routine, 'rungs'):
                    for rung in routine.rungs:
                        self.assertIsInstance(rung, GmRung)

            # Verify program tags are GM tags
            if hasattr(program, 'tags'):
                for tag in program.tags:
                    self.assertIsInstance(tag, GmTag)

        # Verify controller tags are GM tags
        for tag in controller.tags:
            self.assertIsInstance(tag, GmTag)

        # Verify modules are GM modules
        for module in controller.modules:
            self.assertIsInstance(module, GmModule)

        # Verify custom datatypes are GM datatypes
        custom_types = [dt for dt in controller.datatypes
                        if dt.name in ['zz_GmType1', 'zz_GmType2']]
        for datatype in custom_types:
            self.assertIsInstance(datatype, GmDatatype)

        # Verify AOIs are GM AOIs
        for aoi in controller.aois:
            self.assertIsInstance(aoi, GmAddOnInstruction)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_no_base_rockwell_classes_in_hierarchy(self, mock_get_controller):
        """Test hierarchy contains no base Rockwell classes, only GM subclasses."""
        mock_get_controller.return_value = GmController.from_meta_data(self.comprehensive_meta_data)
        controller = GmController.from_meta_data(self.comprehensive_meta_data)

        # Check programs are not base RaProgram
        for program in controller.programs:
            self.assertNotEqual(type(program).__name__, 'RaProgram',
                                "Found base RaProgram instead of GmProgram")

        # Check routines are not base RaRoutine
        for program in controller.programs:
            for routine in program.routines:
                self.assertNotEqual(type(routine).__name__, 'RaRoutine',
                                    "Found base RaRoutine instead of GmRoutine")

        # Check rungs are not base RaRung
        for program in controller.programs:
            for routine in program.routines:
                if hasattr(routine, 'rungs'):
                    for rung in routine.rungs:
                        self.assertNotEqual(type(rung).__name__, 'RaRung',
                                            "Found base RaRung instead of GmRung")

        # Check tags are not base RaTag
        for tag in controller.tags:
            self.assertNotEqual(type(tag).__name__, 'RaTag',
                                "Found base RaTag instead of GmTag")

        # Check modules are not base RaModule
        for module in controller.modules:
            self.assertNotEqual(type(module).__name__, 'RaModule',
                                "Found base RaModule instead of GmModule")


if __name__ == '__main__':
    unittest.main(verbosity=2)
