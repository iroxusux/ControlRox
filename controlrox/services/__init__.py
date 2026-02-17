"""services module for pyrox
"""
from .tasks import generator

from . import (
    debug,
    l5x,
)

# Design services
from .design import (
    convert_markdown_to_html,
    render_checklist,
)

# Plc service classes
from .plc import (
    # Connection imports
    PlcConnectionManager,
    # Factory imports
    AOIFactory,
    DatatypeFactory,
    InstructionFactory,
    ModuleFactory,
    OperandFactory,
    ProgramFactory,
    RoutineFactory,
    RungFactory,
    TagFactory,

    # Controller imports
    ControllerMatcher,
    ControllerFactory,
    ControllerMatcherFactory,
    ControllerInstanceManager,

    # Dialect imports
    DialectTranslatorFactory,

    # Emulation services
    emu,
    create_checklist_from_template,
    inject_emulation_routine,
    remove_emulation_routine,

    # instruction extraction function
    extract_instruction_strings,
)


__all__ = (
    'debug',
    'emu',
    # 'eplan',
    'generator',
    'l5x',

    # Design services
    'convert_markdown_to_html',
    'render_checklist',

    # Connection imports
    'PlcConnectionManager',

    # Plc Factory services
    'AOIFactory',
    'DatatypeFactory',
    'InstructionFactory',
    'ModuleFactory',
    'OperandFactory',
    'ProgramFactory',
    'RoutineFactory',
    'RungFactory',
    'TagFactory',

    # Plc service classes
    'ControllerMatcher',
    'ControllerFactory',
    'ControllerMatcherFactory',
    'ControllerInstanceManager',

    # Dialect services
    'DialectTranslatorFactory',

    # Emulation services
    'create_checklist_from_template',
    'inject_emulation_routine',
    'remove_emulation_routine',

    # Instruction extraction function
    'extract_instruction_strings',
)
