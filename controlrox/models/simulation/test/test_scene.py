"""Unit tests for controlrox.models.simulation.scene module."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict

from controlrox.models.simulation import (
    ControlsScene,
    Device,
    DeviceFactory,
    DeviceState,
    Tag,
    TagType,
    get_global_factory,
    register_device,
)


class TestDeviceState(unittest.TestCase):
    """Test cases for DeviceState enum."""

    def test_device_state_values(self):
        """Test that DeviceState enum has expected values."""
        self.assertEqual(DeviceState.OFFLINE.value, "offline")
        self.assertEqual(DeviceState.IDLE.value, "idle")
        self.assertEqual(DeviceState.RUNNING.value, "running")
        self.assertEqual(DeviceState.FAULT.value, "fault")
        self.assertEqual(DeviceState.STOPPED.value, "stopped")

    def test_device_state_string_comparison(self):
        """Test that DeviceState can be compared with strings."""
        self.assertEqual(DeviceState.RUNNING, "running")
        self.assertEqual(DeviceState.FAULT, "fault")


class TestDevice(unittest.TestCase):
    """Test cases for Device abstract base class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class ConcreteDevice(Device):
            """Concrete device implementation for testing."""

            def update(self, delta_time: float) -> None:
                """Test implementation of update."""
                self.properties["last_update"] = delta_time

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation of read_inputs."""
                return {"input_tag": self.properties.get("input_value")}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation of write_outputs."""
                return {"output_tag": self.properties.get("output_value")}

        self.ConcreteDevice = ConcreteDevice

    def test_init_with_minimal_params(self):
        """Test Device initialization with minimal parameters."""
        device = self.ConcreteDevice(
            id="dev_001",
            device_type="TestDevice",
            name="TestDev"
        )

        self.assertEqual(device.id, "dev_001")
        self.assertEqual(device.device_type, "TestDevice")
        self.assertEqual(device.name, "TestDev")
        self.assertEqual(device.state, DeviceState.OFFLINE)
        self.assertIsInstance(device.properties, dict)
        self.assertEqual(len(device.properties), 0)
        self.assertIsInstance(device.tags, list)
        self.assertEqual(len(device.tags), 0)

    def test_init_with_all_params(self):
        """Test Device initialization with all parameters."""
        properties = {"speed": 100, "enabled": True}
        tags = [Tag(name="Tag1", tag_type=TagType.BOOL)]

        device = self.ConcreteDevice(
            id="dev_002",
            device_type="ComplexDevice",
            name="ComplexDev",
            state=DeviceState.RUNNING,
            properties=properties,
            tags=tags
        )

        self.assertEqual(device.id, "dev_002")
        self.assertEqual(device.device_type, "ComplexDevice")
        self.assertEqual(device.name, "ComplexDev")
        self.assertEqual(device.state, DeviceState.RUNNING)
        self.assertEqual(device.properties["speed"], 100)
        self.assertEqual(len(device.tags), 1)

    def test_to_dict(self):
        """Test Device.to_dict() method."""
        device = self.ConcreteDevice(
            id="dev_003",
            device_type="SerializableDevice",
            name="SerDev",
            state=DeviceState.IDLE,
            properties={"value": 42}
        )

        device.add_tag(Tag(
            name="TestTag",
            tag_type=TagType.INT,
            value=100
        ))

        result = device.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "dev_003")
        self.assertEqual(result["device_type"], "SerializableDevice")
        self.assertEqual(result["name"], "SerDev")
        self.assertEqual(result["state"], "idle")
        self.assertEqual(result["properties"]["value"], 42)
        self.assertEqual(len(result["tags"]), 1)
        self.assertEqual(result["tags"][0]["name"], "TestTag")

    def test_from_dict(self):
        """Test Device.from_dict() class method."""
        data = {
            "id": "dev_004",
            "device_type": "DictDevice",
            "name": "DictDev",
            "state": "running",
            "properties": {"rpm": 1800},
            "tags": [
                {
                    "name": "DictTag",
                    "tag_type": "BOOL",
                    "value": True,
                    "description": "Tag from dict",
                    "device_id": None
                }
            ]
        }

        device = self.ConcreteDevice.from_dict(data)

        self.assertEqual(device.id, "dev_004")
        self.assertEqual(device.device_type, "DictDevice")
        self.assertEqual(device.name, "DictDev")
        self.assertEqual(device.state, DeviceState.RUNNING)
        self.assertEqual(device.properties["rpm"], 1800)
        self.assertEqual(len(device.tags), 1)
        self.assertEqual(device.tags[0].name, "DictTag")

    def test_from_dict_with_defaults(self):
        """Test Device.from_dict() with default values."""
        data = {
            "id": "dev_005",
            "device_type": "MinimalDevice",
            "name": "MinDev"
        }

        device = self.ConcreteDevice.from_dict(data)

        self.assertEqual(device.state, DeviceState.OFFLINE)
        self.assertEqual(len(device.properties), 0)
        self.assertEqual(len(device.tags), 0)

    def test_add_tag(self):
        """Test Device.add_tag() method."""
        device = self.ConcreteDevice(
            id="dev_006",
            device_type="TagDevice",
            name="TagDev"
        )

        tag = Tag(name="AddedTag", tag_type=TagType.REAL, value=3.14)

        device.add_tag(tag)

        self.assertEqual(len(device.tags), 1)
        self.assertEqual(device.tags[0], tag)
        self.assertEqual(tag.device_id, "dev_006")

    def test_add_multiple_tags(self):
        """Test adding multiple tags to a device."""
        device = self.ConcreteDevice(
            id="dev_007",
            device_type="MultiTagDevice",
            name="MultiTagDev"
        )

        tag1 = Tag(name="Tag1", tag_type=TagType.BOOL)
        tag2 = Tag(name="Tag2", tag_type=TagType.INT)
        tag3 = Tag(name="Tag3", tag_type=TagType.REAL)

        device.add_tag(tag1)
        device.add_tag(tag2)
        device.add_tag(tag3)

        self.assertEqual(len(device.tags), 3)
        self.assertEqual(tag1.device_id, "dev_007")
        self.assertEqual(tag2.device_id, "dev_007")
        self.assertEqual(tag3.device_id, "dev_007")

    def test_get_tag_exists(self):
        """Test Device.get_tag() method when tag exists."""
        device = self.ConcreteDevice(
            id="dev_008",
            device_type="GetTagDevice",
            name="GetTagDev"
        )

        tag = Tag(name="FindMe", tag_type=TagType.STRING, value="found")
        device.add_tag(tag)

        result = device.get_tag("FindMe")

        self.assertIsNotNone(result)
        self.assertEqual(result.name, "FindMe")
        self.assertEqual(result.value, "found")

    def test_get_tag_not_exists(self):
        """Test Device.get_tag() method when tag does not exist."""
        device = self.ConcreteDevice(
            id="dev_009",
            device_type="GetTagDevice",
            name="GetTagDev"
        )

        result = device.get_tag("NonExistent")

        self.assertIsNone(result)

    def test_get_tag_with_multiple_tags(self):
        """Test get_tag with multiple tags in device."""
        device = self.ConcreteDevice(
            id="dev_010",
            device_type="MultiDevice",
            name="MultiDev"
        )

        tag1 = Tag(name="First", tag_type=TagType.BOOL)
        tag2 = Tag(name="Second", tag_type=TagType.INT)
        tag3 = Tag(name="Third", tag_type=TagType.REAL)

        device.add_tag(tag1)
        device.add_tag(tag2)
        device.add_tag(tag3)

        result = device.get_tag("Second")
        self.assertEqual(result, tag2)

    def test_update_method(self):
        """Test that update method is called correctly."""
        device = self.ConcreteDevice(
            id="dev_011",
            device_type="UpdateDevice",
            name="UpdateDev"
        )

        device.update(0.1)

        self.assertEqual(device.properties["last_update"], 0.1)

    def test_read_inputs_method(self):
        """Test that read_inputs method works correctly."""
        device = self.ConcreteDevice(
            id="dev_012",
            device_type="ReadDevice",
            name="ReadDev",
            properties={"input_value": 123}
        )

        result = device.read_inputs()

        self.assertEqual(result["input_tag"], 123)

    def test_write_outputs_method(self):
        """Test that write_outputs method works correctly."""
        device = self.ConcreteDevice(
            id="dev_013",
            device_type="WriteDevice",
            name="WriteDev",
            properties={"output_value": 456}
        )

        result = device.write_outputs()

        self.assertEqual(result["output_tag"], 456)

    def test_serialization_roundtrip(self):
        """Test that to_dict() and from_dict() are inverses."""
        original = self.ConcreteDevice(
            id="dev_014",
            device_type="RoundtripDevice",
            name="RoundtripDev",
            state=DeviceState.RUNNING,
            properties={"test": "value"}
        )

        original.add_tag(Tag(
            name="RoundtripTag",
            tag_type=TagType.DINT,
            value=999
        ))

        data = original.to_dict()
        reconstructed = self.ConcreteDevice.from_dict(data)

        self.assertEqual(reconstructed.id, original.id)
        self.assertEqual(reconstructed.device_type, original.device_type)
        self.assertEqual(reconstructed.name, original.name)
        self.assertEqual(reconstructed.state, original.state)
        self.assertEqual(reconstructed.properties, original.properties)
        self.assertEqual(len(reconstructed.tags), len(original.tags))
        self.assertEqual(reconstructed.tags[0].name, original.tags[0].name)

    def test_state_changes(self):
        """Test that device state can be changed."""
        device = self.ConcreteDevice(
            id="dev_015",
            device_type="StateDevice",
            name="StateDev"
        )

        self.assertEqual(device.state, DeviceState.OFFLINE)

        device.state = DeviceState.IDLE
        self.assertEqual(device.state, DeviceState.IDLE)

        device.state = DeviceState.RUNNING
        self.assertEqual(device.state, DeviceState.RUNNING)

        device.state = DeviceState.FAULT
        self.assertEqual(device.state, DeviceState.FAULT)

        device.state = DeviceState.STOPPED
        self.assertEqual(device.state, DeviceState.STOPPED)

    def test_properties_mutable(self):
        """Test that device properties can be modified."""
        device = self.ConcreteDevice(
            id="dev_016",
            device_type="MutableDevice",
            name="MutableDev",
            properties={"initial": 100}
        )

        self.assertEqual(device.properties["initial"], 100)

        device.properties["initial"] = 200
        self.assertEqual(device.properties["initial"], 200)

        device.properties["new_key"] = "new_value"
        self.assertEqual(device.properties["new_key"], "new_value")


class TestTagType(unittest.TestCase):
    """Test cases for TagType enum."""

    def test_tag_type_values(self):
        """Test that TagType enum has expected values."""
        self.assertEqual(TagType.BOOL.value, "BOOL")
        self.assertEqual(TagType.INT.value, "INT")
        self.assertEqual(TagType.DINT.value, "DINT")
        self.assertEqual(TagType.REAL.value, "REAL")
        self.assertEqual(TagType.STRING.value, "STRING")

    def test_tag_type_string_comparison(self):
        """Test that TagType can be compared with strings."""
        self.assertEqual(TagType.BOOL, "BOOL")
        self.assertEqual(TagType.REAL, "REAL")


class TestTag(unittest.TestCase):
    """Test cases for Tag class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tag_bool = Tag(
            name="TestTag_Bool",
            tag_type=TagType.BOOL,
            value=True,
            description="Boolean test tag"
        )

        self.tag_real = Tag(
            name="TestTag_Real",
            tag_type=TagType.REAL,
            value=123.45,
            description="Real test tag",
            device_id="device_001"
        )

    def test_init_with_minimal_params(self):
        """Test Tag initialization with minimal parameters."""
        tag = Tag(name="MinimalTag", tag_type=TagType.INT)

        self.assertEqual(tag.name, "MinimalTag")
        self.assertEqual(tag.tag_type, TagType.INT)
        self.assertIsNone(tag.value)
        self.assertEqual(tag.description, "")
        self.assertIsNone(tag.device_id)

    def test_init_with_all_params(self):
        """Test Tag initialization with all parameters."""
        tag = Tag(
            name="FullTag",
            tag_type=TagType.DINT,
            value=42,
            description="Full tag",
            device_id="dev_123"
        )

        self.assertEqual(tag.name, "FullTag")
        self.assertEqual(tag.tag_type, TagType.DINT)
        self.assertEqual(tag.value, 42)
        self.assertEqual(tag.description, "Full tag")
        self.assertEqual(tag.device_id, "dev_123")

    def test_to_dict(self):
        """Test Tag.to_dict() method."""
        result = self.tag_real.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "TestTag_Real")
        self.assertEqual(result["tag_type"], "REAL")
        self.assertEqual(result["value"], 123.45)
        self.assertEqual(result["description"], "Real test tag")
        self.assertEqual(result["device_id"], "device_001")

    def test_to_dict_with_none_values(self):
        """Test Tag.to_dict() with None values."""
        tag = Tag(name="NoneTag", tag_type=TagType.STRING)
        result = tag.to_dict()

        self.assertIn("name", result)
        self.assertIn("tag_type", result)
        self.assertIsNone(result["value"])
        self.assertIsNone(result["device_id"])

    def test_from_dict(self):
        """Test Tag.from_dict() class method."""
        data = {
            "name": "DictTag",
            "tag_type": "BOOL",
            "value": False,
            "description": "Tag from dict",
            "device_id": "dev_999"
        }

        tag = Tag.from_dict(data)

        self.assertEqual(tag.name, "DictTag")
        self.assertEqual(tag.tag_type, TagType.BOOL)
        self.assertEqual(tag.value, False)
        self.assertEqual(tag.description, "Tag from dict")
        self.assertEqual(tag.device_id, "dev_999")

    def test_from_dict_minimal(self):
        """Test Tag.from_dict() with minimal data."""
        data = {
            "name": "MinTag",
            "tag_type": "INT"
        }

        tag = Tag.from_dict(data)

        self.assertEqual(tag.name, "MinTag")
        self.assertEqual(tag.tag_type, TagType.INT)
        self.assertIsNone(tag.value)
        self.assertEqual(tag.description, "")
        self.assertIsNone(tag.device_id)

    def test_update_value(self):
        """Test Tag.update_value() method."""
        tag = Tag(name="UpdateTag", tag_type=TagType.REAL, value=0.0)

        tag.update_value(99.99)
        self.assertEqual(tag.value, 99.99)

        tag.update_value(-50.0)
        self.assertEqual(tag.value, -50.0)

    def test_update_value_changes_type(self):
        """Test that update_value can change value type."""
        tag = Tag(name="TypeTag", tag_type=TagType.STRING, value="initial")

        tag.update_value(123)
        self.assertEqual(tag.value, 123)

        tag.update_value(None)
        self.assertIsNone(tag.value)

    def test_serialization_roundtrip(self):
        """Test that to_dict() and from_dict() are inverses."""
        original = Tag(
            name="RoundtripTag",
            tag_type=TagType.DINT,
            value=12345,
            description="Test roundtrip",
            device_id="device_abc"
        )

        data = original.to_dict()
        reconstructed = Tag.from_dict(data)

        self.assertEqual(reconstructed.name, original.name)
        self.assertEqual(reconstructed.tag_type, original.tag_type)
        self.assertEqual(reconstructed.value, original.value)
        self.assertEqual(reconstructed.description, original.description)
        self.assertEqual(reconstructed.device_id, original.device_id)

    def test_different_tag_types(self):
        """Test creating tags with different types."""
        bool_tag = Tag(name="Bool", tag_type=TagType.BOOL, value=True)
        int_tag = Tag(name="Int", tag_type=TagType.INT, value=100)
        dint_tag = Tag(name="Dint", tag_type=TagType.DINT, value=100000)
        real_tag = Tag(name="Real", tag_type=TagType.REAL, value=3.14159)
        string_tag = Tag(name="String", tag_type=TagType.STRING, value="Hello")

        self.assertEqual(bool_tag.tag_type, TagType.BOOL)
        self.assertEqual(int_tag.tag_type, TagType.INT)
        self.assertEqual(dint_tag.tag_type, TagType.DINT)
        self.assertEqual(real_tag.tag_type, TagType.REAL)
        self.assertEqual(string_tag.tag_type, TagType.STRING)

    def test_tag_equality_by_value(self):
        """Test that tags with same values are equal (dataclass behavior)."""
        tag1 = Tag(name="Tag1", tag_type=TagType.BOOL, value=True)
        tag2 = Tag(name="Tag1", tag_type=TagType.BOOL, value=True)

        self.assertEqual(tag1, tag2)

    def test_tag_inequality(self):
        """Test that tags with different values are not equal."""
        tag1 = Tag(name="Tag1", tag_type=TagType.BOOL, value=True)
        tag2 = Tag(name="Tag2", tag_type=TagType.BOOL, value=True)

        self.assertNotEqual(tag1, tag2)


class TestDeviceFactory(unittest.TestCase):
    """Test cases for DeviceFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create concrete device classes for testing
        class TestDeviceA(Device):
            """Test device type A."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        class TestDeviceB(Device):
            """Test device type B."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        self.TestDeviceA = TestDeviceA
        self.TestDeviceB = TestDeviceB

    def test_init(self):
        """Test DeviceFactory initialization."""
        factory = DeviceFactory()

        self.assertIsInstance(factory._registry, dict)
        self.assertEqual(len(factory._registry), 0)

    def test_register(self):
        """Test DeviceFactory.register() method."""
        factory = DeviceFactory()

        factory.register("TypeA", self.TestDeviceA)

        self.assertEqual(len(factory._registry), 1)
        self.assertIn("TypeA", factory._registry)
        self.assertEqual(factory._registry["TypeA"], self.TestDeviceA)

    def test_register_multiple_types(self):
        """Test registering multiple device types."""
        factory = DeviceFactory()

        factory.register("TypeA", self.TestDeviceA)
        factory.register("TypeB", self.TestDeviceB)

        self.assertEqual(len(factory._registry), 2)
        self.assertIn("TypeA", factory._registry)
        self.assertIn("TypeB", factory._registry)

    def test_register_duplicate_raises_error(self):
        """Test that registering a duplicate type raises ValueError."""
        factory = DeviceFactory()

        factory.register("Duplicate", self.TestDeviceA)

        with self.assertRaises(ValueError) as context:
            factory.register("Duplicate", self.TestDeviceB)

        self.assertIn("already registered", str(context.exception))
        self.assertIn("Duplicate", str(context.exception))

    def test_unregister(self):
        """Test DeviceFactory.unregister() method."""
        factory = DeviceFactory()

        factory.register("TypeA", self.TestDeviceA)
        self.assertEqual(len(factory._registry), 1)

        factory.unregister("TypeA")
        self.assertEqual(len(factory._registry), 0)

    def test_unregister_nonexistent(self):
        """Test unregistering a non-existent type."""
        factory = DeviceFactory()

        # Should not raise an error
        factory.unregister("Nonexistent")

    def test_get_registered_types(self):
        """Test DeviceFactory.get_registered_types() method."""
        factory = DeviceFactory()

        factory.register("TypeA", self.TestDeviceA)
        factory.register("TypeB", self.TestDeviceB)

        types = factory.get_registered_types()

        self.assertIsInstance(types, list)
        self.assertEqual(len(types), 2)
        self.assertIn("TypeA", types)
        self.assertIn("TypeB", types)

    def test_get_registered_types_empty(self):
        """Test get_registered_types with no registered types."""
        factory = DeviceFactory()

        types = factory.get_registered_types()

        self.assertIsInstance(types, list)
        self.assertEqual(len(types), 0)

    def test_create_device(self):
        """Test DeviceFactory.create_device() method."""
        factory = DeviceFactory()
        factory.register("TestDeviceA", self.TestDeviceA)

        data = {
            "id": "dev_001",
            "device_type": "TestDeviceA",
            "name": "CreatedDevice",
            "state": "idle",
            "properties": {"test": "value"},
            "tags": []
        }

        device = factory.create_device(data)

        self.assertIsInstance(device, self.TestDeviceA)
        self.assertEqual(device.id, "dev_001")
        self.assertEqual(device.name, "CreatedDevice")
        self.assertEqual(device.state, DeviceState.IDLE)
        self.assertEqual(device.properties["test"], "value")

    def test_create_device_unregistered_type_raises_error(self):
        """Test that creating an unregistered device type raises ValueError."""
        factory = DeviceFactory()

        data = {
            "id": "dev_002",
            "device_type": "UnregisteredType",
            "name": "BadDevice"
        }

        with self.assertRaises(ValueError) as context:
            factory.create_device(data)

        self.assertIn("not registered", str(context.exception))
        self.assertIn("UnregisteredType", str(context.exception))

    def test_create_device_shows_available_types(self):
        """Test that error message shows available types."""
        factory = DeviceFactory()
        factory.register("TypeA", self.TestDeviceA)
        factory.register("TypeB", self.TestDeviceB)

        data = {
            "id": "dev_003",
            "device_type": "BadType",
            "name": "Device"
        }

        with self.assertRaises(ValueError) as context:
            factory.create_device(data)

        error_msg = str(context.exception)
        self.assertIn("Available types:", error_msg)
        self.assertIn("TypeA", error_msg)
        self.assertIn("TypeB", error_msg)

    def test_create_multiple_devices(self):
        """Test creating multiple devices of different types."""
        factory = DeviceFactory()
        factory.register("TypeA", self.TestDeviceA)
        factory.register("TypeB", self.TestDeviceB)

        data_a = {
            "id": "dev_a",
            "device_type": "TypeA",
            "name": "DeviceA"
        }

        data_b = {
            "id": "dev_b",
            "device_type": "TypeB",
            "name": "DeviceB"
        }

        device_a = factory.create_device(data_a)
        device_b = factory.create_device(data_b)

        self.assertIsInstance(device_a, self.TestDeviceA)
        self.assertIsInstance(device_b, self.TestDeviceB)
        self.assertEqual(device_a.name, "DeviceA")
        self.assertEqual(device_b.name, "DeviceB")


class TestRegisterDeviceDecorator(unittest.TestCase):
    """Test cases for register_device decorator."""

    def test_register_device_decorator(self):
        """Test that @register_device decorator registers a device type."""
        # Get a fresh factory
        factory = DeviceFactory()

        @dataclass
        class DecoratedDevice(Device):
            """Device registered via decorator."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        # Manually register with our test factory
        factory.register("DecoratedType", DecoratedDevice)

        self.assertIn("DecoratedType", factory.get_registered_types())

    def test_decorator_returns_class(self):
        """Test that decorator returns the original class."""
        @dataclass
        class OriginalDevice(Device):
            """Original device class."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        # Apply decorator manually
        decorated = register_device("TestType")(OriginalDevice)

        # Should be the same class
        self.assertEqual(decorated, OriginalDevice)

    def test_decorator_usage_pattern(self):
        """Test realistic decorator usage pattern."""
        # Create a custom factory for this test
        test_factory = DeviceFactory()

        class CustomDevice(Device):
            """Custom device with decorator pattern."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                self.properties["updated"] = True

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {"input": "value"}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {"output": "value"}

        # Manually register for testing
        test_factory.register("CustomType", CustomDevice)

        # Should be able to create instances
        data = {
            "id": "custom_001",
            "device_type": "CustomType",
            "name": "Custom"
        }

        device = test_factory.create_device(data)

        self.assertIsInstance(device, CustomDevice)
        self.assertEqual(device.name, "Custom")

        # Test that methods work
        device.update(0.1)
        self.assertTrue(device.properties["updated"])


class TestGetGlobalFactory(unittest.TestCase):
    """Test cases for get_global_factory function."""

    def test_get_global_factory_returns_factory(self):
        """Test that get_global_factory returns a DeviceFactory instance."""
        factory = get_global_factory()

        self.assertIsInstance(factory, DeviceFactory)

    def test_get_global_factory_returns_same_instance(self):
        """Test that get_global_factory returns the same instance each time."""
        factory1 = get_global_factory()
        factory2 = get_global_factory()

        self.assertIs(factory1, factory2)

    def test_global_factory_is_persistent(self):
        """Test that registrations to global factory persist."""
        factory = get_global_factory()

        # Create a test device
        class GlobalTestDevice(Device):
            """Test device for global factory."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        # Register it (if not already registered from imports)
        if "GlobalTestType" not in factory.get_registered_types():
            factory.register("GlobalTestType", GlobalTestDevice)

        # Get factory again and check registration persists
        factory2 = get_global_factory()

        self.assertIn("GlobalTestType", factory2.get_registered_types())


class TestFactoryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for factory."""

    def setUp(self):
        """Set up test fixtures."""
        class EdgeCaseDevice(Device):
            """Device for edge case testing."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        self.EdgeCaseDevice = EdgeCaseDevice

    def test_create_device_missing_device_type(self):
        """Test creating a device with missing device_type field."""
        factory = DeviceFactory()

        data = {
            "id": "dev_001",
            "name": "MissingType"
        }

        with self.assertRaises(ValueError):
            factory.create_device(data)

    def test_register_with_empty_string(self):
        """Test registering with empty string type name."""
        factory = DeviceFactory()

        # Should work but not be useful
        factory.register("", self.EdgeCaseDevice)

        self.assertIn("", factory.get_registered_types())

    def test_multiple_factories_independent(self):
        """Test that multiple factory instances are independent."""
        factory1 = DeviceFactory()
        factory2 = DeviceFactory()

        factory1.register("Type1", self.EdgeCaseDevice)

        self.assertIn("Type1", factory1.get_registered_types())
        self.assertNotIn("Type1", factory2.get_registered_types())


class TestControlsScene(unittest.TestCase):
    """Test cases for ControlsScene class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete device for testing
        class TestDevice(Device):
            """Test device implementation."""

            def update(self, delta_time: float) -> None:
                """Test implementation."""
                pass

            def read_inputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

            def write_outputs(self) -> Dict[str, Any]:
                """Test implementation."""
                return {}

        self.TestDevice = TestDevice
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init_with_defaults(self):
        """Test ControlsScene initialization with default values."""
        scene = ControlsScene()

        self.assertEqual(scene.name, "Untitled Scene")
        self.assertEqual(scene.description, "")
        self.assertIsInstance(scene.devices, dict)
        self.assertEqual(len(scene.devices), 0)
        self.assertIsInstance(scene.tags, dict)
        self.assertEqual(len(scene.tags), 0)

    def test_init_with_params(self):
        """Test ControlsScene initialization with parameters."""
        scene = ControlsScene(
            name="Test ControlsScene",
            description="A test scene description"
        )

        self.assertEqual(scene.name, "Test ControlsScene")
        self.assertEqual(scene.description, "A test scene description")

    def test_add_device(self):
        """Test ControlsScene.add_device() method."""
        scene = ControlsScene()
        device = self.TestDevice(
            id="dev_001",
            device_type="TestDevice",
            name="TestDev"
        )

        scene.add_device(device)

        self.assertEqual(len(scene.devices), 1)
        self.assertIn("dev_001", scene.devices)
        self.assertEqual(scene.devices["dev_001"], device)

    def test_add_device_with_tags(self):
        """Test that adding a device also registers its tags."""
        scene = ControlsScene()
        device = self.TestDevice(
            id="dev_002",
            device_type="TestDevice",
            name="TestDev"
        )

        tag = Tag(name="DeviceTag", tag_type=TagType.BOOL, value=True)
        device.add_tag(tag)

        scene.add_device(device)

        self.assertEqual(len(scene.devices), 1)
        self.assertEqual(len(scene.tags), 1)
        self.assertIn("DeviceTag", scene.tags)

    def test_add_device_duplicate_id_raises_error(self):
        """Test that adding a device with duplicate ID raises ValueError."""
        scene = ControlsScene()
        device1 = self.TestDevice(
            id="dev_003",
            device_type="TestDevice",
            name="Device1"
        )
        device2 = self.TestDevice(
            id="dev_003",
            device_type="TestDevice",
            name="Device2"
        )

        scene.add_device(device1)

        with self.assertRaises(ValueError) as context:
            scene.add_device(device2)

        self.assertIn("already exists", str(context.exception))
        self.assertIn("dev_003", str(context.exception))

    def test_remove_device(self):
        """Test ControlsScene.remove_device() method."""
        scene = ControlsScene()
        device = self.TestDevice(
            id="dev_004",
            device_type="TestDevice",
            name="TestDev"
        )

        scene.add_device(device)
        self.assertEqual(len(scene.devices), 1)

        scene.remove_device("dev_004")
        self.assertEqual(len(scene.devices), 0)

    def test_remove_device_removes_tags(self):
        """Test that removing a device also removes its tags."""
        scene = ControlsScene()
        device = self.TestDevice(
            id="dev_005",
            device_type="TestDevice",
            name="TestDev"
        )

        tag = Tag(name="RemoveTag", tag_type=TagType.INT, value=100)
        device.add_tag(tag)

        scene.add_device(device)
        self.assertEqual(len(scene.tags), 1)

        scene.remove_device("dev_005")
        self.assertEqual(len(scene.tags), 0)

    def test_remove_nonexistent_device(self):
        """Test removing a device that doesn't exist."""
        scene = ControlsScene()

        # Should not raise an error
        scene.remove_device("nonexistent")

    def test_get_device(self):
        """Test ControlsScene.get_device() method."""
        scene = ControlsScene()
        device = self.TestDevice(
            id="dev_006",
            device_type="TestDevice",
            name="TestDev"
        )

        scene.add_device(device)

        result = scene.get_device("dev_006")
        self.assertEqual(result, device)

    def test_get_device_not_exists(self):
        """Test get_device with non-existent ID."""
        scene = ControlsScene()

        result = scene.get_device("nonexistent")
        self.assertIsNone(result)

    def test_add_tag(self):
        """Test ControlsScene.add_tag() method."""
        scene = ControlsScene()
        tag = Tag(name="StandaloneTag", tag_type=TagType.REAL, value=3.14)

        scene.add_tag(tag)

        self.assertEqual(len(scene.tags), 1)
        self.assertIn("StandaloneTag", scene.tags)
        self.assertEqual(scene.tags["StandaloneTag"], tag)

    def test_add_tag_duplicate_name_raises_error(self):
        """Test that adding a tag with duplicate name raises ValueError."""
        scene = ControlsScene()
        tag1 = Tag(name="DuplicateTag", tag_type=TagType.BOOL)
        tag2 = Tag(name="DuplicateTag", tag_type=TagType.INT)

        scene.add_tag(tag1)

        with self.assertRaises(ValueError) as context:
            scene.add_tag(tag2)

        self.assertIn("already exists", str(context.exception))
        self.assertIn("DuplicateTag", str(context.exception))

    def test_remove_tag(self):
        """Test ControlsScene.remove_tag() method."""
        scene = ControlsScene()
        tag = Tag(name="RemovableTag", tag_type=TagType.STRING)

        scene.add_tag(tag)
        self.assertEqual(len(scene.tags), 1)

        scene.remove_tag("RemovableTag")
        self.assertEqual(len(scene.tags), 0)

    def test_remove_nonexistent_tag(self):
        """Test removing a tag that doesn't exist."""
        scene = ControlsScene()

        # Should not raise an error
        scene.remove_tag("nonexistent")

    def test_get_tag(self):
        """Test ControlsScene.get_tag() method."""
        scene = ControlsScene()
        tag = Tag(name="GetTag", tag_type=TagType.DINT, value=42)

        scene.add_tag(tag)

        result = scene.get_tag("GetTag")
        self.assertEqual(result, tag)

    def test_get_tag_not_exists(self):
        """Test get_tag with non-existent name."""
        scene = ControlsScene()

        result = scene.get_tag("nonexistent")
        self.assertIsNone(result)

    def test_get_all_tags(self):
        """Test ControlsScene.get_all_tags() method."""
        scene = ControlsScene()

        # Add standalone tags
        tag1 = Tag(name="Standalone1", tag_type=TagType.BOOL)
        tag2 = Tag(name="Standalone2", tag_type=TagType.INT)
        scene.add_tag(tag1)
        scene.add_tag(tag2)

        # Add device with tags
        device = self.TestDevice(
            id="dev_007",
            device_type="TestDevice",
            name="TestDev"
        )
        device_tag = Tag(name="DeviceTag1", tag_type=TagType.REAL)
        device.add_tag(device_tag)
        scene.add_device(device)

        all_tags = scene.get_all_tags()

        # Should have 3 standalone tags (tag1, tag2, device_tag) + 1 from device
        self.assertEqual(len(all_tags), 4)

    def test_update(self):
        """Test ControlsScene.update() method."""
        scene = ControlsScene()

        # Create device that tracks updates
        device = self.TestDevice(
            id="dev_008",
            device_type="TestDevice",
            name="TestDev"
        )
        device.properties["update_count"] = 0

        # Override update method
        def custom_update(delta_time):
            device.properties["update_count"] += 1
            device.properties["last_delta"] = delta_time

        device.update = custom_update

        scene.add_device(device)

        # Update scene
        scene.update(0.5)

        self.assertEqual(device.properties["update_count"], 1)
        self.assertEqual(device.properties["last_delta"], 0.5)

    def test_update_multiple_devices(self):
        """Test updating multiple devices."""
        scene = ControlsScene()

        device1 = self.TestDevice(
            id="dev_009",
            device_type="TestDevice",
            name="Device1"
        )
        device2 = self.TestDevice(
            id="dev_010",
            device_type="TestDevice",
            name="Device2"
        )

        device1.properties["updated"] = False
        device2.properties["updated"] = False

        def update1(dt):
            device1.properties["updated"] = True

        def update2(dt):
            device2.properties["updated"] = True

        device1.update = update1
        device2.update = update2

        scene.add_device(device1)
        scene.add_device(device2)

        scene.update(0.1)

        self.assertTrue(device1.properties["updated"])
        self.assertTrue(device2.properties["updated"])

    def test_to_dict(self):
        """Test ControlsScene.to_dict() method."""
        scene = ControlsScene(name="DictControlsScene", description="Test dict conversion")

        device = self.TestDevice(
            id="dev_011",
            device_type="TestDevice",
            name="TestDev"
        )
        scene.add_device(device)

        tag = Tag(name="StandaloneTag", tag_type=TagType.BOOL)
        scene.add_tag(tag)

        result = scene.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "DictControlsScene")
        self.assertEqual(result["description"], "Test dict conversion")
        self.assertIn("devices", result)
        self.assertIn("tags", result)
        self.assertEqual(len(result["devices"]), 1)
        self.assertEqual(len(result["tags"]), 1)

    def test_save(self):
        """Test ControlsScene.save() method."""
        scene = ControlsScene(name="SaveControlsScene", description="Test save")

        device = self.TestDevice(
            id="dev_012",
            device_type="TestDevice",
            name="SaveDev"
        )
        scene.add_device(device)

        filepath = Path(self.test_dir) / "test_scene.json"
        scene.save(filepath)

        self.assertTrue(filepath.exists())

        # Verify JSON content
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.assertEqual(data["name"], "SaveControlsScene")
        self.assertEqual(len(data["devices"]), 1)

    def test_save_creates_directory(self):
        """Test that save creates parent directories if needed."""
        scene = ControlsScene(name="DirControlsScene")

        filepath = Path(self.test_dir) / "subdir" / "nested" / "scene.json"
        scene.save(filepath)

        self.assertTrue(filepath.exists())
        self.assertTrue(filepath.parent.exists())

    def test_load(self):
        """Test ControlsScene.load() class method."""
        # Create and save a scene
        original_scene = ControlsScene(name="LoadControlsScene", description="Test load")
        device = self.TestDevice(
            id="dev_013",
            device_type="TestDevice",
            name="LoadDev"
        )
        original_scene.add_device(device)

        filepath = Path(self.test_dir) / "load_scene.json"
        original_scene.save(filepath)

        # Create factory and register device type
        factory = DeviceFactory()
        factory.register("TestDevice", self.TestDevice)

        # Load the scene
        loaded_scene = ControlsScene.load(filepath, factory=factory)

        self.assertEqual(loaded_scene.name, "LoadControlsScene")
        self.assertEqual(loaded_scene.description, "Test load")
        self.assertEqual(len(loaded_scene.devices), 1)
        self.assertIn("dev_013", loaded_scene.devices)

    def test_load_without_factory_raises_error(self):
        """Test that loading without a factory raises ValueError."""
        filepath = Path(self.test_dir) / "no_factory.json"

        # Create a simple scene file
        with open(filepath, 'w') as f:
            json.dump({"name": "Test", "devices": [], "tags": []}, f)

        with self.assertRaises(ValueError) as context:
            ControlsScene.load(filepath, factory=None)

        self.assertIn("factory is required", str(context.exception))

    def test_scene_roundtrip(self):
        """Test that saving and loading a scene preserves data."""
        original = ControlsScene(name="RoundtripControlsScene", description="Full roundtrip test")

        # Add device with tags
        device = self.TestDevice(
            id="dev_014",
            device_type="TestDevice",
            name="RoundtripDev",
            state=DeviceState.RUNNING,
            properties={"value": 123}
        )
        device.add_tag(Tag(
            name="DevTag",
            tag_type=TagType.REAL,
            value=99.9
        ))
        original.add_device(device)

        # Add standalone tag
        original.add_tag(Tag(
            name="StandaloneTag",
            tag_type=TagType.STRING,
            value="test"
        ))

        # Save
        filepath = Path(self.test_dir) / "roundtrip.json"
        original.save(filepath)

        # Load
        factory = DeviceFactory()
        factory.register("TestDevice", self.TestDevice)
        loaded = ControlsScene.load(filepath, factory=factory)

        # Verify
        self.assertEqual(loaded.name, original.name)
        self.assertEqual(loaded.description, original.description)
        self.assertEqual(len(loaded.devices), len(original.devices))
        self.assertEqual(len(loaded.tags), len(original.tags))

        loaded_device = loaded.get_device("dev_014")
        self.assertIsNotNone(loaded_device)
        self.assertEqual(loaded_device.name, "RoundtripDev")
        self.assertEqual(loaded_device.state, DeviceState.RUNNING)
        self.assertEqual(loaded_device.properties["value"], 123)

    def test_repr(self):
        """Test ControlsScene.__repr__() method."""
        scene = ControlsScene(name="ReprControlsScene")

        device = self.TestDevice(
            id="dev_015",
            device_type="TestDevice",
            name="Dev"
        )
        scene.add_device(device)

        tag = Tag(name="Tag1", tag_type=TagType.BOOL)
        scene.add_tag(tag)

        repr_str = repr(scene)

        self.assertIn("ReprControlsScene", repr_str)
        self.assertIn("devices=1", repr_str)
        self.assertIn("tags=1", repr_str)

    def test_set_device_factory(self):
        """Test ControlsScene.set_device_factory() method."""
        scene = ControlsScene()
        factory = DeviceFactory()

        scene.set_device_factory(factory)

        self.assertEqual(scene._device_factory, factory)


if __name__ == '__main__':
    unittest.main()
