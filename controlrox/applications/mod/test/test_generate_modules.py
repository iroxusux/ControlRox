"""Comprehensive unit tests for the module generator.

Tests the ModuleGenerator class and its ability to generate Python classes
from JSON configuration files.
"""
from controlrox.applications.mod.generate_modules import ModuleGenerator
import unittest
import json
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModuleGeneratorInit(unittest.TestCase):
    """Test ModuleGenerator initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_init_creates_output_directory(self):
        """Test that __init__ creates the output directory."""
        _ = ModuleGenerator(str(self.config_dir), str(self.output_dir))

        self.assertTrue(self.output_dir.exists())
        self.assertTrue(self.output_dir.is_dir())

    def test_init_stores_directories(self):
        """Test that __init__ stores directory paths correctly."""
        generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

        self.assertEqual(generator.config_dir, self.config_dir)
        self.assertEqual(generator.output_dir, self.output_dir)

    def test_init_with_existing_output_directory(self):
        """Test initialization when output directory already exists."""
        self.output_dir.mkdir()
        _ = ModuleGenerator(str(self.config_dir), str(self.output_dir))

        # Should not raise an error
        self.assertTrue(self.output_dir.exists())


class TestModuleGeneratorGenerateTemplateCode(unittest.TestCase):
    """Test the _generate_template_code method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_generate_template_code_module_name(self):
        """Test template code generation with {module.name}."""
        template = "COP({module.name}:I,Tag,1);"
        result = self.generator._generate_template_code(template)

        self.assertEqual(result, "f'COP({self.base_module.name}:I,Tag,1);'")

    def test_generate_template_code_parent_module(self):
        """Test template code generation with {module.parent_module}."""
        template = "MOV({module.parent_module},Dest);"
        result = self.generator._generate_template_code(template)

        self.assertEqual(result, "f'MOV({self.base_module.parent_module},Dest);'")

    def test_generate_template_code_controller_process_name(self):
        """Test template code generation with {controller.process_name}."""
        template = "Tag_{controller.process_name}_Value"
        result = self.generator._generate_template_code(template)

        self.assertEqual(result, "f'Tag_{self.controller.process_name}_Value'")

    def test_generate_template_code_multiple_placeholders(self):
        """Test template code generation with multiple placeholders."""
        template = "COP({module.name},{module.parent_module},{controller.process_name});"
        result = self.generator._generate_template_code(template)

        expected = "f'COP({self.base_module.name},{self.base_module.parent_module},{self.controller.process_name});'"
        self.assertEqual(result, expected)

    def test_generate_template_code_no_placeholders(self):
        """Test template code generation with no placeholders."""
        template = "Simple text without placeholders"
        result = self.generator._generate_template_code(template)

        self.assertEqual(result, "f'Simple text without placeholders'")


class TestModuleGeneratorGenerateClassCode(unittest.TestCase):
    """Test the _generate_class_code method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_generate_class_code_minimal_config(self):
        """Test code generation with minimal configuration."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET'
        }

        code = self.generator._generate_class_code(config)

        # Check basic structure
        self.assertIn('class TestModule(GeneratedModule):', code)
        self.assertIn("return '1234-TEST'", code)
        self.assertIn('ModuleControlsType.ETHERNET', code)
        self.assertIn('DO NOT EDIT THIS FILE DIRECTLY', code)

    def test_generate_class_code_with_metadata(self):
        """Test code generation with metadata description."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'metadata': {
                'description': 'Test Module Description'
            }
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('Test Module Description', code)
        self.assertIn('"""Test Module Description"""', code)

    def test_generate_class_code_with_parent_class_allen_bradley(self):
        """Test code generation with AllenBradleyModule parent."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'parent_class': 'AllenBradleyModule'
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('class TestModule(GeneratedModule):', code)
        # Should have controls_type property
        self.assertIn('def get_module_controls_type(self) -> ModuleControlsType:', code)

    def test_generate_class_code_with_parent_class_generic_safety_block(self):
        """Test code generation with AllenBradleyGenericSafetyBlock parent."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'SAFETY_BLOCK',
            'parent_class': 'AllenBradleyGenericSafetyBlock'
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('class TestModule(GeneratedModule):', code)
        # Should NOT have controls_type property (inherited)
        self.assertIn('def get_module_controls_type(self) -> ModuleControlsType:', code)

    def test_generate_class_code_with_required_imports(self):
        """Test code generation with required imports."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'required_imports': [
                {
                    'path': r'docs\controls\test.L5X',
                    'elements': ['DataTypes']
                },
                {
                    'path': r'docs\controls\test2.L5X',
                    'elements': ['Tags', 'Programs']
                }
            ]
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('def get_required_imports(self) -> list[tuple[str, list[str]]]:', code)
        self.assertIn(r"(r'docs\\controls\\test.L5X', ['DataTypes'])", code)
        self.assertIn(r"(r'docs\\controls\\test2.L5X', ['Tags', 'Programs'])", code)

    def test_generate_class_code_with_tag_name_methods(self):
        """Test code generation with tag name methods."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'tag_name_methods': {
                'safety_input': 'sz_{module.name}_I',
                'safety_output': 'sz_{module.name}_O',
                'standard_input': 'zz_{module.name}_I',
                'standard_output': 'zz_{module.name}_O'
            }
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('def get_safety_input_tag_name(self) -> str:', code)
        self.assertIn('def get_safety_output_tag_name(self) -> str:', code)
        self.assertIn('def get_standard_input_tag_name(self) -> str:', code)
        self.assertIn('def get_standard_output_tag_name(self) -> str:', code)
        self.assertIn("f'sz_{self.base_module.name}_I'", code)

    def test_generate_class_code_with_tags_using_name_template(self):
        """Test code generation with tags using name_template."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'tags': [
                {
                    'name_template': 'Tag_{controller.process_name}',
                    'datatype': 'DINT',
                    'tag_class': 'Standard',
                    'description': 'Test tag'
                }
            ]
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('def get_required_tags(self, **__) -> list[dict]:', code)
        self.assertIn("'tag_name': f'Tag_{self.controller.process_name}',", code)
        self.assertIn("'datatype': 'DINT',", code)
        self.assertIn("'tag_class': 'Standard',", code)
        self.assertIn("'description': 'Test tag',", code)

    def test_generate_class_code_with_tags_using_name_method(self):
        """Test code generation with tags using name_method."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'tags': [
                {
                    'name_method': 'get_standard_input_tag_name',
                    'datatype': 'DINT'
                }
            ]
        }

        code = self.generator._generate_class_code(config)

        self.assertIn("'tag_name': self.get_standard_input_tag_name(),", code)

    def test_generate_class_code_with_tags_needs_controller_check(self):
        """Test code generation with tags that need controller."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'tags': [
                {
                    'name_template': 'Tag_{controller.process_name}',
                    'datatype': 'DINT'
                }
            ]
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('if not self.controller:', code)
        self.assertIn('raise ValueError("Controller not set for this module")', code)

    def test_generate_class_code_with_safety_rungs(self):
        """Test code generation with safety rungs."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'SAFETY_BLOCK',
            'rungs': {
                'safety': [
                    {
                        'text_template': 'COP({module.name}:I,Tag,1);',
                        'comment': 'Copy input data'
                    }
                ]
            }
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('def get_required_safety_rungs(self, **__):', code)
        self.assertIn('rungs.append(self.controller.create_rung(', code)
        self.assertIn("rung_text=f'COP({self.base_module.name}:I,Tag,1);',", code)
        self.assertIn("comment='Copy input data'", code)

    def test_generate_class_code_with_standard_rungs(self):
        """Test code generation with standard rungs."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'rungs': {
                'standard': [
                    {
                        'text_template': 'MOV(Source,Dest);',
                        'comment': 'Move data'
                    },
                    {
                        'text_template': 'ADD(A,B,C);',
                        'comment': 'Add values'
                    }
                ]
            }
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('def get_required_standard_rungs(self, **__):', code)
        self.assertIn("rung_text=f'MOV(Source,Dest);',", code)
        self.assertIn("comment='Move data'", code)
        self.assertIn("rung_text=f'ADD(A,B,C);',", code)
        self.assertIn("comment='Add values'", code)

    def test_generate_class_code_with_both_safety_and_standard_rungs(self):
        """Test code generation with both safety and standard rungs."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'SAFETY_BLOCK',
            'rungs': {
                'safety': [
                    {
                        'text_template': 'Safety();',
                        'comment': 'Safety rung'
                    }
                ],
                'standard': [
                    {
                        'text_template': 'Standard();',
                        'comment': 'Standard rung'
                    }
                ]
            }
        }

        code = self.generator._generate_class_code(config)

        self.assertIn('def get_required_safety_rungs(self, **__):', code)
        self.assertIn('def get_required_standard_rungs(self, **__):', code)


class TestModuleGeneratorGenerateFromConfig(unittest.TestCase):
    """Test the generate_from_config method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_generate_from_config_creates_output_file(self):
        """Test that generate_from_config creates an output file."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test_module.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        output_file = self.generator.generate_from_config(config_file)

        self.assertTrue(Path(output_file).exists())
        self.assertEqual(Path(output_file).name, 'testmodule.py')

    def test_generate_from_config_writes_valid_python(self):
        """Test that generated file contains valid Python code."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test_module.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        output_file = self.generator.generate_from_config(config_file)

        with open(output_file, 'r') as f:
            content = f.read()

        # Check for Python syntax validity (basic check)
        self.assertIn('class TestModule', content)
        self.assertIn('def get_catalog_number(self)', content)

    def test_generate_from_config_with_invalid_json(self):
        """Test that generate_from_config handles invalid JSON."""
        config_file = self.config_dir / 'invalid.json'
        with open(config_file, 'w') as f:
            f.write('{ invalid json }')

        with self.assertRaises(json.JSONDecodeError):
            self.generator.generate_from_config(config_file)

    def test_generate_from_config_returns_correct_path(self):
        """Test that generate_from_config returns the correct file path."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'MyCustomModule',
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        output_file = self.generator.generate_from_config(config_file)

        self.assertEqual(Path(output_file).name, 'mycustommodule.py')
        self.assertEqual(Path(output_file).parent, self.output_dir)


class TestModuleGeneratorGenerateAll(unittest.TestCase):
    """Test the generate_all method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_generate_all_with_no_configs(self):
        """Test generate_all with no config files."""
        generated_files = self.generator.generate_all()

        self.assertEqual(len(generated_files), 0)

    def test_generate_all_with_single_config(self):
        """Test generate_all with a single config file."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        generated_files = self.generator.generate_all()

        self.assertEqual(len(generated_files), 1)
        self.assertTrue(Path(generated_files[0]).exists())

    def test_generate_all_with_multiple_configs(self):
        """Test generate_all with multiple config files."""
        configs = [
            {
                'catalog_number': '1234-TEST1',
                'class_name': 'TestModule1',
                'controls_type': 'ETHERNET'
            },
            {
                'catalog_number': '1234-TEST2',
                'class_name': 'TestModule2',
                'controls_type': 'PLC'
            },
            {
                'catalog_number': '1234-TEST3',
                'class_name': 'TestModule3',
                'controls_type': 'DRIVE'
            }
        ]

        for i, config in enumerate(configs):
            config_file = self.config_dir / f'test{i+1}.json'
            with open(config_file, 'w') as f:
                json.dump(config, f)

        generated_files = self.generator.generate_all()

        self.assertEqual(len(generated_files), 3)
        for file_path in generated_files:
            self.assertTrue(Path(file_path).exists())

    def test_generate_all_skips_schema_file(self):
        """Test that generate_all skips module_config_schema.json."""
        # Create schema file
        schema_file = self.config_dir / 'module_config_schema.json'
        with open(schema_file, 'w') as f:
            json.dump({'$schema': 'test'}, f)

        # Create regular config
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET'
        }
        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        generated_files = self.generator.generate_all()

        # Should only generate from test.json, not schema
        self.assertEqual(len(generated_files), 1)

    def test_generate_all_handles_errors_gracefully(self):
        """Test that generate_all continues on errors."""
        # Create one valid config
        valid_config = {
            'catalog_number': '1234-VALID',
            'class_name': 'ValidModule',
            'controls_type': 'ETHERNET'
        }
        valid_file = self.config_dir / 'valid.json'
        with open(valid_file, 'w') as f:
            json.dump(valid_config, f)

        # Create one invalid config
        invalid_file = self.config_dir / 'invalid.json'
        with open(invalid_file, 'w') as f:
            f.write('{ invalid json }')

        # Should not raise exception
        generated_files = self.generator.generate_all()

        # Should still generate the valid one
        self.assertEqual(len(generated_files), 1)


class TestModuleGeneratorGenerateInitFile(unittest.TestCase):
    """Test the generate_init_file method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_generate_init_file_creates_file(self):
        """Test that generate_init_file creates __init__.py."""
        # Create a dummy generated file
        generated_file = self.output_dir / 'testmodule.py'
        with open(generated_file, 'w') as f:
            f.write('class TestModule:\n    pass\n')

        self.generator.generate_init_file([str(generated_file)])

        init_file = self.output_dir / '__init__.py'
        self.assertTrue(init_file.exists())

    def test_generate_init_file_includes_imports(self):
        """Test that __init__.py includes proper imports."""
        # Create generated files
        file1 = self.output_dir / 'module1.py'
        with open(file1, 'w') as f:
            f.write('class Module1:\n    pass\n')

        file2 = self.output_dir / 'module2.py'
        with open(file2, 'w') as f:
            f.write('class Module2:\n    pass\n')

        self.generator.generate_init_file([str(file1), str(file2)])

        init_file = self.output_dir / '__init__.py'
        with open(init_file, 'r') as f:
            content = f.read()

        self.assertIn('from .module1 import Module1', content)
        self.assertIn('from .module2 import Module2', content)

    def test_generate_init_file_includes_all_list(self):
        """Test that __init__.py includes __all__ list."""
        generated_file = self.output_dir / 'testmodule.py'
        with open(generated_file, 'w') as f:
            # Write content that looks like a generated module
            f.write('"""Module docstring"""\n')
            f.write('from something import Parent\n\n')
            f.write('class TestModule(Parent):\n')
            f.write('    """Class docstring"""\n')
            f.write('    pass\n')

        self.generator.generate_init_file([str(generated_file)])

        init_file = self.output_dir / '__init__.py'
        with open(init_file, 'r') as f:
            content = f.read()

        self.assertIn("__all__ = [", content)
        self.assertIn("'TestModule',", content)
        self.assertIn(']', content)

    def test_generate_init_file_with_empty_list(self):
        """Test generate_init_file with empty generated files list."""
        self.generator.generate_init_file([])

        init_file = self.output_dir / '__init__.py'
        with open(init_file, 'r') as f:
            content = f.read()

        self.assertIn('__all__ = [', content)
        self.assertIn(']', content)
        # Should be empty list
        self.assertNotIn('import', content.split('__all__')[0].split('\n')[-2])

    def test_generate_init_file_header(self):
        """Test that __init__.py has proper header."""
        generated_file = self.output_dir / 'testmodule.py'
        with open(generated_file, 'w') as f:
            f.write('class TestModule:\n    pass\n')

        self.generator.generate_init_file([str(generated_file)])

        init_file = self.output_dir / '__init__.py'
        with open(init_file, 'r') as f:
            content = f.read()

        self.assertIn('Auto-generated module exports', content)
        self.assertIn('This file is auto-generated. Do not edit directly', content)


class TestModuleGeneratorIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_complete_workflow_simple_module(self):
        """Test complete workflow with a simple module."""
        config = {
            'catalog_number': '1756-EN2T',
            'class_name': 'AB_1756EN2T',
            'parent_class': 'AllenBradleyModule',
            'controls_type': 'ETHERNET',
            'metadata': {
                'vendor': 'Allen Bradley',
                'description': 'Ethernet Communication Module'
            }
        }

        config_file = self.config_dir / 'ab_1756en2t.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        # Generate all
        generated_files = self.generator.generate_all()

        # Generate init
        self.generator.generate_init_file(generated_files)

        # Verify output
        self.assertEqual(len(generated_files), 1)

        output_file = Path(generated_files[0])
        self.assertTrue(output_file.exists())

        with open(output_file, 'r') as f:
            content = f.read()

        self.assertIn('class AB_1756EN2T(GeneratedModule):', content)
        self.assertIn("return '1756-EN2T'", content)
        self.assertIn('Ethernet Communication Module', content)

        # Check __init__.py
        init_file = self.output_dir / '__init__.py'
        self.assertTrue(init_file.exists())

        with open(init_file, 'r') as f:
            init_content = f.read()

        self.assertIn('from .ab_1756en2t import AB_1756EN2T', init_content)
        self.assertIn("'AB_1756EN2T',", init_content)

    def test_complete_workflow_complex_module(self):
        """Test complete workflow with a complex module."""
        config = {
            'catalog_number': '1734-IB8S',
            'class_name': 'AB_1734IB8S',
            'parent_class': 'AllenBradleyGenericSafetyBlock',
            'controls_type': 'SAFETY_INPUT_BLOCK',
            'required_imports': [
                {
                    'path': r'docs\controls\emu\Demo3D_HMI_IN.L5X',
                    'elements': ['DataTypes']
                }
            ],
            'tag_name_methods': {
                'safety_input': 'sz_{module.parent_module}_I',
                'standard_input': 'zz_{module.parent_module}_I'
            },
            'tags': [
                {
                    'name_method': 'get_safety_input_tag_name',
                    'datatype': 'Demo3D_HMI_IN',
                    'tag_class': 'Safety'
                }
            ],
            'rungs': {
                'safety': [
                    {
                        'text_template': 'COP(sz_{module.parent_module}_I,{module.parent_module}:I,1);',
                        'comment': 'Copy input data'
                    }
                ]
            }
        }

        config_file = self.config_dir / 'ab_1734ib8s.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        # Generate all
        generated_files = self.generator.generate_all()

        # Generate init
        self.generator.generate_init_file(generated_files)

        # Verify complex features
        output_file = Path(generated_files[0])
        with open(output_file, 'r') as f:
            content = f.read()

        self.assertIn('def get_required_imports(self)', content)
        self.assertIn('def get_safety_input_tag_name(self)', content)
        self.assertIn('def get_required_tags(self, **__)', content)
        self.assertIn('def get_required_safety_rungs(self, **__)', content)
        self.assertIn("f'sz_{self.base_module.parent_module}_I'", content)
        self.assertIn("'tag_name': self.get_safety_input_tag_name(),", content)

    def test_workflow_with_multiple_modules(self):
        """Test workflow with multiple modules."""
        configs = [
            {
                'catalog_number': 'MODULE-1',
                'class_name': 'Module1',
                'controls_type': 'ETHERNET'
            },
            {
                'catalog_number': 'MODULE-2',
                'class_name': 'Module2',
                'controls_type': 'PLC'
            }
        ]

        for i, config in enumerate(configs):
            config_file = self.config_dir / f'module{i+1}.json'
            with open(config_file, 'w') as f:
                json.dump(config, f)

        generated_files = self.generator.generate_all()
        self.generator.generate_init_file(generated_files)

        # Check both modules generated
        self.assertEqual(len(generated_files), 2)

        # Check __init__.py includes both
        init_file = self.output_dir / '__init__.py'
        with open(init_file, 'r') as f:
            init_content = f.read()

        self.assertIn('Module1', init_content)
        self.assertIn('Module2', init_content)


class TestModuleGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.output_dir = Path(self.temp_dir) / 'output'
        self.config_dir.mkdir()
        self.generator = ModuleGenerator(str(self.config_dir), str(self.output_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_missing_catalog_number(self):
        """Test handling of missing catalog_number."""
        config = {
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        # Should raise KeyError
        with self.assertRaises(KeyError):
            self.generator.generate_from_config(config_file)

    def test_missing_class_name(self):
        """Test handling of missing class_name."""
        config = {
            'catalog_number': '1234-TEST',
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        # Should raise KeyError
        with self.assertRaises(KeyError):
            self.generator.generate_from_config(config_file)

    def test_empty_config(self):
        """Test handling of empty configuration."""
        config = {}

        config_file = self.config_dir / 'empty.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        # Should raise KeyError
        with self.assertRaises(KeyError):
            self.generator.generate_from_config(config_file)

    def test_special_characters_in_class_name(self):
        """Test handling of special characters in class name."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'Test-Module',  # Invalid Python class name
            'controls_type': 'ETHERNET'
        }

        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w') as f:
            json.dump(config, f)

        # Should generate, but result won't be valid Python
        output_file = self.generator.generate_from_config(config_file)
        self.assertTrue(Path(output_file).exists())

    def test_unicode_in_descriptions(self):
        """Test handling of unicode characters in descriptions."""
        config = {
            'catalog_number': '1234-TEST',
            'class_name': 'TestModule',
            'controls_type': 'ETHERNET',
            'metadata': {
                'description': 'Test módule with unicöde ™'
            }
        }

        config_file = self.config_dir / 'test.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)

        output_file = self.generator.generate_from_config(config_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('módule', content)
        self.assertIn('unicöde', content)


if __name__ == '__main__':
    unittest.main()
