"""Module model for pyrox Controller applications."""
from typing import Optional
from controlrox.interfaces import (
    IModule,
)
from .meta import PlcObject


class Module(
    IModule,
    PlcObject[dict],
):

    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:

        super().__init__(
            meta_data=meta_data,
            name=name,
            description=description,
        )

    def get_catalog_number(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the catalog number.")

    def get_ip_address(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the IP address.")

    def get_is_inhibited(self) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses to get the inhibited status.")

    def get_major_version_number(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the major version number.")

    def get_minor_version_number(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the minor version number.")

    def get_parent_module(self) -> IModule:
        raise NotImplementedError("This method should be overridden by subclasses to get the parent module.")

    def get_product_code(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the product code.")

    def get_product_type(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the product type.")

    def get_rpi(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the RPI.")

    def get_vendor(self) -> str:
        raise NotImplementedError("This method should be overridden by subclasses to get the vendor.")

    def set_catalog_number(
        self,
        catalog_number: str
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the catalog number.")

    def set_is_inhibited(
        self,
        inhibited: bool
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the inhibited status.")

    def set_ip_address(
        self,
        ip_address: str
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the IP address.")

    def set_major_version_number(self, major_version_number: str) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the major version number.")

    def set_minor_version_number(self, minor_version_number: str) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the minor version number.")

    def set_parent_module(self, parent_module: IModule) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the parent module.")

    def set_product_code(
        self,
        product_code: str
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the product code.")

    def set_product_type(
        self,
        product_type: str
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the product type.")

    def set_rpi(
        self,
        rpi: str
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the RPI.")

    def set_vendor(
        self,
        vendor: str
    ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses to set the vendor.")
