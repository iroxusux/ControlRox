"""Pure interface definitions for Controlrox framework.

This module provides abstract interfaces that eliminate circular dependencies
between services and models while maintaining clean architectural boundaries.

The interfaces follow the Interface Segregation Principle (ISP) and Dependency
Inversion Principle (DIP) to create a loosely-coupled, extensible system.

Key Design Principles:
    - Interfaces contain only method signatures, no implementations
    - No imports from controlrox.services or controlrox.models modules
    - Pure abstractions with minimal external dependencies
    - Support for dependency injection and plugin architectures
    - Forward-compatible design for future enhancements

Interface Categories:
    - PLC: Control logic controller abstractions
"""
from .constants import ControlRoxEnvironmentKeys

from .plc import (
    # Type Variables
    AOI,
    CTRL,
    DT,
    INST,
    MOD,
    PROG,
    ROUT,
    RUNG,
    TAG,
    META,

    # Protocols
    ICanBeSafe,
    ICanEnableDisable,
    IHasAOIs,
    IHasConnectionTags,
    IHasController,
    IHasDatatypes,
    IHasInstructions,
    IHasOperands,
    IHasRungText,
    IHasBranches,
    IHasSequencedInstructions,
    IHasMetaData,
    IHasModules,
    IHasRoutines,
    IHasPrograms,
    IHasTags,
    IHasRungs,
    ISupportsMetaDataListAssignment,

    # Meta Interfaces
    ATOMIC_DATATYPES,
    INPUT_INSTRUCTIONS,
    OUTPUT_INSTRUCTIONS,
    INSTR_JSR,
    CIPTYPES,
    IPlcObject,
    ILogicAssetType,
    ILogicInstructionType,
    ILogicTagScope,

    # Datatype Interfaces
    IDatatype,
    IDatatypeMember,
    IDatatypeProto,

    # Add-On Instruction Interfaces
    IAddOnInstruction,

    # Tag Interfaces
    ITag,
    ITagKlass,
    ITagType,
    ITagExternalAccess,

    # Logic Interfaces
    ILogicInstruction,

    # Module Interfaces
    IModule,
    IModuleConnectionTag,
    ModuleControlsType,

    # Logic Operand Interfaces
    ILogicOperand,

    # Program Interfaces
    IProgram,

    # Routine Interfaces
    IRoutine,

    # Rung Interfaces
    IRung,
    RungBranch,
    RungElement,
    RungElementType,

    # Introspective Interfaces
    IIntrospectiveModule,

    # Controller Interfaces
    IController,
    IControllerSafetyInfo,

    # Generator Interfaces
    IEmulationGenerator,

    # Dialect Interfaces
    PLCDialect,
    IHasRungsTranslator,
    IHasInstructionsTranslator,
    IHasOperandsTranslator,
)

from .tasks import (
    IControllerApplication,
)


__all__ = (
    # Constants
    "ControlRoxEnvironmentKeys",

    # Type variables section
    "AOI",
    "CTRL",
    "DT",
    "INST",
    "MOD",
    "PROG",
    "ROUT",
    "RUNG",
    "TAG",
    "META",

    # Protocols section
    "ICanBeSafe",
    "ICanEnableDisable",
    "IHasAOIs",
    "IHasConnectionTags",
    'IHasController',
    'IHasDatatypes',
    'IHasInstructions',
    'IHasOperands',
    'IHasRungText',
    'IHasBranches',
    'IHasSequencedInstructions',
    'IHasMetaData',
    'IHasModules',
    'IHasRoutines',
    'IHasPrograms',
    'IHasTags',
    'IHasRungs',
    'ISupportsMetaDataListAssignment',

    # Meta section
    'ATOMIC_DATATYPES',
    'INPUT_INSTRUCTIONS',
    'OUTPUT_INSTRUCTIONS',
    'INSTR_JSR',
    'CIPTYPES',
    'IPlcObject',
    'ILogicAssetType',
    'ILogicInstructionType',
    'ILogicTagScope',

    # Datatype section
    'IDatatype',
    'IDatatypeMember',
    'IDatatypeProto',

    # Add-On Instruction section
    'IAddOnInstruction',

    # Tag section
    'ITag',
    'ITagKlass',
    'ITagType',
    'ITagExternalAccess',

    # Instruction section
    'ILogicInstruction',

    # Module section
    'IModule',
    'IModuleConnectionTag',
    'ModuleControlsType',

    # Operand section
    'ILogicOperand',

    # Program section
    'IProgram',

    # Routine section
    'IRoutine',

    # Rung section
    'IRung',
    'RungElementType',
    'RungElement',
    'RungBranch',

    # Introspective section
    'IIntrospectiveModule',

    # Controller section
    'IController',
    'IControllerSafetyInfo',

    # Generator section
    'IEmulationGenerator',

    # Dialect section
    "PLCDialect",
    "IHasRungsTranslator",
    "IHasInstructionsTranslator",
    "IHasOperandsTranslator",

    # Tasks section
    "IControllerApplication",
)
