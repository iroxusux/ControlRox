from typing import Optional, List, Union
from pyrox.models import FactoryTypeMeta, HashList, MetaFactory
from pyrox.services import log
from controlrox.interfaces import (
    ModuleControlsType,
    IIntrospectiveModule,
    IModule,
)


class IntrospectiveModuleWarehouseFactory(MetaFactory):
    """Factory for creating ModuleWarehouse instances."""

    @classmethod
    def get_all_known_modules(cls) -> List[type[IIntrospectiveModule]]:
        """Get all known module CLASSES from all registered warehouses.

        Returns:
            List[type[IntrospectiveModule]]: List of all known module classes.
        """
        module_classes = []
        warehouses = cls.get_registered_types()

        for warehouse_name, warehouse_cls in warehouses.items():
            if warehouse_cls:
                module_classes.extend(warehouse_cls.get_known_module_classes())
            else:
                log(cls).warning(f'Warehouse class for {warehouse_name} is None')

        return module_classes

    @classmethod
    def get_modules_by_type(
        cls,
        module_type: ModuleControlsType
    ) -> List[IIntrospectiveModule]:
        """Get all modules of a specific type from all registered warehouses.

        Args:
            module_type (ModuleControlsType): The type of module to filter by.

        Returns:
            List[IntrospectiveModule]: List of modules matching the specified type.
        """
        modules = []
        warehouses = cls.get_registered_types()

        for warehouse_name, warehouse_cls in warehouses.items():
            if warehouse_cls:
                modules.extend(warehouse_cls.get_modules_by_type(module_type))
            else:
                log(cls).warning(f'Warehouse class for {warehouse_name} is None')

        return modules

    @classmethod
    def filter_modules_by_type(
        cls,
        modules: Union[List[IModule], HashList[IModule]],
        module_type: ModuleControlsType
    ) -> List[IIntrospectiveModule]:
        """Filter a list of modules by a specific type.

        Args:
            modules (List[IntrospectiveModule]): The list of modules to filter.
            module_type (ModuleControlsType): The type of module to filter by.

        Returns:
            List[IntrospectiveModule]: List of modules matching the specified type.
        """
        filtered = []
        for module in modules:
            imodule = cls.get_imodule_from_meta_data(module, True)
            if not imodule:
                log(cls).warning(f'Module {module} has no introspective_module, skipping...')
                continue
            if imodule.module_controls_type != module_type:
                continue
            filtered.append(imodule)
        return filtered

    @classmethod
    def get_imodule_from_meta_data(
        cls,
        module: IModule,
        lazy_match_catalog: Optional[bool] = False
    ) -> Optional[IIntrospectiveModule]:
        """Create an IntrospectiveModule from a Module instance.
        This method will attempt to match the module to a known IntrospectiveModule subclass

        Args:
            module (Module): The Module instance to wrap.
            lazy_match_catalog (bool, optional): If True, will attempt to match the catalog number
                using a substring match if an exact match is not found. Defaults to False.

        Returns:
            IntrospectiveModule: An instance of the matched IntrospectiveModule subclass,
                or a generic IntrospectiveModule if no match is found.

        Raises:
            ValueError: If the module is None.
        """
        if not module:
            raise ValueError('Module is required to create an IntrospectiveModule.')

        all_introspective_modules = cls.get_all_known_modules()

        for im in all_introspective_modules:
            imodule = im.create_from_module(module)
            imodule.set_base_module(module)

            if lazy_match_catalog and module.catalog_number and module.catalog_number != 'ETHERNET-MODULE':
                if imodule.catalog_number in module.catalog_number:
                    return imodule

            if imodule.catalog_number != module.catalog_number:
                continue
            if imodule.input_connection_point != module.input_connection_point:
                continue
            if imodule.output_connection_point != module.output_connection_point:
                continue
            if imodule.config_connection_point != module.config_connection_point:
                continue
            if imodule.input_connection_size != module.input_connection_size:
                continue
            if imodule.output_connection_size != module.output_connection_size:
                continue
            if imodule.config_connection_size != module.config_connection_size:
                continue
            return imodule

        log(cls).warning(
            'No matching module type found for %s, enable debug for more info.',
            module.name
        )
        log(cls).debug('Module details: %s', {
            'ModuleName': module.name,
            'CatalogNumber': module.catalog_number,
            'InputCxnPoint': module.input_connection_point,
            'OutputCxnPoint': module.output_connection_point,
            'ConfigCxnPoint': module.config_connection_point,
            'InputSize': module.input_connection_size,
            'OutputSize': module.output_connection_size,
            'ConfigSize': module.config_connection_size,
        })
        return None


class IntrospectiveModuleWarehouse(
    MetaFactory,
    metaclass=FactoryTypeMeta['IntrospectiveModuleWarehouse', IntrospectiveModuleWarehouseFactory]
):
    """Class used to manage a collection of IntrospectiveModules.

    Can filter types, catalog numbers, etc.
    """

    supports_registering = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.supports_registering = True  # Subclasses can be used to match

    @classmethod
    def get_factory(cls) -> type[IntrospectiveModuleWarehouseFactory]:
        return IntrospectiveModuleWarehouseFactory

    @classmethod
    def get_known_module_classes(cls) -> list[type[IIntrospectiveModule]]:
        """Get all known module classes from this warehouse.

        Returns:
            list[type[IntrospectiveModule]]: List of IntrospectiveModule subclasses.
        """
        # This should return the actual IntrospectiveModule subclass types
        # that this warehouse knows about. You'll need to implement this
        # based on how your warehouses store their module types.
        classes = []
        for known in cls.get_registered_types().values():
            if issubclass(known, IIntrospectiveModule):
                classes.append(known)
        return classes
