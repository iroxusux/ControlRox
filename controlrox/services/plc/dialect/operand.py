"""Operand dialect translators for different PLC manufacturers."""
import re
from controlrox.interfaces import (
    IHasOperandsTranslator,
)


class RockwellOperandsTranslator(IHasOperandsTranslator):
    """Translates Rockwell-specific operand structures"""
    INST_OPER_RE_PATTERN: str = r'(?:[A-Za-z0-9_]+\()(.*?)(?:\))'

    def get_instruction_operands(
        self,
        instruction_string: str
    ) -> list[str]:
        return re.findall(
            self.INST_OPER_RE_PATTERN,
            instruction_string
        )[0].split(',')


class SiemensOperandsTranslator(IHasOperandsTranslator):
    """Translates Siemens-specific operand structures"""

    def get_instruction_operands(
        self,
        instruction_string: str
    ) -> list[str]:
        raise NotImplementedError("Siemens instruction operand translation not implemented yet.")


__all__ = [
    "RockwellOperandsTranslator",
    "SiemensOperandsTranslator",
]
