"""Ladder branch gui dataclass.
"""
from dataclasses import dataclass, field
from typing import List
from .element import LadderElement


@dataclass
class LadderBranch:
    """Represents a branch structure in ladder logic."""
    start_x: int
    end_x: int
    main_y: int
    start_y: int
    branch_y: int
    end_y: int
    rung_number: int
    branch_id: str
    elements: List[LadderElement]
    children_branch_ids: List[str] = field(default_factory=list)  # IDs ONLY of child nested branches
    root_branch_id: str = ''
    parent_branch_id: str = ''  # For nested branches, this will track which branch this element belongs to
    branch_height: int = 0  # Height of the branch, used for rendering
    branch_level: int = 0
    start_position: int = 0
    end_position: int = 0
