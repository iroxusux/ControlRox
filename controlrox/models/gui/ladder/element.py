"""Ladder element gui dataclass
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from controlrox.interfaces import ILogicInstruction

from .theme import THEME
from .operand import LadderOperand


@dataclass
class LadderElement:
    """Represents a ladder logic element on the canvas."""
    element_type: str  # 'contact', 'coil', 'block', 'wire', 'branch_start', 'branch_end', 'rung'
    x: int
    y: int
    width: int
    height: int
    canvas_id: int
    rung_number: int  # Rung number this element belongs to
    ladder_y: Optional[int] = None  # Y position that connects this element to the ladder rung
    instruction: Optional[ILogicInstruction] = None
    is_selected: bool = False
    branch_level: int = 0
    branch_id: str = ''
    root_branch_id: str = ''
    position: int = 0  # Position in rung sequence

    # Theme settings
    theme_overrides: Optional[Dict[str, Any]] = field(default_factory=dict)
    custom_fill: Optional[str] = THEME["background"]
    custom_outline: Optional[str] = THEME["ladder_rung_color"]
    custom_text_color: Optional[str] = THEME["foreground"]

    # Operand support
    operands: List[LadderOperand] = field(default_factory=list)

    @property
    def center_x(self) -> int:
        """Get the center X coordinate of the element."""
        return self.x + self.width // 2
