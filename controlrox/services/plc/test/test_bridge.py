"""Unit tests for PLC Scene Bridge service."""
import unittest
from unittest.mock import Mock, patch

from controlrox.services.plc.bridge import (
    BindingDirection,
    PlcTagBinding,
    PlcSceneBridge,
)
from pylogix.lgx_response import Response


class TestBindingDirection(unittest.TestCase):
    """Test cases for BindingDirection enum."""

    def test_direction_values(self):
        """Test that enum values are correct."""
        self.assertEqual(BindingDirection.READ.value, "read")
        self.assertEqual(BindingDirection.WRITE.value, "write")
        self.assertEqual(BindingDirection.BOTH.value, "both")

    def test_direction_construction(self):
        """Test constructing enum from string values."""
        self.assertEqual(BindingDirection("read"), BindingDirection.READ)
        self.assertEqual(BindingDirection("write"), BindingDirection.WRITE)
        self.assertEqual(BindingDirection("both"), BindingDirection.BOTH)


class TestPlcTagBinding(unittest.TestCase):
    """Test cases for PlcTagBinding dataclass."""

    def test_minimal_initialization(self):
        """Test binding with minimal required fields."""
        binding = PlcTagBinding(
            tag_name="TestTag",
            object_id="obj1",
            property_path="speed"
        )
        self.assertEqual(binding.tag_name, "TestTag")
        self.assertEqual(binding.object_id, "obj1")
        self.assertEqual(binding.property_path, "speed")
        self.assertEqual(binding.direction, BindingDirection.READ)
        self.assertEqual(binding.data_type, 0)
        self.assertIsNone(binding.transform)
        self.assertIsNone(binding.inverse_transform)
        self.assertTrue(binding.enabled)
        self.assertIsNone(binding.last_plc_value)
        self.assertIsNone(binding.last_scene_value)

    def test_full_initialization(self):
        """Test binding with all fields specified."""
        def transform(x): return x * 2
        def inverse(x): return x / 2

        binding = PlcTagBinding(
            tag_name="Conveyor1_Speed",
            object_id="conveyor_1",
            property_path="speed",
            direction=BindingDirection.BOTH,
            data_type=8,
            transform=transform,
            inverse_transform=inverse,
            enabled=False,
            description="Conveyor speed control"
        )

        self.assertEqual(binding.tag_name, "Conveyor1_Speed")
        self.assertEqual(binding.object_id, "conveyor_1")
        self.assertEqual(binding.direction, BindingDirection.BOTH)
        self.assertEqual(binding.data_type, 8)
        self.assertFalse(binding.enabled)
        self.assertEqual(binding.description, "Conveyor speed control")
        self.assertEqual(binding.transform(10), 20)  # type: ignore
        self.assertEqual(binding.inverse_transform(20), 10)  # type: ignore

    def test_nested_property_path(self):
        """Test binding with nested property path."""
        binding = PlcTagBinding(
            tag_name="Robot_X",
            object_id="robot_1",
            property_path="position.x"
        )
        self.assertEqual(binding.property_path, "position.x")


class TestPlcSceneBridge(unittest.TestCase):
    """Test cases for PlcSceneBridge class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock scene
        self.mock_scene = Mock()
        self.mock_scene.get_scene_object = Mock()

        # Create bridge
        self.bridge = PlcSceneBridge(self.mock_scene)

    def tearDown(self):
        """Clean up after tests."""
        if self.bridge._active:
            self.bridge.stop()

    def test_initialization_with_scene(self):
        """Test bridge initialization with scene."""
        bridge = PlcSceneBridge(self.mock_scene)
        self.assertEqual(bridge._scene, self.mock_scene)
        self.assertEqual(len(bridge._bindings), 0)
        self.assertFalse(bridge._active)
        self.assertTrue(bridge._write_enabled)
        self.assertFalse(bridge._tick_callback_registered)

    def test_initialization_without_scene(self):
        """Test bridge initialization without scene."""
        bridge = PlcSceneBridge()
        self.assertIsNone(bridge._scene)
        self.assertFalse(bridge._active)

    def test_set_scene(self):
        """Test setting a new scene."""
        new_scene = Mock()
        self.bridge.set_scene(new_scene)
        self.assertEqual(self.bridge._scene, new_scene)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_set_scene_stops_active_bridge(self, mock_manager):
        """Test that setting scene stops active bridge."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.start()

        new_scene = Mock()
        self.bridge.set_scene(new_scene)

        self.assertFalse(self.bridge._active)
        self.assertEqual(self.bridge._scene, new_scene)

    def test_add_binding_basic(self):
        """Test adding a basic binding."""
        binding = self.bridge.add_binding(
            tag_name="TestTag",
            object_id="obj1",
            property_path="speed"
        )

        self.assertIsInstance(binding, PlcTagBinding)
        self.assertEqual(binding.tag_name, "TestTag")
        self.assertEqual(binding.object_id, "obj1")
        self.assertEqual(binding.property_path, "speed")
        self.assertEqual(len(self.bridge._bindings), 1)

    def test_add_binding_with_transform(self):
        """Test adding binding with transform functions."""
        def transform(x): return x / 1000.0
        def inverse(x): return x * 1000.0

        binding = self.bridge.add_binding(
            tag_name="Position_MM",
            object_id="obj1",
            property_path="position",
            transform=transform,
            inverse_transform=inverse
        )

        self.assertEqual(binding.transform(1000), 1.0)  # type: ignore
        self.assertEqual(binding.inverse_transform(1.0), 1000.0)  # type: ignore

    def test_add_binding_all_directions(self):
        """Test adding bindings with different directions."""
        read_binding = self.bridge.add_binding(
            "Tag1", "obj1", "prop1", direction=BindingDirection.READ
        )
        write_binding = self.bridge.add_binding(
            "Tag2", "obj2", "prop2", direction=BindingDirection.WRITE
        )
        both_binding = self.bridge.add_binding(
            "Tag3", "obj3", "prop3", direction=BindingDirection.BOTH
        )

        self.assertEqual(read_binding.direction, BindingDirection.READ)
        self.assertEqual(write_binding.direction, BindingDirection.WRITE)
        self.assertEqual(both_binding.direction, BindingDirection.BOTH)
        self.assertEqual(len(self.bridge._bindings), 3)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_add_binding_to_active_bridge(self, mock_manager):
        """Test adding binding to already active bridge sets up watch."""
        self.bridge.start()

        _ = self.bridge.add_binding(
            "NewTag", "obj1", "speed", direction=BindingDirection.READ
        )

        # Should have called add_watch_tag
        mock_manager.add_watch_tag.assert_called()

    def test_remove_binding_success(self):
        """Test successfully removing a binding."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.assertEqual(len(self.bridge._bindings), 1)

        result = self.bridge.remove_binding("Tag1", "obj1", "speed")

        self.assertTrue(result)
        self.assertEqual(len(self.bridge._bindings), 0)

    def test_remove_binding_not_found(self):
        """Test removing non-existent binding."""
        result = self.bridge.remove_binding("NonExistent", "obj1", "speed")
        self.assertFalse(result)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_remove_binding_from_active_bridge(self, mock_manager):
        """Test removing binding from active bridge removes watch."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.start()

        self.bridge.remove_binding("Tag1", "obj1", "speed")

        # Should have called remove_watch_tag
        mock_manager.remove_watch_tag.assert_called_with("Tag1")

    def test_clear_bindings(self):
        """Test clearing all bindings."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.add_binding("Tag2", "obj2", "position")
        self.assertEqual(len(self.bridge._bindings), 2)

        self.bridge.clear_bindings()

        self.assertEqual(len(self.bridge._bindings), 0)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_clear_bindings_stops_active(self, mock_manager):
        """Test that clearing bindings stops active bridge."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.start()
        self.assertTrue(self.bridge._active)

        self.bridge.clear_bindings()

        self.assertFalse(self.bridge._active)

    def test_get_bindings(self):
        """Test retrieving all bindings."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.add_binding("Tag2", "obj2", "position")

        bindings = self.bridge.get_bindings()

        self.assertEqual(len(bindings), 2)
        self.assertIsInstance(bindings[0], PlcTagBinding)

    def test_get_bindings_for_object(self):
        """Test retrieving bindings for specific object."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.add_binding("Tag2", "obj1", "position")
        self.bridge.add_binding("Tag3", "obj2", "speed")

        obj1_bindings = self.bridge.get_bindings_for_object("obj1")

        self.assertEqual(len(obj1_bindings), 2)
        self.assertTrue(all(b.object_id == "obj1" for b in obj1_bindings))

    def test_get_bindings_for_tag(self):
        """Test retrieving bindings for specific tag."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.add_binding("Tag1", "obj2", "speed")
        self.bridge.add_binding("Tag2", "obj1", "position")

        tag1_bindings = self.bridge.get_bindings_for_tag("Tag1")

        self.assertEqual(len(tag1_bindings), 2)
        self.assertTrue(all(b.tag_name == "Tag1" for b in tag1_bindings))

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_start_bridge(self, mock_manager):
        """Test starting the bridge."""
        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.READ)

        self.bridge.start()

        self.assertTrue(self.bridge._active)
        mock_manager.add_watch_tag.assert_called()
        mock_manager.subscribe_to_ticks.assert_called_once_with(self.bridge._on_tick)

    def test_start_bridge_without_scene(self):
        """Test starting bridge without scene logs error."""
        bridge = PlcSceneBridge()  # No scene
        bridge.add_binding("Tag1", "obj1", "speed")

        bridge.start()

        self.assertFalse(bridge._active)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_start_already_active(self, mock_manager):
        """Test starting already active bridge does nothing."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.start()

        call_count = mock_manager.add_watch_tag.call_count
        self.bridge.start()  # Start again

        # Should not add more watches
        self.assertEqual(mock_manager.add_watch_tag.call_count, call_count)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_start_only_watches_read_bindings(self, mock_manager):
        """Test that start only watches READ and BOTH bindings."""
        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.READ)
        self.bridge.add_binding("Tag2", "obj2", "pos", direction=BindingDirection.WRITE)
        self.bridge.add_binding("Tag3", "obj3", "vel", direction=BindingDirection.BOTH)

        self.bridge.start()

        # Should watch Tag1 and Tag3, but not Tag2
        self.assertEqual(mock_manager.add_watch_tag.call_count, 2)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_stop_bridge(self, mock_manager):
        """Test stopping the bridge."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.start()

        self.bridge.stop()

        self.assertFalse(self.bridge._active)
        mock_manager.remove_watch_tag.assert_called_with("Tag1")
        mock_manager.unsubscribe_from_ticks.assert_called_once_with(self.bridge._on_tick)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_stop_inactive_bridge(self, mock_manager):
        """Test stopping inactive bridge does nothing."""
        self.bridge.stop()  # Not started

        mock_manager.remove_watch_tag.assert_not_called()

    def test_get_scene_property_simple(self):
        """Test getting simple property from scene object."""
        mock_obj = Mock()
        mock_obj.speed = 42.5
        self.mock_scene.get_scene_object.return_value = mock_obj

        value = self.bridge._get_scene_property("obj1", "speed")

        self.assertEqual(value, 42.5)
        self.mock_scene.get_scene_object.assert_called_with("obj1")

    def test_get_scene_property_nested(self):
        """Test getting nested property from scene object."""
        mock_obj = Mock()
        mock_obj.position = Mock()
        mock_obj.position.x = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        value = self.bridge._get_scene_property("obj1", "position.x")

        self.assertEqual(value, 100.0)

    def test_get_scene_property_not_found(self):
        """Test getting non-existent property returns None."""
        mock_obj = Mock(spec=['speed'])  # Only has speed
        self.mock_scene.get_scene_object.return_value = mock_obj

        value = self.bridge._get_scene_property("obj1", "nonexistent")

        self.assertIsNone(value)

    def test_get_scene_property_object_not_found(self):
        """Test getting property from non-existent object returns None."""
        self.mock_scene.get_scene_object.return_value = None

        value = self.bridge._get_scene_property("nonexistent", "speed")

        self.assertIsNone(value)

    def test_get_scene_property_no_scene(self):
        """Test getting property with no scene returns None."""
        bridge = PlcSceneBridge()  # No scene

        value = bridge._get_scene_property("obj1", "speed")

        self.assertIsNone(value)

    def test_set_scene_property_simple(self):
        """Test setting simple property on scene object."""
        mock_obj = Mock()
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge._set_scene_property("obj1", "speed", 75.0)

        self.assertEqual(mock_obj.speed, 75.0)

    def test_set_scene_property_nested(self):
        """Test setting nested property on scene object."""
        mock_obj = Mock()
        mock_obj.position = Mock()
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge._set_scene_property("obj1", "position.x", 200.0)

        self.assertEqual(mock_obj.position.x, 200.0)

    def test_set_scene_property_object_not_found(self):
        """Test setting property on non-existent object raises error."""
        self.mock_scene.get_scene_object.return_value = None

        with self.assertRaises(ValueError) as cm:
            self.bridge._set_scene_property("nonexistent", "speed", 50.0)

        self.assertIn("not found", str(cm.exception))

    def test_set_scene_property_no_scene(self):
        """Test setting property with no scene raises error."""
        bridge = PlcSceneBridge()  # No scene

        with self.assertRaises(ValueError) as cm:
            bridge._set_scene_property("obj1", "speed", 50.0)

        self.assertIn("No scene", str(cm.exception))

    def test_on_tag_update_success(self):
        """Test successful tag update applies to scene."""
        mock_obj = Mock()
        self.mock_scene.get_scene_object.return_value = mock_obj

        binding = self.bridge.add_binding("Tag1", "obj1", "speed")

        # Create mock response
        response = Mock(spec=Response)
        response.Status = 'Success'
        response.Value = 50.0

        self.bridge._on_tag_update(binding, response)

        self.assertEqual(mock_obj.speed, 50.0)
        self.assertEqual(binding.last_plc_value, 50.0)
        self.assertEqual(binding.last_scene_value, 50.0)

    def test_on_tag_update_with_transform(self):
        """Test tag update with transform function."""
        mock_obj = Mock()
        self.mock_scene.get_scene_object.return_value = mock_obj

        # Transform: mm to meters
        def transform(x): return x / 1000.0
        binding = self.bridge.add_binding(
            "Tag1", "obj1", "position",
            transform=transform
        )

        response = Mock(spec=Response)
        response.Status = 'Success'
        response.Value = 1000.0  # 1000mm

        self.bridge._on_tag_update(binding, response)

        self.assertEqual(mock_obj.position, 1.0)  # 1 meter
        self.assertEqual(binding.last_plc_value, 1000.0)
        self.assertEqual(binding.last_scene_value, 1.0)

    def test_on_tag_update_disabled_binding(self):
        """Test tag update on disabled binding is ignored."""
        mock_obj = Mock()
        mock_obj.speed = 0.0  # Initial value
        self.mock_scene.get_scene_object.return_value = mock_obj

        binding = self.bridge.add_binding("Tag1", "obj1", "speed")
        binding.enabled = False

        response = Mock(spec=Response)
        response.Status = 'Success'
        response.Value = 50.0

        self.bridge._on_tag_update(binding, response)

        # Should not have set property - value should remain at initial
        self.assertEqual(mock_obj.speed, 0.0)

    def test_on_tag_update_failed_response(self):
        """Test tag update with failed response is ignored."""
        mock_obj = Mock()
        mock_obj.speed = 0.0  # Initial value
        self.mock_scene.get_scene_object.return_value = mock_obj

        binding = self.bridge.add_binding("Tag1", "obj1", "speed")

        response = Mock(spec=Response)
        response.Status = 'Error'

        self.bridge._on_tag_update(binding, response)

        # Should not have set property - value should remain at initial
        self.assertEqual(mock_obj.speed, 0.0)

    def test_on_tag_update_list_response(self):
        """Test tag update with list response extracts first item."""
        mock_obj = Mock()
        self.mock_scene.get_scene_object.return_value = mock_obj

        binding = self.bridge.add_binding("Tag1", "obj1", "speed")

        response = Mock(spec=Response)
        response.Status = 'Success'
        response.Value = 75.0

        self.bridge._on_tag_update(binding, [response])

        self.assertEqual(mock_obj.speed, 75.0)

    def test_on_tag_update_empty_list(self):
        """Test tag update with empty list is ignored."""
        mock_obj = Mock()
        mock_obj.speed = 0.0  # Initial value
        self.mock_scene.get_scene_object.return_value = mock_obj

        binding = self.bridge.add_binding("Tag1", "obj1", "speed")

        self.bridge._on_tag_update(binding, [])

        # Should not have set property - value should remain at initial
        self.assertEqual(mock_obj.speed, 0.0)

    def test_on_tag_update_transform_error(self):
        """Test tag update handles transform errors gracefully."""
        mock_obj = Mock()
        mock_obj.speed = 0.0  # Initial value
        self.mock_scene.get_scene_object.return_value = mock_obj

        def bad_transform(x):
            raise ValueError("Transform error")

        binding = self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            transform=bad_transform
        )

        response = Mock(spec=Response)
        response.Status = 'Success'
        response.Value = 50.0

        self.bridge._on_tag_update(binding, response)

        # Should not have set property due to transform error - value should remain at initial
        self.assertEqual(mock_obj.speed, 0.0)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_update_scene_to_plc(self, mock_manager, mock_time):
        """Test updating PLC with scene values."""
        mock_time.return_value = 1.0  # 1 second = 1000ms

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.WRITE
        )
        self.bridge.start()

        self.bridge.update_scene_to_plc()

        mock_manager.write_watch_tag.assert_called_with("Tag1", 100.0)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_update_scene_to_plc_with_inverse_transform(self, mock_manager, mock_time):
        """Test scene to PLC update with inverse transform."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.position = 1.5  # meters
        self.mock_scene.get_scene_object.return_value = mock_obj

        # Inverse transform: meters to mm
        def inverse(x): return x * 1000.0

        self.bridge.add_binding(
            "Tag1", "obj1", "position",
            direction=BindingDirection.WRITE,
            inverse_transform=inverse
        )
        self.bridge.start()

        self.bridge.update_scene_to_plc()

        mock_manager.write_watch_tag.assert_called_with("Tag1", 1500.0)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_update_scene_to_plc_throttling(self, mock_manager, mock_time):
        """Test that PLC writes are throttled."""
        # First call at 1000ms
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        _ = self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.WRITE
        )
        self.bridge.start()

        # First write
        self.bridge.update_scene_to_plc()
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

        # Second call at 1050ms (only 50ms later, under throttle)
        mock_time.return_value = 1.05
        mock_obj.speed = 120.0
        self.bridge.update_scene_to_plc()

        # Should still be 1 call (throttled)
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

        # Third call at 1150ms (150ms later, over throttle)
        mock_time.return_value = 1.15
        self.bridge.update_scene_to_plc()

        # Should now be 2 calls
        self.assertEqual(mock_manager.write_watch_tag.call_count, 2)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_update_scene_to_plc_only_on_change(self, mock_manager, mock_time):
        """Test that PLC writes only happen when value changes."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        _ = self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.WRITE
        )
        self.bridge.start()

        # First write
        self.bridge.update_scene_to_plc()
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

        # Value hasn't changed - advance time past throttle
        mock_time.return_value = 2.0
        self.bridge.update_scene_to_plc()

        # Should still be 1 call (value didn't change)
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_update_scene_to_plc_inactive_bridge(self, mock_manager):
        """Test that inactive bridge doesn't write to PLC."""
        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.WRITE
        )
        # Don't start bridge

        self.bridge.update_scene_to_plc()

        mock_manager.write_watch_tag.assert_not_called()

    def test_to_dict_serialization(self):
        """Test converting bridge configuration to dictionary."""
        self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.READ,
            description="Test binding"
        )
        self.bridge.add_binding(
            "Tag2", "obj2", "position",
            direction=BindingDirection.WRITE
        )

        config = self.bridge.to_dict()

        self.assertIn('bindings', config)
        self.assertIn('write_enabled', config)
        self.assertIn('write_throttle_ms', config)
        self.assertEqual(len(config['bindings']), 2)

        # Check first binding details
        binding1 = config['bindings'][0]
        self.assertEqual(binding1['tag_name'], 'Tag1')
        self.assertEqual(binding1['object_id'], 'obj1')
        self.assertEqual(binding1['property_path'], 'speed')
        self.assertEqual(binding1['direction'], 'read')
        self.assertEqual(binding1['description'], 'Test binding')

    def test_from_dict_deserialization(self):
        """Test loading bridge configuration from dictionary."""
        config = {
            'bindings': [
                {
                    'tag_name': 'Tag1',
                    'object_id': 'obj1',
                    'property_path': 'speed',
                    'direction': 'read',
                    'data_type': 8,
                    'enabled': True,
                    'description': 'Speed control',
                    'tags': []
                },
                {
                    'tag_name': 'Tag2',
                    'object_id': 'obj2',
                    'property_path': 'position',
                    'direction': 'write',
                    'data_type': 0,
                    'enabled': False,
                    'description': '',
                    'tags': []
                }
            ],
            'write_enabled': False,
            'write_throttle_ms': 200
        }

        self.bridge.from_dict(config)

        self.assertEqual(len(self.bridge._bindings), 2)
        self.assertFalse(self.bridge._write_enabled)
        self.assertEqual(self.bridge._write_throttle_ms, 200)

        bindings = self.bridge.get_bindings()
        self.assertEqual(bindings[0].tag_name, 'Tag1')
        self.assertEqual(bindings[0].description, 'Speed control')

    def test_from_dict_clears_existing(self):
        """Test that from_dict clears existing bindings."""
        self.bridge.add_binding("OldTag", "obj1", "speed")
        self.assertEqual(len(self.bridge._bindings), 1)

        config = {
            'bindings': [
                {
                    'tag_name': 'NewTag',
                    'object_id': 'obj2',
                    'property_path': 'position',
                    'direction': 'read',
                    'data_type': 0,
                    'enabled': True,
                    'description': '',
                    'tags': []
                }
            ]
        }

        self.bridge.from_dict(config)

        self.assertEqual(len(self.bridge._bindings), 1)
        bindings = self.bridge.get_bindings()
        self.assertEqual(bindings[0].tag_name, 'NewTag')

    def test_serialization_round_trip(self):
        """Test that serialization and deserialization preserve data."""
        self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.BOTH,
            description="Test binding"
        )

        # Serialize
        config = self.bridge.to_dict()

        # Create new bridge and deserialize
        new_bridge = PlcSceneBridge(self.mock_scene)
        new_bridge.from_dict(config)

        # Compare
        original_bindings = self.bridge.get_bindings()
        new_bindings = new_bridge.get_bindings()

        self.assertEqual(len(new_bindings), len(original_bindings))
        self.assertEqual(new_bindings[0].tag_name, original_bindings[0].tag_name)
        self.assertEqual(new_bindings[0].object_id, original_bindings[0].object_id)
        self.assertEqual(new_bindings[0].direction, original_bindings[0].direction)

    # ==================== New Features Tests ====================

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_start_subscribes_to_ticks(self, mock_manager):
        """Test that start subscribes to PLC connection ticks."""
        self.bridge.add_binding("Tag1", "obj1", "speed")

        self.bridge.start()

        mock_manager.subscribe_to_ticks.assert_called_once()
        self.assertTrue(self.bridge._tick_callback_registered)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_stop_unsubscribes_from_ticks(self, mock_manager):
        """Test that stop unsubscribes from PLC connection ticks."""
        self.bridge.add_binding("Tag1", "obj1", "speed")
        self.bridge.start()

        self.bridge.stop()

        mock_manager.unsubscribe_from_ticks.assert_called_once()
        self.assertFalse(self.bridge._tick_callback_registered)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_on_tick_calls_update_scene_to_plc(self, mock_manager):
        """Test that _on_tick calls update_scene_to_plc."""
        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)
        self.bridge.start()

        # Call the tick callback
        with patch.object(self.bridge, 'update_scene_to_plc') as mock_update:
            self.bridge._on_tick()
            mock_update.assert_called_once()

    def test_set_write_enabled(self):
        """Test enabling and disabling writes."""
        self.assertTrue(self.bridge._write_enabled)

        self.bridge.set_write_enabled(False)
        self.assertFalse(self.bridge._write_enabled)

        self.bridge.set_write_enabled(True)
        self.assertTrue(self.bridge._write_enabled)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_write_disabled_prevents_updates(self, mock_manager, mock_time):
        """Test that disabling writes prevents PLC updates."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)
        self.bridge.start()
        self.bridge.set_write_enabled(False)

        self.bridge.update_scene_to_plc()

        mock_manager.write_watch_tag.assert_not_called()

    def test_set_write_throttle(self):
        """Test setting write throttle."""
        self.assertEqual(self.bridge._write_throttle_ms, 100)

        self.bridge.set_write_throttle(250)
        self.assertEqual(self.bridge._write_throttle_ms, 250)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_custom_throttle_applied(self, mock_manager, mock_time):
        """Test that custom throttle setting is applied."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)
        self.bridge.set_write_throttle(200)  # 200ms throttle
        self.bridge.start()

        # First write
        self.bridge.update_scene_to_plc()
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

        # 150ms later (under 200ms throttle)
        mock_time.return_value = 1.15
        mock_obj.speed = 120.0
        self.bridge.update_scene_to_plc()
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

        # 250ms later (over 200ms throttle)
        mock_time.return_value = 1.25
        self.bridge.update_scene_to_plc()
        self.assertEqual(mock_manager.write_watch_tag.call_count, 2)

    def test_is_active(self):
        """Test is_active method."""
        self.assertFalse(self.bridge.is_active())

        self.bridge.add_binding("Tag1", "obj1", "speed")
        with patch('controlrox.services.plc.bridge.PlcConnectionManager'):
            self.bridge.start()
            self.assertTrue(self.bridge.is_active())

            self.bridge.stop()
            self.assertFalse(self.bridge.is_active())

    def test_is_write_enabled(self):
        """Test is_write_enabled method."""
        self.assertTrue(self.bridge.is_write_enabled())

        self.bridge.set_write_enabled(False)
        self.assertFalse(self.bridge.is_write_enabled())

    def test_get_write_throttle(self):
        """Test get_write_throttle method."""
        self.assertEqual(self.bridge.get_write_throttle(), 100)

        self.bridge.set_write_throttle(300)
        self.assertEqual(self.bridge.get_write_throttle(), 300)

    def test_get_binding_stats_empty(self):
        """Test get_binding_stats with no bindings."""
        stats = self.bridge.get_binding_stats()

        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['enabled'], 0)
        self.assertEqual(stats['disabled'], 0)
        self.assertEqual(stats['read'], 0)
        self.assertEqual(stats['write'], 0)
        self.assertEqual(stats['both'], 0)
        self.assertFalse(stats['active'])
        self.assertTrue(stats['write_enabled'])

    def test_get_binding_stats_with_bindings(self):
        """Test get_binding_stats with various bindings."""
        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.READ)
        self.bridge.add_binding("Tag2", "obj2", "pos", direction=BindingDirection.WRITE)
        self.bridge.add_binding("Tag3", "obj3", "vel", direction=BindingDirection.BOTH)
        self.bridge.add_binding("Tag4", "obj4", "acc", direction=BindingDirection.READ)

        # Disable one binding
        self.bridge._bindings["Tag4::obj4::acc"].enabled = False

        stats = self.bridge.get_binding_stats()

        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['enabled'], 3)
        self.assertEqual(stats['disabled'], 1)
        self.assertEqual(stats['read'], 2)
        self.assertEqual(stats['write'], 1)
        self.assertEqual(stats['both'], 1)
        self.assertFalse(stats['active'])
        self.assertTrue(stats['write_enabled'])

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_force_write_binding_success(self, mock_manager, mock_time):
        """Test force_write_binding successfully writes."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 150.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)

        result = self.bridge.force_write_binding("Tag1", "obj1", "speed")

        self.assertTrue(result)
        mock_manager.write_watch_tag.assert_called_with("Tag1", 150.0)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_force_write_binding_with_transform(self, mock_manager, mock_time):
        """Test force_write_binding applies inverse transform."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.position = 2.5  # meters
        self.mock_scene.get_scene_object.return_value = mock_obj

        def inverse(x): return x * 1000.0  # meters to mm

        self.bridge.add_binding(
            "Tag1", "obj1", "position",
            direction=BindingDirection.WRITE,
            inverse_transform=inverse
        )

        result = self.bridge.force_write_binding("Tag1", "obj1", "position")

        self.assertTrue(result)
        mock_manager.write_watch_tag.assert_called_with("Tag1", 2500.0)

    def test_force_write_binding_not_found(self):
        """Test force_write_binding with non-existent binding."""
        result = self.bridge.force_write_binding("NonExistent", "obj1", "speed")

        self.assertFalse(result)

    def test_force_write_binding_disabled(self):
        """Test force_write_binding with disabled binding."""
        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)
        self.bridge._bindings["Tag1::obj1::speed"].enabled = False

        result = self.bridge.force_write_binding("Tag1", "obj1", "speed")

        self.assertFalse(result)

    def test_force_write_binding_wrong_direction(self):
        """Test force_write_binding with READ-only binding."""
        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.READ)

        result = self.bridge.force_write_binding("Tag1", "obj1", "speed")

        self.assertFalse(result)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_force_write_bypasses_throttle(self, mock_manager, mock_time):
        """Test that force_write_binding bypasses throttle."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)
        self.bridge.start()

        # First write via update
        self.bridge.update_scene_to_plc()
        self.assertEqual(mock_manager.write_watch_tag.call_count, 1)

        # Immediate force write (0ms later - would be throttled normally)
        mock_obj.speed = 120.0
        result = self.bridge.force_write_binding("Tag1", "obj1", "speed")

        self.assertTrue(result)
        self.assertEqual(mock_manager.write_watch_tag.call_count, 2)

    def test_force_write_binding_none_value(self):
        """Test force_write_binding when property returns None."""
        self.mock_scene.get_scene_object.return_value = Mock(spec=[])  # No attributes

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.WRITE)

        result = self.bridge.force_write_binding("Tag1", "obj1", "speed")

        self.assertFalse(result)

    @patch('time.time')
    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_force_write_binding_transform_error(self, mock_manager, mock_time):
        """Test force_write_binding handles transform errors."""
        mock_time.return_value = 1.0

        mock_obj = Mock()
        mock_obj.speed = 100.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        def bad_inverse(x):
            raise ValueError("Transform error")

        self.bridge.add_binding(
            "Tag1", "obj1", "speed",
            direction=BindingDirection.WRITE,
            inverse_transform=bad_inverse
        )

        result = self.bridge.force_write_binding("Tag1", "obj1", "speed")

        self.assertFalse(result)
        mock_manager.write_watch_tag.assert_not_called()

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_bidirectional_binding_both_directions(self, mock_manager):
        """Test BOTH direction binding works for both read and write."""
        mock_obj = Mock()
        mock_obj.speed = 50.0
        self.mock_scene.get_scene_object.return_value = mock_obj

        self.bridge.add_binding("Tag1", "obj1", "speed", direction=BindingDirection.BOTH)
        self.bridge.start()

        # Test READ direction (PLC -> Scene)
        response = Mock(spec=Response)
        response.Status = 'Success'
        response.Value = 75.0

        binding = self.bridge._bindings["Tag1::obj1::speed"]
        self.bridge._on_tag_update(binding, response)

        self.assertEqual(mock_obj.speed, 75.0)

        # Test WRITE direction (Scene -> PLC)
        with patch('time.time', return_value=1.0):
            mock_obj.speed = 100.0
            self.bridge.update_scene_to_plc()

            mock_manager.write_watch_tag.assert_called_with("Tag1", 100.0)

    @patch('controlrox.services.plc.bridge.PlcConnectionManager')
    def test_start_only_watches_readable_bindings(self, mock_manager):
        """Test that start only sets up watches for READ and BOTH bindings."""
        self.bridge.add_binding("ReadTag", "obj1", "prop1", direction=BindingDirection.READ)
        self.bridge.add_binding("WriteTag", "obj2", "prop2", direction=BindingDirection.WRITE)
        self.bridge.add_binding("BothTag", "obj3", "prop3", direction=BindingDirection.BOTH)

        self.bridge.start()

        # Should set up watches for ReadTag and BothTag, not WriteTag
        calls = mock_manager.add_watch_tag.call_args_list
        watched_tags = [call[1]['tag_name'] if 'tag_name' in call[1] else call[0][0] for call in calls]

        self.assertIn("ReadTag", watched_tags)
        self.assertIn("BothTag", watched_tags)
        self.assertEqual(len(calls), 2)  # Only 2 watches set up


if __name__ == '__main__':
    unittest.main()
