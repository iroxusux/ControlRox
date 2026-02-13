import tkinter as tk
from pyrox.models.gui.tk.frame import TkinterTaskFrame
from controlrox.services.plc.connection import PlcConnectionManager, ConnectionParameters
from pyrox.models.network import Ipv4Address
from pyrox.services.logging import log


class PlcIoFrame(TkinterTaskFrame):
    """Connection view for PLC i/o.
    """

    def __init__(
        self,
        parent,
    ) -> None:
        super().__init__(
            name='PLC I/O',
            parent=parent,
        )

        # Initialize with current connection parameters
        current_params = PlcConnectionManager.connection_parameters

        self.plccfgframe = tk.LabelFrame(self.content_frame, text='PLC Connection Configuration')
        self.plccfgframe.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Status LED
        self.status_canvas = tk.Canvas(self.plccfgframe, width=20, height=20, highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=8)
        self.status_led = self.status_canvas.create_oval(4, 4, 16, 16, fill="grey", outline="black")

        # IP Address
        tk.Label(self.plccfgframe, text='IP Address:').pack(side=tk.LEFT, padx=(5, 2))
        self.ctrl_ip_addr = tk.StringVar(self.plccfgframe, str(current_params.ip_address), 'PLC IP Address')
        self.ip_addr_entry = tk.Entry(self.plccfgframe, textvariable=self.ctrl_ip_addr, width=15)
        self.ip_addr_entry.pack(side=tk.LEFT, padx=2)

        # Slot
        tk.Label(self.plccfgframe, text='Slot:').pack(side=tk.LEFT, padx=(5, 2))
        self.ctrl_slot = tk.StringVar(self.plccfgframe, str(current_params.slot), 'PLC Slot Number')
        self.slot_entry = tk.Entry(self.plccfgframe, textvariable=self.ctrl_slot, width=5)
        self.slot_entry.pack(side=tk.LEFT, padx=2)

        # RPI (Request Packet Interval)
        tk.Label(self.plccfgframe, text='RPI (ms):').pack(side=tk.LEFT, padx=(5, 2))
        self.ctrl_rpi = tk.StringVar(self.plccfgframe, str(current_params.rpi), 'PLC RPI')
        self.rpi_entry = tk.Entry(self.plccfgframe, textvariable=self.ctrl_rpi, width=6)
        self.rpi_entry.pack(side=tk.LEFT, padx=2)

        # Connect button
        self.connect_pb = tk.Button(
            self.plccfgframe,
            text='Connect',
            command=self._on_connect_clicked
        )
        self.connect_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        # Disconnect button
        self.disconnect_pb = tk.Button(
            self.plccfgframe,
            text='Disconnect',
            command=self._on_disconnect_clicked,
            state=tk.DISABLED
        )
        self.disconnect_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        self.plccmdframe = tk.LabelFrame(self.content_frame, text='PLC Commands')
        self.plccmdframe.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.gettags_pb = tk.Button(self.plccmdframe, text='Read Tags')
        self.gettags_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        self.watchtable_pb = tk.Button(self.plccmdframe, text='Watch Table')
        self.watchtable_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        self.tags_frame = tk.Frame(self.content_frame)
        self.tags_frame.pack(side=tk.TOP, fill='both', expand=True)

        # Subscribe to connection ticks for status updates
        PlcConnectionManager.subscribe_to_ticks(self._update_connection_status)

        # Initial status update
        self._update_connection_status()

    def _on_connect_clicked(self) -> None:
        """Handle connect button click."""
        try:
            # Parse and validate connection parameters from GUI
            ip_address = Ipv4Address(self.ctrl_ip_addr.get())
            slot = int(self.ctrl_slot.get())
            rpi = int(self.ctrl_rpi.get())

            # Update connection parameters
            PlcConnectionManager.connection_parameters = ConnectionParameters(
                ip_address=ip_address,
                slot=slot,
                rpi=rpi
            )

            # Attempt connection
            PlcConnectionManager.connect()

            # Update UI state
            self._update_connection_status()

        except ValueError as e:
            log(self).error(f'Invalid connection parameters: {e}')
            self._show_error_status()
        except Exception as e:
            log(self).error(f'Error connecting to PLC: {e}')
            self._show_error_status()

    def _on_disconnect_clicked(self) -> None:
        """Handle disconnect button click."""
        try:
            PlcConnectionManager.disconnect()
            self._update_connection_status()
        except Exception as e:
            log(self).error(f'Error disconnecting from PLC: {e}')

    def _update_connection_status(self) -> None:
        """Update the connection status LED and button states."""
        if PlcConnectionManager._connected:
            # Connected - show green LED
            self.status_canvas.itemconfig(self.status_led, fill="green")
            self.connect_pb.config(state=tk.DISABLED)
            self.disconnect_pb.config(state=tk.NORMAL)
            # Disable parameter entry while connected
            self.ip_addr_entry.config(state=tk.DISABLED)
            self.slot_entry.config(state=tk.DISABLED)
            self.rpi_entry.config(state=tk.DISABLED)
        else:
            # Disconnected - show grey LED
            self.status_canvas.itemconfig(self.status_led, fill="grey")
            self.connect_pb.config(state=tk.NORMAL)
            self.disconnect_pb.config(state=tk.DISABLED)
            # Enable parameter entry while disconnected
            self.ip_addr_entry.config(state=tk.NORMAL)
            self.slot_entry.config(state=tk.NORMAL)
            self.rpi_entry.config(state=tk.NORMAL)

    def _show_error_status(self) -> None:
        """Show error status on LED."""
        self.status_canvas.itemconfig(self.status_led, fill="red")

    def on_connect_pb_clicked(self, callback) -> None:
        """Set custom callback for connect button (in addition to default behavior)."""
        original_command = self._on_connect_clicked

        def combined_callback():
            original_command()
            callback()
        self.connect_pb.config(command=combined_callback)

    def on_disconnect_pb_clicked(self, callback) -> None:
        """Set custom callback for disconnect button (in addition to default behavior)."""
        original_command = self._on_disconnect_clicked

        def combined_callback():
            original_command()
            callback()
        self.disconnect_pb.config(command=combined_callback)

    def destroy(self) -> None:
        """Clean up resources when frame is destroyed."""
        # Unsubscribe from connection ticks
        PlcConnectionManager.unsubscribe_from_ticks(self._update_connection_status)
        super().destroy()
