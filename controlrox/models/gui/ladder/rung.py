"""Ladder Rung visual component for drawing individual rungs.

This module provides a self-contained rung drawing class that manages
all visual elements of a single ladder logic rung, including:
- Power rails (left and right)
- Rung number display
- Comment area
- Bounding box
- Visual elements container
"""

import tkinter as tk
from typing import Optional, List

from controlrox.interfaces import IRung
from controlrox.models.gui.ladder.element import LadderElement
from controlrox.models.gui.ladder.theme import THEME


class LadderRung:
    """Visual representation of a ladder logic rung on a canvas.

    This class encapsulates all drawing logic for a single rung, making it
    easier to manage, duplicate, and integrate into the larger ladder canvas.

    Args:
        canvas: The tkinter Canvas to draw on
        rung: The PLC rung data model
        y_position: Y coordinate where the rung should be drawn
        rail_x_left: X coordinate of the left power rail (default: 40)
        rail_x_right: X coordinate of the right power rail (default: 1400)
        rung_height: Height of the rung drawing area (default: 100)
    """

    # Default dimensions (can be overridden via constructor)
    DEFAULT_RAIL_X_LEFT = 40
    DEFAULT_RAIL_X_RIGHT = 1400
    DEFAULT_RUNG_HEIGHT = 100
    DEFAULT_COMMENT_ASCII_Y_SIZE = 16
    DEFAULT_COMMENT_ASCII_X_SIZE = 6

    def __init__(
        self,
        canvas: tk.Canvas,
        rung: IRung,
        y_position: int,
        rail_x_left: Optional[int] = None,
        rail_x_right: Optional[int] = None,
        rung_height: Optional[int] = None,
    ):
        """Initialize a LadderRung visual component."""
        self.canvas = canvas
        self.rung = rung
        self.y_position = y_position

        # Use provided values or defaults
        self.rail_x_left = rail_x_left if rail_x_left is not None else self.DEFAULT_RAIL_X_LEFT
        self.rail_x_right = rail_x_right if rail_x_right is not None else self.DEFAULT_RAIL_X_RIGHT
        self.rung_height = rung_height if rung_height is not None else self.DEFAULT_RUNG_HEIGHT

        # Storage for drawn elements
        self.elements: List[LadderElement] = []
        self.canvas_ids: List[int] = []

        # Calculated dimensions
        self._comment_height = self._calculate_comment_height()
        self._total_height = self._calculate_total_height()

        # Component references
        self._bounding_box_element: Optional[LadderElement] = None
        self._comment_element: Optional[LadderElement] = None
        self._left_rail_id: Optional[int] = None
        self._right_rail_id: Optional[int] = None
        self._rung_number_text_id: Optional[int] = None

    @property
    def rung_number(self) -> int:
        """Get the rung number."""
        return self.rung.number

    @property
    def comment_height(self) -> int:
        """Get the calculated comment height."""
        return self._comment_height

    @property
    def total_height(self) -> int:
        """Get the total height of this rung (comment + rung area + padding)."""
        return self._total_height

    @property
    def center_y(self) -> int:
        """Get the Y coordinate of the rung's center line (for drawing elements)."""
        return self.y_position + self._comment_height + (self.rung_height // 2)

    def draw(self) -> List[LadderElement]:
        """Draw all components of the rung.

        Returns:
            List of LadderElement objects created during drawing
        """
        self.elements.clear()
        self.canvas_ids.clear()

        # Draw in order: comment -> bounding box -> number -> power rails
        self._draw_comment()
        self._draw_bounding_box()
        self._draw_rung_number()
        self._draw_power_rails()

        return self.elements

    def clear(self) -> None:
        """Remove all visual elements of this rung from the canvas."""
        for canvas_id in self.canvas_ids:
            self.canvas.delete(canvas_id)

        self.canvas_ids.clear()
        self.elements.clear()

    def update_position(self, new_y_position: int) -> None:
        """Update the Y position of this rung.

        Args:
            new_y_position: New Y coordinate for the rung
        """
        delta_y = new_y_position - self.y_position
        self.y_position = new_y_position

        # Move all canvas items
        for canvas_id in self.canvas_ids:
            self.canvas.move(canvas_id, 0, delta_y)

        # Update element positions
        for element in self.elements:
            element.y += delta_y

    def highlight(self, color: str = None) -> None:
        """Highlight the rung (change outline color).

        Args:
            color: Color to use for highlighting (default: theme highlight color)
        """
        if not color:
            color = THEME.get("highlight_color", "yellow")

        if self._bounding_box_element:
            self.canvas.itemconfig(
                self._bounding_box_element.canvas_id,
                outline=color,
                width=3
            )

    def unhighlight(self) -> None:
        """Remove highlighting from the rung."""
        if self._bounding_box_element:
            self.canvas.itemconfig(
                self._bounding_box_element.canvas_id,
                outline=THEME["background"],
                width=1
            )

    def _calculate_comment_height(self) -> int:
        """Calculate the height needed for the rung comment.

        Returns:
            Height in pixels needed for the comment
        """
        if not self.rung.comment or not self.rung.comment.strip():
            return 0

        comment_lines = self.rung.comment.count('\n') + 1
        return comment_lines * self.DEFAULT_COMMENT_ASCII_Y_SIZE

    def _calculate_total_height(self) -> int:
        """Calculate the total height of this rung including comment and padding.

        Returns:
            Total height in pixels
        """
        return self._comment_height + self.rung_height + 20  # 20px padding

    def _draw_bounding_box(self) -> LadderElement:
        """Draw the bounding box and background for the rung number area.

        Returns:
            LadderElement representing the bounding box
        """
        rect_id = self.canvas.create_rectangle(
            0,
            self.y_position,
            self.rail_x_left,
            self.y_position + self._total_height,
            outline=THEME["background"],
            fill=THEME["background"],
            tags=f"rung_{self.rung_number}"
        )

        self.canvas_ids.append(rect_id)

        ladder_element = LadderElement(
            element_type='rung',
            x=0,
            y=self.y_position,
            width=self.rail_x_left,
            height=self._total_height,
            canvas_id=rect_id,
            rung_number=self.rung_number,
            custom_outline=THEME["background"],
            custom_fill=THEME["background"],
        )

        self.elements.append(ladder_element)
        self._bounding_box_element = ladder_element

        return ladder_element

    def _draw_comment(self) -> Optional[LadderElement]:
        """Draw the comment area for the rung.

        Returns:
            LadderElement for the comment, or None if no comment exists
        """
        if not self.rung.comment or not self.rung.comment.strip():
            return None

        # Draw comment background rectangle
        rect_id = self.canvas.create_rectangle(
            self.rail_x_left,
            self.y_position,
            self.rail_x_right,
            self.y_position + self._comment_height,
            outline=THEME["comment_background"],
            fill=THEME["comment_background"],
            tags=f"rung_{self.rung_number}_comment"
        )

        # Draw comment text
        text_id = self.canvas.create_text(
            self.rail_x_left + 5,  # Small padding from left
            self.y_position + 2,   # Small padding from top
            text=self.rung.comment,
            anchor='nw',
            font=(THEME["font"], 10),
            tags=f"rung_{self.rung_number}_comment",
            fill=THEME["comment_foreground"],
        )

        self.canvas_ids.extend([rect_id, text_id])

        ladder_element = LadderElement(
            element_type='rung_comment',
            x=self.rail_x_left,
            y=self.y_position,
            width=self.rail_x_right - self.rail_x_left,
            height=self._comment_height,
            canvas_id=rect_id,
            rung_number=self.rung_number,
            custom_outline=THEME["comment_background"],
            custom_fill=THEME["comment_background"],
            position=-1  # Comments don't have sequence positions
        )

        self.elements.append(ladder_element)
        self._comment_element = ladder_element

        return ladder_element

    def _draw_rung_number(self) -> int:
        """Draw the rung number text.

        Returns:
            Canvas ID of the rung number text
        """
        number_y = self.center_y

        text_id = self.canvas.create_text(
            15,  # Fixed X position for rung numbers
            number_y,
            text=str(self.rung_number),
            anchor='w',
            font=(THEME["font"], 10),
            tags=f"rung_{self.rung_number}",
            fill=THEME["foreground"]
        )

        self.canvas_ids.append(text_id)
        self._rung_number_text_id = text_id

        return text_id

    def _draw_power_rails(self) -> tuple[int, int]:
        """Draw the left and right power rails for this rung.

        Returns:
            Tuple of (left_rail_id, right_rail_id)
        """
        # Calculate rail start and end Y positions
        rail_start_y = self.y_position + self._comment_height
        rail_end_y = rail_start_y + self.rung_height

        # Draw left power rail
        left_rail_id = self.canvas.create_line(
            self.rail_x_left,
            rail_start_y,
            self.rail_x_left,
            rail_end_y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"] + 1,  # Power rails slightly thicker
            tags=f"rung_{self.rung_number}_rail_left"
        )

        # Draw right power rail
        right_rail_id = self.canvas.create_line(
            self.rail_x_right,
            rail_start_y,
            self.rail_x_right,
            rail_end_y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"] + 1,
            tags=f"rung_{self.rung_number}_rail_right"
        )

        self.canvas_ids.extend([left_rail_id, right_rail_id])
        self._left_rail_id = left_rail_id
        self._right_rail_id = right_rail_id

        return left_rail_id, right_rail_id

    def draw_horizontal_connection(
        self,
        start_x: int,
        end_x: int,
        branch_offset_y: int = 0,
        tags: Optional[str] = None
    ) -> int:
        """Draw a horizontal wire connection at the rung's center line.

        Args:
            start_x: Starting X coordinate
            end_x: Ending X coordinate
            branch_offset_y: Vertical offset for branch connections (default: 0)
            tags: Optional canvas tags for the line

        Returns:
            Canvas ID of the drawn line
        """
        y = self.center_y + branch_offset_y

        line_tags = tags or f"rung_{self.rung_number}_wire"

        line_id = self.canvas.create_line(
            start_x,
            y,
            end_x,
            y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"],
            tags=line_tags
        )

        self.canvas_ids.append(line_id)
        return line_id

    def draw_vertical_connection(
        self,
        x: int,
        start_y: int,
        end_y: int,
        tags: Optional[str] = None
    ) -> int:
        """Draw a vertical wire connection (for branches).

        Args:
            x: X coordinate for the vertical line
            start_y: Starting Y coordinate
            end_y: Ending Y coordinate
            tags: Optional canvas tags for the line

        Returns:
            Canvas ID of the drawn line
        """
        line_tags = tags or f"rung_{self.rung_number}_branch_wire"

        line_id = self.canvas.create_line(
            x,
            start_y,
            x,
            end_y,
            fill=THEME["ladder_rung_color"],
            width=THEME["ladder_line_width"],
            tags=line_tags
        )

        self.canvas_ids.append(line_id)
        return line_id

    def get_element_by_type(self, element_type: str) -> Optional[LadderElement]:
        """Get the first element of a specific type.

        Args:
            element_type: Type of element to find (e.g., 'rung', 'rung_comment')

        Returns:
            LadderElement if found, None otherwise
        """
        for element in self.elements:
            if element.element_type == element_type:
                return element
        return None

    def __repr__(self) -> str:
        """String representation of the LadderRung."""
        return (
            f"LadderRung(number={self.rung_number}, "
            f"y={self.y_position}, "
            f"height={self._total_height}, "
            f"elements={len(self.elements)})"
        )


if __name__ == "__main__":
    """Simple test harness for LadderRung visualization."""
    from controlrox.services import ControllerInstanceManager

    # Create test data
    ctrl = ControllerInstanceManager.new_controller()
    test_rung = ctrl.create_rung()
    test_rung.set_number(0)
    test_rung.set_text("XIC(Tag1)XIC(Tag2)OTE(Output);")
    test_rung.set_comment("This is a test rung\nwith multiple lines\nof comments")

    # Create window
    root = tk.Tk()
    root.title("Ladder Rung Test")
    root.geometry("800x400")

    # Create canvas
    canvas = tk.Canvas(root, bg=THEME["background"])
    canvas.pack(fill='both', expand=True)

    # Create and draw ladder rung
    ladder_rung = LadderRung(
        canvas=canvas,
        rung=test_rung,
        y_position=50
    )

    elements = ladder_rung.draw()

    # Draw a test horizontal connection
    ladder_rung.draw_horizontal_connection(
        start_x=ladder_rung.rail_x_left,
        end_x=ladder_rung.rail_x_right
    )

    # Display info
    print(f"Created {ladder_rung}")
    print(f"Total elements: {len(elements)}")
    print(f"Center Y: {ladder_rung.center_y}")
    print(f"Comment height: {ladder_rung.comment_height}")
    print(f"Total height: {ladder_rung.total_height}")

    # Test highlighting
    def toggle_highlight():
        if hasattr(toggle_highlight, 'highlighted'):
            ladder_rung.unhighlight()
            toggle_highlight.highlighted = False
        else:
            ladder_rung.highlight()
            toggle_highlight.highlighted = True

    # Add button to test highlighting
    btn = tk.Button(root, text="Toggle Highlight", command=toggle_highlight)
    btn.pack()

    root.mainloop()
