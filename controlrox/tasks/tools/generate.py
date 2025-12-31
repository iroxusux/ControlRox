"""PLC Inspection Application
    """
import tkinter as tk
from tkinter import ttk
from pyrox.models.gui import PyroxYamlEditor, TaskFrame
from pyrox.services.file import get_save_file
from pyrox.services.gui import GuiManager
from pyrox.services.logging import log
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.services import (
    convert_markdown_to_html,
    render_checklist,
    ControllerInstanceManager,
    inject_emulation_routine,
    remove_emulation_routine
)


class ControllerGenerateTask(ControllerApplicationTask):
    """Controller generation task for the PLC Application.
    """

    def generate_project_design_checklist(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return

        task_frame = TaskFrame(
            master=self.application.workspace.workspace_area.frame_root,
            name='Project Design Checklist'
        )
        self.application.workspace.add_workspace_task_frame(task_frame, True)

        # Create the YAML editor
        yaml_editor = PyroxYamlEditor(
            task_frame.content_frame,
            width=90,
            height=30,
            auto_validate=True,
            show_line_numbers=True
        )
        yaml_editor.pack(fill='both', expand=True)

        ttk.Separator(yaml_editor._toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        btn_export = ttk.Button(
            yaml_editor._toolbar,
            text="Export to .md/.html",
            command=lambda: self.export_to_markdown_and_html(yaml_editor),
            width=10
        )
        btn_export.pack(side=tk.LEFT, padx=2)

    def export_to_markdown_and_html(
        self,
        yaml_editor: PyroxYamlEditor,
    ):
        if not yaml_editor.save_file():
            log(self).warning("YAML content not saved; aborting design checklist export.")
            return

        yaml_file_path = yaml_editor.current_file
        if not yaml_file_path or not yaml_file_path.suffix == '.yaml':
            log(self).warning("Current file is not a YAML file; aborting design checklist export.")
            return

        output_path = get_save_file(
            filetypes=[
                ("Markdown Files", "*.md"),
                ("All Files", "*.*"),
            ]
        )
        if not output_path:
            log(self).warning("No output path selected for design checklist export.")
            return

        render_checklist(
            input_yaml=yaml_file_path,
            output_markdown=output_path,
        )

        convert_markdown_to_html(
            input_markdown=output_path,
            output_html=output_path.rsplit('.', 1)[0] + '.html',
            title='Project Design Checklist'
        )

    def inject_emulation_routine(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return
        inject_emulation_routine(ctrl)

    def remove_emulation_routine(self):
        ctrl = ControllerInstanceManager.get_controller()
        if not ctrl:
            return
        remove_emulation_routine(ctrl)

    def inject(self) -> None:
        tools_menu = self.application.menu.unsafe_get_tools_menu()
        items = tools_menu.get_items()
        if len(items) > 0:
            tools_menu.add_separator()

        backend = GuiManager.unsafe_get_backend()

        logic_srvc_dropdown = backend.create_gui_menu(
            master=tools_menu.menu,
            name='logic_services',
            tearoff=0
        )

        project_srvc_dropdown = backend.create_gui_menu(
            master=logic_srvc_dropdown.menu,
            name='project_services',
            tearoff=0
        )
        project_srvc_dropdown.add_item(label='Generate Project Design Sheet', command=self.generate_project_design_checklist)

        emulation_dropdown = backend.create_gui_menu(
            master=logic_srvc_dropdown.menu,
            name='emulation_generation',
            tearoff=0
        )
        emulation_dropdown.add_item(label='Inject Emulation Logic', command=self.inject_emulation_routine)
        emulation_dropdown.add_item(label='Remove Emulation Logic', command=self.remove_emulation_routine)

        logic_srvc_dropdown.add_submenu(label='Emulation', submenu=emulation_dropdown)
        tools_menu.add_submenu(label='Project Services', submenu=project_srvc_dropdown)
        tools_menu.add_submenu(label='Logic Services', submenu=logic_srvc_dropdown)
        tools_menu.add_separator()
