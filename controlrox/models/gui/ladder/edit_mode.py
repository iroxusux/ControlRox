"""Ladder editor mode."""
from enum import Enum


class LadderEditorMode(Enum):
    """Editing modes for the ladder editor.
    Available modes:
    - VIEW: View mode, no editing allowed.
    - EDIT: Edit mode, allows adding and modifying elements.
    - INSERT_CONTACT: Insert a contact element.
    - INSERT_COIL: Insert a coil element.
    - INSERT_BLOCK: Insert a function block element.
    - INSERT_BRANCH: Insert a branch element.
    - CONNECT_BRANCH: Connect a branch to an existing element.
    """
    VIEW = "view"
    EDIT = "edit"
    INSERT_CONTACT = "insert_contact"
    INSERT_COIL = "insert_coil"
    INSERT_BLOCK = "insert_block"
    INSERT_BRANCH = "insert_branch"
    CONNECT_BRANCH = "connect_branch"
    DRAG_ELEMENT = "draw_element"
