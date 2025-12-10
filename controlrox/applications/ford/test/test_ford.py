"""Comprehensive unit tests for ford.py module.

This test suite verifies that when a FordController is created, all of its 
subcomponents are properly instantiated as Ford-specific subclasses rather than 
generic Rockwell classes.
"""
import unittest
from unittest.mock import patch

from controlrox.applications.ford.ford import (
    FordController,
    FordProgram,
    FordRoutine,
    FordRung,
    FordTag,
    FordModule,
    FordDatatype,
    FordAddOnInstruction,
)
from controlrox.models.plc.rockwell import (
    RaController,
    RaProgram,
    RaRoutine,
    RaRung,
    RaTag,
    RaModule,
    RaDatatype,
    RaAddOnInstruction,
)


class TestFordClassInheritance(unittest.TestCase):
    """Test Ford classes properly inherit from Rockwell base classes."""

    def test_ford_controller_inherits_from_ra_controller(self):
        """Test FordController inherits from RaController."""
        self.assertTrue(issubclass(FordController, RaController))

    def test_ford_program_inherits_from_ra_program(self):
        """Test FordProgram inherits from RaProgram."""
        self.assertTrue(issubclass(FordProgram, RaProgram))

    def test_ford_routine_inherits_from_ra_routine(self):
        """Test FordRoutine inherits from RaRoutine."""
        self.assertTrue(issubclass(FordRoutine, RaRoutine))

    def test_ford_rung_inherits_from_ra_rung(self):
        """Test FordRung inherits from RaRung."""
        self.assertTrue(issubclass(FordRung, RaRung))

    def test_ford_tag_inherits_from_ra_tag(self):
        """Test FordTag inherits from RaTag."""
        self.assertTrue(issubclass(FordTag, RaTag))

    def test_ford_module_inherits_from_ra_module(self):
        """Test FordModule inherits from RaModule."""
        self.assertTrue(issubclass(FordModule, RaModule))

    def test_ford_datatype_inherits_from_ra_datatype(self):
        """Test FordDatatype inherits from RaDatatype."""
        self.assertTrue(issubclass(FordDatatype, RaDatatype))

    def test_ford_aoi_inherits_from_ra_aoi(self):
        """Test FordAddOnInstruction inherits from RaAddOnInstruction."""
        self.assertTrue(issubclass(FordAddOnInstruction, RaAddOnInstruction))


class TestFordControllerFromFile(unittest.TestCase):
    """Test FordController creation from file creates Ford-specific subcomponents."""

    def setUp(self):
        """Set up test fixtures with minimal L5X structure."""
        self.test_l5x_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {
                        'AddOnInstructionDefinition': []
                    },
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'CustomType1', '@Family': 'NoFamily'},
                            {'@Name': 'CustomType2', '@Family': 'NoFamily'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'LocalModule', '@CatalogNumber': '1769-L33ER'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MainProgram',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'MainRoutine',
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
                            {'@Name': 'ControllerTag1', '@TagType': 'Base', '@DataType': 'DINT'},
                        ]
                    },
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_ford_programs(self, mock_l5x_from_file):
        """Test from_file creates FordProgram instances, not RaProgram."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = FordController.from_file('test.L5X')

        self.assertGreater(len(controller.programs), 0)
        for program in controller.programs:
            self.assertIsInstance(program, FordProgram,
                                  f"Expected FordProgram but got {type(program).__name__}")
            self.assertNotEqual(type(program), RaProgram,
                                "Program should be FordProgram, not base RaProgram")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_ford_routines(self, mock_l5x_from_file, mock_get_controller):
        """Test from_file creates FordRoutine instances within programs."""
        mock_l5x_from_file.return_value = self.test_l5x_data
        mock_get_controller.return_value = FordController.from_file('test.L5X')

        controller = FordController.from_file('test.L5X')

        for program in controller.programs:
            self.assertGreater(len(program.routines), 0)
            for routine in program.routines:
                self.assertIsInstance(routine, FordRoutine,
                                      f"Expected FordRoutine but got {type(routine).__name__}")
                self.assertNotEqual(type(routine), RaRoutine,
                                    "Routine should be FordRoutine, not base RaRoutine")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_ford_rungs(self, mock_l5x_from_file, mock_get_controller):
        """Test from_file creates FordRung instances within routines."""
        mock_l5x_from_file.return_value = self.test_l5x_data
        mock_get_controller.return_value = FordController.from_file('test.L5X')

        controller = FordController.from_file('test.L5X')

        for program in controller.programs:
            for routine in program.routines:
                if hasattr(routine, 'rungs') and routine.rungs:
                    for rung in routine.rungs:
                        self.assertIsInstance(rung, FordRung,
                                              f"Expected FordRung but got {type(rung).__name__}")
                        self.assertNotEqual(type(rung), RaRung,
                                            "Rung should be FordRung, not base RaRung")

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_ford_tags(self, mock_l5x_from_file):
        """Test from_file creates FordTag instances for controller tags."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = FordController.from_file('test.L5X')

        self.assertGreater(len(controller.tags), 0)
        for tag in controller.tags:
            self.assertIsInstance(tag, FordTag,
                                  f"Expected FordTag but got {type(tag).__name__}")
            self.assertNotEqual(type(tag), RaTag,
                                "Tag should be FordTag, not base RaTag")

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_ford_modules(self, mock_l5x_from_file):
        """Test from_file creates FordModule instances."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = FordController.from_file('test.L5X')

        self.assertGreater(len(controller.modules), 0)
        for module in controller.modules:
            self.assertIsInstance(module, FordModule,
                                  f"Expected FordModule but got {type(module).__name__}")
            self.assertNotEqual(type(module), RaModule,
                                "Module should be FordModule, not base RaModule")

    @patch('controlrox.models.plc.rockwell.controller.l5x_dict_from_file')
    def test_from_file_creates_ford_datatypes(self, mock_l5x_from_file):
        """Test from_file creates FordDatatype instances."""
        mock_l5x_from_file.return_value = self.test_l5x_data

        controller = FordController.from_file('test.L5X')

        # Filter out built-in datatypes to check only custom ones
        custom_datatypes = [dt for dt in controller.datatypes
                            if dt.name in ['CustomType1', 'CustomType2']]

        self.assertGreater(len(custom_datatypes), 0)
        for datatype in custom_datatypes:
            self.assertIsInstance(datatype, FordDatatype,
                                  f"Expected FordDatatype but got {type(datatype).__name__}")
            self.assertNotEqual(type(datatype), RaDatatype,
                                "Datatype should be FordDatatype, not base RaDatatype")


class TestFordControllerFromMetaData(unittest.TestCase):
    """Test FordController creation from metadata creates Ford-specific subcomponents."""

    def setUp(self):
        """Set up test fixtures with minimal L5X structure."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'TestController',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {
                        'AddOnInstructionDefinition': [
                            {'@Name': 'CustomAOI', '@Revision': '1.0'}
                        ]
                    },
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'FordCustomType', '@Family': 'NoFamily'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'FordModule1', '@CatalogNumber': '1769-L33ER'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'FordProgram1',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'FordRoutine1',
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
                            {'@Name': 'FordTag1', '@TagType': 'Base', '@DataType': 'DINT'},
                            {'@Name': 'FordTag2', '@TagType': 'Base', '@DataType': 'BOOL'}
                        ]
                    },
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_ford_programs(self, mock_get_controller):
        """Test from_meta_data creates FordProgram instances."""
        mock_get_controller.return_value = FordController.from_meta_data(self.test_meta_data)
        controller = FordController.from_meta_data(self.test_meta_data)

        self.assertGreater(len(controller.programs), 0)
        for program in controller.programs:
            self.assertIsInstance(program, FordProgram,
                                  f"Expected FordProgram but got {type(program).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_ford_routines(self, mock_get_controller):
        """Test from_meta_data creates FordRoutine instances."""
        mock_get_controller.return_value = FordController.from_meta_data(self.test_meta_data)
        controller = FordController.from_meta_data(self.test_meta_data)

        for program in controller.programs:
            for routine in program.routines:
                self.assertIsInstance(routine, FordRoutine,
                                      f"Expected FordRoutine but got {type(routine).__name__}")

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_from_meta_data_creates_ford_rungs(self, mock_get_controller):
        """Test from_meta_data creates FordRung instances."""
        mock_get_controller.return_value = FordController.from_meta_data(self.test_meta_data)
        controller = FordController.from_meta_data(self.test_meta_data)

        for program in controller.programs:
            for routine in program.routines:
                if hasattr(routine, 'rungs'):
                    for rung in routine.rungs:
                        self.assertIsInstance(rung, FordRung,
                                              f"Expected FordRung but got {type(rung).__name__}")

    def test_from_meta_data_creates_ford_tags(self):
        """Test from_meta_data creates FordTag instances."""
        controller = FordController.from_meta_data(self.test_meta_data)

        self.assertGreater(len(controller.tags), 0)
        for tag in controller.tags:
            self.assertIsInstance(tag, FordTag,
                                  f"Expected FordTag but got {type(tag).__name__}")

    def test_from_meta_data_creates_ford_modules(self):
        """Test from_meta_data creates FordModule instances."""
        controller = FordController.from_meta_data(self.test_meta_data)

        self.assertGreater(len(controller.modules), 0)
        for module in controller.modules:
            self.assertIsInstance(module, FordModule,
                                  f"Expected FordModule but got {type(module).__name__}")

    def test_from_meta_data_creates_ford_datatypes(self):
        """Test from_meta_data creates FordDatatype instances."""
        controller = FordController.from_meta_data(self.test_meta_data)

        custom_datatypes = [dt for dt in controller.datatypes
                            if dt.name == 'FordCustomType']

        self.assertGreater(len(custom_datatypes), 0)
        for datatype in custom_datatypes:
            self.assertIsInstance(datatype, FordDatatype,
                                  f"Expected FordDatatype but got {type(datatype).__name__}")

    def test_from_meta_data_creates_ford_aois(self):
        """Test from_meta_data creates FordAddOnInstruction instances."""
        controller = FordController.from_meta_data(self.test_meta_data)

        self.assertGreater(len(controller.aois), 0)
        for aoi in controller.aois:
            self.assertIsInstance(aoi, FordAddOnInstruction,
                                  f"Expected FordAddOnInstruction but got {type(aoi).__name__}")


class TestFordControllerCompileMethods(unittest.TestCase):
    """Test FordController compile methods use Ford-specific types."""

    def setUp(self):
        """Set up minimal controller metadata."""
        self.minimal_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'MinimalController',
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

    def test_compile_programs_uses_ford_program_type(self):
        """Test compile_programs creates FordProgram instances."""
        test_data = self.minimal_meta_data.copy()
        test_data['RSLogix5000Content']['Controller']['Programs'] = {
            'Program': [
                {
                    '@Name': 'TestProgram',
                    '@Class': 'Standard',
                    'Tags': {'Tag': []},
                    'Routines': {'Routine': []}
                }
            ]
        }

        controller = FordController(meta_data=test_data)
        controller.compile_programs()

        self.assertEqual(len(controller.programs), 1)

        # Re-import because Factories use importlib.reload
        from controlrox.applications.ford.ford import FordProgram
        self.assertIsInstance(controller.programs[0], FordProgram)

    def test_compile_tags_uses_ford_tag_type(self):
        """Test compile_tags creates FordTag instances."""
        test_data = self.minimal_meta_data.copy()
        test_data['RSLogix5000Content']['Controller']['Tags'] = {
            'Tag': [
                {'@Name': 'TestTag', '@TagType': 'Base', '@DataType': 'DINT'}
            ]
        }

        controller = FordController(meta_data=test_data)
        controller.compile_tags()

        self.assertEqual(len(controller.tags), 1)
        from controlrox.applications.ford.ford import FordTag
        self.assertIsInstance(controller.tags[0], FordTag)

    def test_compile_modules_uses_ford_module_type(self):
        """Test compile_modules creates FordModule instances."""
        test_data = self.minimal_meta_data.copy()
        test_data['RSLogix5000Content']['Controller']['Modules'] = {
            'Module': [
                {'@Name': 'TestModule', '@CatalogNumber': '1769-L33ER'}
            ]
        }

        controller = FordController(meta_data=test_data)
        controller.compile_modules()

        self.assertEqual(len(controller.modules), 1)
        from controlrox.applications.ford.ford import FordModule
        self.assertIsInstance(controller.modules[0], FordModule)

    def test_compile_datatypes_uses_ford_datatype_type(self):
        """Test compile_datatypes creates FordDatatype instances."""
        test_data = self.minimal_meta_data.copy()
        test_data['RSLogix5000Content']['Controller']['DataTypes'] = {
            'DataType': [
                {'@Name': 'TestDatatype', '@Family': 'NoFamily'}
            ]
        }

        controller = FordController(meta_data=test_data)
        controller.compile_datatypes()

        custom_datatypes = [dt for dt in controller.datatypes
                            if dt.name == 'TestDatatype']
        self.assertEqual(len(custom_datatypes), 1)
        from controlrox.applications.ford.ford import FordDatatype
        self.assertIsInstance(custom_datatypes[0], FordDatatype)

    def test_compile_aois_uses_ford_aoi_type(self):
        """Test compile_aois creates FordAddOnInstruction instances."""
        test_data = self.minimal_meta_data.copy()
        test_data['RSLogix5000Content']['Controller']['AddOnInstructionDefinitions'] = {
            'AddOnInstructionDefinition': [
                {'@Name': 'TestAOI', '@Revision': '1.0'}
            ]
        }

        controller = FordController(meta_data=test_data)
        controller.compile_aois()

        self.assertEqual(len(controller.aois), 1)
        from controlrox.applications.ford.ford import FordAddOnInstruction
        self.assertIsInstance(controller.aois[0], FordAddOnInstruction)


class TestFordProgramCommEditRoutine(unittest.TestCase):
    """Test FordProgram comm_edit_routine property."""

    def setUp(self):
        """Set up test program with comm edit routine."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
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
                                '@Name': 'MainProgram',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'A_Comm_Edit',
                                            '@Type': 'RLL',
                                            'RLLContent': {'Rung': []}
                                        },
                                        {
                                            '@Name': 'MainRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {'Rung': []}
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
    def test_comm_edit_routine_returns_ford_routine(self, mock_get_controller):
        """Test comm_edit_routine property returns FordRoutine instance."""
        mock_get_controller.return_value = FordController.from_meta_data(self.test_meta_data)
        controller = FordController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]

        comm_edit = program.comm_edit_routine  # type: ignore

        self.assertIsNotNone(comm_edit)
        self.assertIsInstance(comm_edit, FordRoutine)
        self.assertEqual(comm_edit.name, 'A_Comm_Edit')  # type: ignore

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_comm_edit_routine_returns_none_when_not_present(self, mock_get_controller):
        """Test comm_edit_routine returns None when routine doesn't exist."""
        mock_get_controller.return_value = FordController.from_meta_data(self.test_meta_data)
        test_data = self.test_meta_data.copy()
        test_data['RSLogix5000Content']['Controller']['Programs']['Program'][0]['Routines'] = {
            'Routine': [
                {
                    '@Name': 'MainRoutine',
                    '@Type': 'RLL',
                    'RLLContent': {'Rung': []}
                }
            ]
        }

        controller = FordController.from_meta_data(test_data)
        program = controller.programs[0]

        comm_edit = program.comm_edit_routine

        self.assertIsNone(comm_edit)


class TestFordControllerGeneratorType(unittest.TestCase):
    """Test FordController generator_type attribute."""

    def test_generator_type_is_ford_emulation_generator(self):
        """Test generator_type is set to FordEmulationGenerator."""
        self.assertEqual(FordController.generator_type, 'FordEmulationGenerator')

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
        controller = FordController(meta_data=minimal_meta)
        self.assertEqual(controller.generator_type, 'FordEmulationGenerator')


class TestFordRoutineRungs(unittest.TestCase):
    """Test FordRoutine rungs property returns Ford-specific rungs."""

    def setUp(self):
        """Set up test data with multiple rungs."""
        self.test_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
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
                                '@Name': 'MainProgram',
                                '@Class': 'Standard',
                                'Tags': {'Tag': []},
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'TestRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {'@Number': '0', 'Text': 'NOP();'},
                                                    {'@Number': '1', 'Text': 'XIC(Bit1);'},
                                                    {'@Number': '2', 'Text': 'OTE(Bit2);'}
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
    def test_routine_rungs_returns_list_of_ford_rungs(self, mock_get_controller):
        """Test routine.rungs returns list of FordRung instances."""
        mock_get_controller.return_value = FordController.from_meta_data(self.test_meta_data)
        controller = FordController.from_meta_data(self.test_meta_data)
        program = controller.programs[0]
        routine = program.routines[0]  # type: ignore

        rungs = routine.rungs  # type: ignore

        self.assertIsInstance(rungs, list)
        self.assertEqual(len(rungs), 3)
        for rung in rungs:
            self.assertIsInstance(rung, FordRung,
                                  f"Expected FordRung but got {type(rung).__name__}")


class TestFordControllerIntegration(unittest.TestCase):
    """Integration tests verifying complete Ford controller hierarchy."""

    def setUp(self):
        """Set up comprehensive test data."""
        self.comprehensive_meta_data = {
            'RSLogix5000Content': {
                '@SchemaRevision': '1.0',
                '@SoftwareRevision': '32.00',
                'Controller': {
                    '@Name': 'FordIntegrationTest',
                    '@ProcessorType': 'CompactLogix',
                    '@MajorRev': '32',
                    '@MinorRev': '0',
                    'AddOnInstructionDefinitions': {
                        'AddOnInstructionDefinition': [
                            {'@Name': 'FordAOI1', '@Revision': '1.0'},
                            {'@Name': 'FordAOI2', '@Revision': '2.0'}
                        ]
                    },
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'FordType1', '@Family': 'NoFamily'},
                            {'@Name': 'FordType2', '@Family': 'NoFamily'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'FordModule1', '@CatalogNumber': '1769-L33ER'},
                            {'@Name': 'FordModule2', '@CatalogNumber': '1769-IQ16'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {
                                '@Name': 'MainProgram',
                                '@Class': 'Standard',
                                'Tags': {
                                    'Tag': [
                                        {'@Name': 'ProgTag1', '@TagType': 'Base', '@DataType': 'DINT'}
                                    ]
                                },
                                'Routines': {
                                    'Routine': [
                                        {
                                            '@Name': 'MainRoutine',
                                            '@Type': 'RLL',
                                            'RLLContent': {
                                                'Rung': [
                                                    {'@Number': '0', 'Text': 'XIC(InputBit);'},
                                                    {'@Number': '1', 'Text': 'OTE(OutputBit);'}
                                                ]
                                            }
                                        },
                                        {
                                            '@Name': 'A_Comm_Edit',
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
                            {'@Name': 'CtrlTag1', '@TagType': 'Base', '@DataType': 'DINT'},
                            {'@Name': 'CtrlTag2', '@TagType': 'Base', '@DataType': 'BOOL'}
                        ]
                    },
                    'SafetyInfo': None
                }
            }
        }

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_complete_hierarchy_uses_ford_classes(self, mock_get_controller):
        """Test entire controller hierarchy uses Ford-specific classes."""
        mock_get_controller.return_value = FordController.from_meta_data(self.comprehensive_meta_data)
        controller = FordController.from_meta_data(self.comprehensive_meta_data)

        # Verify controller
        self.assertIsInstance(controller, FordController)

        # Verify all programs are Ford programs
        for program in controller.programs:
            self.assertIsInstance(program, FordProgram)

            # Verify all routines are Ford routines
            for routine in program.routines:
                self.assertIsInstance(routine, FordRoutine)

                # Verify all rungs are Ford rungs
                if hasattr(routine, 'rungs'):
                    for rung in routine.rungs:
                        self.assertIsInstance(rung, FordRung)

            # Verify program tags are Ford tags
            if hasattr(program, 'tags'):
                for tag in program.tags:
                    self.assertIsInstance(tag, FordTag)

        # Verify controller tags are Ford tags
        for tag in controller.tags:
            self.assertIsInstance(tag, FordTag)

        # Verify modules are Ford modules
        for module in controller.modules:
            self.assertIsInstance(module, FordModule)

        # Verify custom datatypes are Ford datatypes
        custom_types = [dt for dt in controller.datatypes
                        if dt.name in ['FordType1', 'FordType2']]
        for datatype in custom_types:
            self.assertIsInstance(datatype, FordDatatype)

        # Verify AOIs are Ford AOIs
        for aoi in controller.aois:
            self.assertIsInstance(aoi, FordAddOnInstruction)

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_no_base_rockwell_classes_in_hierarchy(self, mock_get_controller):
        """Test hierarchy contains no base Rockwell classes, only Ford subclasses."""
        mock_get_controller.return_value = FordController.from_meta_data(self.comprehensive_meta_data)
        controller = FordController.from_meta_data(self.comprehensive_meta_data)

        # Check programs are not base RaProgram
        for program in controller.programs:
            self.assertNotEqual(type(program), RaProgram,
                                "Found base RaProgram instead of FordProgram")

        # Check routines are not base RaRoutine
        for program in controller.programs:
            for routine in program.routines:
                self.assertNotEqual(type(routine), RaRoutine,
                                    "Found base RaRoutine instead of FordRoutine")

        # Check rungs are not base RaRung
        for program in controller.programs:
            for routine in program.routines:
                if hasattr(routine, 'rungs'):
                    for rung in routine.rungs:
                        self.assertNotEqual(type(rung), RaRung,
                                            "Found base RaRung instead of FordRung")

        # Check tags are not base RaTag
        for tag in controller.tags:
            self.assertNotEqual(type(tag), RaTag,
                                "Found base RaTag instead of FordTag")

        # Check modules are not base RaModule
        for module in controller.modules:
            self.assertNotEqual(type(module), RaModule,
                                "Found base RaModule instead of FordModule")


if __name__ == '__main__':
    unittest.main(verbosity=2)
