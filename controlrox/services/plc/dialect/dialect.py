"""Dialect services for PLCs
This module provides classes and interfaces for handling different PLC dialects.
It defines enumerations and interfaces to manage variations in PLC programming
languages, ensuring compatibility and extensibility across different PLC manufacturers.
"""
from pyrox.models import MetaFactory
from controlrox.interfaces import (
    PLCDialect,
    IHasRungsTranslator,
    IHasInstructionsTranslator,
    IHasOperandsTranslator,
)

from .instruction import (
    RockwellInstructionsTranslator,
    SiemensInstructionsTranslator,
)
from .operand import (
    RockwellOperandsTranslator,
    SiemensOperandsTranslator,
)
from .rung import (
    RockwellRungsTranslator,
    SiemensRungsTranslator,
)


class DialectTranslatorFactory(MetaFactory):
    """Dialect Translation Factory.
    This factory manages translators for different PLC dialects.
    """

    @classmethod
    def get_rungs_translator(
        cls,
        dialect: PLCDialect
    ) -> IHasRungsTranslator:
        """Get the appropriate rung translator for the specified dialect.

        Args:
            dialect (PLCDialect): The PLC dialect.

        Returns:
            IHasRungsTranslator: The translator for the specified dialect.
        """
        if dialect == PLCDialect.RSLOGIX5000:
            return RockwellRungsTranslator()
        elif dialect == PLCDialect.STEP7:
            return SiemensRungsTranslator()
        else:
            raise NotImplementedError(f"No rung translator implemented for dialect: {dialect}")

    @classmethod
    def get_instruction_translator(
        cls,
        dialect: PLCDialect
    ) -> IHasInstructionsTranslator:
        """Get the appropriate instruction translator for the specified dialect.

        Args:
            dialect (PLCDialect): The PLC dialect.
        Returns:
            IHasInstructionsTranslator: The translator for the specified dialect.
        """
        if dialect == PLCDialect.RSLOGIX5000:
            return RockwellInstructionsTranslator()
        elif dialect == PLCDialect.STEP7:
            return SiemensInstructionsTranslator()
        else:
            raise NotImplementedError(f"No instruction translator implemented for dialect: {dialect}")

    @classmethod
    def get_operand_translator(
        cls,
        dialect: PLCDialect
    ) -> IHasOperandsTranslator:
        """Get the appropriate operand translator for the specified dialect.

        Args:
            dialect (PLCDialect): The PLC dialect.
        Returns:
            IHasOperandsTranslator: The translator for the specified dialect.
        """
        if dialect == PLCDialect.RSLOGIX5000:
            return RockwellOperandsTranslator()
        elif dialect == PLCDialect.STEP7:
            return SiemensOperandsTranslator()
        else:
            raise NotImplementedError(f"No operand translator implemented for dialect: {dialect}")
