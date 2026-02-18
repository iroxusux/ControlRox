"""PLC Inspection Application
"""
from pyrox.services import EnvManager
from controlrox.models import ControllerApplicationTask
from controlrox.models.gui.plcio import PlcIoFrame
from controlrox.services import PlcConnectionManager


class PlcIoTask(ControllerApplicationTask):
    """Controller verification task for the PLC verification Application.
    """

    def __init__(self, application) -> None:
        super().__init__(application)
        self._frame: PlcIoFrame | None = None
        self.register_menu_command(
            menu=self.tools_menu,
            registry_id='plc.io',
            registry_path='Tools/PLC IO',
            index=0,
            label='PLC I/O',
            command=self.show_plc_io_frame,
            underline=0,
            accelerator='Ctrl+Shift+P',
        )

        # start connection manager if required
        PlcConnectionManager.load_connection_parameters()
        if EnvManager.get('PLC_IO_AUTO_INIT', default=False, cast_type=bool):
            PlcConnectionManager.connect()

    def _create_frame(self) -> PlcIoFrame:
        """Create the PLC I/O frame.
        """
        if self._frame is None or not self._frame.root.winfo_exists():
            self._frame = PlcIoFrame(self.application.workspace.workspace_area)
            self.application.workspace.register_frame(self._frame)
        else:
            self.application.workspace.raise_frame(self._frame)
        return self._frame

    def show_plc_io_frame(self) -> None:
        """Show the PLC I/O frame.
        """
        self._create_frame()

    def uninject(self) -> None:
        """Clean up PLC connections when task is removed."""
        try:
            # Disconnect from PLC to stop timer loops
            if PlcConnectionManager._connected:
                PlcConnectionManager.disconnect()
        except Exception as e:
            # Log but don't raise - we want cleanup to continue
            print(f"Error during PLC disconnection: {e}")

        # Call parent uninject
        super().uninject()
