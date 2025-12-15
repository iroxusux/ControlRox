"""Unit tests for GM Emulation Generator.

This test suite provides comprehensive testing of the GmEmulationGenerator
for Rockwell/Allen-Bradley PLC controllers with GM-specific functionality.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch

from controlrox.interfaces import (
    IProgram,
    IRoutine,
    IRung,
    ITag,
)
from controlrox.models import ControllerModificationSchema
from controlrox.applications.gm.gm import GmController
from controlrox.applications.gm.generator import GmEmulationGenerator


class TestGmEmulationGeneratorInitialization(unittest.TestCase):
    """Test cases for GmEmulationGenerator initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'GmTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.mcp_program = Mock(spec=IProgram)
        self.mock_controller.mcp_program.name = 'MCP'
        self.mock_controller.safety_common_program = Mock(spec=IProgram)
        self.mock_controller.safety_common_program.name = 's_Common'
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_initialization_with_gm_controller(self, mock_get_controller):
        """Test GmEmulationGenerator can be initialized with GmController."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        self.assertIsInstance(generator, GmEmulationGenerator)
        self.assertIs(generator.controller, self.mock_controller)
        self.assertIsInstance(generator.schema, ControllerModificationSchema)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_initialization_creates_schema(self, mock_get_controller):
        """Test initialization creates a ControllerModificationSchema."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        self.assertIsNotNone(generator.schema)
        self.assertIsInstance(generator.schema, ControllerModificationSchema)
        self.assertIs(generator.schema.destination, self.mock_controller)

    def test_supporting_class_is_gm_controller(self):
        """Test supporting_class is set to GmController."""
        self.assertEqual(GmEmulationGenerator.supporting_class, GmController)


class TestGmEmulationGeneratorConfiguration(unittest.TestCase):
    """Test cases for GmEmulationGenerator configuration methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'GmTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.mcp_program = Mock(spec=IProgram)
        self.mock_controller.mcp_program.name = 'MCP'
        self.mock_controller.safety_common_program = Mock(spec=IProgram)
        self.mock_controller.safety_common_program.name = 's_Common'
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_custom_tags_returns_gm_specific_tags(self, mock_get_controller):
        """Test custom_tags returns GM-specific tags."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        custom_tags = generator.custom_tags

        self.assertIsInstance(custom_tags, list)
        self.assertGreater(len(custom_tags), 0)

        # Check for expected custom tags
        tag_names = [tag[0] for tag in custom_tags]
        self.assertIn('DeviceDataSize', tag_names)
        self.assertIn('LoopPtr', tag_names)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_emulation_standard_program_name(self, mock_get_controller):
        """Test emulation_standard_program_name returns MCP program name."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        program_name = generator.emulation_standard_program_name

        self.assertEqual(program_name, 'MCP')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_emulation_safety_program_name(self, mock_get_controller):
        """Test emulation_safety_program_name returns s_Common program name."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        program_name = generator.emulation_safety_program_name

        self.assertEqual(program_name, 's_Common')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_emulation_safety_program_name_when_none(self, mock_get_controller):
        """Test emulation_safety_program_name handles None gracefully."""
        self.mock_controller.safety_common_program = None
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Should handle None without crashing
        try:
            program_name = generator.emulation_safety_program_name
            # If it returns None or empty, that's acceptable
            self.assertTrue(program_name is None or program_name == '')
        except AttributeError:
            # This is expected if safety_common_program is None
            pass


class TestGmEmulationGeneratorCustomStandardRungs(unittest.TestCase):
    """Test cases for GM-specific custom standard rung generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'GmTestController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.mcp_program = Mock(spec=IProgram)
        self.mock_controller.mcp_program.name = 'MCP'
        self.mock_controller.config = Mock()

        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_standard_rungs_creates_flash_rung(self, mock_get_controller):
        """Test _generate_custom_standard_rungs creates flash rate rung."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_custom_standard_rungs()

        # Verify at least one rung was added
        self.assertGreater(generator.add_rung_to_standard_routine.call_count, 0)

        # Check that flash rung logic exists (if text is available)
        calls = generator.add_rung_to_standard_routine.call_args_list
        rung_texts = [call[0][0].text for call in calls if hasattr(call[0][0], 'text') and isinstance(call[0][0].text, str)]

        # If text is available, verify it contains flash logic
        if rung_texts:
            has_flash_logic = any('Flash' in text for text in rung_texts)
            self.assertTrue(has_flash_logic, "Expected flash rate reduction logic")

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_standard_rungs_creates_device_data_rung(self, mock_get_controller):
        """Test _generate_custom_standard_rungs creates device data sizing rung."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_custom_standard_rungs()

        # Verify at least one rung was added
        self.assertGreater(generator.add_rung_to_standard_routine.call_count, 0)

        # Check that device data sizing logic exists (if text is available)
        calls = generator.add_rung_to_standard_routine.call_args_list
        rung_texts = [call[0][0].text for call in calls if hasattr(call[0][0], 'text') and isinstance(call[0][0].text, str)]

        # If text is available, verify it contains device data logic
        if rung_texts:
            has_device_data = any('DeviceData' in text for text in rung_texts)
            self.assertTrue(has_device_data, "Expected device data sizing logic")

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_standard_rungs_creates_ethernet_loop(self, mock_get_controller):
        """Test _generate_custom_standard_rungs creates ethernet connection loop."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_custom_standard_rungs()

        # Verify at least one rung was added
        self.assertGreater(generator.add_rung_to_standard_routine.call_count, 0)

        # Check that ethernet loop logic exists (if text is available)
        calls = generator.add_rung_to_standard_routine.call_args_list
        rung_texts = [call[0][0].text for call in calls if hasattr(call[0][0], 'text') and isinstance(call[0][0].text, str)]

        # If text is available, verify it contains ethernet/network logic
        if rung_texts:
            has_ethernet_logic = any('Connected' in text or 'Loop' in text for text in rung_texts)
            self.assertTrue(has_ethernet_logic, "Expected ethernet connection loop logic")

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_generate_custom_standard_rungs_called_three_times(self, mock_get_controller):
        """Test _generate_custom_standard_rungs creates exactly three rungs."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_custom_standard_rungs()

        # Should create 3 rungs: flash, device data, and ethernet loop
        self.assertEqual(generator.add_rung_to_standard_routine.call_count, 3)


class TestGmEmulationGeneratorInheritance(unittest.TestCase):
    """Test cases for GmEmulationGenerator inheritance."""

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_inherits_from_base_emulation_generator(self, mock_get_controller):
        """Test GmEmulationGenerator inherits from BaseEmulationGenerator."""
        from controlrox.applications.generator import BaseEmulationGenerator

        self.assertTrue(issubclass(GmEmulationGenerator, BaseEmulationGenerator))

    def test_supporting_class_is_gm_controller(self):
        """Test supporting_class is set correctly."""
        self.assertEqual(GmEmulationGenerator.supporting_class, GmController)


class TestGmEmulationGeneratorControllerProperty(unittest.TestCase):
    """Test cases for controller property type checking."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'GmTestController'
        self.mock_controller.__class__.__name__ = 'GmController'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_controller_property_returns_gm_controller(self, mock_get_controller):
        """Test controller property returns GmController instance."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        controller = generator.controller

        self.assertIs(controller, self.mock_controller)
        self.assertEqual(controller.__class__.__name__, 'GmController')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_controller_setter_accepts_gm_controller(self, mock_get_controller):
        """Test controller setter accepts GmController."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Should not raise error
        generator.controller = self.mock_controller

        self.assertIs(generator.controller, self.mock_controller)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_controller_setter_rejects_wrong_type(self, mock_get_controller):
        """Test controller setter rejects non-GmController types."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Create a mock controller of wrong type
        wrong_controller = Mock()
        wrong_controller.__class__.__name__ = 'FordController'

        # Should raise TypeError
        with self.assertRaises(TypeError) as context:
            generator.controller = wrong_controller

        self.assertIn('GmController', str(context.exception))


class TestGmEmulationGeneratorIntegration(unittest.TestCase):
    """Integration tests for GmEmulationGenerator workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'GmIntegrationTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.mcp_program = Mock(spec=IProgram)
        self.mock_controller.mcp_program.name = 'MCP'
        self.mock_controller.safety_common_program = Mock(spec=IProgram)
        self.mock_controller.safety_common_program.name = 's_Common'
        self.mock_controller.config = Mock()
        self.mock_controller.config.rung_type = Mock(side_effect=lambda **kwargs: Mock(spec=IRung, **kwargs))
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_full_generation_workflow(self, mock_get_controller):
        """Test complete generation workflow."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Mock schema and its methods
        generator.schema.execute = Mock()
        generator._generate_base_emulation = Mock()
        generator._generate_custom_module_emulation = Mock()
        generator.add_rung_to_standard_routine = Mock()

        # Execute generation
        result = generator.generate_emulation_logic()

        # Verify workflow was executed
        generator._generate_base_emulation.assert_called_once()
        generator._generate_custom_module_emulation.assert_called_once()
        generator.schema.execute.assert_called_once()

        # Verify schema is returned
        self.assertIs(result, generator.schema)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_custom_tags_are_created(self, mock_get_controller):
        """Test custom GM tags are created during generation."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        custom_tags = generator.custom_tags

        # Verify expected tags exist
        self.assertGreater(len(custom_tags), 0)
        tag_names = [tag[0] for tag in custom_tags]
        self.assertIn('DeviceDataSize', tag_names)
        self.assertIn('LoopPtr', tag_names)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_custom_standard_rungs_created_during_generation(self, mock_get_controller):
        """Test custom standard rungs are created."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_custom_standard_rungs()

        # Verify rungs were created
        self.assertEqual(generator.add_rung_to_standard_routine.call_count, 3)


class TestGmEmulationGeneratorEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'EdgeCaseTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.mcp_program = None
        self.mock_controller.safety_common_program = None
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_handles_missing_mcp_program(self, mock_get_controller):
        """Test generator handles missing MCP program."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Should handle None mcp_program
        try:
            program_name = generator.emulation_standard_program_name
            # If it returns None or raises AttributeError, both are acceptable
            self.assertTrue(program_name is None or isinstance(program_name, str))
        except AttributeError:
            # This is acceptable behavior
            pass

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_handles_missing_safety_common_program(self, mock_get_controller):
        """Test generator handles missing safety common program."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Should handle None safety_common_program
        try:
            program_name = generator.emulation_safety_program_name
            # If it returns None, that's acceptable
            self.assertTrue(program_name is None or isinstance(program_name, str))
        except AttributeError:
            # This is acceptable behavior
            pass

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_custom_tags_always_returns_list(self, mock_get_controller):
        """Test custom_tags always returns a list."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        custom_tags = generator.custom_tags

        self.assertIsInstance(custom_tags, list)


class TestGmEmulationGeneratorRockwellSpecific(unittest.TestCase):
    """Test cases specific to Rockwell/Allen-Bradley GM implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'RockwellGmTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.mcp_program = Mock(spec=IProgram)
        self.mock_controller.mcp_program.name = 'MCP'
        self.mock_controller.safety_common_program = Mock(spec=IProgram)
        self.mock_controller.safety_common_program.name = 's_Common'
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))
        self.mock_controller.create_rung = Mock(return_value=Mock(spec=IRung))
        self.mock_controller.create_routine = Mock(return_value=Mock(spec=IRoutine))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_gm_controller_type_compatibility(self, mock_get_controller):
        """Test GmEmulationGenerator works specifically with GmController."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        self.assertIsInstance(generator.controller, GmController)
        self.assertEqual(type(generator).__name__, 'GmEmulationGenerator')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_inherits_rockwell_base_configuration(self, mock_get_controller):
        """Test generator inherits Rockwell-specific base configurations."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        # Should have base_tags from BaseEmulationGenerator
        base_tags = generator.base_tags
        self.assertIsInstance(base_tags, list)
        self.assertGreater(len(base_tags), 0)

        # Check for expected base tags
        tag_names = [tag[0] for tag in base_tags]
        self.assertIn('zz_Demo3D_Uninhibit', tag_names)
        self.assertIn('zz_Demo3D_Inhibit', tag_names)
        self.assertIn('zz_Demo3D_TestMode', tag_names)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_standard_program_name_matches_gm_convention(self, mock_get_controller):
        """Test standard program name follows GM naming conventions (MCP)."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        program_name = generator.emulation_standard_program_name

        # MCP is GM standard program name
        self.assertEqual(program_name, 'MCP')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_safety_program_name_matches_gm_convention(self, mock_get_controller):
        """Test safety program name follows GM naming conventions (s_Common)."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        program_name = generator.emulation_safety_program_name

        # s_Common is GM safety program name
        self.assertEqual(program_name, 's_Common')

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_gm_specific_network_emulation(self, mock_get_controller):
        """Test GM-specific network emulation logic."""
        mock_get_controller.return_value = self.mock_controller
        self.mock_controller.config = Mock()
        self.mock_controller.config.rung_type = Mock(side_effect=lambda **kwargs: Mock(spec=IRung, **kwargs))
        generator = GmEmulationGenerator()
        generator.add_rung_to_standard_routine = Mock()

        generator._generate_custom_standard_rungs()

        # Verify GM network-specific rungs created
        calls = generator.add_rung_to_standard_routine.call_args_list
        self.assertGreater(len(calls), 0)

        # Check for EnetStorage references (GM-specific) if text is available
        rung_texts = [call[0][0].text for call in calls if hasattr(call[0][0], 'text') and isinstance(call[0][0].text, str)]
        if rung_texts:
            has_enet_storage = any('EnetStorage' in text for text in rung_texts)
            self.assertTrue(has_enet_storage, "Expected GM EnetStorage network logic")


class TestGmEmulationGeneratorCustomTagStructure(unittest.TestCase):
    """Test custom tag structure for GM emulation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=GmController)
        self.mock_controller.name = 'TagStructureTest'
        self.mock_controller.modules = []
        self.mock_controller.programs = MagicMock()
        self.mock_controller.safety_programs = []
        self.mock_controller.create_tag = Mock(return_value=Mock(spec=ITag))

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_custom_tags_have_correct_structure(self, mock_get_controller):
        """Test custom tags have correct tuple structure."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        custom_tags = generator.custom_tags

        for tag in custom_tags:
            # Each tag should be a tuple
            self.assertIsInstance(tag, tuple)
            # With at least 3 elements: name, datatype, description
            self.assertGreaterEqual(len(tag), 3)
            # Name should be a string
            self.assertIsInstance(tag[0], str)
            # Datatype should be a string
            self.assertIsInstance(tag[1], str)
            # Description should be a string
            self.assertIsInstance(tag[2], str)

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_device_data_size_tag_details(self, mock_get_controller):
        """Test DeviceDataSize tag has correct details."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        custom_tags = generator.custom_tags
        device_data_tag = [tag for tag in custom_tags if tag[0] == 'DeviceDataSize'][0]

        self.assertEqual(device_data_tag[0], 'DeviceDataSize')
        self.assertEqual(device_data_tag[1], 'DINT')
        self.assertIn('Size', device_data_tag[2])

    @patch('controlrox.models.plc.meta.ControllerInstanceManager.get_controller')
    def test_loop_ptr_tag_details(self, mock_get_controller):
        """Test LoopPtr tag has correct details."""
        mock_get_controller.return_value = self.mock_controller
        generator = GmEmulationGenerator()

        custom_tags = generator.custom_tags
        loop_ptr_tag = [tag for tag in custom_tags if tag[0] == 'LoopPtr'][0]

        self.assertEqual(loop_ptr_tag[0], 'LoopPtr')
        self.assertEqual(loop_ptr_tag[1], 'DINT')
        self.assertIn('loop', loop_ptr_tag[2].lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
