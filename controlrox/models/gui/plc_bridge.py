"""GUI for PLC-Scene Bridge Management.

Provides a user interface for creating and managing bindings between
PLC tags and scene object properties.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from pyrox.services.logging import log
from pyrox.interfaces import IScene
from pyrox.models.gui.tk.frame import TkinterTaskFrame
from controlrox.services.plc.bridge import PlcSceneBridge, PlcTagBinding, BindingDirection
from controlrox.services.plc.connection import PlcConnectionManager


class PlcSceneBridgeDialog(TkinterTaskFrame):
    """Dialog for managing PLC-Scene bindings.

    Allows users to:
    - View all configured bindings
    - Add new bindings between PLC tags and scene objects
    - Remove or edit existing bindings
    - Enable/disable bindings
    - Start/stop bridge synchronization
    """

    def __init__(self, parent, bridge: PlcSceneBridge, scene: Optional[IScene] = None):
        super().__init__(
            name='plc_bridge_dialog',
            parent=parent,
        )
        self.bridge = bridge
        self.scene = scene

        # Create UI
        self._create_toolbar()
        self._create_bindings_view()
        self._create_status_bar()

        # Initialize
        self._refresh_bindings()
        self._update_status()

        # Auto-refresh
        self._schedule_refresh()

    def _create_toolbar(self):
        """Create toolbar with control buttons."""
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Bridge controls
        control_frame = tk.LabelFrame(toolbar, text="Bridge Control")
        control_frame.pack(side=tk.LEFT, padx=2)

        self.start_button = tk.Button(
            control_frame,
            text="▶ Start",
            command=self._start_bridge,
            bg="lightgreen"
        )
        self.start_button.pack(side=tk.LEFT, padx=2)

        self.stop_button = tk.Button(
            control_frame,
            text="⏹ Stop",
            command=self._stop_bridge,
            bg="lightcoral",
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=2)

        # Binding management
        binding_frame = tk.LabelFrame(toolbar, text="Bindings")
        binding_frame.pack(side=tk.LEFT, padx=2)

        tk.Button(
            binding_frame,
            text="➕ Add Binding",
            command=self._add_binding_dialog
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            binding_frame,
            text="✏ Edit Selected",
            command=self._edit_selected_binding
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            binding_frame,
            text="🗑 Remove Selected",
            command=self._remove_selected_binding
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            binding_frame,
            text="Clear All",
            command=self._clear_all_bindings
        ).pack(side=tk.LEFT, padx=2)

        # Refresh
        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self._refresh_bindings
        ).pack(side=tk.LEFT, padx=5)

    def _create_bindings_view(self):
        """Create treeview for bindings."""
        view_frame = tk.Frame(self.root)
        view_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(view_frame, orient="vertical")
        hsb = ttk.Scrollbar(view_frame, orient="horizontal")

        # Treeview
        self.tree = ttk.Treeview(
            view_frame,
            columns=('Enabled', 'PLCTag', 'Direction', 'Object', 'Property', 'PLCValue', 'SceneValue', 'Description'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Column configuration
        self.tree.heading('Enabled', text='✓')
        self.tree.heading('PLCTag', text='PLC Tag')
        self.tree.heading('Direction', text='Direction')
        self.tree.heading('Object', text='Scene Object')
        self.tree.heading('Property', text='Property')
        self.tree.heading('PLCValue', text='PLC Value')
        self.tree.heading('SceneValue', text='Scene Value')
        self.tree.heading('Description', text='Description')

        self.tree.column('Enabled', width=40)
        self.tree.column('PLCTag', width=150)
        self.tree.column('Direction', width=80)
        self.tree.column('Object', width=120)
        self.tree.column('Property', width=100)
        self.tree.column('PLCValue', width=100)
        self.tree.column('SceneValue', width=100)
        self.tree.column('Description', width=200)

        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        view_frame.grid_rowconfigure(0, weight=1)
        view_frame.grid_columnconfigure(0, weight=1)

        # Context menu
        self.tree.bind('<Button-3>', self._show_context_menu)
        self.tree.bind('<Double-Button-1>', self._toggle_binding_enabled)

    def _create_status_bar(self):
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _refresh_bindings(self):
        """Refresh the bindings display."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate
        bindings = self.bridge.get_bindings()
        for binding in bindings:
            enabled_icon = "✓" if binding.enabled else "✗"
            direction_icon = {
                BindingDirection.READ: "→",
                BindingDirection.WRITE: "←",
                BindingDirection.BOTH: "⇄"
            }.get(binding.direction, "?")

            plc_value = str(binding.last_plc_value) if binding.last_plc_value is not None else "N/A"
            scene_value = str(binding.last_scene_value) if binding.last_scene_value is not None else "N/A"

            self.tree.insert('', tk.END, values=(
                enabled_icon,
                binding.tag_name,
                direction_icon,
                binding.object_id,
                binding.property_path,
                plc_value,
                scene_value,
                binding.description
            ))

        self._update_status()

    def _update_status(self):
        """Update status bar."""
        bindings = self.bridge.get_bindings()
        enabled_count = sum(1 for b in bindings if b.enabled)
        active_status = "ACTIVE" if self.bridge._active else "STOPPED"

        self.status_var.set(
            f"{active_status} | {enabled_count}/{len(bindings)} bindings enabled"
        )

        # Update button states
        if self.bridge._active:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def _start_bridge(self):
        """Start the bridge."""
        try:
            self.bridge.start()
            self._update_status()
            messagebox.showinfo("Bridge Started", "PLC-Scene bridge is now active")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bridge: {e}")
            log(self).error(f"Failed to start bridge: {e}")

    def _stop_bridge(self):
        """Stop the bridge."""
        self.bridge.stop()
        self._update_status()
        messagebox.showinfo("Bridge Stopped", "PLC-Scene bridge has been stopped")

    def _add_binding_dialog(self):
        """Show dialog to add a new binding."""
        dialog = AddBindingDialog(self.root, self.bridge, self.scene)
        self.root.wait_window(dialog)
        self._refresh_bindings()

    def _edit_selected_binding(self):
        """Edit the selected binding."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a binding to edit")
            return

        # Get binding details from tree
        item = self.tree.item(selection[0])
        tag_name = item['values'][1]
        object_id = item['values'][3]
        property_path = item['values'][4]

        # Find binding
        bindings = [b for b in self.bridge.get_bindings()
                    if b.tag_name == tag_name and b.object_id == object_id
                    and b.property_path == property_path]

        if bindings:
            dialog = EditBindingDialog(self.root, self.bridge, bindings[0])
            self.root.wait_window(dialog)
            self._refresh_bindings()

    def _remove_selected_binding(self):
        """Remove the selected binding."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a binding to remove")
            return

        item = self.tree.item(selection[0])
        tag_name = item['values'][1]
        object_id = item['values'][3]
        property_path = item['values'][4]

        if messagebox.askyesno("Confirm Remove", f"Remove binding {tag_name} → {object_id}.{property_path}?"):
            self.bridge.remove_binding(tag_name, object_id, property_path)
            self._refresh_bindings()

    def _clear_all_bindings(self):
        """Clear all bindings."""
        if messagebox.askyesno("Confirm Clear", "Remove all bindings?"):
            self.bridge.clear_bindings()
            self._refresh_bindings()

    def _toggle_binding_enabled(self, event):
        """Toggle enabled state of double-clicked binding."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        tag_name = item['values'][1]
        object_id = item['values'][3]
        property_path = item['values'][4]

        # Find and toggle binding
        for binding in self.bridge.get_bindings():
            if (binding.tag_name == tag_name and binding.object_id == object_id
                    and binding.property_path == property_path):
                binding.enabled = not binding.enabled
                log(self).info(f"Toggled binding {tag_name}: {'enabled' if binding.enabled else 'disabled'}")
                break

        self._refresh_bindings()

    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)

            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit", command=self._edit_selected_binding)
            menu.add_command(label="Remove", command=self._remove_selected_binding)
            menu.add_separator()
            menu.add_command(label="Toggle Enabled", command=lambda: self._toggle_binding_enabled(event))

            menu.post(event.x_root, event.y_root)

    def _schedule_refresh(self):
        """Schedule periodic refresh."""
        if self.bridge._active:
            self._refresh_bindings()
        self.root.after(1000, self._schedule_refresh)


class AddBindingDialog(tk.Toplevel):
    """Dialog for adding a new PLC-Scene binding."""

    def __init__(self, parent, bridge: PlcSceneBridge, scene: Optional[IScene]):
        super().__init__(parent)
        self.bridge = bridge
        self.scene = scene

        self.title("Add PLC-Scene Binding")
        self.geometry("500x400")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create form
        form_frame = tk.Frame(self, padx=10, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        row = 0

        # PLC Tag
        tk.Label(form_frame, text="PLC Tag:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tag_entry = tk.Entry(form_frame, width=40)
        self.tag_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        tk.Button(form_frame, text="Browse...", command=self._browse_tags).grid(row=row, column=2, padx=5)
        row += 1

        # Scene Object
        tk.Label(form_frame, text="Scene Object ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.object_entry = tk.Entry(form_frame, width=40)
        self.object_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        tk.Button(form_frame, text="Browse...", command=self._browse_objects).grid(row=row, column=2, padx=5)
        row += 1

        # Property Path
        tk.Label(form_frame, text="Property Path:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.property_entry = tk.Entry(form_frame, width=40)
        self.property_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        tk.Label(form_frame, text="e.g., speed, position.x").grid(row=row, column=2, padx=5)
        row += 1

        # Direction
        tk.Label(form_frame, text="Direction:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.direction_var = tk.StringVar(value="read")
        direction_frame = tk.Frame(form_frame)
        direction_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        tk.Radiobutton(direction_frame, text="PLC → Scene", variable=self.direction_var, value="read").pack(side=tk.LEFT)
        tk.Radiobutton(direction_frame, text="Scene → PLC", variable=self.direction_var, value="write").pack(side=tk.LEFT)
        tk.Radiobutton(direction_frame, text="Both", variable=self.direction_var, value="both").pack(side=tk.LEFT)
        row += 1

        # Data Type
        tk.Label(form_frame, text="Data Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.datatype_entry = tk.Entry(form_frame, width=40)
        self.datatype_entry.insert(0, "0")
        self.datatype_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        tk.Label(form_frame, text="0 = auto").grid(row=row, column=2, padx=5)
        row += 1

        # Description
        tk.Label(form_frame, text="Description:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.description_entry = tk.Entry(form_frame, width=40)
        self.description_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        row += 1

        form_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Add Binding", command=self._add_binding).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _browse_tags(self):
        """Browse available PLC tags."""
        if not PlcConnectionManager._connected:
            messagebox.showwarning("Not Connected", "Please connect to PLC first")
            return

        # Get tag list
        response = PlcConnectionManager.read_plc_tag_table()
        if response.Status != 'Success' or not response.Value:
            messagebox.showerror("Error", "Failed to read PLC tags")
            return

        # Show selection dialog
        dialog = TagSelectionDialog(self, response.Value)
        self.wait_window(dialog)

        if hasattr(dialog, 'selected_tag'):
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.insert(0, dialog.selected_tag)

    def _browse_objects(self):
        """Browse scene objects."""
        if not self.scene:
            messagebox.showwarning("No Scene", "No scene is loaded")
            return

        objects = self.scene.get_scene_objects()
        if not objects:
            messagebox.showinfo("No Objects", "Scene has no objects")
            return

        # Show selection dialog
        dialog = ObjectSelectionDialog(self, objects)
        self.wait_window(dialog)

        if hasattr(dialog, 'selected_object_id'):
            self.object_entry.delete(0, tk.END)
            self.object_entry.insert(0, dialog.selected_object_id)

    def _add_binding(self):
        """Add the binding."""
        tag_name = self.tag_entry.get().strip()
        object_id = self.object_entry.get().strip()
        property_path = self.property_entry.get().strip()

        if not tag_name or not object_id or not property_path:
            messagebox.showerror("Missing Fields", "Please fill in all required fields")
            return

        try:
            data_type = int(self.datatype_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Data Type", "Data type must be an integer")
            return

        direction = BindingDirection(self.direction_var.get())
        description = self.description_entry.get().strip()

        try:
            self.bridge.add_binding(
                tag_name=tag_name,
                object_id=object_id,
                property_path=property_path,
                direction=direction,
                data_type=data_type,
                description=description
            )
            messagebox.showinfo("Success", "Binding added successfully")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add binding: {e}")


class EditBindingDialog(tk.Toplevel):
    """Dialog for editing an existing binding."""

    def __init__(self, parent, bridge: PlcSceneBridge, binding: PlcTagBinding):
        super().__init__(parent)
        self.bridge = bridge
        self.binding = binding

        self.title("Edit Binding")
        self.geometry("400x300")

        # Form (simplified - just description and enabled for now)
        form_frame = tk.Frame(self, padx=10, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(form_frame, text=f"Tag: {binding.tag_name}").pack(anchor=tk.W, pady=5)
        tk.Label(form_frame, text=f"Object: {binding.object_id}").pack(anchor=tk.W, pady=5)
        tk.Label(form_frame, text=f"Property: {binding.property_path}").pack(anchor=tk.W, pady=5)

        tk.Label(form_frame, text="Description:").pack(anchor=tk.W, pady=(10, 0))
        self.description_entry = tk.Entry(form_frame, width=50)
        self.description_entry.insert(0, binding.description)
        self.description_entry.pack(fill=tk.X, pady=5)

        self.enabled_var = tk.BooleanVar(value=binding.enabled)
        tk.Checkbutton(form_frame, text="Enabled", variable=self.enabled_var).pack(anchor=tk.W, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _save(self):
        """Save changes."""
        self.binding.description = self.description_entry.get()
        self.binding.enabled = self.enabled_var.get()
        messagebox.showinfo("Success", "Binding updated")
        self.destroy()


class TagSelectionDialog(tk.Toplevel):
    """Dialog for selecting a PLC tag."""

    def __init__(self, parent, tags):
        super().__init__(parent)
        self.title("Select PLC Tag")
        self.geometry("600x400")
        self.transient(parent)

        # Listbox with scrollbar
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Populate
        for tag in tags:
            self.listbox.insert(tk.END, tag.TagName)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Select", command=self._select).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

        self.listbox.bind('<Double-Button-1>', lambda e: self._select())

    def _select(self):
        """Select the tag."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_tag = self.listbox.get(selection[0])
            self.destroy()


class ObjectSelectionDialog(tk.Toplevel):
    """Dialog for selecting a scene object."""

    def __init__(self, parent, objects):
        super().__init__(parent)
        self.title("Select Scene Object")
        self.geometry("400x300")
        self.transient(parent)

        # Listbox with scrollbar
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Populate
        for obj in objects:
            obj_id = obj.get_id() if hasattr(obj, 'get_id') else str(obj)
            self.listbox.insert(tk.END, obj_id)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Select", command=self._select).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

        self.listbox.bind('<Double-Button-1>', lambda e: self._select())

    def _select(self):
        """Select the object."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_object_id = self.listbox.get(selection[0])
            self.destroy()
