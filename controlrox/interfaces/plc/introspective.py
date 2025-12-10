"""Introspective module interface.
"""
from abc import abstractmethod
from .meta import IPlcObject
from .module import IModule, ModuleControlsType
from .protocols import IHasConnectionTags
from .rung import IRung


class IIntrospectiveModule(
    IHasConnectionTags,
    IPlcObject[dict],
):

    @property
    def base_module(self) -> IModule:
        """The base module of the introspective module."""
        return self.get_base_module()

    @property
    def catalog_number(self) -> str:
        """The catalog number of the module."""
        return self.get_catalog_number()

    @property
    def module_controls_type(self) -> ModuleControlsType:
        """The controls type of the module."""
        return self.get_module_controls_type()

    @classmethod
    @abstractmethod
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
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_base_module(self) -> IModule:
        """Get the base module of this introspective module.

        Returns:
            IModule: The base module.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_catalog_number(self) -> str:
        """The catalog number of the module."""
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_module_controls_type(self) -> ModuleControlsType:
        """The controls type of the module."""
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_required_imports(self) -> list[tuple[str, list[str]]]:
        """Get the required datatype imports for the module.

        Returns:
            list[tuple[str, list[str]]]: List of tuples containing the module and class name to import.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_required_safety_rungs(
        self,
        **__,
    ) -> list[IRung]:
        """Get the required safety rungs for the module.

        Returns:
            list[IRung]: List of rungs.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_required_standard_rungs(
        self,
        **__,
    ) -> list[IRung]:
        """Get the required standard rungs for the module.

        Returns:
            list[Rung]: List of rungs.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_required_standard_to_safety_mapping(
        self,
        **__,
    ) -> tuple[str, str]:
        """Get the required standard to safety mapping for the module.

        Returns:
            dict[str, str]: Dictionary of standard to safety mapping.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_required_tags(
        self,
        **__,
    ) -> list[dict]:
        """Get the required tags for the module.

        Returns:
            list[dict]: List of tag dictionaries.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_safety_input_tag_name(self) -> str:
        """Get the safety tag name for the module.

        Returns:
            str: Safety tag name.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_safety_output_tag_name(self) -> str:
        """Get the safety output tag name for the module.

        Returns:
            str: Safety output tag name.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_standard_input_tag_name(self) -> str:
        """Get the standard tag name for the module.

        Returns:
            str: Standard tag name.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def get_standard_output_tag_name(self) -> str:
        """Get the standard output tag name for the module.

        Returns:
            str: Standard output tag name.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')

    @abstractmethod
    def set_base_module(
        self,
        module: IModule
    ) -> None:
        """Set the base module of this introspective module.

        Args:
            module (IModule): The base module to set.
        """
        raise NotImplementedError('This method should be implemented by the subclass.')


__all__ = (
    'IIntrospectiveModule',
)
