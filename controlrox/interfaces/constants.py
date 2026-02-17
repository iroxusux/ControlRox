"""Constants interfaces for ControlRox Applications.
This extends the interface from Pyrox.
"""
from enum import Enum
from pyrox.interfaces import EnvironmentKeys


class EnvironmentKeysPLCIO(Enum):
    """Environment keys for PLC I/O settings.
    """
    PLC_IO_AUTO_INIT = "PLC_IO_AUTO_INIT"
    PLC_COMMUNICATION_TIMEOUT = "PLC_COMMUNICATION_TIMEOUT"
    PLC_RETRY_ATTEMPTS = "PLC_RETRY_ATTEMPTS"
    PLC_DEFAULT_IP = "PLC_DEFAULT_IP"
    PLC_DEFAULT_SLOT = "PLC_DEFAULT_SLOT"
    PLC_DEFAULT_PORT = "PLC_DEFAULT_PORT"
    PLC_DEFAULT_RPI = "PLC_DEFAULT_RPI"


class ControlRoxEnvironmentKeys(EnvironmentKeys):
    """Environment keys for ControlRox settings.
    """
    # PLC Connection Settings
    plc = EnvironmentKeysPLCIO
