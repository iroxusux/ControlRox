import json
from pathlib import Path
from typing import Dict, List, Optional, Type, Union



def save(self, filepath: Union[str, Path]) -> None:
    """
    Save scene to JSON file.

    Args:
        filepath: Path to save the scene
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(self.to_dict(), f, indent=2)


def load(filepath: str | Path, device_factory=None) -> "Scene":
    """
    Load scene from JSON file.

    Args:
        filepath: Path to the scene file
        device_factory: DeviceFactory instance for creating devices

    Returns:
        Loaded Scene instance

    Raises:
        ValueError: If device_factory is None
    """
    if device_factory is None:
        raise ValueError("device_factory is required to load a scene")

    with open(filepath, 'r') as f:
        data = json.load(f)

    scene = cls(
        name=data.get("name", "Untitled Scene"),
        description=data.get("description", "")
    )
    scene.set_device_factory(device_factory)

    # Load standalone tags first
    for tag_data in data.get("tags", []):
        tag = Tag.from_dict(tag_data)
        scene.add_tag(tag)

    # Load devices
    for device_data in data.get("devices", []):
        device = device_factory.create_device(device_data)
        scene.add_device(device)

    return scene
