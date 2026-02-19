"""types module for pyrox"""
from . import (
    gui,
    plc,
)

# PLC section
from .plc import (
    # Protocol definitions
    HasController,
    HasInstructions,
    HasPrograms,
    HasRoutines,
    HasRungs,
    HasTags,

    # Meta definitions
    PlcObject,

    # Logic specific types
    Datatype,
    DatatypeMember,
    LogicInstruction,
    LogicOperand,
    Module,
    Program,
    Routine,
    Rung,
    Tag,

    # Controller types
    Controller,
)


# Tasks section
from .tasks import (
    # Application section
    ControllerApplication,

    # Task section
    ControllerApplicationTask,

    # Generator section
    EmulationGenerator,

    # Introspective section
    IntrospectiveModule,

    # Modification section
    ControllerModificationSchema,

    # Validator section
    ControllerValidatorFactory,
    ControllerValidator,
)

# Scene section
from . import scene


__all__ = (
    'gui',
    'plc',

    # PLC section
    # Protocol definitions
    'HasController',
    'HasInstructions',
    'HasPrograms',
    'HasRoutines',
    'HasRungs',
    'HasTags',

    # Meta definitions
    'PlcObject',

    # Logic specific types
    'Datatype',
    'DatatypeMember',
    'LogicInstruction',
    'LogicOperand',
    'Module',
    'Program',
    'Routine',
    'Rung',
    'Tag',

    # Controller types
    'Controller',

    # Tasks section
    # Generator section
    'EmulationGenerator',

    # Introspective section
    'IntrospectiveModule',

    # Modification section
    'ControllerModificationSchema',

    # Validator section
    'ControllerValidatorFactory',
    'ControllerValidator',

    # Application section
    'ControllerApplication',

    # Task section
    'ControllerApplicationTask',

    # Scene section
    'scene',

)
