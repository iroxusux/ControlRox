"""Tag module for plc Tag type
"""
from typing import (
    Optional,
    Union
)
from controlrox.interfaces import (
    IDatatype,
    IHasTags,
    ITag,
    LogicTagScope,
)
from .meta import PlcObject
from .protocols import CanBeSafe


class Tag(
    ITag,
    CanBeSafe,
    PlcObject[dict],
):
    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        container: Optional[IHasTags] = None,
    ):
        CanBeSafe.__init__(self=self)
        PlcObject.__init__(
            self=self,
            meta_data=meta_data,
            name=name,
            description=description
        )

        self._aliased_tag: Optional[ITag] = None
        self._base_tag: Optional[ITag] = None
        self._datatype: Optional[IDatatype] = None
        self._container = container or self.get_controller()

    @property
    def container(self) -> IHasTags:
        if not self._container:
            raise ValueError("Container not set for this tag")
        return self._container

    def get_alias_for_tag(self) -> ITag:
        if not self._aliased_tag:
            self.compile()
        return self._aliased_tag or self

    def get_base_tag(self) -> ITag:
        if not self._base_tag:
            self.compile()
        return self._base_tag or self

    def get_container(self) -> IHasTags:
        if not self._container:
            raise ValueError("Container not set for this tag")
        return self._container

    def get_datatype(self) -> IDatatype:
        if not self._datatype:
            raise NotImplementedError("get_datatype method must be implemented by subclass.")
        return self._datatype

    def get_dimensions(self) -> str:
        raise NotImplementedError("get_dimensions method must be implemented by subclass.")

    def get_endpoint_operands(self) -> list[str]:
        raise NotImplementedError("get_endpoint_operands method must be implemented by subclass.")

    def get_external_access(self) -> str:
        raise NotImplementedError("get_external_access method must be implemented by subclass.")

    def get_opcua_access(self) -> str:
        raise NotImplementedError("get_opcua_access method must be implemented by subclass.")

    def get_safety_class(self) -> str:
        raise NotImplementedError("get_safety_class method must be implemented by subclass.")

    def get_tag_scope(self) -> LogicTagScope:
        raise NotImplementedError("get_tag_scope method must be implemented by subclass.")

    def is_constant(self) -> bool:
        raise NotImplementedError("is_constant method must be implemented by subclass.")

    def set_datatype(self, datatype: Optional[IDatatype]) -> None:
        """set the datatype for this tag

        Args:
            datatype (IDatatype): datatype to set
        """
        raise NotImplementedError("set_datatype method must be implemented by subclass.")

    def set_dimensions(self, value: Union[int, str]) -> None:
        """set the dimensions for this tag

        Args:
            value (Union[int, str]): dimensions to set
        """
        raise NotImplementedError("set_dimensions method must be implemented by subclass.")

    def set_external_access(self, value: str) -> None:
        """set the external access for this tag

        Args:
            value (str): external access to set
        """
        raise NotImplementedError("set_external_access method must be implemented by subclass.")

    def set_safety_class(self, value: str) -> None:
        """set the safety class for this tag

        Args:
            value (str): safety class to set ['Standard', 'Safety']
        """
        raise NotImplementedError("set_safety_class method must be implemented by subclass.")

    def set_opcua_access(self, value: str) -> None:
        """set the opc ua access for this tag

        Args:
            value (str): opc ua access to set
        """
        raise NotImplementedError("set_opcua_access method must be implemented by subclass.")

    def set_is_constant(self, value: bool) -> None:
        """set whether this tag is constant

        Args:
            value (bool): True if constant, False otherwise
        """
        raise NotImplementedError("set_is_constant method must be implemented by subclass.")
