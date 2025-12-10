"""GUI introspection service for PLC objects.

This service provides methods to extract GUI-relevant attributes from PLC objects
without polluting the model layer with presentation concerns.
"""
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass
from enum import Enum

from pyrox.services.logging import log
from controlrox.interfaces import IPlcObject
from controlrox.models.plc.rockwell import meta as plc_meta
from controlrox.models.plc.rockwell.aoi import RaAddOnInstruction
from controlrox.models.plc.rockwell.controller import RaController
from controlrox.models.plc.rockwell.datatype import RaDatatype
from controlrox.models.plc.rockwell.module import RaModule
from controlrox.models.plc.rockwell.program import Program
from controlrox.models.plc.rockwell.routine import Routine
from controlrox.models.plc.rockwell.tag import RaTag


class GuiAttributeType(Enum):
    """Types of GUI attributes."""
    DISPLAY_ONLY = "display_only"
    EDITABLE = "editable"
    READONLY = "readonly"
    HIDDEN = "hidden"


@dataclass
class GuiAttribute:
    """Configuration for a GUI attribute.

    Attributes:
        name: The attribute name on the object
        display_name: Human-readable name for the GUI
        attribute_type: How this attribute should be presented
        widget_type: Suggested widget type for editing
        validation: Optional validation function
        tooltip: Help text for the attribute
        group: Logical grouping for organization
    """
    name: str
    display_name: str
    attribute_type: GuiAttributeType = GuiAttributeType.DISPLAY_ONLY
    widget_type: str = "label"
    validation: Optional[Callable] = None
    tooltip: Optional[str] = None
    group: str = "General"


class PlcGuiIntrospector:
    """Service for extracting GUI-relevant attributes from PLC objects."""

    # Class-level attribute definitions for different PLC object types
    _attribute_definitions: Dict[Type, List[GuiAttribute]] = {}

    @classmethod
    def register_attributes(cls, plc_type: Type, attributes: List[GuiAttribute]):
        """Register GUI attributes for a specific PLC object type.

        Args:
            plc_type: The PLC object type
            attributes: List of GUI attributes for this type
        """
        cls._attribute_definitions[plc_type] = attributes

    @classmethod
    def get_gui_attributes(
        cls,
        plc_object: IPlcObject
    ) -> List[GuiAttribute]:
        """Get GUI attributes for a PLC object.

        Args:
            plc_object: The PLC object to introspect

        Returns:
            List of GUI attributes for this object
        """
        object_type = type(plc_object)

        # Check for exact type match first
        if object_type in cls._attribute_definitions:
            return cls._attribute_definitions[object_type]

        # Check for inheritance-based match
        for registered_type, attributes in cls._attribute_definitions.items():
            if isinstance(plc_object, registered_type):
                return attributes

        # Fallback to base PlcObject attributes
        return cls._get_default_attributes(plc_object)

    @classmethod
    def _get_default_attributes(
        cls,
        plc_object: IPlcObject
    ) -> List[GuiAttribute]:
        """Get default attributes for any PlcObject.

        Args:
            plc_object: The PLC object

        Returns:
            Default GUI attributes
        """
        attributes = []

        # Common attributes for all PLC objects
        if hasattr(plc_object, 'name'):
            attributes.append(GuiAttribute(
                name="name",
                display_name="Name",
                attribute_type=GuiAttributeType.EDITABLE,
                widget_type="text_entry",
                tooltip="The name of this PLC object"
            ))

        if hasattr(plc_object, 'description'):
            attributes.append(GuiAttribute(
                name="description",
                display_name="Description",
                attribute_type=GuiAttributeType.EDITABLE,
                widget_type="text_area",
                tooltip="Description of this PLC object"
            ))

        return attributes

    @classmethod
    def get_attribute_display_name(
        cls,
        plc_object: IPlcObject,
        attribute_name: str
    ) -> str:
        """Get the display name of an attribute for a PLC object.

        Args:
            plc_object: The PLC object
            attribute_name: Name of the attribute
        Returns:
            The display name if found, None otherwise
        """
        attributes = cls.get_gui_attributes(plc_object)

        for attr in attributes:
            if attr.name == attribute_name:
                return attr.display_name

        raise ValueError(f"Attribute '{attribute_name}' not found for object of type '{type(plc_object).__name__}'")

    @classmethod
    def get_attribute_value(
        cls,
        plc_object: IPlcObject,
        attribute_name: str
    ) -> Any:
        """Get the value of an attribute from a PLC object.

        Supports dot notation for nested attributes (e.g., 'controller.name').

        Args:
            plc_object: The PLC object
            attribute_name: Name of the attribute (supports dot notation)

        Returns:
            The attribute value
        """
        try:
            parts = attribute_name.split('.')
            value = plc_object

            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None
            return value
        except Exception as e:
            log(cls).error(f"Error getting attribute '{attribute_name}': {e}")
            return None

    @classmethod
    def set_attribute_value(cls, plc_object: 'plc_meta.PlcObject', attribute_name: str, value: Any) -> bool:
        """Set the value of an attribute on a PLC object.

        Args:
            plc_object: The PLC object
            attribute_name: Name of the attribute
            value: Value to set

        Returns:
            True if successful, False otherwise
        """
        try:
            if hasattr(plc_object, attribute_name):
                setattr(plc_object, attribute_name, value)
                return True
            return False
        except Exception as e:
            log(cls).error(f"Error setting attribute '{attribute_name}': {e}")
            return False

    @classmethod
    def get_grouped_attributes(cls, plc_object: 'plc_meta.PlcObject') -> Dict[str, List[GuiAttribute]]:
        """Get GUI attributes grouped by their group property.

        Args:
            plc_object: The PLC object to introspect

        Returns:
            Dictionary mapping group names to attribute lists
        """
        attributes = cls.get_gui_attributes(plc_object)
        groups = {}

        for attr in attributes:
            group_name = attr.group
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(attr)

        return groups


# Pre-register common PLC object types
def _register_default_attributes():
    """Register default GUI attributes for common PLC types.
    """

    # Base PlcObject attributes (already handled in _get_default_attributes)

    # AOI-specific attributes
    PlcGuiIntrospector.register_attributes(RaAddOnInstruction, [
        GuiAttribute("name", "AOI Name", GuiAttributeType.EDITABLE, "text_entry", group="Identity"),
        GuiAttribute("description", "Description", GuiAttributeType.EDITABLE, "text_area", group="Identity"),
        GuiAttribute("controller.name", "Controller", GuiAttributeType.DISPLAY_ONLY, "label", group="Context"),
    ])

    # Controller-specific attributes
    PlcGuiIntrospector.register_attributes(RaController, [
        GuiAttribute("name", "Controller Name", GuiAttributeType.EDITABLE, "text_entry", group="Identity"),
        GuiAttribute("description", "Description", GuiAttributeType.EDITABLE, "text_area", group="Identity"),
        GuiAttribute("processor_type", "Processor Type", GuiAttributeType.DISPLAY_ONLY, "label", group="Hardware"),
        GuiAttribute("revision", "Revision", GuiAttributeType.DISPLAY_ONLY, "label", group="Hardware"),
        GuiAttribute("project_creation_date", "Created", GuiAttributeType.DISPLAY_ONLY, "label", group="Metadata"),
        GuiAttribute("last_modified_date", "Modified", GuiAttributeType.DISPLAY_ONLY, "label", group="Metadata"),
    ])

    # Datatype-specific attributes
    PlcGuiIntrospector.register_attributes(RaDatatype, [
        GuiAttribute("name", "Datatype Name", GuiAttributeType.EDITABLE, "text_entry", group="Identity"),
        GuiAttribute("description", "Description", GuiAttributeType.EDITABLE, "text_area", group="Identity"),
        GuiAttribute("controller.name", "Controller", GuiAttributeType.DISPLAY_ONLY, "label", group="Context"),
    ])

    # Module-specific attributes
    PlcGuiIntrospector.register_attributes(RaModule, [
        GuiAttribute("name", "Module Name", GuiAttributeType.EDITABLE, "text_entry", group="Identity"),
        GuiAttribute("description", "Description", GuiAttributeType.EDITABLE, "text_area", group="Identity"),
        GuiAttribute("controller.name", "Controller", GuiAttributeType.DISPLAY_ONLY, "label", group="Context"),
    ])

    # Program-specific attributes
    PlcGuiIntrospector.register_attributes(Program, [
        GuiAttribute("name", "Program Name", GuiAttributeType.EDITABLE, "text_entry", group="Identity"),
        GuiAttribute("description", "Description", GuiAttributeType.EDITABLE, "text_area", group="Identity"),
        GuiAttribute("controller.name", "Controller", GuiAttributeType.DISPLAY_ONLY, "label", group="Context"),
        GuiAttribute("routines_dict", "routines", GuiAttributeType.DISPLAY_ONLY, "list_view", group="Contents"),
    ])

    # Routine-specific attributes
    PlcGuiIntrospector.register_attributes(Routine, [])

    # Tag-specific attributes
    PlcGuiIntrospector.register_attributes(RaTag, [
        GuiAttribute("name", "Tag Name", GuiAttributeType.EDITABLE, "text_entry", group="Identity"),
        GuiAttribute("description", "Description", GuiAttributeType.EDITABLE, "text_area", group="Identity"),
        GuiAttribute("tag_type", "Data Type", GuiAttributeType.EDITABLE, "combo_box", group="Configuration"),
        GuiAttribute("scope", "Scope", GuiAttributeType.DISPLAY_ONLY, "label", group="Configuration"),
        GuiAttribute("opc_ua_access", "OPC UA Access", GuiAttributeType.DISPLAY_ONLY, "label", group="Access"),
        GuiAttribute("controller.name", "Controller", GuiAttributeType.DISPLAY_ONLY, "label", group="Context"),
    ])


# Initialize default registrations
_register_default_attributes()


# Convenience functions for common operations
def get_gui_attributes_for_object(plc_object: 'plc_meta.PlcObject') -> List[GuiAttribute]:
    """Convenience function to get GUI attributes for a PLC object.

    Args:
        plc_object: The PLC object

    Returns:
        List of GUI attributes
    """
    return PlcGuiIntrospector.get_gui_attributes(plc_object)


def get_editable_attributes_for_object(plc_object: 'plc_meta.PlcObject') -> List[GuiAttribute]:
    """Get only the editable GUI attributes for a PLC object.

    Args:
        plc_object: The PLC object

    Returns:
        List of editable GUI attributes
    """
    all_attributes = PlcGuiIntrospector.get_gui_attributes(plc_object)
    return [attr for attr in all_attributes if attr.attribute_type == GuiAttributeType.EDITABLE]


def create_attribute_value_dict(
    plc_object: IPlcObject
) -> Dict[str, Any]:
    """Create a dictionary of attribute names to values for a PLC object.

    Args:
        plc_object: The PLC object

    Returns:
        Dictionary mapping attribute names to their current values
    """
    attributes = PlcGuiIntrospector.get_gui_attributes(plc_object)
    result = {}

    for attr in attributes:
        name = PlcGuiIntrospector.get_attribute_display_name(plc_object, attr.name)
        value = PlcGuiIntrospector.get_attribute_value(plc_object, attr.name)

        # Check to see if we need to recursively convert nested PlcObjects
        if isinstance(value, plc_meta.PlcObject):
            value = create_attribute_value_dict(value)

        # Or check to see if it's a dictionary of PlcObjects
        elif isinstance(value, dict):
            value = {k: create_attribute_value_dict(v) if isinstance(v, plc_meta.PlcObject) else v for k, v in value.items()}

        result[name] = value

    return result


if __name__ == "__main__":
    """Test harness for the GUI introspection service."""
    print("PLC GUI Introspection Service Test")
    print("=" * 50)

    # Test with mock objects since we may not have full imports
    class MockPlcObject:
        def __init__(self):
            self.name = "Test Object"
            self.description = "A test PLC object"

    class MockController:
        def __init__(self):
            self.name = "TestController"

    class MockTag(MockPlcObject):
        def __init__(self):
            super().__init__()
            self.tag_type = "DINT"
            self.scope = "Controller"
            self.opc_ua_access = "ReadWrite"
            self.controller = MockController()

    # Test with mock objects
    mock_tag = MockTag()

    # Register test attributes
    PlcGuiIntrospector.register_attributes(MockTag, [
        GuiAttribute("name", "Tag Name", GuiAttributeType.EDITABLE, "text_entry"),
        GuiAttribute("tag_type", "Data Type", GuiAttributeType.EDITABLE, "combo_box"),
        GuiAttribute("scope", "Scope", GuiAttributeType.DISPLAY_ONLY, "label"),
        GuiAttribute("controller.name", "Controller", GuiAttributeType.DISPLAY_ONLY, "label"),
    ])

    # Test introspection
    attributes = PlcGuiIntrospector.get_gui_attributes(mock_tag)  # type: ignore
    print(f"Found {len(attributes)} GUI attributes for MockTag:")

    for attr in attributes:
        value = PlcGuiIntrospector.get_attribute_value(mock_tag, attr.name)  # type: ignore
        print(f"  {attr.display_name}: {value} ({attr.attribute_type.value})")

    print("\nGrouped attributes:")
    grouped = PlcGuiIntrospector.get_grouped_attributes(mock_tag)  # type: ignore
    for group, attrs in grouped.items():
        print(f"  {group}: {[attr.display_name for attr in attrs]}")

    print("\nEditable attributes:")
    editable = get_editable_attributes_for_object(mock_tag)  # type: ignore
    for attr in editable:
        print(f"  {attr.display_name}")

    print("\nAttribute value dictionary:")
    value_dict = create_attribute_value_dict(mock_tag)  # type: ignore
    for name, value in value_dict.items():
        print(f"  {name}: {value}")

    print("\nTest completed successfully!")
