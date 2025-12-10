"""Constants for ControlRox Applications.
"""
from enum import Enum


class TreeViewMode(str, Enum):
    """TreeView display modes."""
    PROPERTIES = 'view_properties'
    TAGS = 'view_tags'
    PROGRAMS = 'view_programs'
    AOIS = 'view_aois'
    DATATYPES = 'view_datatypes'
