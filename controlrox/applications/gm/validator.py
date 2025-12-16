"""GM Controller Validator Class
"""

from controlrox.applications.validator import BaseControllerValidator
from .gm import GmController


class GmControllerValidator(BaseControllerValidator):
    """Validator for GM controllers."""

    supporting_class = GmController
    std_module_rpi = 20.0  # 20ms RPI for standard modules
    drive_module_rpi = 30.0  # 30ms RPI for drives
    sfty_module_input_rpi = 20.0  # 20ms RPI for safety input modules
    sfty_module_output_rpi = 50.0  # 50ms RPI for safety output modules
