"""Ford implimentation specific plc types
"""
from typing import Generic, Optional, TypeVar
from controlrox.interfaces import META
from controlrox.models.plc.rockwell import (
    RaPlcObject,
    RaAddOnInstruction,
    RaController,
    RaDatatype,
    RaLogicInstruction,
    RaModule,
    RaProgram,
    RaRung,
    RaRoutine,
    RaTag,
)


FORD_CTRL = TypeVar('FORD_CTRL', bound='FordController')


class FordPlcObject(
    RaPlcObject[META],
    Generic[META]
):
    """Ford Plc Object"""


class FordAddOnInstruction(FordPlcObject[dict], RaAddOnInstruction):
    """General Motors AddOn Instruction Definition"""


class FordDatatype(FordPlcObject[dict], RaDatatype):
    """General Motors Datatype"""


class FordLogicInstruction(
    FordPlcObject[str],
    RaLogicInstruction,
):
    """Ford Logic Instruction
    """


class FordModule(
    FordPlcObject[dict],
    RaModule
):
    """General Motors Module
    """


class FordRung(
    FordPlcObject[dict],
    RaRung
):
    """Ford Rung
    """


class FordRoutine(
    FordPlcObject[dict],
    RaRoutine
):
    """Ford Routine
    """


class FordTag(
    FordPlcObject[dict],
    RaTag
):
    """Ford Tag
    """


class FordProgram(
    FordPlcObject[dict],
    RaProgram
):
    """Ford Program
    """

    @property
    def comm_edit_routine(self) -> Optional[FordRoutine]:
        return self.routines.get('A_Comm_Edit', None)


class FordController(
    FordPlcObject[dict],
    RaController
):
    """Ford Plc Controller
    """

    generator_type = 'FordEmulationGenerator'


FordPlcObject.supporting_class = FordController
