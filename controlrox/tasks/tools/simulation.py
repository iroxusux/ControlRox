"""PLC Inspection Application
    """
from datetime import datetime
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.models import simulation


class SimulationTask(ControllerApplicationTask):
    """Controller Simulation Task.
    Simulate realworld field devices interacting with a live PLC.
    """

    def _scene_loop(self, scene: simulation.Scene) -> None:
        """Run the simulation loop for the given scene."""
        if not scene:
            return

        time_delta = datetime.now() - self._time_delta
        scene.update(time_delta.total_seconds())
        self._time_delta = datetime.now()
        self.application.gui_backend.schedule_event(
            self._update_interval_ms,
            self._scene_loop,
            scene=scene
        )

    def run(self) -> None:
        self._update_interval_ms = 1000
        self._time_delta = datetime.now()
        scene = simulation.Scene(name="Demo Scene", description="A demo simulation scene.")
        self.application.gui_backend.schedule_event(
            self._update_interval_ms,
            self._scene_loop,
            scene=scene
        )

    def inject(self) -> None:
        self.application.menu.unsafe_get_tools_menu().add_item(
            label='Simulation',
            command=self.run
        )
