"""Datatype for a rockwell plc
"""
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.interfaces import (
    ATOMIC_DATATYPES,
    IDatatype
)

from controlrox.models.plc.datatype import Datatype, DatatypeMember
from controlrox.services.plc.datatype import DatatypeFactory
from controlrox.services import ControllerInstanceManager
from .meta import RaPlcObject, PLC_DT_FILE


class RaDatatypeMember(
    RaPlcObject[dict],
    DatatypeMember,
):

    def get_datatype(self) -> IDatatype:
        if not self._datatype:
            ctrl = ControllerInstanceManager.get_controller()
            if not ctrl:
                raise ValueError("No controller set for this application")
            datatype = ctrl.datatypes.get(self['@DataType'], None)
            if not datatype:
                raise ValueError(f"Datatype '{self['@DataType']}' not found in controller")
            self._datatype = datatype
        return self._datatype

    def get_dimension(self) -> str:
        return self['@Dimension']

    def is_atomic(self) -> bool:
        """Check if the member is atomic.

        Returns:
            bool: True if the member is atomic, False otherwise.
        """
        if self['@DataType'] is None:
            return False
        return self['@DataType'] in ATOMIC_DATATYPES

    def is_hidden(self) -> bool:
        """Check if the member is hidden.

        Returns:
            bool: True if the member is hidden, False otherwise.
        """
        if self['@Hidden'] is None:
            return False
        return self['@Hidden'].lower() == 'true'

    def is_builtin(self) -> bool:
        """Check if the member's datatype is a built-in datatype.

        Returns:
            bool: True if the member's datatype is built-in, False otherwise.
        """
        return self.get_datatype().is_builtin()

    def set_dimension(self, dimension: str) -> None:
        """Set the dimension of the member.

        Args:
            dimension: The dimension to set.
        """
        self['@Dimension'] = dimension


class RaDatatype(
    RaPlcObject[dict],
    Datatype,
    metaclass=FactoryTypeMeta['RaDatatype', DatatypeFactory]
):
    """Datatype Definition for a Rockwell plc
    """

    default_l5x_file_path = PLC_DT_FILE
    default_l5x_asset_key = 'Datatype'

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Name',
            '@Family',
            '@Class',
            'Description',
            'Members',
        ]

    @property
    def raw_members(self) -> list[dict]:
        return self.get_asset_from_meta_data('Members', 'Member')

    @classmethod
    def get_factory(cls):
        return DatatypeFactory

    def compile_endpoint_operands(
        self,
    ) -> None:
        ctrl = ControllerInstanceManager.get_controller()
        self._endpoint_operands.clear()

        for member in self.members:
            if member.is_hidden():
                continue
            if member.is_atomic():
                self._endpoint_operands.append(f'.{member.name}')
                continue
            if ctrl is None:
                continue
            else:
                datatype = ctrl.datatypes.get(member.meta_data['@DataType'], None)
                if not datatype:
                    continue
                self._endpoint_operands.extend([f'.{member.name}{x}' for x in datatype.endpoint_operands])

    def compile_members(
        self,
    ) -> None:
        """Post initialization hook.
        This method is called after the object has been initialized.
        """
        self._members.clear()
        self._endpoint_operands.clear()
        for member in self.raw_members:
            self._members.append(
                RaDatatypeMember(
                    meta_data=member,
                    parent_datatype=self,
                )
            )

    def get_family(self) -> str:
        return self.meta_data.get('@Family', '')

    def is_atomic(self) -> bool:
        """Check if the datatype is atomic.

        Returns:
            bool: True if the datatype is atomic, False otherwise.
        """
        return self.name in ATOMIC_DATATYPES

    def is_builtin(self) -> bool:
        """Check if the datatype is a built-in datatype.

        Returns:
            bool: True if the datatype is built-in, False otherwise.
        """
        return self in BUILTINS


BOOL = RaDatatype(meta_data={'@Name': 'BOOL'})
BIT = RaDatatype(meta_data={'@Name': 'BIT'})
SINT = RaDatatype(meta_data={'@Name': 'SINT'})
INT = RaDatatype(meta_data={'@Name': 'INT'})
DINT = RaDatatype(meta_data={'@Name': 'DINT'})
LINT = RaDatatype(meta_data={'@Name': 'LINT'})
USINT = RaDatatype(meta_data={'@Name': 'USINT'})
UINT = RaDatatype(meta_data={'@Name': 'UINT'})
UDINT = RaDatatype(meta_data={'@Name': 'UDINT'})
ULINT = RaDatatype(meta_data={'@Name': 'ULINT'})
REAL = RaDatatype(meta_data={'@Name': 'REAL'})
LREAL = RaDatatype(meta_data={'@Name': 'LREAL'})
STRING = RaDatatype(meta_data={'@Name': 'STRING'})
TIMER = RaDatatype(meta_data={
    '@Name': 'TIMER',
    'Members': {
        'Member': [
            {'@Name': 'PRE', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'ACC', '@DataType': 'DINT', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'EN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'TT', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
            {'@Name': 'DN', '@DataType': 'BOOL', '@Dimension': '1', '@Hidden': 'false'},
        ]}})
CONTROL = RaDatatype(meta_data={
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
COUNTER = RaDatatype(meta_data={
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
