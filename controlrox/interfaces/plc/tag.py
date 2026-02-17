"""Tag module for plc Tag type
"""
from abc import abstractmethod
from enum import Enum
from typing import Optional, Union
from .datatype import IDatatype
from .meta import IPlcObject, ILogicTagScope, IExternalAccessMixin, IStandardSafetyMixin
from .protocols import ICanBeSafe, IHasTags


ITagKlass = IStandardSafetyMixin
ITagExternalAccess = IExternalAccessMixin


class ITagType(Enum):
    """Tag types for PLC tags
    """
    BASE = 'Base'
    ALIAS = 'Alias'


class ITag(
    IPlcObject[dict],
    ICanBeSafe,
):

    @property
    def constant(self) -> bool:
        """check if this tag is constant

        Returns:
            bool: True if constant, False otherwise
        """
        return self.is_constant()

    @property
    def container(self) -> IHasTags:
        """get the container of this tag

        Returns:
            :class:`IHasTags`: container of this tag
        """
        return self.get_container()

    @property
    def datatype(self) -> Optional['IDatatype']:
        """get the datatype of this tag

        Returns:
            :class:`Optional[IDatatype]`: datatype of this tag
        """
        return self.get_datatype()

    @property
    def dimensions(self) -> str:
        """get the dimensions of this tag

        Returns:
            :class:`str`: dimensions of this tag
        """
        return self.get_dimensions()

    @property
    def external_access(self) -> str:
        """get the external access of this tag

        Returns:
            :class:`str`: external access of this tag
        """
        return self.get_external_access()

    @property
    def klass(self) -> ITagKlass:
        """get the klass of this tag (Standard or Safety)
        Returns:
            :class:`ITagClass`: class of this tag
        """
        return self.get_klass()

    @property
    def tag_type(self) -> ITagType:
        """get the tag type of this tag (Base or Alias)

        Returns:
            :class:`ITagType`: type of this tag
        """
        return self.get_tag_type()

    @abstractmethod
    def get_alias_for_tag(self) -> 'ITag':
        """get the alias tag for this tag

        Returns:
            :class:`ITag`: alias tag for this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the alias tag.")

    @abstractmethod
    def get_base_tag(self) -> 'ITag':
        """get the base tag for this tag

        Returns:
            :class:`ITag`: base tag for this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the base tag.")

    @abstractmethod
    def get_container(self) -> IHasTags:
        """get the container of this tag

        Returns:
            :class:`IHasTags`: container of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the container.")

    @abstractmethod
    def get_datatype(self) -> Optional['IDatatype']:
        """get the datatype of this tag

        Returns:
            :class:`Optional[IDatatype]`: datatype of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the datatype.")

    @abstractmethod
    def get_dimensions(self) -> str:
        """get the dimensions of this tag

        Returns:
            :class:`str`: dimensions of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the dimensions.")

    @abstractmethod
    def get_endpoint_operands(self) -> list[str]:
        """get the endpoint operands for this tag

        Returns:
            :class:`list[str]`: list of endpoint operands
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the endpoint operands.")

    @abstractmethod
    def get_external_access(self) -> str:
        """get the external access of this tag

        Returns:
            :class:`str`: external access of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the external access.")

    @abstractmethod
    def get_klass(self) -> ITagKlass:
        """get the klass of this tag (Standard or Safety)
        Returns:
            :class:`ITagClass`: class of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the klass.")

    @abstractmethod
    def set_klass(self, value: ITagKlass) -> None:
        """set the klass of this tag

        Args:
            value (ITagKlass): klass to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the klass.")

    @abstractmethod
    def get_opcua_access(self) -> str:
        """get the opc ua access of this tag

        Returns:
            :class:`str`: opc ua access of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the opc ua access.")

    @abstractmethod
    def get_tag_scope(self) -> ILogicTagScope:
        """get the tag scope of this tag

        Returns:
            :class:`LogixTagScope`: tag scope of this tag ['Controller', 'Program']
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the tag scope.")

    @abstractmethod
    def get_tag_type(self) -> ITagType:
        """get the tag type of this tag (Base or Alias)

        Returns:
            :class:`ITagType`: type of this tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the tag type.")

    @abstractmethod
    def set_tag_type(self, value: ITagType) -> None:
        """set the tag type of this tag

        Args:
            value (ITagType): type to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the tag type.")

    @abstractmethod
    def is_constant(self) -> bool:
        """check if this tag is constant

        Returns:
            :class:`bool`: True if constant, False otherwise
        """
        raise NotImplementedError("This method should be overridden by subclasses to check if the tag is constant.")

    @abstractmethod
    def set_datatype(
        self,
        datatype: Optional['IDatatype']
    ) -> None:
        """set the datatype of this tag

        Args:
            datatype (Optional[IDatatype]): datatype to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the datatype.")

    @abstractmethod
    def set_dimensions(self, value: Union[str, int]) -> None:
        """set the dimensions of this tag

        Args:
            value (Union[str, int]): dimensions to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the dimensions.")

    @abstractmethod
    def set_external_access(self, value: str) -> None:
        """set the external access of this tag

        Args:
            value (str): external access to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the external access.")

    @abstractmethod
    def set_safety_class(self, value: str) -> None:
        """set the logix class of this tag

        Args:
            value (str): safety class to set ['Standard', 'Safety']
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the safety class.")

    @abstractmethod
    def set_opcua_access(self, value: str) -> None:
        """set the opc ua access of this tag

        Args:
            value (str): opc ua access to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the opc ua access.")

    @abstractmethod
    def set_is_constant(self, value: bool) -> None:
        """set if this tag is constant

        Args:
            value (bool): True if constant, False otherwise
        """
        raise NotImplementedError("This method should be overridden by subclasses to set if the tag is constant.")


__all__ = [
    'ITag',
    'ITagKlass',
    'ITagType',
    'ITagExternalAccess',
]
