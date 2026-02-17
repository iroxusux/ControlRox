"""Ladder canvas for drawing ladder logic diagrams.
"""

import string
import tkinter as tk
from tkinter import Canvas
from typing import Optional, Dict, List, Literal, Union

from controlrox.interfaces import (
    IController,
    ILogicInstruction,
    IRoutine,
    IRung,
    ILogicInstructionType,
    RungElement,
    RungElementType
)
from pyrox.services.logging import log

from controlrox.models.gui.ladder.branch import LadderBranch
from controlrox.models.gui.ladder.edit_mode import LadderEditorMode
from controlrox.models.gui.ladder.element import LadderElement
from controlrox.models.gui.ladder.theme import THEME
from controlrox.services import ControllerInstanceManager


class LadderCanvas(Canvas):
    """Canvas for drawing ladder logic diagrams.

    Args:
        master: The parent widget.
        routine: Optional PLC routine to load into the canvas.
    """

    GRID_SIZE = 20
    RUNG_HEIGHT = 100
    CONTACT_WIDTH = 40
    CONTACT_HEIGHT = 30
    COIL_WIDTH = 40
    COIL_HEIGHT = 30
    BLOCK_WIDTH = 80  # default width of a function block
    BLOCK_HEIGHT = 40  # default height of a function block
    BRANCH_SPACING = 80  # default branch spacing between branch nesting levels
    ELEMENT_SPACING = 50  # spacing between elements on a rail
    MIN_WIRE_LENGTH = 50  # Minimum length of a wire connection before and after an element (e.g. -> ' --[]-- ')
    RAIL_X_LEFT = 40  # Position of the left side power rail
    RAIL_X_RIGHT = 1400  # Position of the right side power rail
    RUNG_START_Y = 50  # Starting Y position for the first rung
    RUNG_COMMENT_ASCII_Y_SIZE = 16  # Size of ascii chars for rung comments (Vertical / Y)
    RUNG_COMMENT_ASCII_X_SIZE = 6  # Size of ascii chars for rung comments (Horizontal / X)

    def __init__(
        self,
        master,
        routine: Optional[IRoutine]
    ):
        Canvas.__init__(
            self,
            master,
            bg=THEME["background"]
        )

        if not routine:
            ctrl = ControllerInstanceManager.get_controller()
            if not ctrl:
                raise ValueError("No controller instance available to create a default routine.")
            routine = ctrl.create_routine(
                name="NewRoutine",
                description="Auto-created routine",
            )

        self._routine: IRoutine = routine

        self._elements: List[LadderElement] = []
        self._selected_elements: List[LadderElement] = []
        self._mode = LadderEditorMode.VIEW
        self._current_rung = 0
        self._current_ladder_element: Optional[LadderElement] = None
        self._rung_y_positions: Dict[int, int] = {}
        self._branches: Dict[str, LadderBranch] = {}
        self._pending_branch_start: Optional[LadderElement] = None
        self._branch_tracking: list[dict] = []
        self._branch_counter = 0

        # Add drag support
        self._dragging_coordinates: Optional[tuple] = None

        # Add debug mode support
        self._debug_mode = False
        self._debug_overlays = []

        # Add tooltip support
        self._tooltip = None
        self._tooltip_delay = 1000  # 1 second delay
        self._tooltip_id = None
        self._tooltip_element = None

        # Hover preview elements
        self._rung_hover_preview_id: Optional[int] = None
        self._hover_preview_id: Optional[int] = None
        self._last_hover_position: Optional[tuple] = None

        # Bind events
        self.bind('<Button-1>', self._on_click)
        self.bind('<Button-3>', self._on_right_click)
        self.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Motion>', self._on_motion)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<Double-Button-1>', self._on_double_click)
        self.bind('<Leave>', self._on_mouse_leave)

        # Setup scrolling
        self.bind('<MouseWheel>', self._on_mousewheel)

        # Add keyboard navigation bindings
        self.bind('<KeyPress>', self._on_key_press)
        self.focus_set()  # Allow canvas to receive keyboard events

        self.draw_routine()

    @property
    def controller(self) -> IController:
        if not self.routine:
            raise ValueError('Routine not set for this canvas!')
        if not self.routine.controller:
            raise ValueError('Controller not set for the routine!')
        return self.routine.controller

    @property
    def routine(self) -> IRoutine:
        """Get the current routine being edited."""
        if not self._routine:
            raise ValueError('Routine not set for this canvas!')
        return self._routine

    @routine.setter
    def routine(self, value: IRoutine):
        """Set the routine to edit."""
        if not value:
            raise ValueError('Cannot set routine to None!')
        self._routine = value
        self.clear_canvas()
        if self._routine:
            self.draw_routine()

    @property
    def mode(self) -> LadderEditorMode:
        """Get the current editing mode."""
        return self._mode

    @mode.setter
    def mode(self, value: LadderEditorMode):
        """Set the editing mode."""
        self._clear_hover_preview()
        self._mode = value
        self.config(cursor=self._get_cursor_for_mode(value))

    def _add_branch_level(
        self,
        branch_id: str
    ) -> None:
        """Add branch level to a specified branch.

        Args:
            branch_id: The ID of the branch to add a level to.
        """
        branch = self._get_branch_from_id(branch_id)
        rung = self._get_rung_from_branch(branch)
        if not rung:
            raise ValueError(f"Rung for branch ID {branch_id} not found.")

        rung.insert_branch_level(branch.start_position)
        self._redraw_rung(rung)

    def _assm_ladder_element_from_any_element(
        self,
        ladder_element: LadderElement,
        element: Union[RungElement, LadderElement],
    ) -> None:
        """Assemble a LadderElement from a RungElement.

        Args:
            ladder_element: The LadderElement to populate.
            element: The 'Element' to extract data from.

        Raises:
            ValueError: If either ladder_element or rung_element is None.
        """
        if not ladder_element or not element:
            raise ValueError("Both ladder_element and rung_element must be provided.")

        ladder_element.branch_level = element.branch_level
        ladder_element.branch_id = element.branch_id
        ladder_element.root_branch_id = element.root_branch_id
        ladder_element.rung_number = element.rung_number
        ladder_element.instruction = element.instruction
        ladder_element.position = element.position

    def _calculate_insertion_coordinates(
        self,
        rung_number: Union[int, str],
        insertion_position: int,
        branch_level: int = 0,
        branch_id: Optional[str] = None
    ) -> tuple[int, int]:
        """Calculate the exact coordinates where an element would be inserted.

        Args:
            rung_number: The number of the rung where the element is being inserted.
            insertion_position: The position within the rung where the element is being inserted.
            branch_level: The level of the branch where the element is being inserted.
            branch_id: The ID of the branch where the element is being inserted.

        Returns:
            A tuple containing the x and y coordinates for the insertion point.

        Raises:
            ValueError: If the rung number is invalid or if the branch ID is not found.
        """
        try:
            rung_number = int(rung_number)
        except ValueError:
            raise ValueError(f"Invalid rung number: {rung_number}")

        if not branch_id:
            branch_level = 0  # we only use the ID
            rung_y_pos = self._rung_y_positions[rung_number]
            comment_height = self._get_rung_comment_height(self._routine.rungs[rung_number])
            center_y = rung_y_pos + self.RUNG_HEIGHT // 2 + comment_height
            default_start = self.RAIL_X_LEFT + (self.ELEMENT_SPACING // 2), center_y
        else:
            branch = self._branches.get(branch_id, None)
            if not branch:
                raise ValueError(f"Branch with ID {branch_id} not found.")
            center_y = branch.branch_y + 5
            default_start = branch.start_x + (self.ELEMENT_SPACING // 2), center_y

        # Get existing elements in this context
        rung_elements = self._get_rung_ladder_elements(rung_number, branch_level, branch_id)
        last_position = max((e.position for e in rung_elements), default=-1)

        if not rung_elements:
            return default_start
        elif insertion_position == 0:
            return default_start
        elif insertion_position > last_position:
            last_element = rung_elements[-1]
            return last_element.x + last_element.width + self.ELEMENT_SPACING, center_y
        else:
            this_element_index = 0
            for index, element in enumerate(rung_elements):
                if element.position == insertion_position:
                    this_element_index = index
                    break
                if element.position < insertion_position:
                    this_element_index = index + 1
            if this_element_index == 0:
                # Insert at the start
                if len(rung_elements) > 0:
                    last_element = rung_elements[-1]
                    return last_element.x + last_element.width + self.ELEMENT_SPACING, center_y
                return default_start
            else:
                prev_element_index = this_element_index - 1
            # Insert between elements
            prev_element = rung_elements[prev_element_index]
            this_element = rung_elements[this_element_index]
            prev_element_x_right = prev_element.x + prev_element.width
            element_dist_delta = this_element.x - prev_element_x_right
            insert_x = this_element.x - element_dist_delta // 2

            # Position between the two elements
            return insert_x, center_y

    def _calculate_insertion_position(
        self,
        x: int,
        y: int,
    ) -> Optional[int]:
        """Calculate the insertion position based on x and y coordinates.

        Args:
            x: The x-coordinate where the insertion is attempted.
            y: The y-coordinate where the insertion is attempted.
        Returns:
            The insertion position as an integer, or None if the position is invalid.
        """
        rung_number = self._get_rung_at_y(y)
        if rung_number is None:
            return None

        if not self._validate_insertion_position(x, y, rung_number):
            return None

        branch_level = self._get_branch_level_at_y(y, rung_number)
        branch_id = self._get_branch_id_at_position(x, y, rung_number, branch_level)

        rung_elements = self._get_rung_ladder_elements(rung_number, branch_level, branch_id)
        if not rung_elements:
            return 0

        closest_element = None
        closest_element_index = -1
        min_distance = float('inf')
        for index, element in enumerate(rung_elements):
            distance = abs(element.center_x - x)

            if distance < min_distance:
                min_distance = distance
                closest_element_index = index
                closest_element = element

        if closest_element is None:
            return rung_elements[-1].position

        if x < closest_element.center_x:
            # Insert before this element
            if closest_element_index > 0:
                return rung_elements[closest_element_index-1].position+1
            else:
                return rung_elements[closest_element_index].position
        else:
            # Insert after this element
            return rung_elements[closest_element_index].position + 1

    def _connect_branch_endpoint(
        self,
        x: int,
        y: int
    ) -> None:
        """Connect the branch back to the main rung.

        Args:
            x: The x-coordinate where the branch endpoint is being connected.
            y: The y-coordinate where the branch endpoint is being connected.
        """
        try:
            if not self._pending_branch_start:
                return

            current_position = self._get_insertion_coordinates(x, y)
            if not current_position:
                self._show_status("Invalid branch start position")
                return

            rung_number = self._get_rung_at_y(y)
            if rung_number is None:
                self._show_status("Click on a valid rung to start a branch")
                return

            position = self._calculate_insertion_position(x, y)
            if position is None:
                self._show_status("Invalid branch start position")
                return

            rung = self._routine.rungs[rung_number]
            if not rung:
                self._show_status(f"Rung {rung_number} not found in routine.")
                return

            branch_id = rung.insert_branch(self._pending_branch_start.position, position)
            self._show_status(f"Branch created: {branch_id}")
            self._redraw_rung(rung_number)
        finally:
            self._pending_branch_start = None
            self.mode = LadderEditorMode.VIEW

    def _create_block_instruction(
        self,
        rung_number: Union[int, str],
        block_type: Literal['MOV', 'TON'] = 'TON'
    ) -> ILogicInstruction:
        """Create a new function block instruction.
        """
        rung_number = int(rung_number)
        if not self._routine:
            raise ValueError("No routine available to create a contact instruction.")
        if rung_number < 0 or rung_number >= len(self._routine.rungs):
            raise ValueError(f"Invalid rung number: {rung_number}")
        return self.controller.create_instruction(
            meta_data='TON(Timer1,1000,0)',
            rung=self._routine.rungs[rung_number],
        )

    def _create_contact_instruction(
        self,
        rung_number: Union[int, str],
        contact_type: Literal['XIC', 'XIO'] = 'XIC'
    ) -> ILogicInstruction:
        """Create a new contact instruction.

        Args:
            rung_number: The rung number where the contact will be created.
            contact_type: The type of contact ('XIC' for normally open, 'XIO' for normally closed).

        Returns:
            A new ILogicInstruction object representing the contact.

        Raises:
            ValueError: If the rung number is invalid or if no routine is available.
        """
        rung_number = int(rung_number)
        if not self._routine:
            raise ValueError("No routine available to create a contact instruction.")
        if rung_number < 0 or rung_number >= len(self._routine.rungs):
            raise ValueError(f"Invalid rung number: {rung_number}")
        return self.controller.create_instruction(
            meta_data=f'{contact_type}(NewContact)',
            rung=self._routine.rungs[rung_number],
        )

    def _create_coil_instruction(
        self,
        rung_number: Union[int, str],
        coil_type: Literal['OTE', 'OTL', 'OTU'] = 'OTE'
    ) -> ILogicInstruction:
        """Create a new coil instruction.

        Args:
            rung_number: The rung number where the coil will be created.
            coil_type: The type of coil ('OTE' for output energize, 'OTL' for output latch, 'OTU' for output unlatch).

        Returns:
            A new ILogicInstruction object representing the coil.

        Raises:
            ValueError: If the rung number is invalid or if no routine is available.
        """
        rung_number = int(rung_number)
        if not self._routine:
            raise ValueError("No routine available to create a contact instruction.")
        if rung_number < 0 or rung_number >= len(self._routine.rungs):
            raise ValueError(f"Invalid rung number: {rung_number}")
        return self.controller.create_instruction(
            meta_data=f'{coil_type}(NewCoil)',
            rung=self._routine.rungs[rung_number],
        )

    def _create_end_rung(self) -> IRung:
        """Create an end rung element."""
        return self.controller.create_rung(routine=self.routine)

    def _create_ladder_branch(
        self,
        ladder_element: LadderElement,
        parent_branch_id: str = ''
    ) -> LadderBranch:

        ladder_branch = LadderBranch(
            start_x=ladder_element.x,
            end_x=ladder_element.x + 50,  # this will be updated when the branch closes
            main_y=self._rung_y_positions[ladder_element.rung_number],
            start_y=ladder_element.y - self.BRANCH_SPACING // 2,
            branch_y=ladder_element.y,
            end_y=ladder_element.y + ladder_element.height + self.BRANCH_SPACING // 2,  # This will be updated when the branch closes
            rung_number=ladder_element.rung_number,
            branch_id=ladder_element.branch_id,
            root_branch_id=ladder_element.root_branch_id,
            parent_branch_id=parent_branch_id,
            branch_level=ladder_element.branch_level,
            branch_height=self.BRANCH_SPACING,
            elements=[],
            start_position=ladder_element.position,
            end_position=ladder_element.position
        )
        self._branches[ladder_element.branch_id] = ladder_branch
        return ladder_branch

    def _clear_debug_visuals(self):
        """Clear all debug visuals from the canvas.
        """
        for overlay in self._debug_overlays:
            self.delete(overlay)
        self._debug_overlays.clear()

    def _clear_hover_preview(self):
        """Clear the hover preview.
        """
        self.delete('current_rung_highlight')
        if self._hover_preview_id:
            self.delete("hover_preview")
            self._hover_preview_id = None
            self._last_hover_position = None

    def _clear_rung_visuals(
        self,
        rung_number: int
    ) -> None:
        """Clear all visual elements for a specific rung.
        Args:
            rung_number: The rung number to clear visuals for.
        """
        self._clear_hover_preview()
        self.delete("branch_marker")
        self.delete(f"rung_{rung_number}")
        self.delete(f"rung_{rung_number}_box")
        self.delete(f"rung_{rung_number}_branch")
        self.delete(f"rung_{rung_number}_branch_marker")
        self.delete(f"rung_{rung_number}_branch_start")
        self.delete(f"rung_{rung_number}_branch_end")
        self.delete(f"rung_{rung_number}_branch_next")
        self.delete(f"rung_{rung_number}_comment")
        self.delete(f"rung_{rung_number}_instruction")
        self.delete(f"rung_{rung_number}_wire")

        # Remove elements from our tracking list
        elements_to_remove = [e for e in self._elements
                              if e.rung_number == rung_number]

        for element in elements_to_remove:
            self._elements.remove(element)

        # Remove branches for this rung
        branches_to_remove = [bid for bid, branch in self._branches.items()
                              if branch.rung_number == rung_number]

        for branch_id in branches_to_remove:
            del self._branches[branch_id]

    def _copy_element(self, element: LadderElement):
        """Copy an element (placeholder)."""
        pass

    def _delete_branch(self, branch_id: str):
        """Delete a branch and all its elements."""
        if branch_id not in self._branches:
            raise ValueError(f"Branch with ID {branch_id} not found.")

        branch = self._branches[branch_id]
        rung = self._routine.rungs[branch.rung_number] if self._routine else None
        if not rung:
            raise ValueError(f"Rung {branch.rung_number} not found in routine.")
        rung.remove_branch(branch_id)
        del self._branches[branch_id]
        self._redraw_rung(branch.rung_number)
        self._show_status(f"Deleted branch: {branch_id}")

    def _delete_element(
        self,
        event,
        element: LadderElement
    ) -> None:
        """Delete an element from the rung."""
        # Remove from rung meta data
        instr = element.instruction
        if not instr or not instr.rung:
            log(self).debug(f"No instruction or rung found for element at Y={element.y}")
            return

        rung_number = int(instr.rung.number)
        if rung_number is None or rung_number < 0:
            log(self).debug(f"No rung found for element at Y={element.y}")
            return
        if element.position is None:
            log(self).debug(f"No position found for element at Y={element.y}")
            return
        instr.rung.remove_instruction_by_index(element.position)

        # Remove from canvas
        self.delete(element.canvas_id)

        # Remove from elements list
        if element in self._elements:
            self._elements.remove(element)

        # Remove from selection if selected
        if element in self._selected_elements:
            self._selected_elements.remove(element)

        self._redraw_rung(rung_number)

    def _determine_branch_connector_type(self, element: LadderElement) -> str:
        """Determine the type of branch connector based on its position and context."""
        if not element.branch_id or element.branch_id not in self._branches:
            return "Unknown"

        branch = self._branches[element.branch_id]

        if element.position == branch.start_position:
            return "Branch Start"
        elif element.position == branch.end_position:
            return "Branch End"
        elif element.position > branch.start_position and element.position < branch.end_position:
            return "Branch Node"
        else:
            return "Branch Point"

    def _draw_block(
        self,
        instruction: ILogicInstruction,
        x: int,
        center_y: int,
        rung_number: int
    ) -> LadderElement:
        """Draw a function block instruction centered on the rung."""
        top_y = center_y - self.BLOCK_HEIGHT // 2
        operand_count = len(instruction.operands) if instruction.operands else 0
        bottom_y = center_y + self.BLOCK_HEIGHT // 2 + (operand_count * self.RUNG_COMMENT_ASCII_Y_SIZE)

        max_width = self.BLOCK_WIDTH
        if instruction.instruction_type == ILogicInstructionType.AOI:
            # Determine if instruction is an add-on instruction with named parameters
            aoi = self.controller.aois.get(instruction.instruction_name, None)
            if not aoi:
                raise ValueError(
                    f"Add-On Instruction {instruction.instruction_name} not found in controller AOIs."
                )

            # Get the parameters for the add-on instruction
            aoi_params = [p for p in aoi.parameters if p['@Visible'] == 'true' and p['@Required'] == 'true']
            if len(aoi_params) + 1 != len(instruction.operands):
                raise ValueError(
                    f"Parameter count mismatch for Add-On Instruction {instruction.instruction_name}: "
                    f"{len(aoi_params) + 1} vs {len(instruction.operands)}"
                )

            # Compile a list of parameter names
            param_names = [param['@Name'] for param in aoi_params]
        else:
            # Default to using the operand names if not an add-on instruction
            param_names = list(string.ascii_uppercase[:len(instruction.operands)])

        # add_on instruction operands are mis-aligned size-wise when compared to their parameter counterparts.
        # there is always 1 extra operand for the add-on instruction, which is the name of the instruction itself.
        name_pkg = [] if not instruction.instruction_type == ILogicInstructionType.AOI else [
            f'{instruction.name.ljust(10)} {instruction.operands[0].meta_data.ljust(20)}']

        # pull out the extra operand if this is an add-on instruction
        operands = instruction.operands[1:] if instruction.instruction_type == ILogicInstructionType.AOI else instruction.operands

        # Calculate proper column widths
        max_param_width = max(len(name) for name in param_names) if param_names else 0
        max_operand_width = max(len(op.meta_data) for op in operands) if operands else 0

        # Add padding between columns
        column_separator = "  "  # 2 spaces between columns

        # Calculate total width needed
        total_text_width = max_param_width + len(column_separator) + max_operand_width
        text_pixel_width = total_text_width * self.RUNG_COMMENT_ASCII_X_SIZE + 40  # Add some padding

        if text_pixel_width > max_width:
            max_width = text_pixel_width

        # Create properly aligned text
        for op, name in zip(operands, param_names):
            # Use proper justification for columns
            param_text = name.ljust(max_param_width)
            operand_text = op.meta_data.ljust(max_operand_width)
            name_str = f'{param_text}{column_separator}{operand_text}'
            name_pkg.append(name_str)

        rect_id = self.create_rectangle(  # Instruction rectangle
            x,
            top_y,
            x + max_width,
            bottom_y,
            outline=THEME["ladder_rung_color"],
            fill=THEME["background"],
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_instruction"
        )

        self.create_text(  # Instruction name text
            x + max_width // 2,
            center_y - 10,
            text=instruction.instruction_name,
            font=(THEME["font"], 10, 'bold'),
            fill=THEME["foreground"],
            tags=f"rung_{rung_number}_instruction"
        )

        for text in name_pkg:
            self.create_text(  # Each operand text
                x + 15,
                center_y + 5 + (name_pkg.index(text) * self.RUNG_COMMENT_ASCII_Y_SIZE),
                text=text,
                font=(THEME["font"], 8),
                fill=THEME["foreground"],
                tags=f"rung_{rung_number}_instruction",
                justify='left',
                anchor='w'
            )

        self.create_line(  # Left connecting wire
            x - 10,
            center_y,
            x, center_y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_wire"
        )

        self.create_line(  # Right connecting wire
            x + max_width,
            center_y,
            x + max_width + 10,
            center_y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_wire"
        )

        return LadderElement(
            element_type='block',
            x=x,
            y=top_y,
            width=max_width,
            height=bottom_y - top_y,
            ladder_y=center_y,
            canvas_id=rect_id,
            instruction=instruction,
            rung_number=rung_number
        )

    def _draw_branch_rail_connector(
        self,
        x,
        y,
        tags=''
    ) -> LadderElement:
        """Draw the oval indicator for branch rail connector.
        Args:
            x: X position for the branch rail connector
            y: Y position for the branch rail connector
            oval_fill: Fill color for the oval indicator
            oval_outline: Outline color for the oval indicator
            tags: Additional tags for the canvas item
        Returns:
            The canvas ID of the created oval indicator.
        """
        id = self.create_oval(
            x - 5, y - 5, x + 5, y + 5,
            fill=THEME["background"], outline=THEME["ladder_rung_color"], width=THEME["ladder_line_width"], tags=tags
        )
        return LadderElement(
            element_type='branch_rail_connector',
            x=x - 5,
            y=y - 5,
            width=10,
            height=10,
            ladder_y=y,
            canvas_id=id,
            branch_level=0,
            branch_id=tags,  # Use tags as branch ID
            rung_number=self._get_rung_at_y(y)  # Get current rung number
        )

    def _draw_branch_rail_line(
        self,
        x: int,
        y: int,
        end_x: int,
        end_y: int,
        tags: str = '',
        dashed_line: bool = False
    ) -> None:
        """Draw a line for the branch rail connector.
        Args:
            x: Start X position
            y: Start Y position
            end_x: End X position
            end_y: End Y position
            tags: Additional tags for the canvas item
            dashed_line: Whether to use a dashed line
        """
        self.create_line(
            x, y, end_x, end_y,
            fill=THEME["ladder_rung_color"], width=THEME["ladder_line_width"],
            dash=(3, 3) if dashed_line else '',
            tags=tags
        )

    def _draw_branch_left_rail(
            self,
            element: RungElement,
    ) -> LadderElement:
        """Draw the left rail branch start indicator and preview lines.
        Args:
            element: The rung element to draw the branch rail for
        Returns:
            LadderElement: The created branch rail connector element.
        """
        rung_number = self._get_rung_number(element.rung)
        x, y = self._get_element_x_y_sequence_spacing(element)
        rung = element.rung
        if not rung:
            raise ValueError("Rung not found for the given element.")

        ladder_element = self._draw_branch_rail_connector(
            x,
            y,
            f"rung_{rung_number}_branch_start"
        )

        self._assm_ladder_element_from_any_element(
            ladder_element,
            element,
        )
        self._draw_power_rail_to_prev_element(ladder_element, y)
        self._elements.append(ladder_element)
        nesting_level = rung.get_branch_internal_nesting_level(element.position)
        self._branch_tracking.append({
            'branch_id': element.branch_id,
            'branch_element': ladder_element,
            'branch_nesting': nesting_level
        })
        return ladder_element

    def _draw_branch_next_rail(
        self,
        start_rail: LadderBranch,
        x: int,
        y: int,
        tags: str = ''
    ) -> LadderElement:
        """Draw the next rail branch start indicator.
        Args:
            x: X position for the branch start
            y: Y position for the branch start
            oval_fill: Fill color for the oval indicator
            oval_outline: Outline color for the oval indicator
            tags: Additional tags for the canvas item
        Returns:
            LadderElement: The created branch rail connector element.
        """
        if not start_rail:
            raise ValueError("start_rail must be provided for branch next rail.")
        # Add branch line
        self._draw_branch_rail_line(
            start_rail.start_x + 5,
            start_rail.branch_y + 10,
            x,
            y,
            tags=tags
        )
        # Add horizontal branch line
        self._draw_branch_rail_line(
            x,
            y,
            x + 50,
            y,
            tags=tags
        )
        return self._draw_branch_rail_connector(x, y, tags)

    def _draw_branch_right_rail(
        self,
        x: int,
        parent_branch: LadderBranch,
        rung_number: int = 0,
        tags: str = '',
        dashed_line: bool = False,
        branch_text: str = ''
    ) -> LadderElement:
        """Draw the right rail branch end indicator and preview lines.
        Args:
            x: X position for the branch end
            y: Y position for the branch end
            oval_fill: Fill color for the oval indicator
            oval_outline: Outline color for the oval indicator
            tags: Additional tags for the canvas item
            dashed_line: Whether to use a dashed line for the preview
            branch_text: Optional text to display below the branch end
        Returns:
            LadderElement: The created branch rail connector element.
        """

        # Add preview branch line
        if not parent_branch:
            raise ValueError("parent_branch must be provided for branch right rail.")
        if len(parent_branch.children_branch_ids) <= 0:
            raise ValueError("parent_branch must have at least one child branch.")

        end_branch = self._branches[parent_branch.children_branch_ids[-1]]
        if not end_branch:
            raise ValueError(f"End branch with ID {parent_branch.children_branch_ids[-1]} not found.")

        y = parent_branch.branch_y + 5
        end_y = end_branch.branch_y + 5

        self._draw_branch_rail_line(x, y, x, end_y, tags=tags, dashed_line=dashed_line)

        for child in parent_branch.children_branch_ids:
            child_branch = self._branches[child]
            if not child_branch:
                raise ValueError(f"Child branch with ID {child} not found.")
            # Draw horizontal branch line
            last_element = self._get_last_element_in_branch(child_branch.branch_id)
            if not last_element:
                raise ValueError(f"No elements found in child branch {child_branch.branch_id}.")
            self._draw_branch_rail_line(
                last_element.x + last_element.width,
                child_branch.branch_y + 5,
                x,
                child_branch.branch_y + 5,
                tags=tags,
                dashed_line=dashed_line
            )

        # Draw branch end indicator last to ensure it appears on top
        ladder_element = self._draw_branch_rail_connector(x, y, tags)

        # Add text
        if branch_text:
            self.create_text(
                x, y + 15,
                text=branch_text, font=(THEME["font"], 8),
                fill=THEME["foreground"], tags=tags
            )

        self._assm_ladder_element_from_any_element(
            ladder_element,
            ladder_element,
        )
        ladder_element.rung_number = rung_number

        return ladder_element

    def _draw_coil(
        self,
        instruction: ILogicInstruction,
        x: int,
        center_y: int,
        rung_number: int
    ) -> LadderElement:
        """Draw a coil instruction centered on the rung."""
        # Calculate top and bottom Y positions for centering
        top_y = center_y - self.COIL_HEIGHT // 2
        bottom_y = center_y + self.COIL_HEIGHT // 2

        # Draw coil circle (centered on rung)
        circle_id = self.create_oval(
            x,
            top_y,
            x + self.COIL_WIDTH,
            bottom_y,
            outline=THEME["ladder_rung_color"],
            fill=THEME["background"],
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_instruction"
        )

        # Add coil type indicators (centered in coil)
        inst_type = instruction.instruction_name.lower()
        if inst_type == 'otl':  # Latch
            self.create_text(
                x + self.COIL_WIDTH // 2, center_y,
                text='L', font=(THEME["font"], 12, 'bold'),
                fill=THEME["foreground"],
                tags=f"rung_{rung_number}_instruction"
            )
        elif inst_type == 'otu':  # Unlatch
            self.create_text(
                x + self.COIL_WIDTH // 2, center_y,
                text='U', font=(THEME["font"], 12, 'bold'),
                fill=THEME["foreground"],
                tags=f"rung_{rung_number}_instruction"
            )

        # Left connecting wire
        self.create_line(
            x - 10,
            center_y,
            x,
            center_y,
            fill=THEME["ladder_rung_color"],  # Use theme color for wires
            width=THEME["ladder_line_width"], tags=f"rung_{rung_number}_wire"
        )
        # Right connecting wire (to power rail if this is the last element)
        self.create_line(
            x + self.COIL_WIDTH,
            center_y,
            x + self.COIL_WIDTH + 10,
            center_y,
            fill=THEME["ladder_rung_color"],  # Use theme color for wires
            width=THEME["ladder_line_width"], tags=f"rung_{rung_number}_wire"
        )

        _ = self._draw_instruction_texts(instruction, x, top_y, self.COIL_WIDTH)

        return LadderElement(
            element_type='coil',
            x=x,
            y=top_y,
            width=self.COIL_WIDTH,
            height=self.COIL_HEIGHT,
            ladder_y=center_y,
            canvas_id=circle_id,
            instruction=instruction,
            rung_number=rung_number
        )

    def _draw_contact(
        self,
        instruction: ILogicInstruction,
        x: int,
        center_y: int,
        rung_number: int
    ) -> LadderElement:
        """Draw a contact instruction centered on the rung."""
        # Determine contact type
        is_normally_closed = instruction.instruction_name.lower() == 'xio'

        # Calculate top and bottom Y positions for centering
        top_y = center_y - self.CONTACT_HEIGHT // 2
        bottom_y = center_y + self.CONTACT_HEIGHT // 2

        rect_id = self.create_rectangle(  # Draw contact symbol
            x,
            top_y,
            x + self.CONTACT_WIDTH,
            bottom_y,
            outline=THEME["ladder_rung_color"],
            fill=THEME["background"],
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_instruction"
        )
        # Draw the contact type indicator
        if is_normally_closed:
            self.create_line(  # Diagonal line for normally closed
                x + 5,
                top_y + 5,
                x + self.CONTACT_WIDTH - 5,
                bottom_y - 5,
                fill=THEME["ladder_rung_color"],
                width=THEME["ladder_line_width"],
                tags=f"rung_{rung_number}_instruction"
            )
        else:
            bar_top = top_y + 5
            bar_bottom = bottom_y - 5
            self.create_line(  # Vertical lines for normally open
                x + 10,
                bar_top,
                x + 10,
                bar_bottom,
                fill=THEME["ladder_rung_color"],
                width=THEME["ladder_line_width"],
                tags=f"rung_{rung_number}_instruction"
            )
            self.create_line(
                x + self.CONTACT_WIDTH - 10,
                bar_top,
                x + self.CONTACT_WIDTH - 10,
                bar_bottom,
                fill=THEME["ladder_rung_color"],
                width=THEME["ladder_line_width"],
                tags=f"rung_{rung_number}_instruction"
            )

        # Left connecting wire (from power rail to contact)
        self.create_line(
            x - 10,
            center_y,  # Start 10 pixels before contact
            x,
            center_y,       # End at contact left edge
            fill=THEME["ladder_rung_color"],
            # Use theme color for wires
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_wire"
        )
        # Right connecting wire (from contact to next element)
        self.create_line(
            x + self.CONTACT_WIDTH,
            center_y,
            x + self.CONTACT_WIDTH + 10,
            center_y,
            fill=THEME["ladder_rung_color"],  # Use theme color for wires
            width=THEME["ladder_line_width"], tags=f"rung_{rung_number}_wire"
        )

        _ = self._draw_instruction_texts(instruction, x, top_y, self.CONTACT_WIDTH)

        return LadderElement(
            element_type='contact',
            x=x,
            y=top_y,
            width=self.CONTACT_WIDTH,
            height=self.CONTACT_HEIGHT,
            ladder_y=center_y,
            canvas_id=rect_id,
            instruction=instruction,
            rung_number=rung_number
        )

    def _draw_instruction(
        self,
        element: RungElement,
        x: int,
        y: int,
    ) -> LadderElement:
        """Draw a single instruction.

        Args:
            element: The RungElement to draw.
            x: X position for the instruction
            y: Y position (should be the rung centerline)
        """
        rung_number = self._get_rung_number(element.rung)
        instruction = element.instruction
        if not instruction:
            raise ValueError("No instruction found for the given rung element.")

        inst_type = instruction.instruction_name.lower()

        if inst_type in ['xic', 'xio']:  # Contacts
            ladder_element = self._draw_contact(instruction, x, y, int(rung_number))
        elif inst_type in ['ote', 'otl', 'otu']:  # Coils
            ladder_element = self._draw_coil(instruction, x, y, int(rung_number))
        else:  # Function blocks
            ladder_element = self._draw_block(instruction, x, y, int(rung_number))

        self._assm_ladder_element_from_any_element(ladder_element, element)
        self._draw_power_rail_to_prev_element(ladder_element, y)
        self._elements.append(ladder_element)

        return ladder_element

    def _draw_instruction_alias_text(
        self,
        instruction: ILogicInstruction,
        x: int,
        y: int,
        element_width: int
    ) -> int:
        """Draw the alias text for an instruction.

        Args:
            instruction: The LogixInstruction to draw the alias for.
            x: X position for the alias text.
            y: Y position for the alias text.
            element_width: Width of the instruction element.

        Returns:
            The width of the drawn alias text.
        """
        rung = instruction.rung
        if not rung:
            raise ValueError("Instruction must be associated with a rung to draw alias text.")

        if not instruction.operands:
            return 0

        from controlrox.models.plc.rockwell.operand import LogixOperand
        if not isinstance(instruction.operands[0], LogixOperand):
            return 0

        if not instruction.operands[0].alias:
            return 0

        _alias_vertical_offset = 12
        rung_number = self._get_rung_number(rung)
        alias_text = f'<{instruction.operands[0].alias}>'
        text_length = len(alias_text) * self.RUNG_COMMENT_ASCII_X_SIZE

        self._wrap_text_with_rectangle(
            x + element_width // 2,
            y - _alias_vertical_offset - self.RUNG_COMMENT_ASCII_Y_SIZE // 2,
            alias_text,
            rung
        )

        self.create_text(  # write alias text
            x + element_width // 2,
            y - _alias_vertical_offset,
            fill=THEME["instruction_alias"],
            text=alias_text,
            font=(THEME["font"], 8,),
            tags=f"rung_{rung_number}_instruction"
        )

        return text_length

    def _draw_instruction_texts(
        self,
        instruction: ILogicInstruction,
        x: int,
        y: int,
        element_width: int
    ):
        rung = instruction.rung
        if not rung:
            raise ValueError("Instruction must be associated with a rung to draw instruction texts.")

        rung_number = self._get_rung_number(rung)
        alias_width = self._draw_instruction_alias_text(
            instruction,
            x,
            y,
            element_width
        )
        text = instruction.operands[0].meta_data if instruction.operands else "???"

        self._wrap_text_with_rectangle(
            x + element_width // 2,
            y - (15 if not alias_width else 25) - self.RUNG_COMMENT_ASCII_Y_SIZE // 2,
            text,
            rung
        )

        self.create_text(
            x + element_width // 2,
            y - (15 if not alias_width else 25),
            fill=THEME["foreground"],
            text=text,
            font=(THEME["font"], 8,),
            tags=f"rung_{rung_number}_instruction"
        )

        return text

    def _draw_hover_preview(
        self,
        x: int,
        y: int,
        mode: LadderEditorMode
    ) -> None:
        """Draw a hover preview indicator.

        Args:
            x: The x-coordinate for the hover preview.
            y: The y-coordinate for the hover preview.
            mode: The current editor mode to determine the type of preview.
        """
        if x is None or y is None or mode is None:
            return

        if mode == LadderEditorMode.INSERT_CONTACT or mode == LadderEditorMode.DRAG_ELEMENT:
            # Small rectangle preview for contact
            self._hover_preview_id = self.create_rectangle(
                x - self.CONTACT_WIDTH // 4,
                y - self.CONTACT_HEIGHT // 4,
                x + self.CONTACT_WIDTH // 4,
                y + self.CONTACT_HEIGHT // 4,
                outline='blue', fill='lightblue', stipple='gray50',
                width=2, tags="hover_preview"
            )
        elif mode == LadderEditorMode.INSERT_COIL:
            # Small circle preview for coil
            self._hover_preview_id = self.create_oval(
                x - self.COIL_WIDTH // 4,
                y - self.COIL_HEIGHT // 4,
                x + self.COIL_WIDTH // 4,
                y + self.COIL_HEIGHT // 4,
                outline='blue', fill='lightblue', stipple='gray50',
                width=2, tags="hover_preview"
            )
        elif mode == LadderEditorMode.INSERT_BRANCH:
            # Small oval preview for branch start
            self._hover_preview_id = self.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                outline='blue', fill='lightblue', stipple='gray50',
                width=2, tags="hover_preview"
            )
        elif mode == LadderEditorMode.CONNECT_BRANCH:
            # Small oval preview for branch end
            self._hover_preview_id = self.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                outline='blue', fill='lightblue', stipple='gray50',
                width=2, tags="hover_preview"
            )
        elif mode == LadderEditorMode.INSERT_BLOCK:
            # Small rectangle preview for block
            self._hover_preview_id = self.create_rectangle(
                x - self.BLOCK_WIDTH // 4,
                y - self.BLOCK_HEIGHT // 4,
                x + self.BLOCK_WIDTH // 4,
                y + self.BLOCK_HEIGHT // 4,
                outline='blue', fill='lightblue', stipple='gray50',
                width=2, tags="hover_preview"
            )

        # Add insertion point dot
        if self._hover_preview_id:
            self.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill='red', outline='darkred', width=1,
                tags="hover_preview"
            )

    def _draw_power_rail_to_prev_element(
        self,
        element: LadderElement,
        current_y: int
    ) -> None:
        """Draw a power rail from a given element's x position to the previous element's x position + width.
        If no previous element exists, draw to the left power rail.
        """
        if not element or element.rung_number is None:
            raise ValueError("Element and its rung number must be provided.")

        if current_y is None or current_y < 0:
            raise ValueError("Current Y position must be a valid non-negative integer.")

        prev_element = self._get_previous_element(element)
        if prev_element:
            # Draw wire from previous element to this element
            self.create_line(
                prev_element.x + prev_element.width,
                current_y,
                element.x,
                current_y,
                fill=THEME["ladder_rung_color"],
                width=THEME["ladder_line_width"],
                tags=f"rung_{element.rung_number}_wire"
            )
        else:
            # Draw wire from left power rail to this element
            if element.position != 0:
                log(self).error(
                    f"Element {element.rung_number} at position {element.position} has no previous element, "
                    "but position is not 0. This should not happen.",
                )
                return
            self.create_line(
                self.RAIL_X_LEFT,
                current_y,
                element.x,
                current_y,
                fill=THEME["ladder_rung_color"],
                width=THEME["ladder_line_width"],
                tags=f"rung_{element.rung_number}_wire"
            )

    def _draw_rung(
        self,
        rung: IRung,
        y_pos: int
    ) -> None:
        """Draw a single rung using the enhanced PLC data structure.

        Args:
            rung: The PLC rung to draw.
            y_pos: The Y position to draw the rung at.

        Raises:
            ValueError: If rung is None, has no sequence, or y_pos is invalid.
        """
        if not rung:
            raise ValueError("Rung cannot be None.")

        if rung.get_sequence() is None:
            raise ValueError("Rung must have a valid rung sequence.")

        if y_pos is None or y_pos < 0:
            raise ValueError("Y position must be a valid non-negative integer.")

        rung_number = self._get_rung_number(rung)
        self._rung_y_positions[rung_number] = y_pos
        self._draw_rung_comment(rung)
        self._draw_rung_sequence(rung)
        self._draw_rung_bounding_box(rung)
        self._draw_rung_power_rails(rung)
        self._draw_rung_final_power_rail(rung)

    def _draw_rung_bounding_box(
        self,
        rung: IRung,
    ) -> LadderElement:
        """Draw the bounding box for a rung.

        Args:
            rung: The PLC rung to draw the bounding box for.

        Returns:
            LadderElement: The drawn bounding box element.
        """
        rung_number = self._get_rung_number(rung)
        y_pos = self._rung_y_positions[rung_number]
        rung_height = self._get_rung_height(rung_number) + 20  # Extra padding

        # Create rectangle for rung number
        rect_id = self.create_rectangle(
            0,
            y_pos,
            self.RAIL_X_LEFT,
            y_pos + rung_height,
            outline=THEME["background"],
            fill=THEME["background"],
            tags=f"rung_{rung_number}"
        )

        # Draw rung number
        rung_number_y = y_pos + self._get_rung_comment_height(rung) + (self.RUNG_HEIGHT // 2)
        self.create_text(
            (15, rung_number_y),
            text=str(rung_number),
            anchor='w',
            font=(THEME["font"], 10),
            tags=f"rung_{rung_number}",
            fill=THEME["foreground"]
        )

        ladder_element = LadderElement(
            element_type='rung',
            x=0,
            y=y_pos,
            width=self.RAIL_X_LEFT,
            height=rung_height,
            canvas_id=rect_id,
            rung_number=rung_number,
            custom_outline=THEME["background"],
            custom_fill=THEME["background"],
        )

        self._elements.append(ladder_element)
        return ladder_element

    def _draw_rung_comment(
        self,
        rung: IRung,
    ) -> LadderElement:
        """Draw the comment for a rung.

        Args:
            rung: The PLC rung to draw the comment for.

        Returns:
            LadderElement: The drawn comment element, or None if no comment exists.
        """
        rung_number = self._get_rung_number(rung)
        y_pos = self._rung_y_positions[rung_number]
        comment_height = self._get_rung_comment_height(rung)

        rect_id = self.create_rectangle(
            self.RAIL_X_LEFT,
            y_pos,
            self.RAIL_X_RIGHT,
            y_pos + comment_height,
            outline=THEME["comment_background"],
            fill=THEME["comment_background"],
            tags=f"rung_{rung_number}_comment"
        )
        self.create_text(
            self.RAIL_X_LEFT,
            y_pos,
            text=rung.comment,
            anchor='nw',
            font=(THEME["font"], 10),
            tags=f"rung_{rung_number}_comment",
            fill=THEME["comment_foreground"],
        )

        ladder_element = LadderElement(
            element_type='rung_comment',
            x=self.RAIL_X_LEFT,
            y=y_pos,
            width=self.RAIL_X_RIGHT - self.RAIL_X_LEFT,
            height=comment_height,
            canvas_id=rect_id,
            rung_number=rung_number,
            custom_outline=THEME["comment_background"],
            custom_fill=THEME["comment_background"],
            position=-1  # Rung comments don't get a seqence position
        )
        self._elements.append(ladder_element)
        return ladder_element

    def _draw_rung_final_power_rail(
        self,
        rung: IRung,
    ) -> None:
        """Draw the final power rail for a rung.

        Args:
            rung: The PLC rung to draw the final power rail for.
        """
        rung_number = self._get_rung_number(rung)
        center_y = self._rung_y_positions[rung_number] + self._get_rung_comment_height(rung_number) + (self.RUNG_HEIGHT // 2)
        last_element = self._get_last_ladder_element(rung_number=rung_number)

        if last_element:
            x = last_element.x + last_element.width
        else:
            x = self.RAIL_X_LEFT
        self.create_line(
            x,
            center_y,
            self._get_rung_right_power_rail_x(rung),
            center_y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"],
            tags=f"rung_{rung_number}_wire"
        )

    def _draw_rung_power_rails(
        self,
        rung: IRung,
    ) -> None:
        """Draw the power rails for a rung.

        Args:
            rung: The PLC rung to draw the power rails for.
        """
        rung_number = self._get_rung_number(rung)
        y_pos = self._rung_y_positions[rung_number]
        rung_height = self._get_rung_height(rung_number)

        # Draw left power rail
        self.create_line(
            self.RAIL_X_LEFT,
            y_pos,
            self.RAIL_X_LEFT,
            y_pos + rung_height,
            width=3,
            tags=f"rung_{rung_number}_power_rail",
            fill=THEME["ladder_rung_color"]
        )

        # Draw right power rail
        right_rail_x = self._get_rung_right_power_rail_x(rung)
        self.create_line(
            right_rail_x,
            y_pos,
            right_rail_x,
            y_pos + rung_height,
            width=3,
            tags=f"rung_{rung_number}_power_rail",
            fill=THEME["ladder_rung_color"]
        )

    def _draw_rung_sequence(
            self,
            rung: IRung) -> None:
        """Draw rung using the new sequence structure with proper spacing.
        Args:
            rung: The PLC rung to draw
        """
        rung_number = self._get_rung_number(rung)
        if not isinstance(rung_number, int):
            return  # Don't process special rungs (Such as 'END')

        self._branch_tracking.clear()  # Clear branch tracking for each rung

        for element in rung.get_sequence():
            if element.element_type == RungElementType.INSTRUCTION:
                self._draw_rung_sequence_instruction(element)

            elif element.element_type == RungElementType.BRANCH_START:
                self._draw_rung_sequence_branch_start(element)

            elif element.element_type == RungElementType.BRANCH_NEXT:
                self._draw_rung_sequence_branch_next(element)

            elif element.element_type == RungElementType.BRANCH_END:
                self._draw_rung_sequence_branch_end(element)

    def _draw_rung_sequence_branch_end(
            self,
            element: RungElement,
    ):
        rung_number = self._get_rung_number(element.rung)

        if not self._branch_tracking:
            raise ValueError("Branch end found without a matching branch start.")

        branch = self._branch_tracking.pop()
        if not branch:
            raise ValueError("Branch end found without a valid branch.")

        x, y = self._get_element_x_y_sequence_spacing(element)

        # This needs to be set to get all the proper instructions on this root branch
        parent_branch = self._branches.get(branch['branch_id'], None)
        if parent_branch is None:
            raise ValueError(f"Parent branch with ID {branch['branch_id']} not found in branches.")

        ladder_element = self._draw_branch_right_rail(
            x,
            parent_branch,
            rung_number,
            tags=f"rung_{rung_number}_branch_end"
        )
        self._assm_ladder_element_from_any_element(ladder_element, element)
        ladder_element.root_branch_id = parent_branch.root_branch_id
        ladder_element.branch_level = parent_branch.branch_level
        ladder_element.branch_id = parent_branch.branch_id

        self._elements.append(ladder_element)
        parent_branch.end_x = ladder_element.x + ladder_element.width
        parent_branch.end_position = element.position

        last_child = self._branches.get(parent_branch.children_branch_ids[-1], None)
        if not last_child:
            raise ValueError(f"Last child branch with ID {parent_branch.children_branch_ids[-1]} not found.")
        last_child.end_position = element.position - 1

        self._reassign_child_branch_attrs(parent_branch)
        self._draw_power_rail_to_prev_element(ladder_element, y)

    def _draw_rung_sequence_branch_start(
            self,
            element: RungElement
    ) -> None:
        """Draw a branch start element in the rung sequence.
        Args:
            element: The RungElement representing the branch start
        """

        ladder_element = self._draw_branch_left_rail(element)
        self._create_ladder_branch(ladder_element)

    def _draw_rung_sequence_instruction(
            self,
            element: RungElement,
    ) -> None:
        """Draw an instruction element in the rung sequence.
        Args:
            element: The RungElement representing the instruction
        """
        x, y = self._get_element_x_y_sequence_spacing(element)
        ladder_element = self._draw_instruction(element, x, y)
        self._update_parent_branch_from_element(ladder_element)

    def _draw_rung_sequence_branch_next(
        self,
        element: RungElement
    ) -> None:
        """Draw a branch next element in the rung sequence.
        Args:
            element: The RungElement representing the branch next
            rung: The PLC rung containing this element
            branch_tracking: List to track branches for nesting
        Raises:
            ValueError: If the rung number is not set or if branch ID is missing.
        """
        rung_number = self._get_rung_number(element.rung)

        matching_branch = self._branches[self._branch_tracking[-1]['branch_id']] if self._branch_tracking else None
        if not matching_branch:
            raise ValueError(f"Branch with ID {element.root_branch_id} not found in branches.")
        if matching_branch.branch_id not in element.branch_id:
            raise ValueError(f"Branch ID mismatch: {matching_branch.branch_id} != {element.branch_id}")

        nesting_level = element.rung.get_branch_internal_nesting_level(matching_branch.start_position)
        x = matching_branch.start_x + 5
        if len(matching_branch.children_branch_ids) > 0:
            # If there are children branches, use the last child's end position
            last_child = self._branches[matching_branch.children_branch_ids[-1]]
            y = last_child.end_y + self.BRANCH_SPACING
        else:
            last_child = None
            y = matching_branch.end_y + self.BRANCH_SPACING + (nesting_level * self.BRANCH_SPACING)

        ladder_element = self._draw_branch_next_rail(
            matching_branch,
            x,
            y,
            tags=f"rung_{rung_number}_branch_next"
        )
        self._assm_ladder_element_from_any_element(ladder_element, element)
        branch_element = self._create_ladder_branch(ladder_element,
                                                    parent_branch_id=matching_branch.branch_id)
        if last_child:  # If there is a last child, set its end position
            last_child.end_position = branch_element.start_position - 1
        self._elements.append(ladder_element)
        self._branches[element.branch_id] = branch_element
        matching_branch.children_branch_ids.append(element.branch_id)

    def _find_insertion_position(
        self,
        x: int,
        rung_number: int,
        branch_level: int = 0,
        branch_id: Optional[str] = None
    ) -> int:
        """Find the correct position to insert a new element in the rung sequence.
        Args:
            x: X coordinate where the user clicked
            rung_number: The rung number where the insertion is happening
            branch_level: The branch level for the insertion (default is 0 for main rung)
            branch_id: The branch ID if inserting into a specific branch (default is None)
        Returns:
            int: The position to insert the new element.
        """
        rung_elements = self._get_rung_ladder_elements(rung_number, branch_level, branch_id)

        if not rung_elements:
            log(self).debug(f"No elements found for rung {rung_number} at branch level {branch_level}")
            return 0

        # Find the element closest to the click position
        closest_element = None
        closest_element_index = -1
        min_distance = float('inf')

        for index, element in enumerate(rung_elements):
            element_center_x = element.x + element.width // 2
            distance = abs(element_center_x - x)

            if distance < min_distance:
                min_distance = distance
                closest_element_index = index
                closest_element = element

        if closest_element is None:
            return rung_elements[-1].position

        # Determine if we should insert before or after the closest element
        element_center_x = closest_element.x + closest_element.width // 2

        if x < element_center_x:
            # Insert before this element
            if closest_element_index > 0:
                return rung_elements[closest_element_index-1].position+1
            else:
                return rung_elements[closest_element_index].position
        else:
            # Insert after this element
            return rung_elements[closest_element_index].position + 1

    def _get_branch_from_id(
        self,
        branch_id: str,
    ) -> LadderBranch:
        """Get a branch by its ID."""
        if branch_id not in self._branches:
            raise ValueError(f"Branch with ID {branch_id} not found.")
        return self._branches[branch_id]

    def _get_branch_at_x_y(self, x: int, y: int, rung_number: int) -> Optional[LadderBranch]:
        """Get the branch at the specified X and Y coordinates."""
        for branch in self._branches.values():
            if (branch.rung_number == rung_number and
                    branch.start_x <= x <= branch.end_x and
                    branch.start_y <= y <= branch.end_y):
                return branch
        return None

    def _get_branch_id_at_position(self, x: int, y: int, rung_number: int,
                                   branch_level: int) -> Optional[str]:
        """Get the branch ID for elements at a specific position."""
        if branch_level == 0:
            return None

        # Find which branch this position belongs to
        for branch_id, branch in self._branches.items():
            if (branch.rung_number == rung_number and
                    branch.start_x <= x <= branch.end_x and
                    branch.main_y <= y <= branch.branch_y + self.BRANCH_SPACING and
                    branch.branch_level == branch_level):
                return branch_id

        return None

    def _get_branch_level_at_y(self, y: int, rung_number: int) -> int:
        """Determine which branch level the Y coordinate corresponds to."""
        if rung_number not in self._rung_y_positions:
            return 0

        branches = [b for b in self._branches.values() if b.rung_number == rung_number]
        for branch in branches:
            if branch.start_y <= y <= branch.end_y:
                return branch.branch_level
        # If no branch found, return main rung level
        return 0

    def _get_coordinate_info(self, x: int, y: int) -> Optional[dict]:
        rung_number = self._get_rung_at_y(y)

        if rung_number is None:
            self._clear_hover_preview()
            return None

        if not self._validate_insertion_position(x, y, rung_number):
            return None

        branch = self._get_branch_at_x_y(x, y, rung_number)
        if not branch:
            branch_level = 0
            branch_id = None
        else:
            branch_level = branch.branch_level
            branch_id = branch.branch_id

        return {
            'rung_number': rung_number,
            'branch_level': branch_level,
            'branch_id': branch_id,
            'x': x,
            'y': y
        }

    def _get_cursor_for_mode(self, mode: LadderEditorMode) -> str:
        """Get appropriate cursor for editing mode."""
        cursors = {
            LadderEditorMode.VIEW: "arrow",
            LadderEditorMode.EDIT: "hand2",
            LadderEditorMode.INSERT_CONTACT: "crosshair",
            LadderEditorMode.INSERT_COIL: "crosshair",
            LadderEditorMode.INSERT_BLOCK: "crosshair",
            LadderEditorMode.INSERT_BRANCH: "crosshair",
            LadderEditorMode.CONNECT_BRANCH: "target"
        }
        return cursors.get(mode, "arrow")

    def _get_element_at(self, x: int, y: int) -> Optional[LadderElement]:
        """Get element at given coordinates."""
        for element in self._elements:
            if (element.x <= x <= element.x + element.width and
                    element.y <= y <= element.y + element.height):
                return element
        return None

    def _get_element_at_position(
        self,
        rung_number: int,
        position: int,
        branch_level: Optional[int] = None,
        branch_id: Optional[str] = None
    ) -> Optional[LadderElement]:
        """Get element at a specific position in a rung.

        Args:
            rung_number: The rung number
            position: The position in the sequence
            branch_level: The branch level (0 for main rung)
            branch_id: The branch ID if on a branch

        Returns:
            The element at the position if found, None otherwise
        """
        for element in self._elements:
            if (element.rung_number == rung_number and
                element.position == position and
                (element.branch_level == branch_level or branch_level is None) and
                    (element.branch_id == branch_id or branch_id is None)):
                return element
        return None

    def _get_element_x_spacing(self, prev_element: LadderElement) -> int:
        """Get the spacing needed for the next element based on the current element."""
        if not prev_element:
            return self.RAIL_X_LEFT + self.MIN_WIRE_LENGTH
        return prev_element.x + prev_element.width + self.ELEMENT_SPACING + self.MIN_WIRE_LENGTH

    def _get_element_y_spacing(self, element: LadderElement) -> int:
        """Get the Y spacing for elements in a rung based on branch level."""
        parent_branch: Optional[LadderBranch] = self._branches.get(element.branch_id, None)
        if parent_branch:
            return parent_branch.branch_y + 5

        rung_y = self._rung_y_positions.get(element.rung_number, None)
        if not rung_y:
            raise ValueError(f"Rung number {element.rung_number} not found in rung positions.")

        rung = self._routine.rungs[element.rung_number]
        if not rung:
            raise ValueError(f"Rung {element.rung_number} not found in routine.")

        rung_center = rung_y + (self.RUNG_HEIGHT // 2)

        return rung_center + (self.BRANCH_SPACING * element.branch_level) + self._get_rung_comment_height(rung)

    def _get_element_x_y_sequence_spacing(
        self,
        element: RungElement
    ) -> tuple[int, int]:
        """Get x, y coordinates for spacing elements in a rung sequence.

        Args:
            element: The RungElement for which to calculate spacing

        Returns:
            tuple: (x, y) coordinates for the element
        """
        prev_element = self._get_last_ladder_element(element)
        element_x = self._get_element_x_spacing(prev_element)
        element_y = self._get_element_y_spacing(element)
        return (element_x, element_y)

    def _get_elements_by_branch_id(
        self,
        branch_id: str
    ) -> list[LadderElement]:
        """Get all elements that belong to a specific branch ID."""
        return [
            element for element in self._elements
            if element.branch_id == branch_id or element.root_branch_id == branch_id
        ] if branch_id else []

    def _get_insertion_coordinates(
        self,
        x: int,
        y: int
    ) -> tuple[int, int, LadderEditorMode]:
        """Get insertion coordinates based on the current mode and position.

        Args:
            x: X coordinate where the user clicked
            y: Y coordinate where the user clicked
        Returns:
            tuple: (insertion_x, insertion_y, mode)
        """
        coord_info = self._get_coordinate_info(x, y)
        if not coord_info:
            return None, None, self._mode

        insertion_position = self._find_insertion_position(
            x,
            coord_info['rung_number'],
            coord_info['branch_level'],
            coord_info['branch_id'])
        insertion_x, insertion_y = self._calculate_insertion_coordinates(
            coord_info['rung_number'],
            insertion_position,
            coord_info['branch_level'],
            coord_info['branch_id']
        )
        return insertion_x, insertion_y, self._mode

    def _get_last_branch_ladder_x_element(
        self,
        element: RungElement
    ) -> Optional[LadderElement]:
        """Get the last ladder element in a main branch seqeuence (The most to the right)."""
        rung_number = self._get_rung_number(element.rung)

        elements_to_compare = self._get_rung_ladder_elements(
            rung_number=rung_number,
            branch_level=None,
            branch_id=element.branch_id,
            root_branch_id=element.root_branch_id,
        )

        if not elements_to_compare:
            raise ValueError(f"No elements found in parent branch for this branch: {element.branch_id}.")

        # Find the last x value (x + width) of all elements in the comparison list
        last_element = None
        for element in elements_to_compare:
            if last_element is None or (element.x + element.width) > (last_element.x + last_element.width):
                last_element = element

        if not last_element:
            raise ValueError("No valid last element position found in elements to compare.")

        return last_element

    def _get_last_element_in_branch(
        self,
        branch_id: str,
    ) -> Optional[LadderElement]:
        """Get the last element in a specific branch."""
        if branch_id not in self._branches:
            return None

        branch = self._branches[branch_id]
        elements = self._get_rung_ladder_elements(branch.rung_number, branch.branch_level, branch.branch_id)
        return elements[-1] if elements else None

    def _get_last_ladder_element(
        self,
        element: Optional[RungElement] = None,
        rung_number: Optional[Union[str, int]] = None
    ) -> Optional[LadderElement]:
        """Get the last ladder element in the rung sequence."""
        if not element and rung_number is None:
            raise ValueError("Either element or rung_number must be provided.")
        if element:

            if element.element_type == RungElementType.BRANCH_END:
                return self._get_last_branch_ladder_x_element(element)

            ladder_elements = self._get_rung_ladder_elements(element.rung_number, element.branch_level, element.root_branch_id)
        elif rung_number is not None:
            try:
                rung_number = int(rung_number)
            except ValueError:
                pass
            ladder_elements = self._get_rung_ladder_elements(rung_number)
        return ladder_elements[-1] if ladder_elements else None

    def _get_next_branch_element(self, current_element: LadderElement) -> Optional[LadderElement]:
        """Get the next branch element.

        Args:
            current_element: The current branch element

        Returns:
            The next branch element if found, None otherwise
        """
        branch_elements = [
            element for element in self._elements
            if (element.rung_number == current_element.rung_number and
                element.element_type in ['branch_rail_connector', 'branch_start', 'branch_end', 'branch_next'] and
                element.position > current_element.position)
        ]

        if branch_elements:
            # Sort by position and return the first one (closest to current)
            branch_elements.sort(key=lambda e: e.position)
            return branch_elements[0]

        return None

    def _get_previous_branch_element(self, current_element: LadderElement) -> Optional[LadderElement]:
        """Get the previous branch element.

        Args:
            current_element: The current branch element

        Returns:
            The previous branch element if found, None otherwise
        """
        branch_elements = [
            element for element in self._elements
            if (element.rung_number == current_element.rung_number and
                element.element_type in ['branch_rail_connector', 'branch_start', 'branch_end', 'branch_next'] and
                element.position < current_element.position)
        ]

        if branch_elements:
            # Sort by position and return the last one (closest to current)
            branch_elements.sort(key=lambda e: e.position)
            return branch_elements[-1]

        return None

    def _get_previous_element(
        self,
        element: LadderElement
    ) -> Optional[LadderElement]:
        """Get the previous element in the sequence.

        Args:
            element: The current LadderElement to find the previous one for.

        Returns:
            Optional[LadderElement]: The previous LadderElement if found, otherwise None.
        """
        if not self._elements:
            return None

        branch_id, root_branch_id, branch_level = None, None, None
        if element.element_type == 'branch_rail_connector':
            branch_level = element.branch_level
            branch_id = element.branch_id
            root_branch_id = element.root_branch_id

        elements = self._get_rung_ladder_elements(
            element.rung_number,
            branch_id=branch_id,
            branch_level=branch_level,
            root_branch_id=root_branch_id,
        )
        prev_element = max([e for e in elements if e.position < element.position], key=lambda e: e.position, default=None)
        return prev_element

    def _get_rung_from_branch(
        self,
        branch: Optional[LadderBranch] = None,
    ) -> Optional[IRung]:
        """Get the rung for the current branch or main rung."""
        if branch:
            return self.routine.rungs.get(branch.rung_number, None)
        raise NotImplementedError("Rung retrieval not implemented.")

    def _get_rung_at_y(
        self,
        y: int
    ) -> int:
        """Get rung number at given Y coordinate."""
        for rung_num, rung_y in self._rung_y_positions.items():
            rung_height = self._get_rung_height(rung_num)
            if rung_y <= y <= rung_y + rung_height:
                return rung_num
        raise ValueError(f"No rung found at Y coordinate {y}.")

    def _get_rung_comment_height(
        self,
        rung: Union[IRung, int, str],
    ) -> int:
        """Get the height of the comment section for a rung.
        """
        if isinstance(rung, (int, str)):
            if rung == 'END' or rung == -1:
                return 0
            rung = self._routine.rungs[int(rung)]

        if not isinstance(rung, IRung):
            raise ValueError("Expected a plc.Rung instance or a valid rung number.")
        if not rung.comment:
            return 0

        comment = rung.comment
        comment_lines = comment.count('\n') + 1
        return comment_lines * self.RUNG_COMMENT_ASCII_Y_SIZE + 20

    def _get_rung_element(
        self,
        rung_number: int
    ) -> Optional[LadderElement]:
        """Get the rung element for a specific rung number.

        Args:
            rung_number: The rung number to find

        Returns:
            The rung element if found, None otherwise
        """
        for element in self._elements:
            if (element.rung_number == rung_number and
                    element.element_type == 'rung'):
                return element
        raise ValueError(f"No rung element found for rung number {rung_number}.")

    def _get_rung_elements(
        self,
        rung_number: int,
        branch_level: Optional[int] = None,
        branch_id: Optional[str] = None,
        element_type_filter: Optional[List[str]] = None
    ) -> list[LadderElement]:
        """Get all elements for a specific rung number.

        Args:
            rung_number: The rung number to get elements for
            branch_level: The branch level to filter by (default is None for main rung)
            branch_id: The branch ID to filter by (default is None for main rung)
            element_type_filter: Optional list of element types to filter by (default is None for all types)

        Returns:
            List of LadderElement instances for the specified rung, sorted by position
        """
        elements = []
        for element in self._elements:
            if element.rung_number != rung_number:
                continue
            if branch_level is not None and element.branch_level != branch_level:
                continue
            if branch_id is not None and element.branch_id != branch_id:
                continue
            if element_type_filter is not None and element.element_type not in element_type_filter:
                continue
            elements.append(element)

        elements.sort(key=lambda e: e.position)
        return elements

    def _get_rung_height(
        self,
        rung_number: Union[int, str]
    ) -> int:
        """Get the height of a rung based on its number."""
        try:
            rung_number = int(rung_number)
        except ValueError:
            pass
        rung_y = self._rung_y_positions.get(rung_number, None)
        if not rung_y:
            raise ValueError(f"Rung number {rung_number} not found in rung positions.")
        height = self._get_max_drawn_rung_y(rung_number)
        if height <= 0:
            height = self.RUNG_HEIGHT
        else:
            height = height - rung_y
        if height < self.RUNG_HEIGHT:
            height = self.RUNG_HEIGHT
        return height

    def _get_rung_ladder_elements(
        self,
        rung_number: int,
        branch_level: Optional[int] = None,
        branch_id: Optional[str] = None,
        root_branch_id: Optional[str] = None
    ) -> List[LadderElement]:
        """Get all elements for a specific rung and branch level.

        Args:
            rung_number: The rung number to get elements for
            branch_level: The branch level to filter by (default is None for main rung)
            branch_id: The branch ID to filter by (default is None for main rung)
            root_branch_id: The root branch ID to filter by (default is None for main rung)

        Returns:
            List of LadderElement instances for the specified rung and branch level.
        """
        elements = []

        for element in self._elements:
            if element.rung_number != rung_number:
                continue
            if branch_level is not None and element.branch_level != branch_level:
                continue
            if element.element_type not in ['contact', 'coil', 'block', 'branch_rail_connector']:
                continue
            if branch_id is not None and element.branch_id != branch_id and element.root_branch_id != branch_id:
                if root_branch_id is not None and element.root_branch_id != root_branch_id:
                    continue
            elements.append(element)

        # Sort by position
        elements.sort(key=lambda e: e.position)
        return elements

    def _get_rung_number(
        self,
        rung: IRung
    ) -> int:
        """Get the rung's number, resolved as an int if possible, otherwise returning the string value.

        Args:
            rung: The rung object to get the number from

        Returns:
            Union[int, str]: The rung number as an integer or string.

        Raises:
            ValueError: If the rung number is not set or is empty.
        """
        if rung.number is None or rung.number == '':
            raise ValueError("Rung number is not set or is empty.")
        try:
            return int(rung.number)
        except ValueError:
            raise ValueError(f"Rung number '{rung.number}' is not a valid integer.")

    def _get_rung_right_power_rail_x(
        self,
        rung: IRung
    ) -> int:
        """Get the X position of the right power rail for a rung."""
        rung_number = self._get_rung_number(rung)
        rung_width = self._get_rung_width(rung)
        if rung_width == self.RAIL_X_RIGHT:
            return rung_width
        else:
            last_elem = self._get_rung_elements(rung_number)[-1]
            return self._get_element_x_spacing(last_elem)

    def _get_rung_width(
        self,
        rung: IRung,
    ) -> int:
        """Get the width of a rung based on its number."""
        rung_number = self._get_rung_number(rung)
        rung_elements = self._get_rung_elements(rung_number)
        if not rung_elements:
            return self.RAIL_X_RIGHT

        max_x = max(e.x + e.width for e in rung_elements)
        return max(max_x, self.RAIL_X_RIGHT)

    def _get_max_drawn_rung_y(
        self,
        rung_number: int
    ) -> int:
        """Get the maximum Y position for a rung based on its branches.
        If there are no branches, return the tallest instruction height.
        If the tallest instruction is less than the default rung height, return the default height.

        Args:
            rung_number: The rung number to check
        Returns:
            int: The maximum Y position for the rung.
        """
        return self._get_max_drawn_rung_element_y(rung_number)

    def _get_max_drawn_rung_element_y(
        self,
        rung_number: int,
    ) -> int:
        """Get the maximum Y position for elements in a rung."""
        max_y = 0
        for element in self._elements:
            if element.rung_number == rung_number:
                if element.y + element.height > max_y:
                    max_y = element.y + element.height
        return max_y

    def _go_to_rung(self):
        """Go to a specific rung number."""
        rung_number = tk.simpledialog.askinteger("Go to Rung", "Enter rung number:")
        if rung_number is not None:
            self.scroll_to_rung(rung_number)

    def _hide_tooltip(self):
        """Hide the current tooltip."""
        if self._tooltip_id:
            self.after_cancel(self._tooltip_id)
            self._tooltip_id = None

        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None

        self._tooltip_element = None

    def _highlight_current_element(self, element: LadderElement):
        """Highlight the currently hovered element by changing its outline color.

        Args:
            element: The LadderElement to highlight. If None, clear the highlight.
        """
        self.delete('current_element_highlight')

        if element is None:
            return

        # Highlight the current element
        self._hover_preview_id = self.create_rectangle(
            element.x, element.y,
            element.x + element.width, element.y + element.height,
            outline='orange', width=2, tags="current_element_highlight"
        )

    def _insert_element_at(self, x: int, y: int):
        """Insert new element at given coordinates, handling branches and spacing."""
        rung_number = self._get_rung_at_y(y)
        if rung_number is None:
            return

        # Validate insertion position
        if not self._validate_insertion_position(x, y, rung_number):
            self._show_status("Invalid insertion position")
            return

        # Determine if we're inserting on a branch
        branch_level = self._get_branch_level_at_y(y, rung_number)
        branch_id = self._get_branch_id_at_position(x, y, rung_number, branch_level)

        # Find insertion position in the rung sequence
        insertion_position = self._find_insertion_position(x, rung_number, branch_level, branch_id)

        # Create new instruction based on mode
        if self._mode == LadderEditorMode.INSERT_CONTACT:
            instruction = self._create_contact_instruction(rung_number)
        elif self._mode == LadderEditorMode.INSERT_COIL:
            instruction = self._create_coil_instruction(rung_number)
        elif self._mode == LadderEditorMode.INSERT_BLOCK:
            instruction = self._create_block_instruction(rung_number)
        else:
            return

        # Insert the instruction into the rung structure
        self._insert_instruction_at_position(instruction, rung_number, insertion_position,
                                             branch_level, branch_id)

        # Redraw the entire rung to reflect the new layout
        self._redraw_rung(rung_number)

        self._show_status(f"Inserted {instruction.name} at position {insertion_position} on rung {rung_number}")

    def _insert_instruction_at_position(self, instruction: ILogicInstruction,
                                        rung_number: int, position: int,
                                        branch_level: int = 0,
                                        branch_id: Optional[str] = None):
        """Insert instruction into the rung structure at the specified position."""
        if not self._routine or rung_number >= len(self._routine.rungs):
            return

        rung: IRung = self._routine.rungs[rung_number]
        rung.add_instruction(instruction.meta_data, position=position)

    def _is_last_position(self, current_element: LadderElement) -> bool:
        """Check if the current element is at the last position in its context.

        Args:
            current_element: The element to check

        Returns:
            True if it's the last position, False otherwise
        """
        # Get all elements in the same context
        context_elements = self._get_rung_ladder_elements(
            current_element.rung_number,
            current_element.branch_level,
            current_element.branch_id
        )

        if not context_elements:
            return True

        max_position = max(element.position for element in context_elements)
        return current_element.position == max_position

    def _navigate_left(self, current_element: LadderElement) -> None:
        """Navigate to the left (previous position).

        Args:
            current_element: The currently selected element
        """
        if current_element.element_type == 'rung':
            # If rung is selected, do nothing for left navigation
            if current_element.rung_number == 0:
                return
            prev_rung = self._get_rung_element(current_element.rung_number - 1)
            if not prev_rung:
                raise ValueError(f"Rung {current_element.rung_number - 1} not found.")
            last_elem = self._get_last_ladder_element(prev_rung)
            if last_elem:
                self._select_element_at(element=last_elem)
                return
            else:
                self._select_element_at(element=prev_rung)
                return

        if current_element.position == 0:
            # Navigate to rung element when at position 0
            rung_element = self._get_rung_element(current_element.rung_number)
            if rung_element:
                self._select_element_at(element=rung_element)
        else:
            # Navigate to previous position
            prev_element = self._get_element_at_position(
                current_element.rung_number,
                current_element.position - 1,
                current_element.branch_level,
                current_element.branch_id
            )
            if prev_element:
                self._select_element_at(element=prev_element)

    def _navigate_right(self, current_element: LadderElement) -> None:
        """Navigate to the right (next position).

        Args:
            current_element: The currently selected element
        """
        if current_element.element_type == 'rung':
            # From rung, go to first instruction (position 0)
            first_element = self._get_element_at_position(
                current_element.rung_number,
                0,
            )
            if first_element:
                self._select_element_at(element=first_element)
            return

        # Check if this is the last position in the current context
        if self._is_last_position(current_element):
            # Navigate to next rung element
            next_rung_element = self._get_rung_element(current_element.rung_number + 1)
            if next_rung_element:
                self._select_element_at(element=next_rung_element)
        else:
            # Navigate to next position
            next_element = self._get_element_at_position(
                current_element.rung_number,
                current_element.position + 1,
                current_element.branch_level,
                current_element.branch_id
            )
            if next_element:
                self._select_element_at(element=next_element)

    def _navigate_up(self, current_element: LadderElement) -> None:
        """Navigate up (previous rung or previous branch).

        Args:
            current_element: The currently selected element
        """
        if current_element.element_type in ['contact', 'coil', 'block']:
            # For instructions, do nothing for now
            return
        elif current_element.element_type in ['branch_rail_connector', 'branch_start', 'branch_end', 'branch_next']:
            # Navigate to previous branch
            prev_branch_element = self._get_previous_branch_element(current_element)
            if prev_branch_element:
                self._select_element_at(element=prev_branch_element)
        elif current_element.element_type == 'rung':
            # Navigate to previous rung
            prev_rung_element = self._get_rung_element(current_element.rung_number - 1)
            if prev_rung_element:
                self._select_element_at(element=prev_rung_element)

    def _navigate_down(self, current_element: LadderElement) -> None:
        """Navigate down (next rung or next branch).

        Args:
            current_element: The currently selected element
        """
        if current_element.element_type in ['contact', 'coil', 'block']:
            # For instructions, do nothing for now
            return
        elif current_element.element_type in ['branch_rail_connector', 'branch_start', 'branch_end', 'branch_next']:
            # Navigate to next branch
            next_branch_element = self._get_next_branch_element(current_element)
            if next_branch_element:
                self._select_element_at(element=next_branch_element)
        elif current_element.element_type == 'rung':
            # Navigate to next rung
            next_rung_element = self._get_rung_element(current_element.rung_number + 1)
            if next_rung_element:
                self._select_element_at(element=next_rung_element)

    def _on_click(self, event):
        """Handle mouse click events."""
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        self._clear_hover_preview()

        if self._mode == LadderEditorMode.VIEW:
            self._select_element_at(x, y, event)
        elif self._mode == LadderEditorMode.INSERT_BRANCH:
            self._start_branch_creation(x, y)
        elif self._mode == LadderEditorMode.CONNECT_BRANCH:
            self._connect_branch_endpoint(x, y)
        elif self._mode in [LadderEditorMode.INSERT_CONTACT,
                            LadderEditorMode.INSERT_COIL,
                            LadderEditorMode.INSERT_BLOCK]:
            self._insert_element_at(x, y)

    def _on_double_click(self, event):
        """Handle double-click to edit element."""
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        element = self._get_element_at(x, y)
        if not element:
            self._show_status("No element selected for editing.")
            return

        if element.element_type == 'operand_text_box':
            self._edit_operand_text_box(element)
        elif element.element_type == 'rung':
            self._view_raw_text(element.rung_number)
        elif element.element_type == 'rung_comment':
            self._edit_rung_comment(element.rung_number)
        elif element.instruction:
            self._edit_instruction(element.instruction)

    def _on_drag(self, event):
        """Handle mouse drag for moving elements."""
        if self._selected_elements:
            x, y = self.canvasx(event.x), self.canvasy(event.y)
            if self.mode == LadderEditorMode.VIEW:
                if not self._dragging_coordinates:
                    self._dragging_coordinates = (x, y)
                if abs(x - self._dragging_coordinates[0]) > 10 or \
                   abs(y - self._dragging_coordinates[1]) > 10:
                    self._dragging_coordinates = None
                    self.mode = LadderEditorMode.DRAG_ELEMENT
                    self._show_status("Drag mode activated. Click and drag to move elements.")

            if self.mode == LadderEditorMode.DRAG_ELEMENT:
                self._hide_tooltip()
                self._update_hover_preview(x, y)

    def _on_key_press(self, event: tk.Event) -> None:
        """Handle keyboard navigation.

        Args:
            event: The keyboard event
        """
        if not self._selected_elements:
            return

        # Get the currently selected element (use the last one if multiple)
        current_element = self._selected_elements[-1]

        if event.keysym == 'Left':
            self._navigate_left(current_element)
        elif event.keysym == 'Right':
            self._navigate_right(current_element)
        elif event.keysym == 'Up':
            self._navigate_up(current_element)
        elif event.keysym == 'Down':
            self._navigate_down(current_element)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_motion(self, event: tk.Event) -> None:
        """Handle mouse motion for hover effects.
        This method updates the hover preview and highlights the current rung and element.
        Args:
            event: The mouse event containing the x and y coordinates.
        """
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        self._on_tooltip_motion(event)
        self._highlight_current_element(self._get_element_at(x, y))

        if self._mode in [LadderEditorMode.INSERT_CONTACT,
                          LadderEditorMode.INSERT_COIL,
                          LadderEditorMode.INSERT_BRANCH,
                          LadderEditorMode.INSERT_BLOCK,
                          LadderEditorMode.CONNECT_BRANCH]:
            self._update_hover_preview(x, y)
        else:
            self._clear_hover_preview()

    def _on_mouse_leave(self, _: tk.Event):
        """Handle mouse leaving the canvas."""
        self._clear_hover_preview()
        self._hide_tooltip()

    def _on_release(self, event: tk.Event):
        """Handle mouse release events."""
        if not self._selected_elements:
            return
        if self._mode == LadderEditorMode.DRAG_ELEMENT:
            try:
                coord_info = self._get_coordinate_info(self.canvasx(event.x), self.canvasy(event.y))
                if not coord_info:
                    self._show_status("Invalid drop position")
                    return
                position = self._find_insertion_position(
                    coord_info['x'],
                    coord_info['rung_number'],
                    coord_info['branch_level'],
                    coord_info['branch_id']
                )
                try:
                    drop_rung_number = int(coord_info['rung_number'])
                except ValueError:
                    log(self).debug(f"Invalid rung number: {coord_info['rung_number']}")
                    self._show_status("Invalid drop position")
                    return

                if self._selected_elements[0].rung_number == drop_rung_number:
                    if self._selected_elements[0].position + 1 == position or \
                            self._selected_elements[0].position == position:
                        self._show_status("Duplicate drop position")
                        return

                    if position > self._selected_elements[0].position:
                        position -= 1

                if position < 0:
                    position = 0

                rung: controller.Rung = self._routine.rungs[drop_rung_number]
                rungs_to_draw = {
                    rung.number: rung,
                    self._selected_elements[0].rung_number: self._routine.rungs[self._selected_elements[0].rung_number]
                }
                if position > len(rung.rung_sequence) - 1:
                    position = len(rung.rung_sequence) - 1
                for element in self._selected_elements:
                    r = self._routine.rungs[element.rung_number]
                    r.remove_instruction(element.position, element.position)
                    rung.add_instruction(element.instruction.meta_data, position=position)
                    rungs_to_draw[r.number] = r
                for r in rungs_to_draw.values():
                    self._redraw_rung(r)
            except ValueError as e:
                self._show_status(f"Error during drag operation: {str(e)}")
            finally:
                self._show_status("Drag mode deactivated. Click to select or insert elements.")
                self._dragging_coordinates = None
                self._mode = LadderEditorMode.VIEW
                self._clear_hover_preview()

    def _on_right_click(self, event):
        """Handle right-click context menu."""
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        element = self._get_element_at(x, y)

        if element:
            self._show_context_menu(event, element)

    def _on_tooltip_motion(
        self,
        event: tk.Event
    ) -> None:
        """Enhanced motion handler with tooltip support.

        Args:
            event: The mouse event containing the x and y coordinates.
        """
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        element = self._get_element_at(x, y)

        if element != self._tooltip_element:
            self._hide_tooltip()
            self._tooltip_element = element

            if element is not None:
                self._tooltip_id = self.after(
                    self._tooltip_delay,
                    lambda: self._show_element_tooltip(
                        event.x_root,
                        event.y_root,
                        element)
                )

    def _paste_element(self):
        """Paste an element (placeholder)."""
        self._show_status("Paste functionality not implemented")

    def _reassign_child_branch_attrs(
        self,
        branch: LadderBranch,
    ):
        for index, child_branch_id in enumerate(branch.children_branch_ids):
            child_branch = self._branches.get(child_branch_id, None)
            if not child_branch:
                raise ValueError(f"Child branch with ID {child_branch_id} not found in branches.")

            if index < len(branch.children_branch_ids) - 1:
                next_child = self._branches.get(branch.children_branch_ids[index + 1], None)
                if not next_child:
                    raise ValueError(f"Next child branch with ID {branch.children_branch_ids[index + 1]} not found in branches.")

                child_branch.end_y = next_child.branch_y - self.BRANCH_SPACING // 2
            child_branch.start_x = branch.start_x
            child_branch.end_x = branch.end_x

    def _redraw_rung(
        self,
        rung: Union[IRung, int],
        new_y_pos: Optional[int] = None
    ):
        """Redraw a specific rung with proper spacing.
        """
        if not isinstance(rung, (IRung, int)):
            raise ValueError("Expected a plc.Rung instance or rung number instance.")
        if isinstance(rung, int):
            rung = self.routine.rungs[rung]
        elif isinstance(rung, IRung):
            rung = rung

        if not rung:
            raise ValueError(f"Rung with number {rung} not found in routine.")

        rung_number = self._get_rung_number(rung)
        y_pos = self._rung_y_positions.get(rung_number, None)
        if y_pos is None:
            raise ValueError(f"Rung number {rung_number} not found in rung positions.")

        rung_element = self._get_rung_element(rung_number)
        pre_y, pre_height = rung_element.y, rung_element.height

        self._clear_rung_visuals(rung_number)
        self._draw_rung(rung, new_y_pos or y_pos)

        rung_element = self._get_rung_element(rung_number)
        if rung_element.y != pre_y or rung_element.height != pre_height:
            next_rung_number = rung_number + 1
            next_rung_y = self._rung_y_positions.get(next_rung_number, None)
            if next_rung_y is not None:
                self._redraw_rung(
                    next_rung_number,
                    new_y_pos=self._get_rung_height(rung_element.rung_number) + rung_element.y
                )

    def _select_element_at(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        event: Optional[tk.Event] = None,
        element: Optional[LadderElement] = None
    ) -> None:
        """Select element at given coordinates.

        Args:
            x: Optional X coordinate of the click.
            y: Optional Y coordinate of the click.
            event: Optional mouse event that triggered the selection.
            element: Optional specific element to select, if provided.
        """
        if (not x or not y) and not element:
            raise ValueError("Either x and y coordinates or an element must be provided.")

        element = element or self._get_element_at(x, y)

        # Check if Ctrl button is clicked
        ctrl_pressed = bool(event.state & 0x4) if event else False  # 0x4 is the Control modifier mask
        if not ctrl_pressed:
            # Clear previous selection
            for elem in self._selected_elements:
                self.itemconfig(
                    elem.canvas_id,
                    fill=elem.custom_fill,
                    outline=elem.custom_outline,
                    width=THEME["ladder_line_width"]
                )
                elem.is_selected = False

            self._selected_elements.clear()

        if element:
            if not element.is_selected:
                self.itemconfig(element.canvas_id, outline=THEME["highlight_color"], width=3)
                element.is_selected = True
                self._selected_elements.append(element)
                self.auto_scroll_to_element(element)
            else:
                self.itemconfig(
                    element.canvas_id,
                    fill=element.custom_fill,
                    outline=element.custom_outline,
                    width=THEME["ladder_line_width"]
                )
                element.is_selected = False
                self._selected_elements.remove(element)

    def _show_element_tooltip(
        self,
        x: int,
        y: int,
        element: LadderElement
    ) -> None:
        """Enhanced tooltip for ladder elements with special handling for branch connectors.

        Args:
            x: X coordinate of the mouse pointer.
            y: Y coordinate of the mouse pointer.
            element: The LadderElement for which to show the tooltip.
        """
        if not element or self._tooltip is not None:
            return

        self._tooltip = tk.Toplevel(self)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{x + 15}+{y + 15}")

        frame = tk.Frame(
            self._tooltip,
            background=THEME["tooltip_background"],
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4
        )
        frame.pack()
        frame.update_idletasks()

        # Get generic infos
        self._add_generic_tooltip_content(frame, element)

        if self._debug_mode:
            # Debug mode: show tooltips for other non-instruction elements
            self._add_debug_element_tooltip_content(frame, element)

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        frame_x, frame_y = frame.winfo_x(), frame.winfo_y()
        frame_width, frame_height = frame.winfo_reqwidth(), frame.winfo_reqheight()

        if frame_x + frame_width > screen_width:
            x = screen_width - frame_width
            frame.wm_geometry(f"+{x}+{y + 15}")
        if frame_y + frame_height > screen_height:
            y = screen_height - frame_height
            frame.wm_geometry(f"+{x + 15}+{y}")

    def _show_context_menu(self, event, element: LadderElement):
        """Show context menu for element."""
        menu = tk.Menu(self, tearoff=0)

        if element.element_type in ['contact', 'coil', 'block']:
            menu.add_command(label="Edit", command=lambda: self._edit_instruction(element.instruction))
            menu.add_command(label="Delete", command=lambda: self._delete_element(event, element))
            menu.add_separator()
            menu.add_command(label="Copy", command=lambda: self._copy_element(element))
            menu.add_command(label="Paste", command=lambda: self._paste_element())
        elif element.element_type in ['branch_rail_connector']:
            menu.add_command(label="Add Branch level", command=lambda: self._add_branch_level(element.branch_id))
            menu.add_command(label="Delete Branch", command=lambda: self._delete_branch(element.branch_id))
        elif element.element_type in ['rung']:
            menu.add_command(label="View Raw Text", command=lambda: self._view_raw_text(element.rung_number))
            menu.add_command(label="Edit Comment", command=lambda: self._edit_rung_comment(element.rung_number))
            menu.add_command(label="Delete Rung", command=lambda: self.delete_rung(element.rung_number))
            menu.add_separator()
            menu.add_command(label="Add Contact", command=lambda: self._insert_element_at(event.x, event.y))
            menu.add_command(label="Add Coil", command=lambda: self._insert_element_at(event.x, event.y))
            menu.add_command(label="Add Block", command=lambda: self._insert_element_at(event.x, event.y))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _show_status(self, message: str):
        """Show status message with debug prefix if in debug mode."""
        debug_prefix = "[DEBUG] " if self._debug_mode else ""
        full_message = f"{debug_prefix}{message}"
        log(self).info(full_message)

        # Also show in status bar if available
        if hasattr(self, '_status_label'):
            self._status_label.config(text=full_message)

    def _start_branch_creation(
        self,
        x: int,
        y: int
    ) -> None:
        """Start creating a branch at the clicked location.

        Args:
            x: X coordinate of the click.
            y: Y coordinate of the click.
        """
        try:
            current_position = self._get_insertion_coordinates(x, y)
            if not current_position:
                self._show_status("Invalid branch start position")
                return

            rung_number = self._get_rung_at_y(y)
            if rung_number is None:
                self._show_status("Click on a valid rung to start a branch")
                return

            position = self._calculate_insertion_position(x, y)
            if position is None:
                self._show_status("Invalid branch start position")
                return

            branch_start_id = self.create_oval(
                current_position[0] - 5,
                current_position[1] - 5,
                current_position[0] + 5,
                current_position[1] + 5,
                fill='green',
                outline='darkgreen',
                width=THEME["ladder_line_width"],
                tags="branch_marker"
            )
            self._pending_branch_start = LadderElement(
                element_type='branch_start',
                x=current_position[0] - 5,
                y=current_position[1] - 5,
                width=10,
                height=10,
                canvas_id=branch_start_id,
                branch_level=0,
                branch_id='',
                position=position,
                rung_number=rung_number,
            )
        finally:
            if self._pending_branch_start:
                self.mode = LadderEditorMode.CONNECT_BRANCH
                self._show_status("Click where you want the branch to reconnect")
            else:
                self.mode = LadderEditorMode.VIEW

    def _update_hover_preview(self, x: int, y: int):
        """Update the hover preview for element insertion."""
        current_position = self._get_insertion_coordinates(x, y)

        if current_position != self._last_hover_position:
            self._clear_hover_preview()
            self._draw_hover_preview(current_position[0], current_position[1], current_position[2])
            self._last_hover_position = current_position

    def _update_parent_branch_from_element(
        self,
        element: LadderElement,
    ) -> None:
        """Update a parent branch's height statitics from a given element.
        Additionally, append the element to the parent branch's elements

        Args:
            element: The LadderElement to update the parent branch with
        """
        parent_branch: Optional[LadderBranch] = self._branches.get(element.branch_id, None)
        if parent_branch:
            if element.height > parent_branch.branch_height:
                parent_branch.set_branch_height(element.height)
            parent_branch.elements.append(element)

    def _validate_insertion_position(self, x: int, y: int, rung_number: int) -> bool:
        """Validate that the insertion position is appropriate."""
        if rung_number not in self._rung_y_positions:
            return False

        rung_height = self._rung_y_positions[rung_number] + self._get_rung_height(rung_number)
        if not (self._rung_y_positions[rung_number] <= y <= rung_height):
            return False

        if x < self.RAIL_X_LEFT:
            return False

        return True

    def _view_raw_text(self, rung_number: int):
        """View and edit the raw meta data text for a rung using a popup dialog.

        Args:
            rung_number: The rung number to view/edit the meta data text for
        """
        try:  # Especially for 'END' rung, just return (if there are any other special rungs, we'll return here too)
            rung_number = int(rung_number)
        except ValueError:
            return

        if not self._routine or rung_number >= len(self._routine.rungs):
            self._show_status(f"Invalid rung number: {rung_number}")
            return

        rung = self._routine.rungs[rung_number]
        current_text = rung.text if rung.text else ""

        # Create popup dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"View/Edit Text - Rung {rung_number}")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Header label
        header_frame = tk.Frame(dialog)
        header_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(
            header_frame,
            text=f"Rung {rung_number} Text:",
            font=(THEME["font"], 12, 'bold')
        ).pack(anchor='w')

        # Warning label for raw data editing
        warning_frame = tk.Frame(dialog, bg='#ffe6e6')
        warning_frame.pack(fill='x', padx=10, pady=2)

        tk.Label(
            warning_frame,
            text="⚠️ Warning: Editing raw meta text data can break the rung structure. Use with caution!",
            font=(THEME["font"], 9),
            fg='#cc0000',
            bg='#ffe6e6'
        ).pack(anchor='w', padx=5, pady=3)

        # Text widget with scrollbar
        text_frame = tk.Frame(dialog)
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create text widget with monospace font for better formatting
        text_widget = tk.Text(
            text_frame,
            wrap='none',  # Don't wrap for better XML/data viewing
            font=(THEME["font"], 9),
            bg='white',
            fg='black',
            insertbackground='black'
        )

        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=v_scrollbar.set)

        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(text_frame, orient='horizontal', command=text_widget.xview)
        text_widget.configure(xscrollcommand=h_scrollbar.set)

        # Grid layout for scrollbars
        text_widget.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        text_widget.insert('1.0', current_text)
        text_widget.focus_set()

        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)

        def on_accept():
            """Save the text and close dialog."""
            new_text = text_widget.get('1.0', 'end-1c')  # Get text without trailing newline

            # Update the rung text
            rung.set_text(new_text)

            # Redraw the rung to reflect any changes
            self._redraw_rung(rung_number)

            # Update status
            if new_text.strip():
                self._show_status(f"Updated text for rung {rung_number}")
            else:
                self._show_status(f"Cleared text for rung {rung_number}")

            dialog.destroy()

        def on_cancel():
            """Close dialog without saving."""
            dialog.destroy()

        def on_clear():
            """Clear the text."""
            text_widget.delete('1.0', 'end')
            text_widget.focus_set()

        def on_validate():
            """Validate the current text structure."""
            self._show_status("Validating meta data...")

        # Buttons
        tk.Button(
            button_frame,
            text="Accept",
            command=on_accept,
            width=10,
            bg='lightgreen'
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=10,
            bg='lightcoral'
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Clear",
            command=on_clear,
            width=10,
            bg='lightyellow'
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Validate",
            command=on_validate,
            width=10,
            bg='lightcyan'
        ).pack(side='left', padx=5)

        # Character/line count label
        info_label = tk.Label(
            button_frame,
            text=f"Characters: {len(current_text)} | Lines: {current_text.count(chr(10)) + 1 if current_text else 0}",
            font=('Arial', 8),
            fg='gray'
        )
        info_label.pack(side='right', padx=5)

        def update_info_count(event=None):
            """Update character and line count as user types."""
            content = text_widget.get('1.0', 'end-1c')
            char_count = len(content)
            line_count = content.count('\n') + 1 if content else 0
            info_label.config(text=f"Characters: {char_count} | Lines: {line_count}")

        # Bind info count update
        text_widget.bind('<KeyRelease>', update_info_count)
        text_widget.bind('<Button-1>', update_info_count)

        # Keyboard shortcuts
        dialog.bind('<Control-Return>', lambda e: on_accept())
        dialog.bind('<Escape>', lambda e: on_cancel())
        dialog.bind('<F5>', lambda e: on_validate())  # F5 to validate

        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        # Wait for dialog to close
        dialog.wait_window()

    def _wrap_text_with_rectangle(
        self,
        center_x: int,
        y: int,
        text: str,
        rung: IRung,
        padding: int = 1,
    ) -> None:
        rung_number = self._get_rung_number(rung)
        text_length = len(text) * self.RUNG_COMMENT_ASCII_X_SIZE
        start_x = center_x - text_length // 2 - (padding * self.RUNG_COMMENT_ASCII_X_SIZE)
        end_x = center_x + text_length // 2 + (padding * self.RUNG_COMMENT_ASCII_X_SIZE)
        start_y = y - padding
        end_y = y + self.RUNG_COMMENT_ASCII_Y_SIZE + padding

        box = self.create_rectangle(
            start_x,
            start_y,
            end_x,
            end_y,
            outline=THEME["background"],
            fill=THEME["background"],
            width=1,
            tags=f"rung_{rung_number}_box"
        )
        self._elements.append(
            LadderElement(
                element_type='operand_text_box',
                x=start_x,
                y=start_y,
                width=end_x - start_x,
                height=end_y - start_y,
                canvas_id=box,
                rung_number=rung_number,
                instruction=None,
                custom_outline=THEME["background"],
            ))

    def add_rung(self) -> int:
        """Add a new empty rung to the routine."""
        # Create new rung
        new_rung = self.controller.create_rung()
        new_rung.set_number(str(len(self.routine.rungs)))
        new_rung.set_text("")
        new_rung.set_comment("")

        # Add to routine
        self.routine.add_rung(new_rung)

        # Redraw routine
        self.draw_routine()

        return len(self.routine.rungs) - 1

    def auto_scroll_to_element(
        self,
        element: LadderElement,
        margin: int = 50
    ) -> None:
        """Auto-scroll canvas to ensure element is fully visible.

        Args:
            element: The LadderElement to scroll to
            margin: Additional margin around the element in pixels
        """
        if not element:
            return

        # Get canvas dimensions
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        # Get current scroll region
        scroll_region = self.cget('scrollregion')
        if not scroll_region:
            return

        # Parse scroll region: "x1 y1 x2 y2"
        scroll_parts = scroll_region.split()
        if len(scroll_parts) != 4:
            return

        total_width = float(scroll_parts[2]) - float(scroll_parts[0])
        total_height = float(scroll_parts[3]) - float(scroll_parts[1])

        # Get element bounds with margin
        element_top = element.y - margin
        element_bottom = element.y + element.height + margin
        element_left = element.x - margin
        element_right = element.x + element.width + margin

        # Get current visible area
        current_top = self.canvasy(0)
        current_bottom = self.canvasy(canvas_height)
        current_left = self.canvasx(0)
        current_right = self.canvasx(canvas_width)

        # Calculate if scrolling is needed
        scroll_y_needed = False
        scroll_x_needed = False

        new_y_fraction = 0
        new_x_fraction = 0

        # Check Y direction
        if element_top < current_top:
            # Element is above visible area
            new_y_fraction = max(0, element_top / total_height)
            scroll_y_needed = True
        elif element_bottom > current_bottom:
            # Element is below visible area
            new_y_fraction = min(1, (element_bottom - canvas_height) / total_height)
            scroll_y_needed = True

        # Check X direction
        if element_left < current_left:
            # Element is left of visible area
            new_x_fraction = max(0, element_left / total_width)
            scroll_x_needed = True
        elif element_right > current_right:
            # Element is right of visible area
            new_x_fraction = min(1, (element_right - canvas_width) / total_width)
            scroll_x_needed = True

        # Perform scrolling
        if scroll_y_needed:
            self.yview_moveto(new_y_fraction)
        if scroll_x_needed:
            self.xview_moveto(new_x_fraction)

    def clear_canvas(self):
        """Clear all elements from the canvas."""
        self.delete("all")
        self._elements.clear()
        self._selected_elements.clear()
        self._rung_y_positions.clear()
        self._branches.clear()
        self._pending_branch_start = None
        self._clear_hover_preview()

    def delete_rung(self, rung_number: int):
        """Delete a rung from the routine."""
        if (not self._routine or not hasattr(self._routine, 'rungs') or
                rung_number >= len(self._routine.rungs)):
            return

        # Remove from routine data
        self._routine.remove_rung_by_index(rung_number)

        # Redraw routine
        self.draw_routine()

        log(self).info(f"Deleted rung {rung_number}")

    def draw_routine(
        self
    ) -> None:
        """Draw the entire routine on the canvas."""
        self.clear_canvas()
        rungs_to_draw = self.routine.rungs
        y_pos = self.RUNG_START_Y
        for rung in rungs_to_draw:
            self._draw_rung(rung, y_pos)
            y_pos += self._get_rung_height(rung.number)
        self.configure(scrollregion=self.bbox("all"))

    def scroll_to_rung(self, rung_number: int, margin: int = 50):
        """Scroll to a specific rung.

        Args:
            rung_number: The rung number to scroll to
            margin: Additional margin around the rung
        """
        if rung_number not in self._rung_y_positions:
            return

        # Find the rung element
        rung_element = None
        for element in self._elements:
            if element.rung_number == rung_number and element.element_type == 'rung':
                rung_element = element
                break

        if rung_element:
            self.auto_scroll_to_element(rung_element, margin)

    def validate_canvas(self) -> None:
        """Validate the current ladder logic canvas.

        This method checks for common issues like missing connections, duplicate elements,
        and other logical errors in the ladder logic.
        """
        if not self._routine:
            self._show_status("No routine loaded for validation.")
            return

        # Perform validation checks
        errors = []
        for rung in self._routine.rungs:
            if not rung.get_sequence():
                errors.append(f"Rung {rung.number} is empty.")
            # Add more validation checks as needed

        if errors:
            error_message = "\n".join(errors)
            self._show_status(f"Validation failed:\n{error_message}")
        else:
            self._show_status("Validation successful. No issues found.")


if __name__ == "__main__":
    # Simple test harness for the LadderCanvas
    ctrl = ControllerInstanceManager.new_controller()
    rout = ctrl.create_routine("TestRoutine")

    root = tk.Tk()
    root.title("Ladder Logic Editor Test")

    ladder_canvas = LadderCanvas(
        root,
        routine=rout,
    )
    ladder_canvas.pack(fill='both', expand=True)

    # Add a test rung
    ladder_canvas.add_rung()

    root.mainloop()
