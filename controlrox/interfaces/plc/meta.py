"""meta interfaces for PLC objects
"""
from abc import abstractmethod
from enum import Enum
from typing import (
    Generic,
    Self
)
from .protocols import IHasController, IHasMetaData, META

# ------------------ L5X Keyword Defitions -------------------- #
TAG = 'Tag'
DATATYPE = 'DataType'
TAGTYPE = 'TagType'

# ------------------ Input Instructions ----------------------- #
# All input instructions assume every operand is type INPUT
INSTR_XIC = 'XIC'
INSTR_XIO = 'XIO'
INSTR_LIM = 'LIM'
INSTR_MEQ = 'MEQ'
INSTR_EQU = 'EQU'
INSTR_NEQ = 'NEQ'
INSTR_LES = 'LES'
INSTR_GRT = 'GRT'
INSTR_LEQ = 'LEQ'
INSTR_GEQ = 'GEQ'
INSTR_ISINF = 'IsINF'
INSTR_ISNAN = 'IsNAN'

INPUT_INSTRUCTIONS = [
    INSTR_XIC,
    INSTR_XIO
]

# ------------------ Output Instructions ----------------------- #
# The first index of the tuple is the instruction type
# the second index is the location of the output operand. -1 indicates the final position of an instructions operands
# (i.e., the last operand)
INSTR_OTE = ('OTE', -1)
INSTR_OTU = ('OTU', -1)
INSTR_OTL = ('OTL', -1)
INSTR_TON = ('TON', 0)
INSTR_TOF = ('TOF', 0)
INSTR_RTO = ('RTO', 0)
INSTR_CTU = ('CTU', 0)
INSTR_CTD = ('CTD', 0)
INSTR_RES = ('RES', -1)
INSTR_MSG = ('MSG', -1)
INSTR_GSV = ('GSV', -1)
ISNTR_ONS = ('ONS', -1)
INSTR_OSR = ('OSR', -1)
INSTR_OSF = ('OSF', -1)
INSTR_IOT = ('IOT', -1)
INSTR_CPT = ('CPT', 0)
INSTR_ADD = ('ADD', -1)
INSTR_SUB = ('SUB', -1)
INSTR_MUL = ('MUL', -1)
INSTR_DIV = ('DIV', -1)
INSTR_MOD = ('MOD', -1)
INSTR_SQR = ('SQR', -1)
INSTR_NEG = ('NEG', -1)
INSTR_ABS = ('ABS', -1)
INSTR_MOV = ('MOV', -1)
INSTR_MVM = ('MVM', -1)
INSTR_AND = ('AND', -1)
INSTR_OR = ('OR', -1)
INSTR_XOR = ('XOR', -1)
INSTR_NOT = ('NOT', -1)
INSTR_SWPB = ('SWPB', -1)
INSTR_CLR = ('CLR', -1)
INSTR_BTD = ('BTD', 2)
INSTR_FAL = ('FAL', 4)
INSTR_COP = ('COP', 1)
INSTR_FLL = ('FLL', 1)
INSTR_AVE = ('AVE', 2)
INSTR_SIZE = ('SIZE', -1)
ISNTR_CPS = ('CPS', 1)

OUTPUT_INSTRUCTIONS = [
    INSTR_OTE,
    INSTR_OTU,
    INSTR_OTL,
    INSTR_TON,
    INSTR_TOF,
    INSTR_RTO,
    INSTR_CTU,
    INSTR_CTD,
    INSTR_RES,
    INSTR_MSG,
    INSTR_GSV,
    ISNTR_ONS,
    INSTR_OSR,
    INSTR_OSF,
    INSTR_IOT,
    INSTR_CPT,
    INSTR_ADD,
    INSTR_SUB,
    INSTR_MUL,
    INSTR_DIV,
    INSTR_MOD,
    INSTR_SQR,
    INSTR_NEG,
    INSTR_ABS,
    INSTR_MOV,
    INSTR_MVM,
    INSTR_AND,
    INSTR_OR,
    INSTR_XOR,
    INSTR_NOT,
    INSTR_SWPB,
    INSTR_CLR,
    INSTR_BTD,
    INSTR_FAL,
    INSTR_COP,
    INSTR_FLL,
    INSTR_AVE,
    INSTR_SIZE,
    ISNTR_CPS
]


# ------------------ Special Instructions ----------------------- #
# Special instructions not known to be input or output instructions
INSTR_JSR = 'JSR'


# ------------------ Atomic Datatypes ------------------------- #
# Atomic datatypes in Logix that are not explicitly defined by the xml formatting file.
ATOMIC_DATATYPES = [
    'BIT',
    'BOOL',
    'SINT',
    'INT',
    'DINT',
    'LINT',
    'REAL',
    'LREAL',
    'USINT',
    'UINT',
    'UDINT',
    'ULINT',
    'STRING',
    'TIMER',
]


# ------------------- CIP Types --------------------------------- #
# CIP Type format: Type ID: (Size in bytes, Type Name, Struct Format)
CIPTYPES = {
    0x00: (1, "UNKNOWN", '<B'),
    0xa0: (88, "STRUCT", '<B'),
    0xc0: (8, "DT", '<Q'),
    0xc1: (1, "BOOL", '<?'),
    0xc2: (1, "SINT", '<b'),
    0xc3: (2, "INT", '<h'),
    0xc4: (4, "DINT", '<i'),
    0xc5: (8, "LINT", '<q'),
    0xc6: (1, "USINT", '<B'),
    0xc7: (2, "UINT", '<H'),
    0xc8: (4, "UDINT", '<I'),
    0xc9: (8, "LWORD", '<Q'),
    0xca: (4, "REAL", '<f'),
    0xcc: (8, "LDT", '<Q'),
    0xcb: (8, "LREAL", '<d'),
    0xd0: (1, "O_STRING", '<B'),
    0xd1: (1, "BYTE", "<B"),
    0xd2: (2, "WORD", "<I"),
    0xd3: (4, "DWORD", '<i'),
    0xd6: (4, "TIME32", '<I'),
    0xd7: (8, "TIME", '<Q'),
    0xda: (1, "STRING", '<B'),
    0xdf: (8, "LTIME", '<Q')
}


class LogicTagScope(Enum):
    """logix tag scope enumeration
    """
    PROGRAM = 0
    PUBLIC = 1
    CONTROLLER = 2


class LogicInstructionType(Enum):
    """logix instruction type enumeration
    """
    INPUT = 1
    OUTPUT = 2
    UNKNOWN = 3
    JSR = 4
    AOI = 5


class LogicAssetType(Enum):
    """logix element resolver enumeration
    """
    DEFAULT = 0
    TAG = 1
    DATATYPE = 2
    AOI = 3
    MODULE = 4
    PROGRAM = 5
    ROUTINE = 6
    PROGRAMTAG = 7
    RUNG = 8
    ALL = 9


class IPlcObject(
    IHasController,
    IHasMetaData[META],
    Generic[META],
):
    """Base interface for PLC objects.
    """

    @property
    def description(self) -> str:
        """Get the description of this object.

        Returns:
            str: The description of this object.
        """
        return self.get_description()

    @property
    def name(self) -> str:
        """Get the name of this object.

        Returns:
            str: The name of this object.
        """
        return self.get_name()

    @property
    def process_name(self) -> str:
        """Get the process name of this object's controller without plant or customer prefixes / suffixes.

        Returns:
            str: The process name of this object's controller.
        """
        return self.get_process_name()

    @abstractmethod
    def compile(self) -> Self:
        """Compile this object.

        Additionally, this method will call all functions in the on_compiled list.

        Returns:
            Self: This object for method chaining.
        """
        raise NotImplementedError("This method should be overridden by subclasses to compile the object.")

    @abstractmethod
    def invalidate(self) -> None:
        """Invalidate this object.

        This method will call the _invalidate method to reset the object's state.
        """
        raise NotImplementedError("This method should be overridden by subclasses to invalidate the object.")

    @abstractmethod
    def get_process_name(self) -> str:
        """Get the process name of this object's controller without plant or customer prefixes / suffixes.

        Returns:
            str: The process name of this object's controller.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the process name.")

    @abstractmethod
    def get_description(self) -> str:
        """Get the description of this object.

        Returns:
            str: The description of this object.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the description.")

    @abstractmethod
    def set_description(
        self,
        description: str
    ) -> None:
        """Set the description of this object.

        Args:
            description: The description to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the description.")

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this object.

        Returns:
            str: The name of this object.
        """
        raise NotImplementedError("This method should be overridden by subclasses to get the name.")

    @abstractmethod
    def set_name(
        self,
        name: str
    ) -> None:
        """Set the name of this object.

        Args:
            name: The name to set.
        """
        raise NotImplementedError("This method should be overridden by subclasses to set the name.")


__all__ = [
    'IPlcObject',
    'LogicTagScope',
    'LogicInstructionType',
    'LogicAssetType',
    'CIPTYPES',
]
