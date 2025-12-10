"""Datatype for a rockwell plc
"""
from abc import abstractmethod
from .meta import IPlcObject


class IDatatypeProto(
    IPlcObject[dict]
):

    @abstractmethod
    def is_atomic(self) -> bool:
        """check if this member is an atomic datatype

        Returns:
            :class:`bool`: True if atomic, False otherwise
        """
        raise NotImplementedError("Subclasses must implement 'is_atomic' property")

    @abstractmethod
    def is_builtin(self) -> bool:
        """check if this member is a built-in datatype

        Returns:
            :class:`bool`: True if built-in, False otherwise
        """
        raise NotImplementedError("Subclasses must implement 'is_builtin' property")


class IDatatypeMember(
    IDatatypeProto,
):

    @property
    def datatype(self) -> 'IDatatype':
        """get the datatype of this member

        Returns:
            :class:`Datatype`: datatype of this member
        """
        return self.get_datatype()

    @property
    def dimension(self) -> str:
        """get the dimension of this member

        Returns:
            :class:`str`: dimension of this member
        """
        return self.get_dimension()

    @property
    def hidden(self) -> bool:
        """check if the member is hidden

        Returns:
            bool: True if hidden, False otherwise
        """
        return self.is_hidden()

    @property
    def parent_datatype(self) -> 'IDatatype':
        """get the parent datatype of this member

        Returns:
            :class:`Datatype`: parent datatype of this member
        """
        return self.get_parent_datatype()

    @abstractmethod
    def get_datatype(self) -> 'IDatatype':
        """get the datatype of this member

        Returns:
            :class:`Datatype`: datatype of this member
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the datatype.")

    @abstractmethod
    def get_dimension(self) -> str:
        """get the dimension of this member

        Returns:
            :class:`str`: dimension of this member
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the dimension.")

    @abstractmethod
    def get_parent_datatype(self) -> 'IDatatype':
        """get the parent datatype of this member

        Returns:
            :class:`Datatype`: parent datatype of this member
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the parent datatype.")

    @abstractmethod
    def is_hidden(self) -> bool:
        """check if the member is hidden

        Returns:
            bool: True if hidden, False otherwise
        """
        raise NotImplementedError("This method should be overridden by subclasses to check if the member is hidden.")

    @abstractmethod
    def set_datatype(
        self,
        datatype: 'IDatatype'
    ) -> None:
        """set the datatype of this member

        Args:
            datatype (IDatatype): datatype to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the datatype.")

    @abstractmethod
    def set_dimension(
        self,
        dimension: str
    ) -> None:
        """set the dimension of this member

        Args:
            dimension (str): dimension to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the dimension.")


class IDatatype(
    IDatatypeProto,
):
    """Datatype Definition for a rockwell plc
    """

    @property
    def endpoint_operands(self) -> list[str]:
        """get the endpoint operands for this datatype
        for example, for a datatype with members like::
        .. code-block:: xml
        <Datatype Name="MyDatatype" ...>
            <Member Name="MyAtomicMember" @Datatype="BOOL" ... />
            <Member Name="MyMember" @Datatype="SomeOtherDatatype" ...>
                <Member Name"MyChildMember" @Datatype="BOOL" ... />
            </Member>
        </Datatype>

        the endpoint operands would be:
            ['.MyAtomicMember', '.MyMember.MyChildMember']
        Returns:
            list[str]: List of endpoint operands.
        """
        return self.get_endpoint_operands()

    @property
    def family(self) -> str:
        """get the family of this datatype

        Returns:
            str: family of this datatype
        """
        return self.get_family()

    @property
    def members(self) -> list['IDatatypeMember']:
        """get the members of this datatype

        Returns:
            list[IDatatypeMember]: members of this datatype
        """
        return self.get_members()

    @abstractmethod
    def compile_endpoint_operands(self) -> None:
        """Compile endpoint operands for this datatype
        """
        raise NotImplementedError("Subclasses must implement 'compile_endpoint_operands' method")

    @abstractmethod
    def compile_members(self) -> None:
        """Compile members for this datatype
        """
        raise NotImplementedError("Subclasses must implement 'compile_members' method")

    @abstractmethod
    def get_endpoint_operands(self) -> list[str]:
        """get the endpoint operands for this datatype
        for example, for a datatype with members like::
        .. code-block:: xml
        <Datatype Name="MyDatatype" ...>
            <Member Name="MyAtomicMember" @Datatype="BOOL" ... />
            <Member Name="MyMember" @Datatype="SomeOtherDatatype" ...>
                <Member Name"MyChildMember" @Datatype="BOOL" ... />
            </Member>
        </Datatype>

        the endpoint operands would be:
            ['.MyAtomicMember', '.MyMember.MyChildMember']

        Returns:
            list[str]: List of endpoint operands.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the endpoint operands.")

    @abstractmethod
    def get_family(self) -> str:
        """get the family of this datatype

        Returns:
            str: family of this datatype
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the family.")

    @abstractmethod
    def get_members(self) -> list['IDatatypeMember']:
        """get the members of this datatype

        Returns:
            list[IDatatypeMember]: members of this datatype
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the members.")


__all__ = [
    'IDatatype',
    'IDatatypeMember',
    'IDatatypeProto',
]
