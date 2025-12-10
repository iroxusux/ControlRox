"""services module for pyrox
"""
from .tasks import generator

from . import (
    debug,
    l5x,
)

# Plc service classes
from .plc import (
    # Factory imports
    AOIFactory,
    DatatypeFactory,
    InstructionFactory,
    ModuleFactory,
    ProgramFactory,
    RoutineFactory,
    RungFactory,
    TagFactory,

    # Controller imports
    ControllerMatcher,
    ControllerFactory,
    ControllerMatcherFactory,
    ControllerInstanceManager,

    # Emulation services
    emu,
    create_checklist_from_template,
    inject_emulation_routine,
    remove_emulation_routine,
)


__all__ = (
    'debug',
    'emu',
    # 'eplan',
    'generator',
    'l5x',

    # Plc Factory services
    'AOIFactory',
    'DatatypeFactory',
    'InstructionFactory',
    'ModuleFactory',
    'ProgramFactory',
    'RoutineFactory',
    'RungFactory',
    'TagFactory',

    # Plc service classes
    'ControllerMatcher',
    'ControllerFactory',
    'ControllerMatcherFactory',
    'ControllerInstanceManager',

    # Emulation services
    'create_checklist_from_template',
    'inject_emulation_routine',
    'remove_emulation_routine',
)
