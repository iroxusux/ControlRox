"""Tag module for plc Tag type
"""
from typing import (
    DefaultDict,
    Optional,
    Union,
    Self,
)
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.interfaces import (
    IController,
    IProgram,
    ILogicTagScope
)

from controlrox.models.plc.tag import Tag
from controlrox.services.plc.tag import TagFactory
from .meta import RaPlcObject


class DataValueMember(RaPlcObject[dict]):
    """type class for plc Tag DataValueMember

        Args:
            l5x_meta_data (str): meta data
            controller (Self): controller dictionary
        """

    def __init__(
        self,
        meta_data: Optional[dict] = DefaultDict(None),
        name: str = '',
        description: str = '',
        parent: Optional[Union['RaTag', Self]] = None
    ):

        if not meta_data:
            raise ValueError('Cannot have an empty DataValueMember!')

        if not isinstance(meta_data, dict):
            raise ValueError('DataValueMember meta_data must be a dict!')

        if not parent:
            raise ValueError('Cannot have a datavalue member without a parent!')

        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
        )

        self._parent = parent
        if self.value:
            self.set_value(self.value)  # set the value to ensure it is valid escaped data

    @property
    def value(self) -> str:
        return self.get_value()

    def get_value(self) -> str:
        return self.meta_data.get('@Value', '')

    def set_value(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Value must be a string!")

        value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        self['@Value'] = value

    @property
    def parent(self) -> Union['RaTag', Self]:
        return self._parent


class TagEndpoint(RaPlcObject):
    def __init__(
        self,
        meta_data: str,
        parent_tag: 'RaTag'
    ):
        super().__init__(
            meta_data=meta_data,
        )
        self._parent_tag: 'RaTag' = parent_tag

    @property
    def name(self) -> str:
        """get the name of this tag endpoint

        Returns:
            :class:`str`: name of this tag endpoint
        """
        if not isinstance(self._meta_data, str):
            raise ValueError("TagEndpoint meta_data must be a string!")
        return self._meta_data


class RaTag(
    RaPlcObject[dict],
    Tag,
    metaclass=FactoryTypeMeta['RaTag', TagFactory]
):
    def __new__(cls, *args, **kwargs) -> 'RaTag':
        instance = super(RaTag, cls).__new__(cls)
        return instance  # TODO: investigate why this is needed

    def __post_init__(self, **kwargs) -> None:
        self._datavalue_members: list[DataValueMember] = []

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Name',
            '@Class',
            '@TagType',
            '@DataType',
            '@Dimensions',
            '@Radix',
            '@AliasFor',
            '@Constant',
            '@ExternalAccess',
            'ConsumeInfo',
            'ProduceInfo',
            'Description',
            'Data',
        ]

    @property
    def alias_for(self) -> str:
        return self.meta_data.get('@AliasFor', '')

    @property
    def alias_for_base_name(self) -> str:
        """get the base name of the aliased tag

        Returns:
            :class:`str`
        """
        if not self.alias_for:
            return ''

        return self.alias_for.split('.')[0].split(':')[0]

    @property
    def klass(self) -> str:
        return self['@Class']

    @klass.setter
    def klass(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Class must be a string!")

        if value not in ['Standard', 'Safety']:
            raise ValueError("Class must be one of: Standard, Safety!")

        self['@Class'] = value

    @property
    def constant(self) -> str:
        return self['@Constant']

    @constant.setter
    def constant(self, value: Union[str, bool]):
        if isinstance(value, bool):
            value = 'true' if value else 'false'

        if not self.is_valid_rockwell_bool(value):
            raise self.InvalidNamingException

        self['@Constant'] = value

    @property
    def data(self) -> list[dict]:
        if not isinstance(self['Data'], list):
            return [self['Data']]

        return self['Data']

    @property
    def raw_datatype(self) -> str:
        return self['@DataType']

    @raw_datatype.setter
    def raw_datatype(self, value: str):
        if not self.is_valid_string(value) or not value:
            raise ValueError("Data type must be a valid string!")

        self['@DataType'] = value
        self['Data'] = []

    @property
    def datavalue_members(self) -> list[DataValueMember]:
        if not self._datavalue_members:
            self.compile_datavalue_members()
        return self._datavalue_members

    @property
    def decorated_data(self) -> Optional[dict]:
        for x in self.data:
            if x and x['@Format'] == 'Decorated':
                return x

    @property
    def dimensions(self) -> str:
        """get the dimensions of this tag

        Returns:
            :class:`str`: dimensions of this datatype
        """
        return self['@Dimensions']

    @dimensions.setter
    def dimensions(self, value: Union[str, int]):
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Dimensions must be a positive integer!")
            value = str(value)

        if not isinstance(value, str):
            raise ValueError("Dimensions must be a string or an integer!")

        self['@Dimensions'] = value

    @property
    def endpoint_operands(self) -> list[str]:
        """get the endpoint operands for this tag

        Returns:
            :class:`list[str]`: list of endpoint operands
        """
        if not self.raw_datatype or not self.controller:
            return []

        datatype = self.controller.get_datatypes().get(self.raw_datatype, None)
        if not datatype:
            return []

        endpoints = datatype.endpoint_operands
        if not endpoints:
            return []

        endpoints = [
            TagEndpoint(
                meta_data=f'{self.name}{x}',
                parent_tag=self
            ) for x in endpoints
        ]

        return [x.name for x in endpoints]

    @property
    def external_access(self) -> str:
        return self['@ExternalAccess']

    @external_access.setter
    def external_access(self, value: str):
        if not isinstance(value, str):
            raise ValueError("External access must be a string!")

        if value not in ['None', 'ReadOnly', 'Read/Write']:
            raise ValueError("External access must be one of: None, ReadOnly, Read/Write!")

        self['@ExternalAccess'] = value

    @property
    def l5k_data(self) -> Optional[dict]:
        for x in self.data:
            if x and x['@Format'] == 'L5K':
                return x

    @property
    def opc_ua_access(self) -> str:
        return self['@OpcUaAccess']

    @property
    def scope(self) -> ILogicTagScope:
        if isinstance(self.container, IController):
            return ILogicTagScope.CONTROLLER
        elif isinstance(self.container, IProgram) or isinstance(self.container, IProgram):
            return ILogicTagScope.PROGRAM
        else:
            raise ValueError('Unknown tag scope!')

    @property
    def tag_type(self) -> str:
        return self['@TagType']

    @tag_type.setter
    def tag_type(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Tag type must be a string!")

        if value not in ['Base', 'Structure', 'Array']:
            raise ValueError("Tag type must be one of: Atomic, Structure, Array!")

        self['@TagType'] = value

    def compile(self):
        if not self.container:
            raise ValueError('Cannot compile a tag without a container!')

        self.compile_datavalue_members()
        return self

    def compile_datavalue_members(self):
        for raw_member in self.get_raw_datavalue_members():
            member = DataValueMember(
                meta_data=raw_member,
                parent=self
            )
            self._datavalue_members.append(member)

    @classmethod
    def get_factory(cls):
        return TagFactory

    def get_alias_string(
        self,
        additional_elements: str = ''
    ) -> str:
        """get the alias string for this tag

        Returns:
            :class:`str`: alias string of this tag
        """
        if not additional_elements:
            additional_elements = ''

        if not self.alias_for:
            return f'{self.name}{additional_elements}'

        parent_tag = self.get_parent_tag(self)
        if not parent_tag:
            return f'{self.alias_for}{additional_elements}'

        alias_element_pointer = self.alias_for.find('.')
        if alias_element_pointer != -1:
            additional_elements = f'{self.alias_for[alias_element_pointer:]}{additional_elements}'

        return parent_tag.get_alias_string(additional_elements=additional_elements)

    def get_base_tag(
        self,
        tracked_tag: Optional['RaTag'] = None
    ):
        tag = self if not tracked_tag else tracked_tag

        if not tag.alias_for:
            return tag

        alias = tag.get_parent_tag(tag)

        if not alias:
            return tag

        if alias.alias_for:
            return self.get_base_tag(tracked_tag=alias)
        else:
            return alias

    @staticmethod
    def get_parent_tag(tag: 'RaTag') -> Optional['RaTag']:
        if not tag.alias_for:
            return None

        alias = None

        if tag.container:
            alias = tag.container.get_tags().get(tag.alias_for_base_name, None)

        if not alias and tag.controller:
            alias = tag.controller.get_tags().get(tag.alias_for_base_name, None)

        if not isinstance(alias, RaTag):
            return None

        return alias

    def get_raw_datavalue_members(self) -> list[dict]:
        if not self.decorated_data:
            return []

        if not self.decorated_data.get('Structure', None):
            return []

        if not self.decorated_data['Structure'].get('DataValueMember', None):
            return []

        if not isinstance(self.decorated_data['Structure']['DataValueMember'], list):
            return [self.decorated_data['Structure']['DataValueMember']]

        return self.decorated_data['Structure']['DataValueMember']

    def invalidate(self):
        self._datavalue_members.clear()
        super().invalidate()
