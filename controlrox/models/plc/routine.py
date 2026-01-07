"""Pyrox routine model
"""
from typing import (
    Optional,
)
from pyrox.models import FactoryTypeMeta
from controlrox.interfaces import (
    IHasRoutines,
    IRoutine,
)
from controlrox.services import RoutineFactory
from .protocols import HasInstructions, HasRoutines, HasRungs
from .meta import PlcObject


class Routine(
    IRoutine,
    HasInstructions,
    HasRungs,
    PlcObject[dict],
    metaclass=FactoryTypeMeta['Routine', RoutineFactory]
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
    def container(self) -> IHasRoutines:
        return self.get_container()

    @classmethod
    def get_factory(cls):
        return RoutineFactory

    def block(self) -> None:
        raise NotImplementedError("block method must be implemented by subclass.")

    def check_for_jsr(
        self,
        routine_name: str,
    ) -> bool:
        raise NotImplementedError("check_for_jsr method must be implemented by subclass.")

    def compile(self):
        self.compile_rungs()
        return self

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
