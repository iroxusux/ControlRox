"""Meta definition for PLC models and architecture.
"""
from typing import (
    Callable,
    Generic,
    Optional,
    Self,
    Union
)
from pyrox.models.abc import (
    EnforcesNaming,
    HashList,
    PyroxObject,
)
from controlrox.interfaces import IController, IPlcObject, META
from controlrox.services import ControllerInstanceManager
from .protocols import HasController, HasMetaData


class PlcObject(
    IPlcObject[META],
    HasController,
    HasMetaData[META],
    EnforcesNaming,
    PyroxObject,
    Generic[META],
):
    """Base class for a PLC object.

    Args:
        meta_data: Metadata for this object.
        name: The name of this object.
        description: The description of this object.
        controller: The controller this object belongs to.

    Attributes:
        meta_data: The metadata dictionary or string for this object.
        name: The name of this object.
        description: The description of this object.
        controller: The controller this object belongs to.
    """

    def __init__(
        self,
        meta_data: Optional[Union[dict, str, None]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> None:
        HasController.__init__(self)
        HasMetaData.__init__(self, meta_data=meta_data)
        PyroxObject.__init__(self, **kwargs)

        if not name and isinstance(self.meta_data, dict):
            name = (
                self.meta_data.get("Name", None) or
                self.meta_data.get("@Name", None) or
                self.meta_data.get("name", None) or
                self.meta_data.get("@name", None)
            )

        if not description and isinstance(self.meta_data, dict):
            description = (
                self.meta_data.get("Description", None) or
                self.meta_data.get("@Description", None) or
                self.meta_data.get("description", None) or
                self.meta_data.get("@description", None)
            )

        # initialize internal datas
        self._name = name or ""
        self._description = description or ""

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.name)

    @property
    def name(self) -> str:
        """Get this object's name.
        PlcObject isn't named, so return the class name.
        This attribute is read-only for this class.

        Returns:
            str: The name of this object.
        """
        return self._name

    @property
    def process_name(self) -> str:
        """Get the process name of this object's controller without plant or customer prefixes / suffixes.

        Returns:
            str: The process name of this object's controller.
        """
        return self.name  # Override in subclasses if needed

    @property
    def description(self) -> str:
        """Get the description of this object.

        Returns:
            str: The description of this object.
        """
        return self._description

    def add_asset_to_meta_data(
        self,
        asset: IPlcObject,
        asset_list: Union[HashList, list],
        raw_asset_list: list[dict],
        index: Optional[int] = None,
        inhibit_invalidate: bool = False,
        invalidate_method: Optional[Callable] = None
    ) -> None:
        """Add an asset to this object's metadata.

        Args:
            asset: The asset to add.
            asset_list: The HashList containing the asset.
            raw_asset_list: The raw metadata list.
            index: The index to insert the asset at. If None, appends to the end.
            inhibit_invalidate: If True, does not invalidate the object after adding.
            invalidate_method: Optional method to call to invalidate the object.

        Raises:
            ValueError: If asset is wrong type or already exists.
        """
        if not isinstance(asset, (PlcObject, str)):
            raise ValueError(f"asset must be of type PlcObject or string! Got {type(asset)}")

        if not isinstance(asset_list, Union[list, HashList]):
            raise ValueError('asset list must be of type HashList or list!')

        if not isinstance(raw_asset_list, list):
            raise ValueError('raw asset list must be of type list!')

        if asset.name in asset_list:
            self.remove_asset_from_meta_data(
                asset,
                asset_list,
                raw_asset_list,
                inhibit_invalidate=True
            )

        if isinstance(asset, PlcObject):
            if not isinstance(asset.meta_data, dict):
                raise ValueError('asset meta_data must be of type dict!')

            if index is None:
                index = index or len(raw_asset_list)

            raw_asset_list.insert(index, asset.meta_data)
            asset_list.append(asset)

        if inhibit_invalidate:
            return

        if invalidate_method and callable(invalidate_method):
            invalidate_method()
            return

        self.invalidate()

    def remove_asset_from_meta_data(
        self,
        asset: IPlcObject,
        asset_list: Union[HashList, list],
        raw_asset_list: list[dict],
        inhibit_invalidate: bool = False,
        invalidate_method: Optional[Callable] = None
    ) -> None:
        """Remove an asset from this object's metadata.

        Args:
            asset: The asset to remove.
            asset_list: The HashList containing the asset.
            raw_asset_list: The raw metadata list.
            inhibit_invalidate: If True, does not invalidate the object after removing.
            invalidate_method: Optional method to call to invalidate the object.

        Raises:
            ValueError: If asset is wrong type or doesn't exist.
        """
        if not isinstance(asset, PlcObject):
            raise ValueError(f"asset must be of type {PlcObject.__name__}!")

        if not isinstance(asset_list, Union[list, HashList]):
            raise ValueError('asset list must be of type HashList or list!')

        if not isinstance(raw_asset_list, list):
            raise ValueError('raw asset list must be of type list!')

        if asset in asset_list:
            raw_asset_to_remove = next((x for x in raw_asset_list if x["@Name"] == asset.name), None)
            if raw_asset_to_remove is not None:
                raw_asset_list.remove(raw_asset_to_remove)

        if inhibit_invalidate:
            return

        if invalidate_method and callable(invalidate_method):
            invalidate_method()
            return

        self.invalidate()

    def compile(self) -> Self:
        """Compile this object.

        Additionally, this method will call all functions in the on_compiled list.

        Returns:
            Self: This object for method chaining.
        """
        raise NotImplementedError("This method should be overridden by subclasses to compile the object.")

    def set_description(
        self,
        description: str
    ) -> None:
        """Set the description of this object.

        Args:
            description: The new description for this object.
        """
        self._description = description

        if isinstance(self.meta_data, dict):
            self.meta_data["Description"] = description

    def set_name(
        self,
        name: str
    ) -> None:
        """Set the name of this object.

        Args:
            name: The new name for this object.

        Raises:
            ValueError: If the name is not a valid string.
        """
        if not isinstance(name, str):
            raise self.InvalidNamingException(f"Name must be a string, got {type(name)}")
        if not self.is_valid_string(name):
            raise self.InvalidNamingException(f"Invalid name: {name}")
        self._name = name

        if isinstance(self.meta_data, dict):
            self.meta_data["@Name"] = name

    def get_controller(self) -> Optional[IController]:
        """Get the controller this object belongs to.

        Returns:
            Optional[IController]: The controller if set, None otherwise.
        """
        if self._controller:
            return self._controller
        self._controller = ControllerInstanceManager.get_controller()
        return self._controller

    def set_controller(
        self,
        controller: Optional[IController]
    ) -> None:
        """Set the controller for this object.

        Args:
            controller: The controller to set.
        """
        ControllerInstanceManager.set_controller(controller)
        self._controller = ControllerInstanceManager.get_controller()

    def invalidate(self) -> None:
        """Invalidate this object.

        This method will call the _invalidate method to reset the object's state.
        """
        raise NotImplementedError("This method should be overridden by subclasses to invalidate the object.")
