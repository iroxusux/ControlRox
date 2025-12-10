from controlrox.models import eplan
from controlrox.models import rockwell as plc


class BaseEplanProject(eplan.project.EplanProject):
    """Base class for Eplan project generation logic."""
    supporting_class = plc.Controller
