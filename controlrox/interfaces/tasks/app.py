
"""Application Interface for ControlRox module.
"""
from abc import abstractmethod
from typing import (
    Optional,
)
from controlrox.interfaces.plc import IController


class IControllerApplication:

    @property
    def controller(self) -> Optional[IController]:
        """Get the controller associated with this application.

        Returns:
            IController: The controller instance.
        """
        return self.get_controller()

    @controller.setter
    def controller(self, controller: Optional[IController]) -> None:
        """Set the controller associated with this application.

        Args:
            controller (IController): The controller instance.
        """
        self.set_controller(controller)

    @abstractmethod
    def get_controller(self) -> Optional[IController]:
        """Get the controller associated with this application.

        Returns:
            IController: The controller instance.
        """
        ...

    @abstractmethod
    def set_controller(
        self,
        controller: Optional[IController]
    ) -> None:
        """Set the controller associated with this application.

        Args:
            controller (IController): The controller instance.
        """
        ...
