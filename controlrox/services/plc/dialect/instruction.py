"""Rung dialect translators for different PLC manufacturers."""
import re
from controlrox.interfaces import (
    IHasInstructionsTranslator,
)


class RockwellInstructionsTranslator(IHasInstructionsTranslator):
    """Translates Rockwell-specific instruction structures"""
    INST_OPER_RE_PATTERN: str = r'(?:[A-Za-z0-9_]+\()(.*?)(?:\))'

    def get_instruction_operands(self, instruction: str) -> list[str]:
        return re.findall(
            self.INST_OPER_RE_PATTERN,
            instruction
        )[0].split(',')


class SiemensInstructionsTranslator(IHasInstructionsTranslator):
    """Translates Siemens-specific instruction structures"""

    def get_instruction_operands(self, instruction: str) -> list[str]:
        raise NotImplementedError("Siemens instruction operand translation not implemented yet.")


__all__ = [
    "RockwellInstructionsTranslator",
    "SiemensInstructionsTranslator",
]
