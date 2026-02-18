import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from pylogix.lgx_response import Response

from pyrox.models.gui.tk.frame import TkinterTaskFrame
from pyrox.models.network import Ipv4Address
from pyrox.services import log, SceneRunnerService

from controlrox.models.gui.plc_bridge import PlcSceneBridgeDialog
from controlrox.services.plc.connection import PlcConnectionManager, ConnectionParameters
from controlrox.services.plc.bridge import PlcSceneBridge


class PlcIoFrame(TkinterTaskFrame):
    """Connection view for PLC i/o.
    """

    def __init__(
        self,
        parent,
    ) -> None:
        super().__init__(
            name='plc i/o',
            parent=parent,
        )

        # Initialize with current connection parameters
        current_params = PlcConnectionManager.connection_parameters

        # Initialize PLC bridge
        self._plc_bridge = None

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

        self.gettags_pb = tk.Button(
            self.plccmdframe,
            text='Read Tags',
            command=self._on_read_tags_clicked
        )
        self.gettags_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        self.watchtable_pb = tk.Button(
            self.plccmdframe,
            text='Watch Table',
            command=self._on_watch_table_clicked
        )
        self.watchtable_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        self.bridge_pb = tk.Button(
            self.plccmdframe,
            text='PLC-Scene Bridge',
            command=self._on_bridge_clicked
        )
        self.bridge_pb.pack(side=tk.LEFT, fill=tk.X, padx=2)

        self.tags_frame = tk.Frame(self.content_frame)
        self.tags_frame.pack(side=tk.TOP, fill='both', expand=True)

        # Watch table dialog reference
        self._watch_table_dialog = None
        self._bridge_dialog = None

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

    def _on_read_tags_clicked(self) -> None:
        """Handle Read Tags button click to display all PLC tags."""
        if not PlcConnectionManager._connected:
            messagebox.showwarning("Not Connected", "Please connect to PLC first.")
            return

        try:
            log(self).info("Reading PLC tag table...")
            response = PlcConnectionManager.read_plc_tag_table(all_tags=True)

            if response.Status == 'Success' and response.Value:
                # Create a dialog to show tags
                dialog = tk.Toplevel(self.root)
                dialog.title("PLC Tag Table")
                dialog.geometry("800x600")

                # Add instructions
                instruction_frame = tk.Frame(dialog)
                instruction_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
                tk.Label(
                    instruction_frame,
                    text="Double-click a tag to add it to the Watch Table"
                ).pack(side=tk.LEFT)

                # Create treeview with scrollbar
                tree_frame = tk.Frame(dialog)
                tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

                scrollbar = ttk.Scrollbar(tree_frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                tree = ttk.Treeview(
                    tree_frame,
                    columns=('TagName', 'DataType', 'InstanceID'),
                    show='headings',
                    yscrollcommand=scrollbar.set
                )
                scrollbar.config(command=tree.yview)

                tree.heading('TagName', text='Tag Name')
                tree.heading('DataType', text='Data Type')
                tree.heading('InstanceID', text='Instance ID')

                tree.column('TagName', width=400)
                tree.column('DataType', width=200)
                tree.column('InstanceID', width=150)

                # Populate tree with tags
                for tag in response.Value:
                    tree.insert('', tk.END, values=(
                        tag.TagName,
                        tag.DataType,
                        tag.InstanceID
                    ))

                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # Add double-click handler to add tag to watch table
                def on_tag_double_click(event):
                    selection = tree.selection()
                    if selection:
                        item = tree.item(selection[0])
                        tag_name = item['values'][0]
                        PlcConnectionManager.add_watch_tag(tag_name)
                        log(self).info(f"Added '{tag_name}' to watch table")
                        messagebox.showinfo("Tag Added", f"'{tag_name}' added to watch table")

                tree.bind('<Double-Button-1>', on_tag_double_click)

                # Add close button
                tk.Button(
                    dialog,
                    text='Close',
                    command=dialog.destroy
                ).pack(side=tk.BOTTOM, pady=5)

                log(self).info(f"Read {len(response.Value)} tags from PLC")
            else:
                messagebox.showerror("Error", f"Failed to read tag table: {response.Status}")
                log(self).error(f"Failed to read tag table: {response.Status}")

        except Exception as e:
            messagebox.showerror("Error", f"Error reading tags: {e}")
            log(self).error(f"Error reading PLC tags: {e}")

    def _on_watch_table_clicked(self) -> None:
        """Handle Watch Table button click to open watch table dialog."""
        if not PlcConnectionManager._connected:
            messagebox.showwarning("Not Connected", "Please connect to PLC first.")
            return

        if self._watch_table_dialog is None or not self._watch_table_dialog.winfo_exists():
            self._watch_table_dialog = WatchTableDialog(self.root, PlcConnectionManager)
        else:
            self._watch_table_dialog.lift()
            self._watch_table_dialog.focus()

    def _on_bridge_clicked(self) -> None:
        """Handle PLC-Scene Bridge button click to open bridge manager."""
        # Note: You'll need to pass the actual scene and bridge instances
        # This is a placeholder that creates a new bridge if none exists
        if not PlcConnectionManager._connected:
            messagebox.showwarning("Not Connected", "Please connect to PLC first.")
            return

        # Import here to avoid circular dependency issues

        # Get scene
        scene = SceneRunnerService.get_scene()

        # Create or get bridge instance
        # In a real application, you'd store this in the application context
        if not self._plc_bridge:
            self._plc_bridge = PlcSceneBridge(scene=scene)
        else:
            self._plc_bridge.set_scene(scene)

        if self._bridge_dialog is None or not self._bridge_dialog.root.winfo_exists():
            self._bridge_dialog = PlcSceneBridgeDialog(self.root, self._plc_bridge, scene)
            self._bridge_dialog.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
        # Close watch table dialog if open
        if self._watch_table_dialog and self._watch_table_dialog.winfo_exists():
            self._watch_table_dialog.destroy()

        # Unsubscribe from connection ticks
        PlcConnectionManager.unsubscribe_from_ticks(self._update_connection_status)

        if self._plc_bridge:
            self._plc_bridge.stop()  # Stop the bridge if it's running

        super().destroy()


class WatchTableDialog(tk.Toplevel):
    """Dialog for managing and viewing watched PLC tags."""

    def __init__(self, parent, connection_manager):
        super().__init__(parent)
        self.connection_manager = connection_manager
        self.title("PLC Watch Table")
        self.geometry("900x600")

        # Make dialog stay on top
        self.attributes('-topmost', False)

        # Toolbar frame
        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Button(
            toolbar,
            text='Add Tag',
            command=self._add_tag_dialog
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text='Remove Selected',
            command=self._remove_selected_tag
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text='Clear All',
            command=self._clear_all_tags
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar,
            text='Refresh',
            command=self._refresh_table
        ).pack(side=tk.LEFT, padx=2)

        # Auto-refresh control
        self.auto_refresh_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            toolbar,
            text='Auto-refresh',
            variable=self.auto_refresh_var
        ).pack(side=tk.LEFT, padx=10)

        # Tree frame with scrollbars
        tree_frame = tk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('TagName', 'Value', 'DataType', 'LastUpdate', 'Errors'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading('TagName', text='Tag Name')
        self.tree.heading('Value', text='Value')
        self.tree.heading('DataType', text='Data Type')
        self.tree.heading('LastUpdate', text='Last Update')
        self.tree.heading('Errors', text='Error Count')

        self.tree.column('TagName', width=300)
        self.tree.column('Value', width=200)
        self.tree.column('DataType', width=100)
        self.tree.column('LastUpdate', width=150)
        self.tree.column('Errors', width=100)

        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bind double-click to edit value
        self.tree.bind('<Double-Button-1>', self._on_value_double_click)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initial population
        self._refresh_table()

        # Start auto-refresh timer
        self._schedule_refresh()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _add_tag_dialog(self):
        """Show dialog to add a new tag to watch table."""
        tag_name = simpledialog.askstring(
            "Add Tag",
            "Enter tag name to watch:",
            parent=self
        )

        if tag_name:
            try:
                self.connection_manager.add_watch_tag(tag_name.strip())
                self._refresh_table()
                self.status_var.set(f"Added tag: {tag_name}")
                log(self).info(f"Added tag '{tag_name}' to watch table")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add tag: {e}")
                log(self).error(f"Failed to add tag: {e}")

    def _remove_selected_tag(self):
        """Remove selected tag from watch table."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a tag to remove.")
            return

        item = self.tree.item(selection[0])
        tag_name = item['values'][0]

        if messagebox.askyesno("Confirm Remove", f"Remove '{tag_name}' from watch table?"):
            self.connection_manager.remove_watch_tag(tag_name)
            self._refresh_table()
            self.status_var.set(f"Removed tag: {tag_name}")
            log(self).info(f"Removed tag '{tag_name}' from watch table")

    def _clear_all_tags(self):
        """Clear all tags from watch table."""
        if messagebox.askyesno("Confirm Clear", "Remove all tags from watch table?"):
            self.connection_manager.clear_watch_table()
            self._refresh_table()
            self.status_var.set("Cleared all tags")
            log(self).info("Cleared watch table")

    def _refresh_table(self):
        """Refresh the watch table display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get current watch table
        watch_table = self.connection_manager.get_watch_table()

        # Populate tree
        for tag_name, entry in watch_table.items():
            last_update = entry.last_update.strftime('%H:%M:%S.%f')[:-3] if entry.last_update else 'Never'

            self.tree.insert('', tk.END, values=(
                tag_name,
                str(entry.last_value) if entry.last_value is not None else 'N/A',
                entry.data_type,
                last_update,
                entry.error_count
            ))

        # Format timestamp for status
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M:%S')
        self.status_var.set(f"Watching {len(watch_table)} tags - Last refresh: {current_time}")

    def _on_value_double_click(self, event):
        """Handle double-click on value to edit it."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column != '#2':  # Only allow editing the Value column
            return

        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        tag_name = item['values'][0]
        current_value = item['values'][1]

        # Show dialog to edit value
        new_value = simpledialog.askstring(
            "Edit Value",
            f"Enter new value for '{tag_name}':",
            initialvalue=str(current_value),
            parent=self
        )

        if new_value is not None:
            try:
                # Try to convert to appropriate type
                try:
                    # Try integer first
                    typed_value = int(new_value)
                except ValueError:
                    try:
                        # Try float
                        typed_value = float(new_value)
                    except ValueError:
                        # Keep as string
                        typed_value = new_value

                # Write the value
                def write_callback(response: Response | list[Response]):
                    if isinstance(response, list):
                        response = response[0]

                    if response.Status == 'Success':
                        self.status_var.set(f"Successfully wrote {typed_value} to {tag_name}")
                        self._refresh_table()
                    else:
                        messagebox.showerror("Write Failed", f"Failed to write to {tag_name}: {response.Status}")

                self.connection_manager.write_watch_tag(
                    tag_name,
                    typed_value,
                    callback=write_callback
                )

                log(self).info(f"Writing value {typed_value} to tag '{tag_name}'")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to write value: {e}")
                log(self).error(f"Failed to write value to {tag_name}: {e}")

    def _schedule_refresh(self):
        """Schedule periodic refresh of the table."""
        if self.auto_refresh_var.get():
            self._refresh_table()

        # Schedule next refresh (every 500ms)
        self.after(500, self._schedule_refresh)

    def _on_close(self):
        """Handle window close event."""
        self.destroy()
