"""Module model for pyrox Controller applications
"""
from enum import Enum
from typing import Optional
from pyrox.models.factory import FactoryTypeMeta
from controlrox.interfaces import (
    IModule
)
from controlrox.models.plc.module import Module
from controlrox.services import ControllerInstanceManager
from controlrox.services.plc.module import ModuleFactory
from .meta import RaPlcObject, PLC_MOD_FILE


class RaModuleControlsType(Enum):
    """Module controls type enumeration
    """
    UNKOWN = 'Unknown'
    PLC = 'PLC'
    RACK_COMM_CARD = 'RackCommCard'
    ENCODER = 'Encoder'
    ETHERNET = 'Ethernet'
    ETHERNET_SWITCH = 'EthernetSwitch'
    SERIAL = 'Serial'
    BLOCK = 'Block'
    INPUT_BLOCK = 'InputBlock'
    OUTPUT_BLOCK = 'OutputBlock'
    INPUT_OUTPUT_BLOCK = 'InputOutputBlock'
    CONFIG_BLOCK = 'ConfigBlock'
    SAFETY_BLOCK = 'SafetyBlock'
    SAFETY_INPUT_BLOCK = 'SafetyInputBlock'
    SAFETY_OUTPUT_BLOCK = 'SafetyOutputBlock'
    SAFETY_INPUT_OUTPUT_BLOCK = 'SafetyInputOutputBlock'
    SAFETY_CONFIG_BLOCK = 'SafetyConfigBlock'
    DRIVE = 'Drive'
    POINT_IO = 'PointIO'

    @staticmethod
    def all_block_types() -> list['RaModuleControlsType']:
        """Get all block types

        Returns:
            :class:`list[ModuleControlsType]`: list of all block types
        """
        return [
            RaModuleControlsType.BLOCK,
            RaModuleControlsType.INPUT_BLOCK,
            RaModuleControlsType.OUTPUT_BLOCK,
            RaModuleControlsType.INPUT_OUTPUT_BLOCK,
            RaModuleControlsType.CONFIG_BLOCK,
            RaModuleControlsType.SAFETY_BLOCK,
            RaModuleControlsType.SAFETY_INPUT_BLOCK,
            RaModuleControlsType.SAFETY_OUTPUT_BLOCK,
            RaModuleControlsType.SAFETY_INPUT_OUTPUT_BLOCK,
            RaModuleControlsType.SAFETY_CONFIG_BLOCK,
        ]


class RaModuleConnectionTag(RaPlcObject):

    @property
    def config_size(self) -> int:
        return int(self['@ConfigSize'])

    @property
    def data(self) -> list[dict]:
        if not self['Data']:
            return [{}]
        return self['Data']

    @property
    def data_decorated(self) -> dict:
        if not isinstance(self.data, list):
            datas = [self.data]
        else:
            datas = self.data
        return next((x for x in datas if x.get('@Format', '') == 'Decorated'), {})

    @property
    def data_decorated_structure(self) -> dict:
        return self.data_decorated.get('Structure', {})

    @property
    def data_decorated_structure_array_member(self) -> dict:
        return self.data_decorated_structure.get('ArrayMember', {})

    @property
    def data_decorated_stucture_datatype(self) -> str:
        return self.data_decorated_structure.get('@DataType', '')

    @property
    def data_decorated_stucture_size(self) -> str:
        return self.data_decorated_structure_array_member.get('@Dimensions', '')

    @property
    def data_l5x(self) -> dict:
        return next((x for x in self.data if x.get('@Format', '') == 'L5X'), {})

    def get_data_multiplier(self) -> int:
        """get the data multiplier for this tag

        Returns:
            :class:`int`: data multiplier
        """
        if not self.data_decorated_stucture_datatype:
            return 0

        match self.data_decorated_stucture_datatype:
            case 'SINT':
                return 1
            case 'INT':
                return 2
            case 'DINT' | 'REAL' | 'DWORD':
                return 4
            case 'LINT' | 'LREAL' | 'LWORD':
                return 8
            case _:
                raise ValueError(f"Unsupported datatype: {self.data_decorated_stucture_datatype}")

    def get_resolved_size(self) -> int:
        """get the resolved size for this tag

        Returns:
            :class:`int`: resolved size
        """
        if not self.data_decorated_stucture_size:
            return 0

        native_size = int(self.data_decorated_stucture_size)
        return native_size * self.get_data_multiplier()


class RaModule(
    RaPlcObject[dict],
    Module,
    metaclass=FactoryTypeMeta['RaModule', ModuleFactory]
):

    default_l5x_file_path = PLC_MOD_FILE
    default_l5x_asset_key = 'Module'

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: str = '',
        description: str = '',
    ) -> None:

        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
        )

        self._config_tag: Optional[RaModuleConnectionTag] = None
        self._input_tag: Optional[RaModuleConnectionTag] = None
        self._output_tag: Optional[RaModuleConnectionTag] = None

    @property
    def communications(self) -> dict:
        return self.get_communications()

    @property
    def config_tag(self) -> Optional[RaModuleConnectionTag]:
        return self.get_config_tag()

    @property
    def connections(self) -> list[dict]:
        return self.get_connections()

    @property
    def controller_connection(self) -> dict:
        return self.get_controller_connection()

    @property
    def dict_key_order(self) -> list[str]:
        return [
            '@Name',
            '@CatalogNumber',
            '@Vendor',
            '@ProductType',
            '@ProductCode',
            '@Major',
            '@Minor',
            '@ParentModule',
            '@ParentModPortId',
            '@Inhibited',
            '@MajorFault',
            'Description',
            'EKey',
            'Ports',
            'Communications',
        ]

    @property
    def input_tag(self) -> Optional[RaModuleConnectionTag]:
        return self.get_input_tag()

    @property
    def major_fault(self) -> bool:
        return self.get_major_fault()

    @property
    def output_tag(self) -> Optional[RaModuleConnectionTag]:
        return self.get_output_tag()

    @classmethod
    def get_factory(cls):
        return ModuleFactory

    def get_ip_address(self) -> str:
        return self.ports[0]['@Address'] if self.ports and len(self.ports) > 0 else ''

    def set_ip_address(self, ip_address: str):
        if self.ports and len(self.ports) > 0:
            self.ports[0]['@Address'] = ip_address

    def get_catalog_number(self) -> str:
        return self.meta_data.get('@CatalogNumber', '')

    def set_catalog_number(self, catalog_number: str):
        self['@CatalogNumber'] = catalog_number

    def get_communications(self) -> dict:
        return self['Communications']

    def set_communications(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("Communications must be a dictionary!")

        self['Communications'] = value

    def get_controller_connection(self) -> dict:
        if not self.connections or len(self.connections) == 0:
            return {}
        return self.connections[0]

    def get_connections(self) -> list[dict]:
        if not self.communications:
            return []
        if not self.communications.get('Connections', None):
            return []

        if not isinstance(self.communications['Connections'], dict):
            self.communications['Connections'] = {'Connection': []}
        if not isinstance(self.communications['Connections'].get('Connection', []), list):
            self.communications['Connections']['Connection'] = [self.communications['Connections']['Connection']]
        return self.communications['Connections'].get('Connection', [])

    def get_is_inhibited(self) -> bool:
        return self['@Inhibited'].lower() == 'true'

    def set_is_inhibited(self, inhibited: bool):
        str_value = 'true' if inhibited else 'false'
        self['@Inhibited'] = str_value

    def get_major_version_number(self) -> str:
        return self.meta_data.get('@Major', '')

    def set_major_version_number(self, major_version_number: str):
        try:
            self['@Major'] = str(int(major_version_number))
        except ValueError:
            raise ValueError("@Major must be an integer!")

    def get_minor_version_number(self) -> str:
        return self.meta_data.get('@Minor', '')

    def set_minor_version_number(self, minor_version_number: str):
        try:
            self['@Minor'] = str(int(minor_version_number))
        except ValueError:
            raise ValueError("@Minor must be an integer!")

    def get_parent_module(self):
        ctrl = ControllerInstanceManager.get_controller()
        if ctrl is None:
            raise ValueError("Controller not set for this module")
        parent_mod = ctrl.modules.get(self['@ParentModule'], None)
        if not parent_mod:
            raise ValueError(f"Parent module '{self['@ParentModule']}' not found in controller")
        return parent_mod

    def set_parent_module(self, parent_module: IModule):
        self['@ParentModule'] = parent_module.name

    def get_product_code(self) -> str:
        return self.meta_data.get('@ProductCode', '')

    def set_product_code(self, product_code: str):
        try:
            self['@ProductCode'] = str(int(product_code))
        except ValueError:
            raise ValueError("@ProductCode must be an integer!")

    def get_product_type(self) -> str:
        return self.meta_data.get('@ProductType', '')

    def set_product_type(self, product_type: str):
        try:
            self['@ProductType'] = str(int(product_type))
        except ValueError:
            raise ValueError("@ProductType must be an integer!")

    def get_vendor(self) -> str:
        return self.meta_data.get('@Vendor', '')

    def set_vendor(self, vendor: str):
        try:
            self['@Vendor'] = str(int(vendor))
        except ValueError:
            raise ValueError("Vendor must be an integer!")

    def get_config_connection_point(self) -> int:
        if not self.connections or len(self.connections) == 0:
            return -1
        return int(self.connections[0].get('@ConfigCxnPoint', 0))

    def get_input_connection_point(self) -> int:
        if not self.connections or len(self.connections) == 0:
            return -1
        return int(self.connections[0].get('@InputCxnPoint', 0))

    def get_output_connection_point(self) -> int:
        if not self.connections or len(self.connections) == 0:
            return -1
        return int(self.connections[0].get('@OutputCxnPoint', 0))

    def get_config_connection_size(self) -> int:
        if not self._config_tag:
            self.compile_tag_meta_data()
        if not self._config_tag:
            return 0
        return self._config_tag.config_size

    def get_input_connection_size(self) -> int:
        if not self.controller_connection:
            return 0
        return int(self.controller_connection.get('@InputSize', 0))

    def get_output_connection_size(self) -> int:
        if not self.controller_connection:
            return 0
        return int(self.controller_connection.get('@OutputSize', 0))

    def get_config_tag(self) -> Optional[RaModuleConnectionTag]:
        if not self._config_tag:
            self.compile_tag_meta_data()
        return self._config_tag

    def get_input_tag(self) -> Optional[RaModuleConnectionTag]:
        if not self._input_tag:
            self.compile_tag_meta_data()
        return self._input_tag

    def get_output_tag(self) -> Optional[RaModuleConnectionTag]:
        if not self._output_tag:
            self.compile_tag_meta_data()
        return self._output_tag

    def get_major_fault(self) -> bool:
        return self.meta_data.get('@MajorFault', 'false') == 'true'

    def set_major_fault(self, value: bool):
        str_value = 'true' if value else 'false'
        self['@MajorFault'] = str_value

    @property
    def ekey(self) -> dict:
        return self['EKey']

    @property
    def ports(self) -> list[dict]:
        if not self['Ports']:
            return []

        if not isinstance(self['Ports']['Port'], list):
            return [self['Ports']['Port']]

        return self['Ports']['Port']

    @property
    def rpi(self) -> str:
        return self.controller_connection.get('@RPI', '')

    def get_rpi(self) -> str:
        return self.rpi

    def set_rpi(self, rpi: str):
        if self.controller_connection:
            self.controller_connection['@RPI'] = rpi

    def compile(self):
        self.compile_tag_meta_data()
        return self

    def compile_tag_meta_data(self):
        if not self.communications:
            return

        config_tag_data = self.communications.get('ConfigTag', None)
        if config_tag_data:
            self._config_tag = RaModuleConnectionTag(meta_data=config_tag_data)

        if not self.connections:
            return

        input_tag_data = self.controller_connection.get('InputTag', None)
        output_tag_data = self.controller_connection.get('OutputTag', None)

        if input_tag_data:
            self._input_tag = RaModuleConnectionTag(meta_data=input_tag_data)
        if output_tag_data:
            self._output_tag = RaModuleConnectionTag(meta_data=output_tag_data)
