"""Translation dialects for PLC programming languages.
This module defines various dialects used in PLC programming languages
to handle differences in syntax, data types, and conventions across different
while handling multiple PLC manufacturers and models.
"""

from enum import Enum


class PLCDialect(Enum):
    """Enumeration of PLC programming language dialects."""
    RSLOGIX5000 = 'RSLogix5000'
    STEP7 = 'Step7'
    CX_PROGRAMMER = 'CXProgrammer'
    TIA_PORTAL = 'TIAPortal'
    GENERIC = 'Generic'
    # Add more dialects as needed for different PLC manufacturers/models

    @staticmethod
    def list_dialects():
        """List all available PLC dialects."""
        return [dialect.value for dialect in PLCDialect]


class IHasOperandsTranslator:
    """Interface for operand translators for different PLC dialects."""

    def get_instruction_operands(
        self,
        instruction_string: str
    ) -> list[str]:
        """Get the representation of the operand based on the dialect.

        Args:
            instruction_string (str): The instruction string to be translated.

        Returns:
            list[str]: A list of operands for the instruction.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class IHasInstructionsTranslator:
    """Interface for instruction translators for different PLC dialects."""

    def get_instruction_name(
        self,
        instruction: str
    ) -> str:
        """Get the name of the instruction based on the dialect.

        Args:
            instruction (str): The instruction string to be translated.

        Returns:
            str: The name of the instruction.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    def get_instruction_operands(
        self,
        instruction: str
    ) -> list[str]:
        """Get the operands of the instruction based on the dialect.

        Args:
            instruction (str): The instruction string to be translated.

        Returns:
            list[str]: A list of operands for the instruction.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class IHasRungsTranslator:
    """Interface for rung translators for different PLC dialects."""

    def get_raw_rungs(
        self,
        routine_data: dict
    ) -> list[dict]:
        """Get the raw rungs from the routine data based on the dialect.

        Args:
            routine_data (dict): The routine data containing rungs.

        Returns:
            list[dict]: A list of raw rung data dictionaries.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
