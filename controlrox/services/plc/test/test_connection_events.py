"""Integration tests: PlcConnectionManager publishes PlcConnectionEventBus events.

These tests verify that the correct bus events are fired at the right points
in PlcConnectionManager's lifecycle — without making real PLC network calls.
"""
import unittest
from unittest.mock import Mock, patch

from controlrox.services.plc.connection import (
    ConnectionParameters,
    PlcConnectionManager,
)
from controlrox.services.plc.events import (
    PlcConnectionEventBus,
    PlcConnectionEventType,
)
from pyrox.models.network import Ipv4Address


def _reset_manager():
    """Reset PlcConnectionManager class-level state between tests."""
    PlcConnectionManager._connected = False
    PlcConnectionManager._commands = []
    PlcConnectionManager._subscribers = []
    PlcConnectionManager._watch_table = {}
    PlcConnectionManager.connection_parameters = ConnectionParameters(
        ip_address=Ipv4Address('192.168.1.1'),
        slot=0,
        rpi=250,
    )


class TestConnectionLoopEventsOnFirstConnect(unittest.TestCase):
    """_connection_loop publishes CONNECTED on the first successful strobe."""

    def setUp(self):
        _reset_manager()
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()
        _reset_manager()

    def test_connected_event_published_on_first_success(self):
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, received.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=True), \
             patch.object(PlcConnectionManager, '_run_commands'), \
             patch.object(PlcConnectionManager, '_schedule'):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_type, PlcConnectionEventType.CONNECTED)
        self.assertEqual(received[0].ip_address, '192.168.1.1')
        self.assertEqual(received[0].slot, 0)

    def test_connected_event_not_repeated_when_already_connected(self):
        """If already connected, a second successful strobe must not re-fire CONNECTED."""
        PlcConnectionManager._connected = True
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, received.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=True), \
             patch.object(PlcConnectionManager, '_run_commands'), \
             patch.object(PlcConnectionManager, '_schedule'):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received), 0)

    def test_no_disconnected_event_on_first_failed_strobe(self):
        """If not yet connected, a strobe failure should only fire CONNECTION_FAILED."""
        PlcConnectionManager._connected = False
        received_types = []
        for et in PlcConnectionEventType:
            PlcConnectionEventBus.subscribe(et, lambda e: received_types.append(e.event_type))

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=False):
            PlcConnectionManager._connection_loop()

        self.assertIn(PlcConnectionEventType.CONNECTION_FAILED, received_types)
        self.assertNotIn(PlcConnectionEventType.DISCONNECTED, received_types)
        self.assertNotIn(PlcConnectionEventType.CONNECTED, received_types)


class TestConnectionLoopEventsOnStrobeFail(unittest.TestCase):
    """_connection_loop fires CONNECTION_FAILED (and DISCONNECTED if was connected)."""

    def setUp(self):
        _reset_manager()
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()
        _reset_manager()

    def test_connection_failed_event_published(self):
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTION_FAILED, received.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=False):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_type, PlcConnectionEventType.CONNECTION_FAILED)

    def test_disconnected_event_published_when_was_connected(self):
        PlcConnectionManager._connected = True
        received_disconnected = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, received_disconnected.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=False):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received_disconnected), 1)
        self.assertFalse(PlcConnectionManager._connected)

    def test_disconnected_not_fired_when_was_not_connected(self):
        PlcConnectionManager._connected = False
        received_disconnected = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, received_disconnected.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=False):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received_disconnected), 0)


class TestConnectionLoopEventsOnException(unittest.TestCase):
    """_connection_loop fires CONNECTION_FAILED (and DISCONNECTED if was connected)
    when _strobe_plc raises."""

    def setUp(self):
        _reset_manager()
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()
        _reset_manager()

    def test_connection_failed_published_on_exception(self):
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTION_FAILED, received.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', side_effect=OSError("network error")):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received), 1)

    def test_disconnected_published_on_exception_when_was_connected(self):
        PlcConnectionManager._connected = True
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, received.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', side_effect=OSError("network error")):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received), 1)
        self.assertFalse(PlcConnectionManager._connected)

    def test_connected_not_published_on_exception(self):
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, received.append)

        with patch.object(PlcConnectionManager, '_strobe_plc', side_effect=RuntimeError("boom")):
            PlcConnectionManager._connection_loop()

        self.assertEqual(len(received), 0)


class TestDisconnectEvents(unittest.TestCase):
    """disconnect() fires DISCONNECTED exactly once when connected."""

    def setUp(self):
        _reset_manager()
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()
        _reset_manager()

    def test_disconnected_event_published(self):
        PlcConnectionManager._connected = True
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, received.append)

        with patch.object(PlcConnectionManager._timer_service, 'clear_all_tasks'):
            PlcConnectionManager.disconnect()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_type, PlcConnectionEventType.DISCONNECTED)

    def test_disconnected_event_carries_ip_and_slot(self):
        PlcConnectionManager._connected = True
        PlcConnectionManager.connection_parameters = ConnectionParameters(
            ip_address=Ipv4Address('10.20.30.40'), slot=3
        )
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, received.append)

        with patch.object(PlcConnectionManager._timer_service, 'clear_all_tasks'):
            PlcConnectionManager.disconnect()

        self.assertEqual(received[0].ip_address, '10.20.30.40')
        self.assertEqual(received[0].slot, 3)

    def test_no_event_when_already_disconnected(self):
        PlcConnectionManager._connected = False
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, received.append)

        PlcConnectionManager.disconnect()

        self.assertEqual(len(received), 0)


class TestSaveConnectionParametersEvents(unittest.TestCase):
    """save_connection_parameters() fires PARAMETERS_CHANGED."""

    def setUp(self):
        _reset_manager()
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()
        _reset_manager()

    def test_parameters_changed_event_published(self):
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.PARAMETERS_CHANGED, received.append)

        with patch('controlrox.services.plc.connection.EnvManager'):
            PlcConnectionManager.save_connection_parameters()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_type, PlcConnectionEventType.PARAMETERS_CHANGED)

    def test_parameters_changed_event_carries_current_params(self):
        PlcConnectionManager.connection_parameters = ConnectionParameters(
            ip_address=Ipv4Address('172.16.0.1'), slot=2
        )
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.PARAMETERS_CHANGED, received.append)

        with patch('controlrox.services.plc.connection.EnvManager'):
            PlcConnectionManager.save_connection_parameters()

        self.assertEqual(received[0].ip_address, '172.16.0.1')
        self.assertEqual(received[0].slot, 2)

    def test_no_other_events_published_on_save(self):
        """save_connection_parameters should only publish PARAMETERS_CHANGED."""
        for et in [
            PlcConnectionEventType.CONNECTED,
            PlcConnectionEventType.DISCONNECTED,
            PlcConnectionEventType.CONNECTION_FAILED,
        ]:
            PlcConnectionEventBus.subscribe(et, lambda e: self.fail(f"Unexpected event: {e.event_type}"))

        with patch('controlrox.services.plc.connection.EnvManager'):
            PlcConnectionManager.save_connection_parameters()


class TestEventBusIsolation(unittest.TestCase):
    """Verify bus state does not leak between unrelated manager operations."""

    def setUp(self):
        _reset_manager()
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()
        _reset_manager()

    def test_subscribing_to_one_type_does_not_affect_others(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)

        # Trigger a disconnect event — cb must not be called
        PlcConnectionManager._connected = True
        with patch.object(PlcConnectionManager._timer_service, 'clear_all_tasks'):
            PlcConnectionManager.disconnect()

        cb.assert_not_called()

    def test_clearing_bus_prevents_stale_callbacks_from_running(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        PlcConnectionEventBus.clear()

        with patch.object(PlcConnectionManager, '_strobe_plc', return_value=True), \
             patch.object(PlcConnectionManager, '_run_commands'), \
             patch.object(PlcConnectionManager, '_schedule'):
            PlcConnectionManager._connection_loop()

        cb.assert_not_called()


if __name__ == '__main__':
    unittest.main()
