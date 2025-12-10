"""Warehouse module for pyrox module applications.
"""
from typing import Any
from controlrox.interfaces import (
    ModuleControlsType,
    IIntrospectiveModule,
    IModule,
    IRung,
)

from controlrox.models.plc.meta import PlcObject
from controlrox.models.plc.module import Module

__all__ = (
    'IntrospectiveModule',
)


class IntrospectiveModule(
    IIntrospectiveModule,
    PlcObject[dict],
):
    """Introspective Module for a rockwell plc.
    This is a wrapper around the Module class to provide introspection capabilities.
    Such as, a Siemens G115Drive, or a Rockwell 1756-L85E controller.
    It is used to extend capabilities of known modules, or to provide a way to introspect unknown modules.
    """

    def __init__(
        self,
        module: Module,
    ) -> None:
        PlcObject.__init__(
            self,
            name=module.name,
            description=module.description,
        )
        self._module = module
        self._config_tag = None
        self._input_tag = None
        self._output_tag = None

    @property
    def base_module(self) -> IModule:
        """The base module of the introspective module."""
        return self.get_base_module()

    @classmethod
    def create_from_module(
        cls,
        module: IModule
    ) -> 'IIntrospectiveModule':
        """Create an introspective module from a base module.

        Args:
            module (IModule): The base module to create from.
        Returns:
            IIntrospectiveModule: The created introspective module.
        """
        if not isinstance(module, Module):
            raise TypeError('module must be an instance of IModule')
        return cls(module)

    def get_base_module(self) -> IModule:
        """Get the base module of this introspective module.

        Returns:
            IModule: The base module.
        """
        if not self._module:
            raise ValueError('Base module is not set.')
        return self._module

    def get_catalog_number(self) -> str:
        """The catalog number of the module."""
        return ''

    def get_config_connection_point(self) -> int:
        """The configuration connection point of the module."""
        return 0

    def get_config_connection_size(self) -> int:
        """The configuration size of the module."""
        return 0

    def get_config_tag(self) -> Any:
        """The configuration connection tag of the module."""
        return None

    def get_input_connection_point(self) -> int:
        """The input connection point of the module."""
        return 0

    def get_input_connection_size(self) -> int:
        """The input size of the module."""
        return 0

    def get_input_tag(self) -> Any:
        """The input tag of the module."""
        return None

    def get_output_connection_point(self) -> int:
        """The output connection point of the module."""
        return 0

    def get_output_connection_size(self) -> int:
        """The output size of the module."""
        return 0

    def get_output_tag(self) -> Any:
        """The output tag of the module."""
        return None

    def get_module_controls_type(self) -> ModuleControlsType:
        """The controls type of the module."""
        return ModuleControlsType.UNKOWN

    def get_required_imports(self) -> list[tuple[str, list[str]]]:
        """Get the required datatype imports for the module.

        Returns:
            list[tuple[str, list[str]]]: List of tuples containing the module and class name to import.
        """
        return []

    def get_required_safety_rungs(
        self,
        **__,
    ) -> list[IRung]:
        """Get the required safety rungs for the module.

        Returns:
            list[IRung]: List of rungs.
        """
        return []

    def get_required_standard_rungs(
        self,
        **__,
    ) -> list[IRung]:
        """Get the required standard rungs for the module.

        Returns:
            list[Rung]: List of rungs.
        """
        return []

    def get_required_standard_to_safety_mapping(
        self,
        **__,
    ) -> tuple[str, str]:
        """Get the required standard to safety mapping for the module.

        Returns:
            dict[str, str]: Dictionary of standard to safety mapping.
        """
        return ('', '')

    def get_required_tags(
        self,
        **__,
    ) -> list[dict]:
        """Get the required tags for the module.

        Returns:
            list[dict]: List of tag dictionaries.
        """
        return []

    def get_safety_input_tag_name(self) -> str:
        """Get the safety tag name for the module.

        Returns:
            str: Safety tag name.
        """
        return ''

    def get_safety_output_tag_name(self) -> str:
        """Get the safety output tag name for the module.

        Returns:
            str: Safety output tag name.
        """
        return ''

    def get_standard_input_tag_name(self) -> str:
        """Get the standard tag name for the module.

        Returns:
            str: Standard tag name.
        """
        return ''

    def get_standard_output_tag_name(self) -> str:
        """Get the standard output tag name for the module.

        Returns:
            str: Standard output tag name.
        """
        return ''

    def set_base_module(
        self,
        module: IModule
    ) -> None:
        """Set the base module of this introspective module.

        Args:
            module (IModule): The base module to set.
        """
        self._module = module
