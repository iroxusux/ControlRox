"""
Simulation framework for field devices and I/O simulation.

This package provides a framework for creating, managing, and persisting
simulated field devices that can interact with a live PLC.
"""

# Scene-related imports
from .scene import (
    # Scene
    ControlsScene,
    register_device,
    get_global_factory,

    # Device
    Device,
    DeviceState,
    DeviceFactory,

    # Tag
    Tag,
    TagType,
)


__all__ = [
    # Scene-related exports
    # Scene
    "ControlsScene",
    "register_device",
    "get_global_factory",

    # Device
    "Device",
    "DeviceState",
    "DeviceFactory",

    # Tag
    "Tag",
    "TagType",
]
