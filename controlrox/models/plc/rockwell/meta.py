"""Meta definitions for PLC models and architecture.
"""
from pathlib import Path
from typing import (
    Generic,
    Optional,
    Union
)
from pyrox.models import HashList
from pyrox.services.dict import insert_key_at_index
from controlrox.interfaces import (
    META,
    IController,
)
from controlrox.models.plc.meta import PlcObject
from controlrox.services.l5x import l5x_dict_from_file

INST_RE_PATTERN: str = r'[A-Za-z0-9_]+\(\S*?\)'
INST_TYPE_RE_PATTERN: str = r'([A-Za-z0-9_]+)(?:\(.*?)(?:\))'
INST_OPER_RE_PATTERN: str = r'(?:[A-Za-z0-9_]+\()(.*?)(?:\))'

PLC_ROOT_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / 'root.L5X'
PLC_PROG_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_program.L5X'
PLC_ROUT_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_routine.L5X'
PLC_DT_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_datatype.L5X'
PLC_AOI_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_aoi.L5X'
PLC_MOD_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_module.L5X'
PLC_RUNG_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_rung.L5X'
PLC_TAG_FILE = Path(__file__).resolve().parents[4] / 'docs' / 'controls' / '_tag.L5X'

BASE_FILES = [
    PLC_ROOT_FILE,
    PLC_PROG_FILE,
    PLC_ROUT_FILE,
    PLC_DT_FILE,
    PLC_AOI_FILE,
    PLC_MOD_FILE,
    PLC_RUNG_FILE,
    PLC_TAG_FILE,
]

RE_PATTERN_META_PRE = r"(?:"
RE_PATTERN_META_POST = r"\()(.*?)(?:\))"


XIC_OPERAND_RE_PATTERN = r"(?:XIC\()(.*)(?:\))"
XIO_OPERAND_RE_PATTERN = r"(?:XIO\()(.*)(?:\))"

INPUT_INSTRUCTIONS_RE_PATTER = [
    XIC_OPERAND_RE_PATTERN,
    XIO_OPERAND_RE_PATTERN
]


OTE_OPERAND_RE_PATTERN = r"(?:OTE\()(.*?)(?:\))"
OTL_OPERAND_RE_PATTERN = r"(?:OTL\()(.*?)(?:\))"
OTU_OPERAND_RE_PATTERN = r"(?:OTU\()(.*?)(?:\))"
MOV_OPERAND_RE_PATTERN = r"(?:MOV\()(.*?)(?:\))"
MOVE_OPERAND_RE_PATTERN = r"(?:MOVE\()(.*?)(?:\))"
COP_OPERAND_RE_PATTERN = r"(?:COP\()(.*?)(?:\))"
CPS_OPERAND_RE_PATTERN = r"(?:CPS\()(.*?)(?:\))"

OUTPUT_INSTRUCTIONS_RE_PATTERN = [
    OTE_OPERAND_RE_PATTERN,
    OTL_OPERAND_RE_PATTERN,
    OTU_OPERAND_RE_PATTERN,
    MOV_OPERAND_RE_PATTERN,
    MOVE_OPERAND_RE_PATTERN,
    COP_OPERAND_RE_PATTERN,
    CPS_OPERAND_RE_PATTERN
]


# ------------------- Logix Assets ------------------------------ #
# Hardcoded asset types for L5X files
L5X_ASSET_DATATYPES = 'DataTypes'
L5X_ASSET_TAGS = 'Tags'
L5X_ASSET_PROGRAMS = 'Programs'
L5X_ASSET_ADDONINSTRUCTIONDEFINITIONS = 'AddOnInstructionDefinitions'
L5X_ASSET_MODULES = 'Modules'

L5X_ASSETS = [
    L5X_ASSET_DATATYPES,
    L5X_ASSET_TAGS,
    L5X_ASSET_PROGRAMS,
    L5X_ASSET_ADDONINSTRUCTIONDEFINITIONS,
    L5X_ASSET_MODULES
]

# ------------------- L5X Common Properties --------------------- #
# Common properties found in L5X files
L5X_PROP_NAME = '@Name'
L5X_PROP_DESCRIPTION = 'Description'


class RaPlcObject(
    Generic[META],
    PlcObject[META],
):
    """Base class for a L5X PLC object.
    """

    default_l5x_file_path: Optional[Union[Path, str]] = None
    default_l5x_asset_key: Optional[str] = None

    def __init__(
        self,
        meta_data: Optional[Union[dict, str]] = None,
        name: str = '',
        description: str = '',
        controller: Optional[IController] = None,
        **kwargs
    ) -> None:
        meta_data = self.get_default_meta_data(
            meta_data=meta_data,
            file_location=self.default_l5x_file_path,
            l5x_dict_key=self.default_l5x_asset_key
        )
        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
            controller=controller,
            **kwargs
        )
        if self._name:
            self.set_name(self._name)
        if self._description:
            self.set_description(self._description)
        self.init_dict_order()

    @property
    def dict_key_order(self) -> list[str]:
        """Get the order of keys in the metadata dict.

        This is intended to be overridden by subclasses to provide a specific order of keys.

        Returns:
            list[str]: List of keys in preferred order.
        """
        return []

    @classmethod
    def get_default_meta_data(
        cls,
        meta_data: Optional[Union[dict, str]],
        file_location: Optional[Union[str, Path]],
        l5x_dict_key: Optional[str]
    ) -> Optional[Union[dict, str]]:
        """Validate passed meta data and load default meta data if necessary.

        Args:
            meta_data: The metadata to validate or load.
            file_location: The file location to load default metadata from if necessary.
            l5x_dict_key: The key in the L5X file to load the metadata
        Returns:
            Union[dict, str]: The validated or loaded metadata.
        Raises:
            ValueError: If file_location or l5x_dict_key is not provided when meta_data is None.
        """
        if meta_data is not None and not isinstance(meta_data, (dict, str)):
            raise ValueError(f"meta_data must be of type dict, str, or None! Got {type(meta_data)}")

        if isinstance(meta_data, str):
            return meta_data  # Assume it's an attribute string and let the caller handle it

        if meta_data is not None:
            return meta_data  # Already a dict, so just return it

        file_location = file_location or cls.default_l5x_file_path
        l5x_dict_key = l5x_dict_key or cls.default_l5x_asset_key

        if not isinstance(meta_data, dict) and meta_data is not None:
            raise ValueError(f"meta_data must be of type dict or None! Got {type(meta_data)}")

        if file_location is None:
            return meta_data  # No file location to load from, so just return what was passed in

        meta_dict = l5x_dict_from_file(file_location)
        if not meta_dict:
            raise ValueError(f"Could not load default meta data from file location {file_location}!")

        if l5x_dict_key is None:
            meta_data = meta_dict
            return meta_data  # No dict key to load from, so just return what was passed in

        meta_data = meta_dict[l5x_dict_key]
        if meta_data is None or not isinstance(meta_data, dict):
            raise ValueError(f"Default meta data from file location {file_location} is invalid!")

        return meta_data

    def get_asset_from_meta_data(
        self,
        asset_name: str,
        asset_list_name: str
    ) -> list[dict]:
        """Get an asset from this object's metadata.

        Args:
            asset_name: The name of the asset to get.
            asset_list: The name of the list containing the asset.

        Returns:
            Optional[Self]: The asset if found, None otherwise.

        Raises:
            ValueError: If asset_list is wrong type.
        """
        if not self[asset_name]:
            self[asset_name] = {asset_list_name: []}
        if not isinstance(self[asset_name][asset_list_name], list):
            if self[asset_name][asset_list_name] == {} or self[asset_name][asset_list_name] is None:
                self[asset_name][asset_list_name] = []
            else:
                self[asset_name][asset_list_name] = [self[asset_name][asset_list_name]]
        return self[asset_name][asset_list_name]

    def init_dict_order(self):
        """Initialize the dict order for this object.

        This method relies on the child classes to define their own dict_key_order property.
        """
        if not self.dict_key_order:
            return

        if isinstance(self.meta_data, dict):
            for index, key in enumerate(self.dict_key_order):
                if key not in self.meta_data:
                    insert_key_at_index(d=self.meta_data, key=key, index=index)

    def redefine_raw_asset_list_from_asset_list(
        self,
        asset_list: HashList,
        raw_asset_list: list[dict]
    ) -> None:
        """Redefine the raw asset list from the asset list.

        Args:
            asset_list: The HashList containing the assets.
            raw_asset_list: The raw metadata list to redefine.
        """
        if not isinstance(asset_list, HashList):
            raise ValueError('asset list must be of type HashList!')

        if not isinstance(raw_asset_list, list):
            raise ValueError('raw asset list must be of type list!')

        raw_asset_list.clear()
        for asset in asset_list:
            if isinstance(asset, (PlcObject)):
                if not isinstance(asset.meta_data, dict):
                    raise ValueError('asset meta_data must be of type dict!')
                raw_asset_list.append(asset.meta_data)
            else:
                raise ValueError(f"asset must be of type PlcObject! Got {type(asset)}")

        self.invalidate()
