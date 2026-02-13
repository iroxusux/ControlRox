"""PLC Inspection Application
"""
from controlrox.models import ControllerApplicationTask
from controlrox.models.gui.plcio import PlcIoFrame


class PlcIoTask(ControllerApplicationTask):
    """Controller verification task for the PLC verification Application.
    """

    def show_plc_io_frame(self) -> None:
        """Show the PLC I/O frame.
        """
        frame = PlcIoFrame(self.application.workspace.root)
        self.application.workspace.register_frame(frame)

    def inject(self) -> None:
        self.tools_menu.add_item(
            label='PLC I/O',
            command=self.show_plc_io_frame,
            accelerator='Ctrl+Shift+P',
            underline=0,
        )
