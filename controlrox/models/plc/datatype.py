"""Datatype for a rockwell plc
"""
from typing import (
    Optional,
    Self,
)
from controlrox.interfaces import (
    IDatatypeMember,
    IDatatype,
    IDatatypeProto,
)
from .meta import PlcObject


class DatatypeProto(
    IDatatypeProto,
    PlcObject[dict],

):

    def is_atomic(self) -> bool:
        raise NotImplementedError("Subclasses must implement 'is_atomic' property")

    def is_builtin(self) -> bool:
        raise NotImplementedError("Subclasses must implement 'is_builtin' property")


class DatatypeMember(
    IDatatypeMember,
    DatatypeProto
):
    def __init__(
        self,
        meta_data: Optional[dict],
        parent_datatype: 'IDatatype',
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """type member of a datatype

        Args:
            meta_data: Metadata for this object.
            parent_datatype: The parent datatype of this member.
            name: The name of this object.
            description: The description of this object.
        """
        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
        )
        self._parent_datatype = parent_datatype
        self._datatype = None

    def get_datatype(self) -> 'IDatatype':
        if not self._datatype:
            raise ValueError("Datatype not set for this member")
        return self._datatype

    def get_dimension(self) -> str:
        raise NotImplementedError("Subclasses must implement 'dimension' property")

    def get_parent_datatype(self) -> 'IDatatype':
        return self._parent_datatype

    def is_atomic(self) -> bool:
        raise NotImplementedError("Subclasses must implement 'is_atomic' property")

    def is_hidden(self) -> bool:
        raise NotImplementedError("Subclasses must implement 'hidden' property")

    def set_datatype(
        self,
        datatype: Optional[IDatatype]
    ) -> None:
        if datatype is not None and not isinstance(datatype, IDatatype):
            raise TypeError("datatype must be an instance of IDatatype or None")
        self._datatype = datatype

    def set_dimension(self, dimension: str) -> None:
        raise NotImplementedError("Subclasses must implement 'set_dimension' method")


class Datatype(
    IDatatype,
    DatatypeProto,
):
    """Datatype
    """

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        super().__init__(
            meta_data,
            name=name,
            description=description,
        )
        self._members: list[IDatatypeMember] = []
        self._endpoint_operands: list[str] = []

    def compile(self) -> Self:
        self.compile_members()
        self.compile_endpoint_operands()
        return self

    def compile_endpoint_operands(self) -> None:
        raise NotImplementedError("Subclasses must implement 'compile_endpoint_operands' method")

    def compile_members(self) -> None:
        raise NotImplementedError("Subclasses must implement 'compile_members' method")

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
        if self.is_atomic():
            return ['']
        if not self._endpoint_operands:
            self.compile_endpoint_operands()
        return self._endpoint_operands

    def get_family(self) -> str:
        raise NotImplementedError("Subclasses must implement 'get_family' method")

    def get_members(self) -> list[IDatatypeMember]:
        if not self._members:
            self.compile_members()
        return self._members


BOOL = Datatype(meta_data={'@Name': 'BOOL'})
BIT = Datatype(meta_data={'@Name': 'BIT'})
SINT = Datatype(meta_data={'@Name': 'SINT'})
INT = Datatype(meta_data={'@Name': 'INT'})
DINT = Datatype(meta_data={'@Name': 'DINT'})
LINT = Datatype(meta_data={'@Name': 'LINT'})
USINT = Datatype(meta_data={'@Name': 'USINT'})
UINT = Datatype(meta_data={'@Name': 'UINT'})
UDINT = Datatype(meta_data={'@Name': 'UDINT'})
ULINT = Datatype(meta_data={'@Name': 'ULINT'})
REAL = Datatype(meta_data={'@Name': 'REAL'})
LREAL = Datatype(meta_data={'@Name': 'LREAL'})
STRING = Datatype(meta_data={'@Name': 'STRING'})
TIMER = Datatype(meta_data={
    '@Name': 'TIMER',
    'Members': {
        'Member': [
            {'@Name': 'PRE', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'ACC', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'EN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'TT', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'DN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
        ]}})
CONTROL = Datatype(meta_data={
    '@Name': 'CONTROL',
    'Members': {
        'Member': [
            {'@Name': 'LEN', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'POS', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'EN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'EU', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'DN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'EM', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'ER', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'UL', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'IN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'FD', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
        ]}})
COUNTER = Datatype(meta_data={
    '@Name': 'COUNTER',
    'Members': {
        'Member': [
            {'@Name': 'PRE', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'ACC', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'CU', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'CD', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'DN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
        ]}})

BUILTINS = [
    BOOL,
    BIT,
    SINT,
    INT,
    DINT,
    LINT,
    USINT,
    UINT,
    UDINT,
    ULINT,
    REAL,
    LREAL,
    STRING,
    TIMER,
    COUNTER,
]
