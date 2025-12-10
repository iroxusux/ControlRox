from abc import abstractmethod
from enum import Enum
from typing import Any
from .meta import IPlcObject
from .protocols import IHasConnectionTags


class ModuleControlsType(Enum):
    """Module controls type enumeration."""
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
    SAFETY_SCANNER = 'SafetyScanner'

    @staticmethod
    def all_block_types() -> list['ModuleControlsType']:
        """Get all block types

        Returns:
            :class:`list[ModuleControlsType]`: list of all block types
        """
        return [
            ModuleControlsType.BLOCK,
            ModuleControlsType.INPUT_BLOCK,
            ModuleControlsType.OUTPUT_BLOCK,
            ModuleControlsType.INPUT_OUTPUT_BLOCK,
            ModuleControlsType.CONFIG_BLOCK,
            ModuleControlsType.SAFETY_BLOCK,
            ModuleControlsType.SAFETY_INPUT_BLOCK,
            ModuleControlsType.SAFETY_OUTPUT_BLOCK,
            ModuleControlsType.SAFETY_INPUT_OUTPUT_BLOCK,
            ModuleControlsType.SAFETY_CONFIG_BLOCK,
        ]


class IModuleConnectionTag(
    IPlcObject[dict]
):
    @abstractmethod
    def get_data(self) -> Any:
        """get the data of this module connection tag

        Returns:
            :class:`Any`: data of this module connection tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the data.")

    @abstractmethod
    def get_tag_name(self) -> str:
        """get the tag name of this module connection tag

        Returns:
            :class:`str`: tag name of this module connection tag
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the tag name.")


class IModule(
    IPlcObject[dict],
    IHasConnectionTags
):

    @property
    def catalog_number(self) -> str:
        return self.get_catalog_number()

    @property
    def inhibited(self) -> bool:
        return self.get_is_inhibited()

    @property
    def ip_address(self) -> str:
        return self.get_ip_address()

    @property
    def vendor(self) -> str:
        return self.get_vendor()

    @property
    def product_type(self) -> str:
        return self.get_product_type()

    @property
    def product_code(self) -> str:
        return self.get_product_code()

    @property
    def major_version(self) -> str:
        return self.get_major_version_number()

    @property
    def minor_version(self) -> str:
        return self.get_minor_version_number()

    @property
    def parent_module(self) -> 'IModule':
        return self.get_parent_module()

    @property
    def rpi(self) -> str:
        return self.get_rpi()

    @abstractmethod
    def get_catalog_number(self) -> str:
        """get the catalog number of this module

        Returns:
            :class:`str`: catalog number of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the catalog number.")

    @abstractmethod
    def get_ip_address(self) -> str:
        """get the IP address of this module

        Returns:
            :class:`str`: IP address of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the IP address.")

    @abstractmethod
    def get_is_inhibited(self) -> bool:
        """get if this module is inhibited

        Returns:
            :class:`bool`: True if inhibited, False otherwise
        """
        raise NotImplementedError("This method should be overridden by subclasses to get if the module is inhibited.")

    @abstractmethod
    def get_major_version_number(self) -> str:
        """get the major version number of this module

        Returns:
            :class:`str`: major version number of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the major version number.")

    @abstractmethod
    def get_minor_version_number(self) -> str:
        """get the minor version number of this module

        Returns:
            :class:`str`: minor version number of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the minor version number.")

    @abstractmethod
    def get_parent_module(self) -> 'IModule':
        """get the parent module of this module

        Returns:
            :class:`IModule`: parent module of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the parent module.")

    @abstractmethod
    def get_product_code(self) -> str:
        """get the product code of this module

        Returns:
            :class:`str`: product code of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the product code.")

    @abstractmethod
    def get_product_type(self) -> str:
        """get the product type of this module

        Returns:
            :class:`str`: product type of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the product type.")

    @abstractmethod
    def get_rpi(self) -> str:
        """get the RPI of this module

        Returns:
            :class:`str`: RPI of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the RPI.")

    @abstractmethod
    def get_vendor(self) -> str:
        """get the vendor of this module

        Returns:
            :class:`str`: vendor of this module
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the vendor.")

    @abstractmethod
    def set_catalog_number(
        self,
        catalog_number: str
    ) -> None:
        """set the catalog number of this module

        Args:
            catalog_number (str): catalog number to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the catalog number.")

    @abstractmethod
    def set_is_inhibited(
        self,
        inhibited: bool
    ) -> None:
        """set if this module is inhibited

        Args:
            inhibited (bool): True to inhibit, False otherwise
        """
        raise NotImplementedError("This method should be overridden by subclasses to set if the module is inhibited.")

    @abstractmethod
    def set_major_version_number(
        self,
        major_version_number: str
    ) -> None:
        """set the major version number of this module

        Args:
            major_version_number (str): major version number to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the major version number.")

    @abstractmethod
    def set_minor_version_number(
        self,
        minor_version_number: str
    ) -> None:
        """set the minor version number of this module

        Args:
            minor_version_number (str): minor version number to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the minor version number.")

    @abstractmethod
    def set_parent_module(
        self,
        parent_module: 'IModule'
    ) -> None:
        """set the parent module of this module

        Args:
            parent_module (IModule): parent module to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the parent module.")

    @abstractmethod
    def set_product_code(
        self,
        product_code: str
    ) -> None:
        """set the product code of this module

        Args:
            product_code (str): product code to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the product code.")

    @abstractmethod
    def set_product_type(
        self,
        product_type: str
    ) -> None:
        """set the product type of this module

        Args:
            product_type (str): product type to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the product type.")

    @abstractmethod
    def set_rpi(
        self,
        rpi: str
    ) -> None:
        """set the RPI of this module

        Args:
            rpi (str): RPI to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the RPI.")

    @abstractmethod
    def set_vendor(
        self,
        vendor: str
    ) -> None:
        """set the vendor of this module

        Args:
            vendor (str): vendor to set
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the vendor.")


__all__ = [
    'IModule',
    'IModuleConnectionTag',
    'ModuleControlsType',
]
