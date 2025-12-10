from pyrox.models import ApplicationTask
from .app import ControllerApplication


class ControllerApplicationTask(
    ApplicationTask[ControllerApplication],
):

    def __init__(
        self,
        application: ControllerApplication,
    ) -> None:
        self._application = application

    def inject(self) -> None:
        """Inject this task into the application.
        """
        return
