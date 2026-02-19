"""PLC connection event bus.

Provides a lightweight pub/sub mechanism for PLC connectivity events so that
any part of the application can react to connect / disconnect / error
transitions without depending directly on
:class:`~controlrox.services.plc.PlcConnectionManager`.

Usage::

    from controlrox.services.plc.events import (
        PlcConnectionEvent,
        PlcConnectionEventBus,
        PlcConnectionEventType,
    )

    def on_connected(event: PlcConnectionEvent) -> None:
        print(f"PLC connected: {event.ip_address}")

    PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, on_connected)

    # Later, to clean up:
    PlcConnectionEventBus.unsubscribe(PlcConnectionEventType.CONNECTED, on_connected)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from pyrox.services.logging import log


class PlcConnectionEventType(Enum):
    """Types of PLC connection events."""

    CONNECTED = auto()              # Successfully established communication with PLC
    DISCONNECTED = auto()           # Connection torn down (normal or abnormal)
    CONNECTION_FAILED = auto()      # Attempted to connect / strobe but failed
    PARAMETERS_CHANGED = auto()     # Connection parameters (IP, slot, RPI) were updated


@dataclass
class PlcConnectionEvent:
    """Event data for PLC connection events.

    Attributes:
        event_type:  Which kind of event occurred.
        ip_address:  String form of the PLC IP address at the time of the event.
        slot:        Chassis slot number in use at the time of the event.
        data:        Optional additional context (e.g. error messages).
    """

    event_type: PlcConnectionEventType
    ip_address: str = ''
    slot: int = 0
    data: Optional[Dict[str, Any]] = field(default_factory=dict)


class PlcConnectionEventBus:
    """Static event bus for PLC connection lifecycle events.

    Mirrors the pattern used by :class:`pyrox.services.scene.SceneEventBus`.
    All methods are class methods so no instance is ever required.

    Example — subscribe from a task or GUI component::

        class MyTask:
            def inject(self) -> None:
                PlcConnectionEventBus.subscribe(
                    PlcConnectionEventType.CONNECTED,
                    self._on_plc_connected,
                )
                PlcConnectionEventBus.subscribe(
                    PlcConnectionEventType.DISCONNECTED,
                    self._on_plc_disconnected,
                )

            def uninject(self) -> None:
                PlcConnectionEventBus.unsubscribe(
                    PlcConnectionEventType.CONNECTED,
                    self._on_plc_connected,
                )
                PlcConnectionEventBus.unsubscribe(
                    PlcConnectionEventType.DISCONNECTED,
                    self._on_plc_disconnected,
                )

            def _on_plc_connected(self, event: PlcConnectionEvent) -> None:
                print(f"PLC online: {event.ip_address}")

            def _on_plc_disconnected(self, event: PlcConnectionEvent) -> None:
                print("PLC offline")
    """

    _subscribers: Dict[PlcConnectionEventType, List[Callable[[PlcConnectionEvent], None]]] = {}

    @classmethod
    def subscribe(
        cls,
        event_type: PlcConnectionEventType,
        callback: Callable[[PlcConnectionEvent], None],
    ) -> None:
        """Register *callback* to be called whenever *event_type* is published.

        Duplicate registrations of the same callback for the same event type
        are silently ignored.

        Args:
            event_type: The :class:`PlcConnectionEventType` to listen for.
            callback:   Callable accepting one :class:`PlcConnectionEvent` arg.
        """
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []

        if callback not in cls._subscribers[event_type]:
            cls._subscribers[event_type].append(callback)
            log(cls).debug("Subscribed %s to %s", getattr(callback, '__name__', repr(callback)), event_type.name)

    @classmethod
    def unsubscribe(
        cls,
        event_type: PlcConnectionEventType,
        callback: Callable[[PlcConnectionEvent], None],
    ) -> None:
        """Remove *callback* from the subscriber list for *event_type*.

        No-op if the callback was never subscribed.

        Args:
            event_type: The :class:`PlcConnectionEventType` to stop listening to.
            callback:   The exact callable reference passed to :meth:`subscribe`.
        """
        if event_type in cls._subscribers:
            if callback in cls._subscribers[event_type]:
                cls._subscribers[event_type].remove(callback)
                log(cls).debug("Unsubscribed %s from %s", getattr(callback, '__name__', repr(callback)), event_type.name)

    @classmethod
    def publish(cls, event: PlcConnectionEvent) -> None:
        """Broadcast *event* to all registered subscribers.

        Faulty subscribers (those that raise an exception) are automatically
        removed so they cannot block future events.

        Args:
            event: The :class:`PlcConnectionEvent` to broadcast.
        """
        subscribers = cls._subscribers.get(event.event_type, [])

        log(cls).debug(
            "Publishing %s to %d subscriber(s)",
            event.event_type.name,
            len(subscribers),
        )

        dead_callbacks: List[Callable] = []
        for callback in subscribers.copy():
            try:
                callback(event)
            except Exception as exc:
                log(cls).error(
                    "Error in PlcConnectionEventBus subscriber %s: %s",
                    getattr(callback, '__name__', repr(callback)),
                    exc,
                )
                dead_callbacks.append(callback)

        for callback in dead_callbacks:
            cls.unsubscribe(event.event_type, callback)

    @classmethod
    def clear(cls) -> None:
        """Remove all subscriptions.  Primarily useful in unit tests."""
        cls._subscribers.clear()
        log(cls).debug("Cleared all PlcConnectionEventBus subscriptions")

    @classmethod
    def get_subscriber_count(cls, event_type: PlcConnectionEventType) -> int:
        """Return the number of active subscribers for *event_type*.

        Args:
            event_type: The event type to query.

        Returns:
            Number of currently registered callbacks.
        """
        return len(cls._subscribers.get(event_type, []))
