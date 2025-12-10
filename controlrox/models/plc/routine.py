"""Pyrox routine model
"""
from typing import (
    Optional,
)
from controlrox.interfaces import (
    IRoutine,
)
from controlrox.services import ControllerInstanceManager
from .protocols import HasInstructions, HasRoutines, HasRungs
from .meta import PlcObject


class Routine(
    IRoutine,
    HasInstructions,
    HasRungs,
    PlcObject[dict],
):
    def __init__(
        self,
        meta_data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        container: Optional[HasRoutines] = None,
    ) -> None:
        HasInstructions.__init__(self)
        HasRungs.__init__(self)
        PlcObject.__init__(
            self=self,
            meta_data=meta_data,
            name=name,
            description=description,
        )
        self._container: Optional[HasRoutines] = container

    @property
    def container(self) -> Optional[HasRoutines]:
        return self.get_container()

    def block(self) -> None:
        raise NotImplementedError("block method must be implemented by subclass.")

    def check_for_jsr(
        self,
        routine_name: str,
    ) -> bool:
        raise NotImplementedError("check_for_jsr method must be implemented by subclass.")

    def compile_rungs(self):
        """compile the rungs in this routine

        This method compiles the rungs from the raw metadata and initializes the list.
        """
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            raise ValueError("No active controller found for compiling rungs.")

        self._rungs = []
        for index, rung in enumerate(self.raw_rungs):
            self._rungs.append(ctrl.create_rung(
                meta_data=rung,
                routine=self,
                rung_number=index
            ))

    def get_container(self) -> HasRoutines:
        if self._container is None:
            raise ValueError("Container is not set for this routine.")
        return self._container

    def set_container(self, container: HasRoutines) -> None:
        if not isinstance(container, HasRoutines):
            raise TypeError("Container must implement IHasRoutines interface.")
        self._container = container

    def unblock(self) -> None:
        raise NotImplementedError("unblock method must be implemented by subclass.")
