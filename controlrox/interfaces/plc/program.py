"""Program interface for PLCs."""
from .meta import IPlcObject
from .protocols import (
    ICanBeSafe,
    ICanEnableDisable,
    IHasInstructions,
    IHasRoutines,
    IHasTags,
)


class IProgram(
    ICanBeSafe,
    ICanEnableDisable,
    IPlcObject[dict],
    IHasInstructions,
    IHasRoutines,
    IHasTags,
):
    """Program interface for PLCs.
    """


__all__ = [
    'IProgram',
]
