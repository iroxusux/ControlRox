"""Matcher for Ford controllers."""
from controlrox.services import ControllerMatcher
from .gm import GmController


class GmControllerMatcher(ControllerMatcher):
    """Matcher for GM controllers."""

    @classmethod
    def get_controller_constructor(cls):
        return GmController

    @staticmethod
    def get_datatype_patterns() -> list[str]:
        return [
            'zz_Version',
            'zz_Prompt',
            'zz_PFEAlarm',
            'za_Toggle'
        ]

    @staticmethod
    def get_module_patterns() -> list[str]:
        return [
            'sz_*',
            'zz_*',
            'cg_*',
            'zs_*'
        ]

    @staticmethod
    def get_program_patterns() -> list[str]:
        return [
            'MCP',
            'PFE',
            'GROUP1',
            'GROUP2',
            'HMI1',
            'HMI2',
        ]

    @staticmethod
    def get_safety_program_patterns() -> list[str]:
        return [
            's_Common',
            's_Segment1',
            's_Segment2',
        ]

    @staticmethod
    def get_tag_patterns() -> list[str]:
        return [
            'z_FifoDataElement',
            'z_JunkData',
            'z_NoData'
        ]
