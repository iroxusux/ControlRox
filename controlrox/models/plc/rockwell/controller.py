"""PLC type module for Pyrox framework."""
from __future__ import annotations

from typing import (
    List,
    Optional,
)

from pyrox.models.abc.list import HashList
from pyrox.models.abc.factory import FactoryTypeMeta
from pyrox.services.dict import replace_strings_in_dict
from pyrox.services.file import get_save_file
from pyrox.services.logging import log
from controlrox.interfaces import (
    IAddOnInstruction,
    IControllerSafetyInfo,
    IDatatype,
    ILogicInstruction,
    IModule,
    ITag,
    IProgram,
    ILogicAssetType
)
from controlrox.models.plc.controller import Controller
from controlrox.services.l5x import l5x_dict_from_file
from controlrox.services.plc import ControllerFactory

from .meta import (
    RaPlcObject,
    L5X_ASSET_ADDONINSTRUCTIONDEFINITIONS,
    L5X_ASSET_DATATYPES,
    L5X_ASSET_MODULES,
    L5X_ASSET_PROGRAMS,
    L5X_ASSET_TAGS,
    L5X_ASSETS,
)


__all__ = (
    'RaController',
    'ControllerSafetyInfo',
)


class ControllerSafetyInfo(
    RaPlcObject,
    IControllerSafetyInfo
):
    def __init__(
        self,
        meta_data: str,
        **kwargs
    ) -> None:
        super().__init__(
            meta_data=meta_data,
            **kwargs
        )

    @property
    def safety_tag_map(self) -> str:
        return self.get_safety_tag_map()

    @property
    def safety_tag_map_dict_list(self) -> list[dict]:
        if not self.safety_tag_map:
            return []

        if not isinstance(self.safety_tag_map, str):
            raise ValueError("Safety tag map must be a string!")

        string_data = self.safety_tag_map.strip().split(',')
        if len(string_data) == 1 and string_data[0] == '':
            return []

        dict_list = []
        for pair in string_data:
            dict_list.append({
                '@Name': pair.split('=')[0].strip(),
                'TagName': pair.split('=')[0].strip(),
                'SafetyTagName': pair.split('=')[1].strip()
            })

        return dict_list

    def get_safety_locked(self) -> bool:
        return self['@SafetyLocked'] == 'true'

    def set_safety_locked(self, safety_locked: bool) -> None:
        if not isinstance(safety_locked, bool):
            raise ValueError("Safety locked must be a boolean!")
        self['@SafetyLocked'] = 'true' if safety_locked else 'false'

    def get_signature_runmode_protected(self) -> bool:
        return self['@SignatureRunModeProtect'] == 'true'

    def set_signature_runmode_protected(self, signature_runmode_protected: bool):
        if not isinstance(signature_runmode_protected, bool):
            raise ValueError("Signature runmode protect must be a boolean!")
        self['@SignatureRunModeProtect'] = 'true' if signature_runmode_protected else 'false'

    def get_configure_safety_io_always(self) -> bool:
        return self['@ConfigureSafetyIOAlways'] == 'true'

    def set_configure_safety_io_always(self, configure_safety_io_always: bool):
        if not isinstance(configure_safety_io_always, bool):
            raise ValueError("Configure safety IO always must be a boolean!")
        self['@ConfigureSafetyIOAlways'] = 'true' if configure_safety_io_always else 'false'

    def get_safety_level(self) -> str:
        return self['@SafetyLevel']

    def set_safety_level(self, safety_level: str):
        if not isinstance(safety_level, str):
            raise ValueError("Safety level must be a string!")

        if not any(x in safety_level for x in ['SIL1', 'SIL2', 'SIL3', 'SIL4']):
            raise ValueError("Safety level must contain one of: SIL1, SIL2, SIL3, SIL4!")

        self['@SafetyLevel'] = safety_level

    def get_safety_tag_map(self) -> str:
        if self['SafetyTagMap'] is None:
            return ''

        return self['SafetyTagMap']

    def set_safety_tag_map(self, safety_tag_map: str):
        if not isinstance(safety_tag_map, str):
            raise ValueError("Safety tag map must be a string!")

        if not safety_tag_map:
            self['SafetyTagMap'] = None
            return

        # Validate format: should be "tag_name=safety_tag_name, ..."
        pairs = safety_tag_map.split(',')
        for pair in pairs:
            pair = pair.strip()
            if not pair:
                continue
            if '=' not in pair or len(pair.split('=')) != 2:
                raise ValueError("Safety tag map must be in the format 'tag_name=safety_tag_name, ...'")

        self['SafetyTagMap'] = safety_tag_map.strip()

    def add_safety_tag_mapping(
        self,
        tag_name: str,
        safety_tag_name: str
    ) -> None:
        """Add a new safety tag mapping to the safety tag map.

        Args:
            tag_name (str): The standard tag name
            safety_tag_name (str): The corresponding safety tag name

        Raises:
            ValueError: If tag names are not strings
        """
        if not isinstance(tag_name, str) or not isinstance(safety_tag_name, str):
            raise ValueError("Tag names must be strings!")

        if not self.safety_tag_map:
            self.set_safety_tag_map(f"{tag_name}={safety_tag_name}")
            return

        self.set_safety_tag_map(self.safety_tag_map.strip())

        if f',{tag_name}={safety_tag_name}' in self.safety_tag_map:
            self.set_safety_tag_map(self.safety_tag_map.replace(f",{tag_name}={safety_tag_name}", ''))
        elif f"{tag_name}={safety_tag_name}," in self.safety_tag_map:
            self.set_safety_tag_map(self.safety_tag_map.replace(f"{tag_name}={safety_tag_name},", ''))
        self.set_safety_tag_map(self.safety_tag_map + f",{tag_name}={safety_tag_name}")

    def remove_safety_tag_mapping(
        self,
        tag_name: str,
        safety_tag_name: str
    ) -> None:
        """Remove a safety tag mapping from the safety tag map.

        Args:
            tag_name (str): The standard tag name
            safety_tag_name (str): The corresponding safety tag name
        Raises:
            ValueError: If tag names are not strings
        """
        if not isinstance(tag_name, str) or not isinstance(safety_tag_name, str):
            raise ValueError("Tag names must be strings!")

        if not self.safety_tag_map:
            return

        self.set_safety_tag_map(self.safety_tag_map.strip())
        if f",{tag_name}={safety_tag_name}" in self.safety_tag_map:
            self.set_safety_tag_map(self.safety_tag_map.replace(f",{tag_name}={safety_tag_name}", ''))
        elif f"{tag_name}={safety_tag_name}," in self.safety_tag_map:
            self.set_safety_tag_map(self.safety_tag_map.replace(f"{tag_name}={safety_tag_name},", ''))
        elif f"{tag_name}={safety_tag_name}" in self.safety_tag_map:
            self.set_safety_tag_map(self.safety_tag_map.replace(f"{tag_name}={safety_tag_name}", ''))


class RaController(
    RaPlcObject[dict],
    Controller,
    metaclass=FactoryTypeMeta['RaController', ControllerFactory]
):
    generator_type = 'EmulationGenerator'
    default_l5x_file_path = None
    default_l5x_asset_key = None

    def __getitem__(self, key):
        return self.controller_meta_data.get(key, None)

    def __setitem__(self, key, value):
        self.controller_meta_data[key] = value
        if key == '@MajorRev' or key == '@MinorRev':
            log(self).info('Changing revisions of processor...')
            self.content_meta_data['@SoftwareRevision'] = f'{self.major_revision}.{self.minor_revision}'
            if not self.plc_module:
                raise RuntimeError('No PLC module found in controller!')
            self.plc_module['@Major'] = self.major_revision
            self.plc_module['@Minor'] = self.minor_revision

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        file_location: Optional[str] = None,
        **kwargs
    ) -> None:
        kwargs['name'] = self._get_name_from_meta_data(meta_data)
        super().__init__(
            meta_data=meta_data,
            **kwargs
        )

        self.file_location, self.ip_address, self.slot = file_location, None, None

        self._aois: HashList[IAddOnInstruction] = HashList('name')
        self._datatypes: HashList[IDatatype] = HashList('name')
        self._modules: HashList[IModule] = HashList('name')
        self._programs: HashList[IProgram] = HashList('name')
        self._tags: HashList[ITag] = HashList('name')
        self._safety_info: IControllerSafetyInfo = ControllerSafetyInfo(
            meta_data=self.content_meta_data['Controller'].get('SafetyInfo', None),
        )
        self._processor_type = self.l5x_meta_data.get('@ProcessorType', '')

    @property
    def content_meta_data(self) -> dict:
        if self.meta_data is None:
            raise RuntimeError('Meta data is not set!')
        return self.meta_data['RSLogix5000Content']

    @property
    def controller_meta_data(self) -> dict:
        return self.content_meta_data['Controller']

    @property
    def controller_type(self) -> str:
        return self.__class__.__name__

    @property
    def file_location(self) -> str:
        if self._file_location is None:
            file_location = get_save_file(filetypes=[('.L5x', 'L5X Files')])
            if not file_location:
                raise RuntimeError('File location is not set!')
            self._file_location = file_location
        return self._file_location

    @file_location.setter
    def file_location(
        self,
        value: Optional[str]
    ):
        if not isinstance(value, str) and value is not None:
            raise ValueError('File location must be a string or None!')
        self._file_location = value

    @property
    def input_instructions(self) -> list[ILogicInstruction]:
        instr = []
        [instr.extend(x.get_input_instructions()) for x in self.programs]
        return instr

    @property
    def instructions(self) -> list[ILogicInstruction]:
        """get the instructions in this controller

        Returns:
            :class:`list[ILogicInstruction]`
        """
        instr = []
        [instr.extend(x.get_instructions()) for x in self.programs]
        return instr

    @property
    def ip_address(self) -> Optional[str]:
        return self._ip_address

    @ip_address.setter
    def ip_address(
        self,
        value: Optional[str]
    ) -> None:
        if not isinstance(value, str) and value is not None:
            raise ValueError('IP address must be a string or None!')
        self._assign_address(value)

    @property
    def l5x_meta_data(self) -> dict:
        return self.content_meta_data['Controller']

    @l5x_meta_data.setter
    def l5x_meta_data(self, value) -> None:
        self.content_meta_data['Controller'] = value

    @property
    def major_revision(self) -> int:
        rev = self['@MajorRev']
        if not rev:
            raise RuntimeError('Major revision is not set!')
        return int(rev)

    @major_revision.setter
    def major_revision(self, value: int):
        self['@MajorRev'] = int(value)

    @property
    def minor_revision(self) -> int:
        rev = self['@MinorRev']
        if not rev:
            raise RuntimeError('Minor revision is not set!')
        return int(rev)

    @minor_revision.setter
    def minor_revision(self, value: int):
        self['@MinorRev'] = int(value)

    @property
    def output_instructions(self) -> list[ILogicInstruction]:
        instr = []
        [instr.extend(x.get_output_instructions()) for x in self.programs]
        return instr

    @property
    def plc_module(self) -> Optional[dict]:
        if not self.raw_modules:
            return None
        for module in self.raw_modules:
            if not isinstance(module, dict):
                continue
            if module['@Name'] == 'Local':
                return module
        return None

    @property
    def plc_module_icp_port(self) -> Optional[dict]:
        if not self.plc_module_ports:
            return None
        for port in self.plc_module_ports:
            if not isinstance(port, dict):
                continue
            if port['@Type'] == 'ICP' or port['@Type'] == '5069':
                return port
        return None

    @property
    def plc_module_ports(self) -> list[dict]:
        if not self.plc_module:
            return []

        if not isinstance(self.plc_module['Ports']['Port'], list):
            return [self.plc_module['Ports']['Port']]
        return self.plc_module['Ports']['Port']

    @property
    def safety_info(self) -> IControllerSafetyInfo:
        return self._safety_info

    @property
    def slot(self) -> Optional[int]:
        if not self.plc_module_icp_port:
            return None
        return int(self.plc_module_icp_port['@Address'])

    @slot.setter
    def slot(self,
             value: Optional[int]
             ) -> None:
        if value is not None:
            value = int(value)
            if value < 0 or value > 16:
                raise ValueError('Slot must be between 0 and 16!')
        self._slot = value

    @classmethod
    def from_file(
        cls,
        file_location: str,
        meta_data: Optional[dict] = None
    ) -> 'RaController':
        """Create a controller instance from a file.

        Args:
            file_location: The path to the L5X file.
            meta_data: Optional metadata for the controller.
        Returns:
            RaController: The created controller instance.
        """
        if meta_data is None:
            meta_data = l5x_dict_from_file(file_location)
            if not meta_data:
                raise ValueError(f'No L5X data could be read from file: {file_location}')

        controller = cls(meta_data=meta_data, file_location=file_location)
        controller.compile()
        return controller

    @classmethod
    def from_meta_data(
        cls,
        meta_data: dict,
        file_location: str = '',
        comms_path: str = '',
        slot: int = 0
    ) -> 'RaController':
        """Create a controller instance from metadata.

        Args:
            meta_data: The metadata dictionary.
            file_location: Optional file location.
            comms_path: Optional communication path.
            slot: Optional slot number.
        Returns:
            RaController: The created controller instance.
        """
        controller = cls(meta_data=meta_data, file_location=file_location)
        controller.compile()

        if comms_path:
            controller.set_comms_path(comms_path)
        if slot != 0:
            controller.slot = slot

        return controller

    @classmethod
    def get_factory(cls):
        return ControllerFactory

    def _assign_address(
        self,
        address: Optional[str]
    ) -> None:
        if address is None:
            self._ip_address = None
            return
        octets = address.split('.')
        if not octets or len(octets) != 4:
            raise ValueError('IP Octets invalid!')

        for _, v in enumerate(octets):
            if 0 > int(v) > 255:
                raise ValueError(f'IP address octet range ivalid: {v}')

        self._ip_address = address

    def _compile_atomic_datatypes(self) -> None:
        """Compile atomic datatypes from the controller's datatypes."""
        from .datatype import BUILTINS
        for dt in BUILTINS:
            self._datatypes.append(dt)  # type: ignore

    def _get_name_from_meta_data(
        self,
        meta_data: Optional[dict]
    ) -> str:
        if not meta_data:
            raise RuntimeError('Meta data is not set!')

        lgx_content_dict = meta_data.get('RSLogix5000Content', None)
        if not lgx_content_dict:
            raise RuntimeError('RSLogix5000Content meta data is not set!')

        ctrl_dict = lgx_content_dict.get('Controller', None)
        if not ctrl_dict:
            raise RuntimeError('Controller meta data is not set!')

        return ctrl_dict.get('@Name', '')

    def compile_datatypes(self) -> None:
        self._compile_atomic_datatypes()
        return super().compile_datatypes()

    def get_comms_path(self) -> str:
        path = self['@CommPath']
        return path or ''

    def set_comms_path(self, comms_path: str) -> None:
        if not isinstance(comms_path, str):
            raise ValueError('CommPath must be a string!')
        self['@CommPath'] = comms_path

    def get_controller_safety_info(self) -> IControllerSafetyInfo:
        """Get the safety info of the controller.

        Returns:
            IControllerSafetyInfo: The controller safety info.
        """
        return self._safety_info

    def get_raw_l5x_asset_list(
        self,
        asset_type: str
    ) -> list[dict]:
        if asset_type not in L5X_ASSETS:
            raise ValueError(f'Invalid asset type: {asset_type}')

        asset_dict = self[asset_type]

        if not asset_dict or not isinstance(asset_dict, dict):
            asset_dict = {asset_type[:-1]: []}

        asset_list = asset_dict.get(asset_type[:-1], [])
        if not isinstance(asset_list, list):
            asset_list = [asset_list]

        return asset_list

    def import_assets_from_file(
        self,
        file_location: str,
        asset_types: Optional[List[str]] = L5X_ASSETS
    ) -> None:
        """Import assets from an L5X file into this controller.
            .. -------------------------------
            .. arguments::
            :class:`str` file_location:
                the L5X file to import from
            :class:`list[str]` asset_types:
                the types of assets to import (e.g., ['DataTypes', 'Tags'])
            """
        l5x_dict = l5x_dict_from_file(file_location)
        if not l5x_dict:
            log(self).warning(f'No L5X dictionary could be read from file: {file_location}')
            return

        self.import_assets_from_l5x_dict(l5x_dict, asset_types=asset_types)

    def import_assets_from_l5x_dict(
        self,
        l5x_dict: dict,
        asset_types: Optional[List[str]] = L5X_ASSETS
    ) -> None:
        """Import assets from an L5X dictionary into this controller.
            .. -------------------------------
            .. arguments::
            :class:`dict` l5x_dict:
                the L5X dictionary to import from
            :class:`list[str]` asset_types:
                the types of assets to import (e.g., ['DataTypes', 'Tags'])
            """
        if not l5x_dict:
            log(self).warning('No L5X dictionary provided for import.')
            return

        if 'RSLogix5000Content' not in l5x_dict:
            log(self).warning('No RSLogix5000Content found in provided L5X dictionary.')
            return
        if 'Controller' not in l5x_dict['RSLogix5000Content']:
            log(self).warning('No Controller found in RSLogix5000Content in provided L5X dictionary.')
            return

        if not asset_types:
            log(self).warning('No asset types provided to import!')
            return

        controller_data = l5x_dict['RSLogix5000Content']['Controller']

        for asset_type in asset_types:
            if asset_type not in controller_data:
                log(self).warning(f'No {asset_type} found in Controller in provided L5X dictionary.')
                continue

            items = controller_data[asset_type]

            item_list = items.get(asset_type[:-1], [])
            if not isinstance(item_list, list):
                item_list = [item_list]

            for item in item_list:
                try:
                    match asset_type:
                        case 'DataTypes':
                            datatype = self.create_datatype(meta_data=item)
                            self.add_datatype(datatype)
                            log(self).info(f'Datatype {datatype.name} imported successfully.')
                        case 'Tags':
                            tag = self.create_tag(meta_data=item, container=self)
                            self.add_tag(tag)
                            log(self).info(f'Tag {tag.name} imported successfully.')
                        case 'Programs':
                            program = self.create_program(meta_data=item)
                            self.add_program(program)
                            log(self).info(f'Program {program.name} imported successfully.')
                        case 'AddOnInstructionDefinitions':
                            aoi = self.create_aoi(meta_data=item)
                            self.add_aoi(aoi)
                            log(self).info(f'AOI {aoi.name} imported successfully.')
                        case 'Modules':
                            module = self.create_module(meta_data=item)
                            self.add_module(module)
                            log(self).info(f'Module {module.name} imported successfully.')
                        case _:
                            log(self).warning(f'Unknown asset type: {asset_type}. Skipping...')
                except ValueError as e:
                    log(self).warning(f'Failed to add {asset_type[:-1]}:\n{e}')
                    continue

    def get_created_date(self) -> str:
        return self.l5x_meta_data.get('@ProjectCreationDate', 'N/A?')

    def get_modified_date(self) -> str:
        return self.l5x_meta_data.get('@LastModifiedDate', 'N/A?')

    def get_raw_aois(self) -> List[dict]:
        return self.get_raw_l5x_asset_list(L5X_ASSET_ADDONINSTRUCTIONDEFINITIONS)

    def get_raw_datatypes(self) -> List[dict]:
        return self.get_raw_l5x_asset_list(L5X_ASSET_DATATYPES)

    def get_raw_modules(self) -> List[dict]:
        return self.get_raw_l5x_asset_list(L5X_ASSET_MODULES)

    def get_raw_programs(self) -> List[dict]:
        return self.get_raw_l5x_asset_list(L5X_ASSET_PROGRAMS)

    def get_raw_tags(self) -> List[dict]:
        return self.get_raw_l5x_asset_list(L5X_ASSET_TAGS)

    def get_revision(self) -> str:
        return f'{self.major_revision}.{self.minor_revision}'

    def rename_asset(
        self,
        element_type: ILogicAssetType,
        name: str,
        replace_name: str
    ):
        if not element_type or not name or not replace_name:
            return

        match element_type:
            case ILogicAssetType.TAG:
                replace_strings_in_dict(
                    self.raw_tags,
                    name,
                    replace_name
                )

            case ILogicAssetType.ALL:
                replace_strings_in_dict(
                    self.l5x_meta_data,
                    name,
                    replace_name
                )

            case _:
                return


# Assign support class for factory automation
RaPlcObject.supporting_class = RaController
