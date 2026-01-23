"""
Scene management for field device simulations.
"""
from abc import abstractmethod
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable, List, Dict, Optional, Type, Union
from enum import Enum
from pyrox.interfaces import ISceneObjectFactory
from pyrox.models import Scene, SceneObject, SceneObjectFactory


class TagType(str, Enum):
    """Types of PLC tags."""
    BOOL = "BOOL"
    INT = "INT"
    DINT = "DINT"
    REAL = "REAL"
    STRING = "STRING"


@dataclass
class Tag:
    """
    Represents a PLC tag associated with a device.

    Attributes:
        name: Tag name in the PLC (e.g., "Conveyor_1_Run")
        tag_type: Data type of the tag
        value: Current value of the tag
        description: Human-readable description
        device_id: Optional reference to the device that owns this tag
    """
    name: str
    tag_type: TagType
    value: Any = None
    description: str = ""
    device_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert tag to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "tag_type": self.tag_type.value,
            "value": self.value,
            "description": self.description,
            "device_id": self.device_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        """Create tag from dictionary."""
        return cls(
            name=data["name"],
            tag_type=TagType(data["tag_type"]),
            value=data.get("value"),
            description=data.get("description", ""),
            device_id=data.get("device_id"),
        )

    def update_value(self, value: Any) -> None:
        """Update the tag value."""
        self.value = value


class DeviceState(str, Enum):
    """Common device states."""
    OFFLINE = "offline"
    IDLE = "idle"
    RUNNING = "running"
    FAULT = "fault"
    STOPPED = "stopped"


class Device(SceneObject):
    """
    Base class for field devices in the simulation.
    """

    def __init__(
        self,
        id: str,
        name: str,
        device_type: str,
        description: str = "",
        state: DeviceState = DeviceState.OFFLINE,
        tags: Optional[List[Tag]] = None,
        properties: Optional[dict] = None
    ) -> None:
        super().__init__(
            id,
            name,
            'device',
            description,
            properties
        )
        self._device_type = device_type
        self._state: DeviceState = state
        self._tags: List[Tag] = tags if tags is not None else list()
        self.__post_init__()

    def __post_init__(self) -> None:
        """Hook for subclasses to initialize additional attributes."""
        pass

    @property
    def device_type(self) -> str:
        return self._device_type

    @property
    def state(self) -> DeviceState:
        return self._state

    @state.setter
    def state(self, value: DeviceState) -> None:
        self._state = value

    @property
    def tags(self) -> List[Tag]:
        return self._tags

    @tags.setter
    def tags(self, value: List[Tag]) -> None:
        self._tags = value

    def to_dict(self) -> dict:
        """Convert device to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "device_type": self.device_type,
            "name": self.name,
            "state": self.state.value,
            "properties": self.properties,
            "tags": [tag.to_dict() for tag in self.tags],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Device":
        """Create device from dictionary."""
        device = cls(
            id=data["id"],
            name=data["name"],
            device_type=data["device_type"],
            state=DeviceState(data.get("state", DeviceState.OFFLINE.value)),
            properties=data.get("properties", {}),
        )

        # Reconstruct tags
        device.tags = [Tag.from_dict(tag_data) for tag_data in data.get("tags", [])]

        return device

    def add_tag(self, tag: Tag) -> None:
        """Add a tag to this device."""
        tag.device_id = self.id
        self.tags.append(tag)

    def get_tag(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        for tag in self.tags:
            if tag.name == name:
                return tag
        return None

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Update the device state. Called each simulation tick.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass

    @abstractmethod
    def read_inputs(self) -> Dict[str, Any]:
        """
        Read input values from PLC tags.

        Returns:
            Dictionary of tag names to values
        """
        pass

    @abstractmethod
    def write_outputs(self) -> Dict[str, Any]:
        """
        Write output values to PLC tags.

        Returns:
            Dictionary of tag names to values to be written
        """
        pass


class DeviceFactory(SceneObjectFactory):
    """
    Factory for registering and creating device instances.

    Allows custom device types to be registered and instantiated
    from serialized data.
    """

    def create_device(self, data: dict) -> Device:
        """
        Create a device instance from serialized data.

        Args:
            data: Dictionary containing device data

        Returns:
            Device instance

        Raises:
            ValueError: If device_type is not registered
        """
        device_type = data.get("device_type")

        if device_type not in self._registry:
            raise ValueError(
                f"Device type '{device_type}' is not registered. "
                f"Available types: {self.get_registered_types()}"
            )

        device_class = self._registry[device_type]

        if not issubclass(device_class, Device):
            raise TypeError(
                f"Registered class for type '{device_type}' is not a Device subclass"
            )

        return device_class.from_dict(data)


# Global factory instance
_global_factory = DeviceFactory()


def register_device(device_type: str) -> Callable:
    """
    Decorator to register a device class with the global factory.

    Usage:
        @register_device("Motor")
        class Motor(Device):
            ...

    Args:
        device_type: String identifier for the device type

    Returns:
        Decorator function
    """
    def decorator(device_class: Type[Device]) -> Type[Device]:
        _global_factory.register(device_type, device_class)
        return device_class
    return decorator


def get_global_factory() -> DeviceFactory:
    """Get the global device factory instance."""
    return _global_factory


class ControlsScene(Scene):
    """
    Manages a collection of devices and tags for simulation.

    A scene represents a complete simulation environment that can be
    saved to and loaded from JSON files.
    """

    def __init__(
        self,
        name: str = "Untitled Scene",
        description: str = "",
        factory: Optional[ISceneObjectFactory] = None,
        device_factory: Optional[DeviceFactory] = None
    ):
        """
        Initialize a new scene.

        Args:
            name: Scene name
            description: Scene description
        """
        super().__init__(name, description, factory)
        self._tags: Dict[str, Tag] = {}
        self._devices: Dict[str, Device] = {}
        self._device_factory = device_factory if device_factory is not None else get_global_factory()

    @property
    def devices(self) -> Dict[str, Device]:
        return self._devices

    @devices.setter
    def devices(self, value: Dict[str, Device]) -> None:
        self._devices = value

    @property
    def tags(self) -> Dict[str, Tag]:
        return self._tags

    @tags.setter
    def tags(self, value: Dict[str, Tag]) -> None:
        self._tags = value

    @property
    def device_factory(self) -> DeviceFactory:
        return self._device_factory

    def add_device(self, device: Device) -> None:
        """
        Add a device to the scene.

        Args:
            device: Device instance to add

        Raises:
            ValueError: If device ID already exists
        """
        if device.id in self.devices:
            raise ValueError(f"Device with ID '{device.id}' already exists in scene")
        self.devices[device.id] = device

        # Also register device's tags (skip if already exists)
        for tag in device.tags:
            if tag.name not in self.tags:
                self.tags[tag.name] = tag

    def remove_device(self, device_id: str) -> None:
        """
        Remove a device from the scene.

        Args:
            device_id: ID of device to remove
        """
        if device_id in self.devices:
            # Remove associated tags
            device = self.devices[device_id]
            for tag in device.tags:
                self.tags.pop(tag.name, None)

            del self.devices[device_id]

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get a device by ID."""
        return self.devices.get(device_id)

    def get_all_devices(self) -> dict[str, Device]:
        """Get all devices in the scene."""
        return self._devices

    def set_devices(self, devices: dict[str, Device]) -> None:
        """Set the devices in the scene."""
        self._devices = devices

    def add_tag(self, tag: Tag) -> None:
        """
        Add a standalone tag to the scene.

        Args:
            tag: Tag instance to add

        Raises:
            ValueError: If tag name already exists
        """
        if tag.name in self.tags:
            raise ValueError(f"Tag with name '{tag.name}' already exists in scene")

        self.tags[tag.name] = tag

    def remove_tag(self, tag_name: str) -> None:
        """Remove a tag from the scene."""
        self.tags.pop(tag_name, None)

    def get_tag(self, tag_name: str) -> Optional[Tag]:
        """Get a tag by name."""
        return self.tags.get(tag_name)

    def get_all_tags(self) -> List[Tag]:
        """Get all tags (both standalone and device-associated)."""
        all_tags = list(self._tags.values())

        # Add tags from devices
        for device in self.devices.values():
            all_tags.extend(device.tags)

        return all_tags

    def set_tags(self, tags: Dict[str, Tag]) -> None:
        """Set the standalone tags in the scene."""
        self._tags = tags

    def get_device_factory(self) -> DeviceFactory:
        """Get the device factory."""
        return self._device_factory

    def set_device_factory(self, factory: DeviceFactory) -> None:
        """Set the device factory."""
        self._device_factory = factory

    def update(self, delta_time: float) -> None:
        """
        Update all devices in the scene.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        for device in self.devices.values():
            device.update(delta_time)

    @classmethod
    def from_dict(
        cls,
        data: Dict,
        factory: ISceneObjectFactory
    ) -> "ControlsScene":
        """Create scene from dictionary."""
        if factory is None:
            raise ValueError("scene_object_factory is required to load scene")

        scene = cls(
            name=data.get("name", "Untitled Scene"),
            description=data.get("description", ""),
            factory=factory
        )

        # Load scene objects
        for scene_object_data in data.get("scene_objects", []):
            scene_object = factory.create_scene_object(scene_object_data)
            scene.add_scene_object(scene_object)

        # Load standalone tags
        for tag_data in data.get("tags", []):
            tag = Tag.from_dict(tag_data)
            scene.add_tag(tag)

        # Load devices
        for device_data in data.get("devices", []):
            device = Device.from_dict(device_data)
            scene.add_device(device)

        return scene

    def to_dict(self) -> dict:
        """Convert scene to dictionary for JSON serialization."""
        d = super().to_dict()
        d['devices'] = [device.to_dict() for device in self.devices.values()]
        d['tags'] = [tag.to_dict() for tag in self.tags.values()]
        return d

    @classmethod
    def load(
        cls,
        filepath: Union[str, Path],
        factory: ISceneObjectFactory
    ) -> "ControlsScene":
        """Load scene from JSON file."""
        if factory is None:
            raise ValueError("scene_object_factory is required to load scene")

        filepath = Path(filepath)

        with open(filepath, 'r') as f:
            data = json.load(f)

        return cls.from_dict(data, factory=factory)

    def __repr__(self) -> str:
        return (
            f"Scene(name='{self.name}', "
            f"devices={len(self.devices)}, "
            f"tags={len(self.tags)})"
        )
