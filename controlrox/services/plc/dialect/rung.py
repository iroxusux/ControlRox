"""Rung dialect translators for different PLC manufacturers."""
from controlrox.interfaces import (
    IHasRungsTranslator,
)


class RockwellRungsTranslator(IHasRungsTranslator):
    """Translates Rockwell-specific rung structures"""

    def get_raw_rungs(self, routine_data: dict) -> list[dict]:
        """Extract rungs from Rockwell's RLLContent structure"""
        if not routine_data.get('RLLContent'):
            routine_data['RLLContent'] = {'Rung': []}

        rungs = routine_data['RLLContent']['Rung']
        if not isinstance(rungs, list):
            rungs = [rungs]
        return rungs


class SiemensRungsTranslator(IHasRungsTranslator):
    """Translates Siemens-specific rung structures"""

    def get_raw_rungs(self, routine_data: dict) -> list[dict]:
        """Extract rungs from Siemens Network structure"""
        # Siemens uses 'Networks' instead of 'RLLContent'
        if not routine_data.get('Networks'):
            routine_data['Networks'] = {'Network': []}

        networks = routine_data['Networks']['Network']
        if not isinstance(networks, list):
            networks = [networks]
        return networks


__all__ = [
    "RockwellRungsTranslator",
    "SiemensRungsTranslator",
]
