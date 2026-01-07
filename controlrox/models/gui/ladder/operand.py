"""Ladder operand gui dataclass.
"""
from dataclasses import dataclass
from typing import Optional
from controlrox.interfaces import ILogicInstruction


@dataclass
class LadderOperand:
    """Represents an operand within a ladder element.
    """
    text: str
    x: int
    y: int
    width: int
    height: int
    canvas_id: int
    instruction: Optional[ILogicInstruction] = None
