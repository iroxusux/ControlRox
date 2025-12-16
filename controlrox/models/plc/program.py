"""Program module for pyrox
"""
from controlrox.interfaces import IProgram
from .meta import PlcObject
from .protocols import (
    CanBeSafe,
    CanEnableDisable,
    HasInstructions,
    HasRoutines,
    HasTags,
)


class Program(
    IProgram,
    CanBeSafe,
    CanEnableDisable,
    HasInstructions,
    HasRoutines,
    HasTags,
    PlcObject[dict],
):

    def __init__(
        self,
        enabled: bool = True,
        meta_data=None,
        name: str = '',
        description: str = '',
    ) -> None:
        CanBeSafe.__init__(self)
        CanEnableDisable.__init__(self, enabled=enabled)
        HasInstructions.__init__(self)
        HasRoutines.__init__(self)
        HasTags.__init__(self)
        PlcObject.__init__(
            self,
            meta_data=meta_data,
            name=name,
            description=description,
        )

    def compile(self):
        return self
