"""PLC Scene Bridge Service.

Bridges PLC tags with scene objects, enabling real-time bidirectional synchronization
between PLCs and physics simulation scenes.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any, Optional
from pyrox.services.logging import log
from pyrox.interfaces import IScene
from controlrox.services.plc.connection import PlcConnectionManager
from pylogix.lgx_response import Response


class BindingDirection(Enum):
    """Direction of data flow for PLC-Scene bindings."""
    READ = "read"  # PLC → Scene (PLC controls scene)
    WRITE = "write"  # Scene → PLC (Scene updates PLC)
    BOTH = "both"  # Bidirectional synchronization


@dataclass
class PlcTagBinding:
    """Represents a binding between a PLC tag and a scene object property.

    Examples:
        # Simple binding: PLC tag directly controls object property
        PlcTagBinding(
            tag_name="Conveyor1_Speed",
            object_id="conveyor_1",
            property_path="speed",
            direction=BindingDirection.READ
        )

        # Complex binding: With transformation
        PlcTagBinding(
            tag_name="Robot1_Position_X",
            object_id="robot_1",
            property_path="position.x",
            direction=BindingDirection.READ,
            transform=lambda x: x / 1000.0  # Convert mm to meters
        )

        # Bidirectional: Sync both ways
        PlcTagBinding(
            tag_name="Sensor1_Active",
            object_id="sensor_1",
            property_path="is_active",
            direction=BindingDirection.BOTH
        )
    """
    tag_name: str
    object_id: str
    property_path: str
    direction: BindingDirection = BindingDirection.READ
    data_type: int = 0
    transform: Optional[Callable[[Any], Any]] = None
    inverse_transform: Optional[Callable[[Any], Any]] = None
    enabled: bool = True
    last_plc_value: Any = None
    last_scene_value: Any = None
    # Metadata
    description: str = ""
    tags: list[str] = field(default_factory=list)


class PlcSceneBridge:
    """Service that bridges PLC tags with scene objects.

    This service enables:
    - Real-time synchronization between PLC tags and scene object properties
    - Bidirectional data flow (PLC → Scene and Scene → PLC)
    - Value transformation and scaling
    - Connection management through GUI
    - Integration with existing PLC watch table and scene runner

    Usage Examples:
        # Initialize bridge with scene
        bridge = PlcSceneBridge(scene)

        # READ: PLC controls scene (PLC → Scene)
        bridge.add_binding(
            tag_name="Conveyor1_Speed",
            object_id="conveyor_1",
            property_path="belt_speed",
            direction=BindingDirection.READ
        )

        # WRITE: Scene updates PLC (Scene → PLC)
        bridge.add_binding(
            tag_name="Sensor1_Triggered",
            object_id="sensor_1",
            property_path="is_triggered",
            direction=BindingDirection.WRITE
        )

        # BOTH: Bidirectional sync
        bridge.add_binding(
            tag_name="Robot1_Position",
            object_id="robot_1",
            property_path="x",
            direction=BindingDirection.BOTH,
            transform=lambda x: x / 1000.0,  # PLC → Scene (mm to m)
            inverse_transform=lambda x: x * 1000.0  # Scene → PLC (m to mm)
        )

        # Start synchronization (automatic read/write on PLC ticks)
        bridge.start()

        # Optional: Control write behavior
        bridge.set_write_enabled(True)
        bridge.set_write_throttle(100)  # Min 100ms between writes
    """

    def __init__(self, scene: Optional[IScene] = None):
        """Initialize the PLC-Scene bridge.

        Args:
            scene: The scene to bind PLC tags to
        """
        self._scene = scene
        self._bindings: dict[str, PlcTagBinding] = {}
        self._active = False
        self._write_enabled = True
        self._last_write_time: dict[str, float] = {}
        self._write_throttle_ms = 100  # Minimum time between writes for same tag
        self._tick_callback_registered = False

    def set_scene(self, scene: Optional[IScene]) -> None:
        """Set the scene for bindings.

        Args:
            scene: The scene to bind to
        """
        if self._active:
            self.stop()
        self._scene = scene

    def add_binding(
        self,
        tag_name: str,
        object_id: str,
        property_path: str,
        direction: BindingDirection = BindingDirection.READ,
        data_type: int = 0,
        transform: Optional[Callable[[Any], Any]] = None,
        inverse_transform: Optional[Callable[[Any], Any]] = None,
        description: str = ""
    ) -> PlcTagBinding:
        """Add a binding between a PLC tag and scene object property.

        Args:
            tag_name: PLC tag name
            object_id: Scene object ID
            property_path: Object property path (e.g., 'speed', 'position.x')
            direction: Data flow direction
            data_type: PyLogix data type code
            transform: Function to transform PLC value to scene value
            inverse_transform: Function to transform scene value to PLC value
            description: Human-readable description of binding

        Returns:
            The created PlcTagBinding
        """
        binding = PlcTagBinding(
            tag_name=tag_name,
            object_id=object_id,
            property_path=property_path,
            direction=direction,
            data_type=data_type,
            transform=transform,
            inverse_transform=inverse_transform,
            description=description
        )

        binding_key = f"{tag_name}::{object_id}::{property_path}"
        self._bindings[binding_key] = binding

        # If already active, set up the watch immediately
        if self._active and direction in (BindingDirection.READ, BindingDirection.BOTH):
            self._setup_watch_for_binding(binding)

        log(self).info(
            f"Added binding: {tag_name} → {object_id}.{property_path} ({direction.value})"
        )
        return binding

    def remove_binding(self, tag_name: str, object_id: str, property_path: str) -> bool:
        """Remove a binding.

        Args:
            tag_name: PLC tag name
            object_id: Scene object ID
            property_path: Property path

        Returns:
            True if binding was removed, False if not found
        """
        binding_key = f"{tag_name}::{object_id}::{property_path}"
        if binding_key in self._bindings:
            binding = self._bindings[binding_key]

            # Remove from watch table if it was being watched
            if self._active and binding.direction in (BindingDirection.READ, BindingDirection.BOTH):
                # Only remove if no other bindings use this tag
                if not any(b.tag_name == tag_name for k, b in self._bindings.items() if k != binding_key):
                    PlcConnectionManager.remove_watch_tag(tag_name)

            del self._bindings[binding_key]
            log(self).info(f"Removed binding: {binding_key}")
            return True
        return False

    def clear_bindings(self) -> None:
        """Clear all bindings."""
        if self._active:
            self.stop()
        self._bindings.clear()
        log(self).info("Cleared all bindings")

    def get_bindings(self) -> list[PlcTagBinding]:
        """Get all bindings.

        Returns:
            List of all PlcTagBinding objects
        """
        return list(self._bindings.values())

    def get_bindings_for_object(self, object_id: str) -> list[PlcTagBinding]:
        """Get all bindings for a specific scene object.

        Args:
            object_id: Scene object ID

        Returns:
            List of bindings for the object
        """
        return [b for b in self._bindings.values() if b.object_id == object_id]

    def get_bindings_for_tag(self, tag_name: str) -> list[PlcTagBinding]:
        """Get all bindings for a specific PLC tag.

        Args:
            tag_name: PLC tag name

        Returns:
            List of bindings for the tag
        """
        return [b for b in self._bindings.values() if b.tag_name == tag_name]

    def is_active(self) -> bool:
        """Check if the bridge is currently active.

        Returns:
            True if bridge is running, False otherwise
        """
        return self._active

    def is_write_enabled(self) -> bool:
        """Check if writing to PLC is enabled.

        Returns:
            True if writes are enabled, False otherwise
        """
        return self._write_enabled

    def get_write_throttle(self) -> float:
        """Get the current write throttle setting.

        Returns:
            Throttle time in milliseconds
        """
        return self._write_throttle_ms

    def get_binding_stats(self) -> dict:
        """Get statistics about current bindings.

        Returns:
            Dictionary with binding statistics
        """
        read_count = sum(1 for b in self._bindings.values()
                         if b.direction == BindingDirection.READ)
        write_count = sum(1 for b in self._bindings.values()
                          if b.direction == BindingDirection.WRITE)
        both_count = sum(1 for b in self._bindings.values()
                         if b.direction == BindingDirection.BOTH)
        enabled_count = sum(1 for b in self._bindings.values() if b.enabled)

        return {
            'total': len(self._bindings),
            'enabled': enabled_count,
            'disabled': len(self._bindings) - enabled_count,
            'read': read_count,
            'write': write_count,
            'both': both_count,
            'active': self._active,
            'write_enabled': self._write_enabled
        }

    def start(self) -> None:
        """Start the bridge - begin synchronization."""
        if self._active:
            log(self).warning("Bridge already active")
            return

        if not self._scene:
            log(self).error("Cannot start bridge without a scene")
            return

        # Set up watches for all READ and BOTH bindings
        for binding in self._bindings.values():
            if binding.enabled and binding.direction in (BindingDirection.READ, BindingDirection.BOTH):
                self._setup_watch_for_binding(binding)

        # Register tick callback for write support
        if not self._tick_callback_registered:
            PlcConnectionManager.subscribe_to_ticks(self._on_tick)
            self._tick_callback_registered = True

        self._active = True
        log(self).info(f"PLC-Scene bridge started with {len(self._bindings)} bindings")

    def stop(self) -> None:
        """Stop the bridge - cease synchronization."""
        if not self._active:
            return

        # Remove all watches (but only tags we added)
        watched_tags = set()
        for binding in self._bindings.values():
            if binding.direction in (BindingDirection.READ, BindingDirection.BOTH):
                watched_tags.add(binding.tag_name)

        for tag_name in watched_tags:
            PlcConnectionManager.remove_watch_tag(tag_name)

        # Unregister tick callback
        if self._tick_callback_registered:
            PlcConnectionManager.unsubscribe_from_ticks(self._on_tick)
            self._tick_callback_registered = False

        self._active = False
        log(self).info("PLC-Scene bridge stopped")

    def _on_tick(self) -> None:
        """Called on each PLC tick - automatically updates scene to PLC."""
        self.update_scene_to_plc()

    def set_write_enabled(self, enabled: bool) -> None:
        """Enable or disable writing to PLC.

        Args:
            enabled: True to enable writes, False to disable
        """
        self._write_enabled = enabled
        log(self).info(f"PLC write {'enabled' if enabled else 'disabled'}")

    def set_write_throttle(self, throttle_ms: float) -> None:
        """Set the minimum time between writes for the same tag.

        Args:
            throttle_ms: Throttle time in milliseconds
        """
        self._write_throttle_ms = throttle_ms
        log(self).info(f"PLC write throttle set to {throttle_ms}ms")

    def update_scene_to_plc(self) -> None:
        """Update PLC with current scene values (for WRITE and BOTH bindings).

        This is called automatically on each PLC tick when the bridge is active.
        Can also be called manually for immediate updates.
        """
        if not self._active or not self._write_enabled:
            return

        import time
        current_time = time.time() * 1000  # Convert to ms

        for binding in self._bindings.values():
            if not binding.enabled:
                continue

            if binding.direction not in (BindingDirection.WRITE, BindingDirection.BOTH):
                continue

            # Throttle writes
            last_write = self._last_write_time.get(binding.tag_name, 0)
            if current_time - last_write < self._write_throttle_ms:
                continue

            # Get current scene value
            scene_value = self._get_scene_property(binding.object_id, binding.property_path)
            if scene_value is None:
                continue

            # Check if value changed
            if scene_value == binding.last_scene_value:
                continue

            # Transform value if needed
            plc_value = scene_value
            if binding.inverse_transform:
                try:
                    plc_value = binding.inverse_transform(scene_value)
                except Exception as e:
                    log(self).error(f"Transform error for {binding.tag_name}: {e}")
                    continue

            # Write to PLC
            PlcConnectionManager.write_watch_tag(binding.tag_name, plc_value)
            binding.last_scene_value = scene_value
            self._last_write_time[binding.tag_name] = current_time
            log(self).debug(
                f"Wrote to PLC: {binding.tag_name} = {plc_value} "
                f"(from {binding.object_id}.{binding.property_path})"
            )

    def force_write_binding(
        self,
        tag_name: str,
        object_id: str,
        property_path: str
    ) -> bool:
        """Force an immediate write for a specific binding, bypassing throttle.

        Args:
            tag_name: PLC tag name
            object_id: Scene object ID
            property_path: Property path

        Returns:
            True if write was successful, False otherwise
        """
        binding_key = f"{tag_name}::{object_id}::{property_path}"
        binding = self._bindings.get(binding_key)

        if not binding:
            log(self).warning(f"Binding not found: {binding_key}")
            return False

        if not binding.enabled:
            log(self).warning(f"Binding disabled: {binding_key}")
            return False

        if binding.direction not in (BindingDirection.WRITE, BindingDirection.BOTH):
            log(self).warning(f"Binding is not configured for writing: {binding_key}")
            return False

        # Get current scene value
        scene_value = self._get_scene_property(binding.object_id, binding.property_path)
        if scene_value is None:
            log(self).warning(f"Could not get scene value for {binding_key}")
            return False

        # Transform value if needed
        plc_value = scene_value
        if binding.inverse_transform:
            try:
                plc_value = binding.inverse_transform(scene_value)
            except Exception as e:
                log(self).error(f"Transform error for {binding.tag_name}: {e}")
                return False

        # Write to PLC
        import time
        PlcConnectionManager.write_watch_tag(binding.tag_name, plc_value)
        binding.last_scene_value = scene_value
        self._last_write_time[binding.tag_name] = time.time() * 1000
        log(self).info(f"Force wrote to PLC: {binding.tag_name} = {plc_value}")
        return True

    def _setup_watch_for_binding(self, binding: PlcTagBinding) -> None:
        """Set up PLC watch for a binding."""
        def callback(response: Response | list[Response]) -> None:
            self._on_tag_update(binding, response)

        PlcConnectionManager.add_watch_tag(
            binding.tag_name,
            data_type=binding.data_type,
            callback=callback
        )

    def _on_tag_update(
        self,
        binding: PlcTagBinding,
        response: Response | list[Response] | None
    ) -> None:
        """Handle PLC tag update - apply to scene object.

        Args:
            binding: The binding that triggered this update
            response: PLC response with tag value
        """
        if not binding.enabled:
            return

        # Handle list response
        if isinstance(response, list):
            response = response[0] if response else None

        if not response or response.Status != 'Success':
            return

        # Get PLC value
        plc_value = response.Value
        binding.last_plc_value = plc_value

        # Transform value if needed
        scene_value = plc_value
        if binding.transform:
            try:
                scene_value = binding.transform(plc_value)
            except Exception as e:
                log(self).error(f"Transform error for {binding.tag_name}: {e}")
                return

        # Set scene property
        try:
            log(self).debug(
                f"Setting {binding.object_id}.{binding.property_path} = {scene_value} (type: {type(scene_value).__name__})"
            )
            self._set_scene_property(binding.object_id, binding.property_path, scene_value)
            binding.last_scene_value = scene_value
            log(self).debug(f"Successfully set {binding.object_id}.{binding.property_path}")
        except Exception as e:
            log(self).error(
                f"Error setting {binding.object_id}.{binding.property_path} = {scene_value}: {e}"
            )

    def _get_scene_property(self, object_id: str, property_path: str) -> Any:
        """Get a property value from a scene object.

        Args:
            object_id: Object ID in scene
            property_path: Property path (e.g., 'speed' or 'position.x')

        Returns:
            Property value or None if not found
        """
        if not self._scene:
            return None

        obj = self._scene.get_scene_object(object_id)
        if not obj:
            return None

        # Navigate property path
        parts = property_path.split('.')
        current = obj
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return None

        return current

    def _set_scene_property(self, object_id: str, property_path: str, value: Any) -> None:
        """Set a property value on a scene object.

        Args:
            object_id: Object ID in scene
            property_path: Property path (e.g., 'speed' or 'position.x')
            value: Value to set
        """
        if not self._scene:
            raise ValueError("No scene set")

        obj = self._scene.get_scene_object(object_id)
        if not obj:
            raise ValueError(f"Object {object_id} not found in scene")

        # Navigate to parent of property
        parts = property_path.split('.')
        current = obj
        for part in parts[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise ValueError(f"Property path {property_path} not found on {object_id}")

        # Set final property
        property_name = parts[-1]
        setattr(current, property_name, value)

    def to_dict(self) -> dict:
        """Serialize bridge configuration to dictionary.

        Returns:
            Dictionary representation of bridge configuration
        """
        return {
            'bindings': [
                {
                    'tag_name': b.tag_name,
                    'object_id': b.object_id,
                    'property_path': b.property_path,
                    'direction': b.direction.value,
                    'data_type': b.data_type,
                    'enabled': b.enabled,
                    'description': b.description,
                    'tags': b.tags
                }
                for b in self._bindings.values()
            ],
            'write_enabled': self._write_enabled,
            'write_throttle_ms': self._write_throttle_ms
        }

    def from_dict(self, data: dict) -> None:
        """Load bridge configuration from dictionary.

        Args:
            data: Dictionary created by to_dict()
        """
        self.clear_bindings()

        for binding_data in data.get('bindings', []):
            self.add_binding(
                tag_name=binding_data['tag_name'],
                object_id=binding_data['object_id'],
                property_path=binding_data['property_path'],
                direction=BindingDirection(binding_data['direction']),
                data_type=binding_data.get('data_type', 0),
                description=binding_data.get('description', '')
            )

        self._write_enabled = data.get('write_enabled', True)
        self._write_throttle_ms = data.get('write_throttle_ms', 100)
