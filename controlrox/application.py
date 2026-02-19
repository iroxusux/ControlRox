from __future__ import annotations
from typing import Any, Optional, Union
import tkinter as tk
from tkinter import ttk

from pyrox.models import HashList, PyroxObject
from pyrox.models.gui import commandbar
from pyrox.models.gui import contextmenu
from pyrox.models.gui import treeview
from pyrox.services.logging import log
from pyrox.services import object as object_services
from controlrox.applications.constants import TreeViewMode
from controlrox.applications.ladder import LadderEditorApplicationTask
from controlrox.interfaces.plc.controller import IController
from controlrox.models import (
    ControllerApplication,
    Routine,
)
from controlrox.services import plc_gui_introspection


__all__ = [
    'ControlRoxApplication',
]


class ControlRoxApplication(ControllerApplication):
    def __init__(self) -> None:
        super().__init__()
        self._object_lookup_cache: dict[str, object] = {}

        # Create the sidebar frame first, then delegate the rest of workspace setup
        self.controller_treeview_frame = ttk.Frame(
            master=self.workspace.sidebar_organizer,
        )
        self._build_workspace_elements()

        # Load last opened controller
        self.load_last_opened_controller()

    def _build_workspace_elements(self) -> None:
        """Build and register all workspace sidebar elements."""
        self.workspace.add_sidebar_widget(
            self.controller_treeview_frame,
            "",
            "controller",
            "📁",
            closeable=False
        )

        self.treeview_commandbar = commandbar.PyroxCommandBar(
            master=self.controller_treeview_frame
        )
        self.controller_treeview = treeview.PyroxTreeView(
            parent=self.controller_treeview_frame  # TODO: parent should be named master to be consistent
        )

        # Layout
        self.treeview_commandbar.frame.pack(fill='x', side='bottom')
        self.controller_treeview.pack(fill='both', expand=True, side='top')

        # Initialize
        self.controller_treeview.subscribe_to_selection(self._handle_treeview_selection)
        self._build_treeview_command_bar()

        # Set initial status
        self.workspace.set_status("Ready")

    def _build_treeview_command_bar(self) -> None:
        """Build the command bar for the controller treeview."""
        log(self).debug('Building treeview command bar...')
        self.treeview_commandbar.add_button(commandbar.CommandButton(
            id='view_properties',
            text='Properties',
            command=self._display_controller_properties_in_treeview,
            tooltip='View controller properties',
            selectable=True
        ))

        self.treeview_commandbar.add_button(commandbar.CommandButton(
            id='view_tags',
            text='Tags',
            command=lambda: self._display_common_list_in_treeview(
                item_attr_name='tags',
                tab_to_select=TreeViewMode.TAGS
            ),
            tooltip='View controller tags',
            selectable=True
        ))

        self.treeview_commandbar.add_button(commandbar.CommandButton(
            id='view_programs',
            text='Programs',
            command=lambda: self._display_common_list_in_treeview(
                item_attr_name='programs',
                tab_to_select=TreeViewMode.PROGRAMS
            ),
            tooltip='View controller programs',
            selectable=True
        ))

        self.treeview_commandbar.add_button(commandbar.CommandButton(
            id='view_aois',
            text='AOIs',
            command=lambda: self._display_common_list_in_treeview(
                item_attr_name='aois',
                tab_to_select=TreeViewMode.AOIS
            ),
            tooltip='View controller AddOnInstructions',
            selectable=True
        ))

        self.treeview_commandbar.add_button(commandbar.CommandButton(
            id='view_datatypes',
            text='Data Types',
            command=lambda: self._display_common_list_in_treeview(
                item_attr_name='datatypes',
                tab_to_select=TreeViewMode.DATATYPES
            ),
            tooltip='View controller Data Types',
            selectable=True
        ))

    def _config_menu_file_entries(self) -> None:
        """Configure the file menu entries based on the controller state."""
        log(self).debug('Configuring file menu entries based on controller state.')
        self.gui.gui_menu().file_menu.config_item(
            index='Save Controller',
            state='disabled' if not self.controller else 'normal'
        )
        self.gui.gui_menu().file_menu.config_item(
            index='Save Controller As...',
            state='disabled' if not self.controller else 'normal'
        )
        self.gui.gui_menu().file_menu.config_item(
            index='Close Controller',
            state='disabled' if not self.controller else 'normal'
        )

    def _display_common_list_in_treeview(
        self,
        items: Optional[Union[list[Any], HashList[Any]]] = None,
        item_attr_name: Optional[str] = None,
        tab_to_select: Optional[TreeViewMode] = None
    ) -> None:
        """Display a common list of PLC objects in the treeview."""
        if not self.controller:
            self.controller_treeview.clear()
            return

        if not items:
            items = getattr(self.controller, item_attr_name, None) if item_attr_name else None

        if not items:
            self.controller_treeview.clear()
            return

        data = {}
        for obj in items:
            data[getattr(obj, 'name', str(obj))] = plc_gui_introspection.create_attribute_value_dict(obj)
        self.controller_treeview.display_object(
            data,
            force_open=True
        )

        if tab_to_select:
            self.treeview_commandbar.set_selected(tab_to_select, True)
        else:
            self.treeview_commandbar.set_selected(TreeViewMode.PROPERTIES, True)

    def _display_controller_properties_in_treeview(self) -> None:
        """Display the controller properties in the treeview."""
        if not self.controller:
            self.controller_treeview.clear()
            return
        self.controller_treeview.display_object(
            plc_gui_introspection.create_attribute_value_dict(self.controller),
            force_open=True
        )
        self.treeview_commandbar.set_selected(TreeViewMode.PROPERTIES, True)

    def _get_plc_object_from_selected_tree_item(
        self,
        tree_item_id: str
    ) -> Optional[object]:
        """Get the PLC object associated with the selected tree item.
        """
        if tree_item_id in self._object_lookup_cache:
            return self._object_lookup_cache[tree_item_id]

        def get_list_to_insepct(commandbar_selection: list[str]) -> Optional[list[Any]]:
            if not self.controller:
                return None
            if TreeViewMode.TAGS.value in commandbar_selection:
                return self.controller.tags.as_list_values()
            if TreeViewMode.PROGRAMS.value in commandbar_selection:
                return self.controller.programs.as_list_values()
            if TreeViewMode.AOIS.value in commandbar_selection:
                return self.controller.aois.as_list_values()
            if TreeViewMode.DATATYPES.value in commandbar_selection:
                return self.controller.datatypes.as_list_values()
            return None

        if not tree_item_id:
            return None

        object_path = self.controller_treeview.get_object_path(tree_item_id)
        if object_path[0] == 'Root':  # We don't want to search for Root
            if len(object_path) == 1:
                return None  # No object to return
            object_path = object_path[1:]

        list_to_inspect = get_list_to_insepct(self.treeview_commandbar.get_selected_buttons())
        if not list_to_inspect:
            log(self).debug('No list to inspect found based on current treeview commandbar selection.')
            return None

        target, parent, attr_name = object_services.resolve_object_path_with_parent(object_path, list_to_inspect)

        if not parent or not attr_name:
            return None

        if not target:
            if object_services.is_iterable(parent):
                if attr_name in parent:
                    return parent[attr_name]

                else:
                    for item in parent:
                        if str(item) == attr_name:
                            return item

        self._object_lookup_cache[tree_item_id] = target

        return target

    def _handle_treeview_selection(
        self,
        tree_item_id: str,
        selected_object: Optional[object],
        is_right_click: bool = False,
        context_menu: Optional[contextmenu.PyroxContextMenu] = None,
        event: Optional[tk.Event] = None
    ) -> None:
        """Handle selection in the treeview."""
        if not tree_item_id:
            return

        if not selected_object:
            selected_object = self._get_plc_object_from_selected_tree_item(tree_item_id)

        log(self).debug(f'Selected object: (id{tree_item_id}) {getattr(selected_object, "name", str(selected_object))}')
        # Further handling can be implemented here
        if is_right_click and context_menu and event:
            self._populate_context_menu_from_selection(selected_object, context_menu)
            context_menu.show_at_event(event)

    def _launch_ladder_editor_for_routine(
        self,
        routine: Routine
    ) -> None:
        """Launch the ladder editor for a given routine."""
        if not routine or not isinstance(routine, Routine):
            log(self).error('Invalid routine provided for ladder editor launch.')
            return

        LadderEditorApplicationTask(self).run(
            routine=routine,
            controller=self.controller
        )

    def _populate_context_menu_from_routine(
        self,
        routine: Routine,
        context_menu: contextmenu.PyroxContextMenu
    ) -> None:
        """Populate a context menu based on the selected routine in the treeview.
        """
        if not routine or not isinstance(routine, Routine):
            return

        context_menu.add_item(contextmenu.MenuItem(
            id='edit_routine',
            label='Edit Routine',
            command=lambda: self._launch_ladder_editor_for_routine(routine)
        ))

    def _populate_context_menu_from_selection(
        self,
        selected_object: Optional[object],
        context_menu: contextmenu.PyroxContextMenu
    ) -> None:
        """Populate a context menu based on the selected object in the treeview.
        """
        if not selected_object or not isinstance(selected_object, PyroxObject):
            return
        log(self).debug(f'Populating context menu for selected PyroxObject: {getattr(selected_object, "name", str(selected_object))}')

        if isinstance(selected_object, Routine):
            return self._populate_context_menu_from_routine(selected_object, context_menu)

    def invalidate(self) -> None:
        super().invalidate()
        self._object_lookup_cache.clear()

    def on_close(self) -> None:
        """Clean up ControlRox-specific resources before closing."""
        log(self).debug('ControlRox application closing - cleaning up PLC connections...')

        # Import here to avoid circular import
        from controlrox.services.plc.connection import PlcConnectionManager

        try:
            # Disconnect from PLC if connected (this stops timer loops)
            if PlcConnectionManager._connected:
                log(self).info('Disconnecting from PLC before application close...')
                PlcConnectionManager.disconnect()
                log(self).debug('PLC disconnected successfully.')
        except Exception as e:
            log(self).error(f'Error disconnecting PLC during close: {e}')

        # Clear object lookup cache
        try:
            self._object_lookup_cache.clear()
        except Exception as e:
            log(self).error(f'Error clearing object cache: {e}')

        # Call parent on_close
        super().on_close()

    def refresh(
        self,
        restore_app_state: bool = True
    ) -> None:
        super().refresh(False)
        self._display_controller_properties_in_treeview()
        self._config_menu_file_entries()

        if restore_app_state:
            self.set_app_state_normal()

    def set_controller(self, controller: IController | None) -> None:
        super().set_controller(controller)
        self._display_controller_properties_in_treeview()
        self._config_menu_file_entries()
        self.refresh()
