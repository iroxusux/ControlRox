from pyrox.interfaces import IApplication
from pyrox.models import ApplicationTask
from .app import ControllerApplication


class ControllerApplicationTask(
    ApplicationTask,
):

    def __init__(
        self,
        application: ControllerApplication,
    ) -> None:
        self._application = application

    @property
    def application(self) -> ControllerApplication:
        """Get the parent application of this task.

        Returns:
            ControllerApplication: The parent application instance.
        """
        return self.get_application()

    @application.setter
    def application(
        self,
        application: IApplication
    ) -> None:
        """Set the parent application for this task.

        Args:
            application: The application instance to set.
        """
        self.set_application(application)

    def get_application(self) -> ControllerApplication:
        return self._application

    def set_application(self, application: IApplication) -> None:
        if not isinstance(application, ControllerApplication):
            raise TypeError(f'Expected application of type ControllerApplication, got {type(application)}')
        self._application = application

    def inject(self) -> None:
        """Inject this task into the application.
        """
        return
