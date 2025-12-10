"""Generic Generated Module Class.
This is the base class for all auto-generated module classes.
"""
from pyrox.models.abc.factory import FactoryTypeMeta
from controlrox.models import (
    Controller,
    IntrospectiveModule,
)
from controlrox.services import ControllerInstanceManager
from controlrox.services.plc.introspective import IntrospectiveModuleWarehouse


class GeneratedModule(
    IntrospectiveModule,
    metaclass=FactoryTypeMeta['GeneratedModule', IntrospectiveModuleWarehouse]
):
    """Generic Generated Module.

    This class is intended to be the base class for all auto-generated module classes.
    """

    supports_registering = False

    def __init_subclass__(cls, **kwargs):
        cls.supports_registering = True
        return super().__init_subclass__(**kwargs)

    @classmethod
    def get_factory(cls):
        return IntrospectiveModuleWarehouse

    @property
    def controller(self) -> Controller:
        """Get the controller instance."""
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError("No active controller found for this GeneratedModule.")
        return ctrl

    def get_safety_input_tag_name(self):
        return f'sz_Demo3D_{self.base_module.name}_I'

    def get_safety_output_tag_name(self):
        return f'sz_Demo3D_{self.base_module.name}_O'

    def get_standard_input_tag_name(self):
        return f'zz_Demo3D_{self.base_module.name}_I'

    def get_standard_output_tag_name(self):
        return f'zz_Demo3D_{self.base_module.name}_O'
