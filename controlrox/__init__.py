""" A Window Manager toolset for modification and management of Programmable Logic Controllers (PLCs) and other industrial automation devices.
This package provides a framework for building applications that interact with PLCs, including models for application configuration, tasks,
and services for file and directory operations.
It also includes utility classes for managing user interfaces, such as list boxes and context menus.
"""
# import Pyrox to ensure all static registrations are done
import pyrox  # noqa: F401

from . import (
    interfaces,
    services,
    models,
    tasks,
    applications,
)


__all__ = (
    'interfaces',
    'applications',
    'services',
    'models',
    'tasks',
)
