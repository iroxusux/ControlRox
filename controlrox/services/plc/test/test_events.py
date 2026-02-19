"""Unit tests for PlcConnectionEventBus, PlcConnectionEvent, and PlcConnectionEventType."""
import unittest
from unittest.mock import Mock

from controlrox.services.plc.events import (
    PlcConnectionEvent,
    PlcConnectionEventBus,
    PlcConnectionEventType,
)


class TestPlcConnectionEventType(unittest.TestCase):
    """Test cases for the PlcConnectionEventType enum."""

    def test_all_event_types_exist(self):
        """All expected event types must be present."""
        expected = {'CONNECTED', 'DISCONNECTED', 'CONNECTION_FAILED', 'PARAMETERS_CHANGED'}
        actual = {member.name for member in PlcConnectionEventType}
        self.assertEqual(actual, expected)

    def test_event_types_are_unique(self):
        """Each event type must have a distinct value."""
        values = [member.value for member in PlcConnectionEventType]
        self.assertEqual(len(values), len(set(values)))

    def test_comparison(self):
        """Event types should compare equal to themselves and not to others."""
        self.assertEqual(PlcConnectionEventType.CONNECTED, PlcConnectionEventType.CONNECTED)
        self.assertNotEqual(PlcConnectionEventType.CONNECTED, PlcConnectionEventType.DISCONNECTED)


class TestPlcConnectionEvent(unittest.TestCase):
    """Test cases for the PlcConnectionEvent dataclass."""

    def test_required_field(self):
        """event_type is required; defaults are used for the rest."""
        event = PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED)
        self.assertEqual(event.event_type, PlcConnectionEventType.CONNECTED)
        self.assertEqual(event.ip_address, '')
        self.assertEqual(event.slot, 0)
        self.assertIsInstance(event.data, dict)
        self.assertEqual(event.data, {})

    def test_full_initialization(self):
        """All fields can be set explicitly."""
        event = PlcConnectionEvent(
            event_type=PlcConnectionEventType.CONNECTION_FAILED,
            ip_address='192.168.1.10',
            slot=2,
            data={'reason': 'timeout'},
        )
        self.assertEqual(event.event_type, PlcConnectionEventType.CONNECTION_FAILED)
        self.assertEqual(event.ip_address, '192.168.1.10')
        self.assertEqual(event.slot, 2)
        self.assertEqual(event.data, {'reason': 'timeout'})

    def test_data_field_is_independent_per_instance(self):
        """Each event instance must get its own data dict (default_factory)."""
        e1 = PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED)
        e2 = PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED)
        e1.data['key'] = 'value'  # type: ignore
        self.assertNotIn('key', e2.data)  # type: ignore


class TestPlcConnectionEventBusSubscribeUnsubscribe(unittest.TestCase):
    """Basic subscribe / unsubscribe behaviour."""

    def setUp(self):
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()

    def test_subscribe_adds_callback(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 1)

    def test_subscribe_multiple_callbacks(self):
        cb1, cb2 = Mock(), Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb1)
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb2)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 2)

    def test_subscribe_same_callback_twice_is_idempotent(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 1)

    def test_unsubscribe_removes_callback(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        PlcConnectionEventBus.unsubscribe(PlcConnectionEventType.CONNECTED, cb)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 0)

    def test_unsubscribe_unknown_callback_is_noop(self):
        cb = Mock()
        # Should not raise even if cb was never subscribed
        PlcConnectionEventBus.unsubscribe(PlcConnectionEventType.CONNECTED, cb)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 0)

    def test_unsubscribe_unknown_event_type_is_noop(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, cb)
        # Unsubscribing from a different event type must not affect the other
        PlcConnectionEventBus.unsubscribe(PlcConnectionEventType.CONNECTED, cb)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.DISCONNECTED), 1)

    def test_subscriptions_are_independent_per_event_type(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 1)
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.DISCONNECTED), 0)


class TestPlcConnectionEventBusPublish(unittest.TestCase):
    """Publish / dispatch behaviour."""

    def setUp(self):
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()

    def test_publish_calls_subscriber(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        event = PlcConnectionEvent(
            event_type=PlcConnectionEventType.CONNECTED,
            ip_address='10.0.0.1',
            slot=0,
        )
        PlcConnectionEventBus.publish(event)
        cb.assert_called_once_with(event)

    def test_publish_calls_all_subscribers(self):
        cb1, cb2 = Mock(), Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb1)
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb2)
        event = PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED)
        PlcConnectionEventBus.publish(event)
        cb1.assert_called_once_with(event)
        cb2.assert_called_once_with(event)

    def test_publish_does_not_call_other_event_type_subscribers(self):
        cb_connected = Mock()
        cb_disconnected = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb_connected)
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, cb_disconnected)

        PlcConnectionEventBus.publish(PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED))

        cb_connected.assert_called_once()
        cb_disconnected.assert_not_called()

    def test_publish_with_no_subscribers_is_noop(self):
        # Should not raise
        PlcConnectionEventBus.publish(PlcConnectionEvent(event_type=PlcConnectionEventType.DISCONNECTED))

    def test_publish_passes_correct_event_data(self):
        received = []
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.PARAMETERS_CHANGED, received.append)
        event = PlcConnectionEvent(
            event_type=PlcConnectionEventType.PARAMETERS_CHANGED,
            ip_address='172.16.0.5',
            slot=3,
            data={'rpi': 500},
        )
        PlcConnectionEventBus.publish(event)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].ip_address, '172.16.0.5')
        self.assertEqual(received[0].slot, 3)
        self.assertEqual(received[0].data, {'rpi': 500})

    def test_faulty_subscriber_is_removed_and_others_still_called(self):
        """A callback that raises must be silently dropped; remaining callbacks
        should still be invoked."""
        def bad_cb(event):
            raise RuntimeError("intentional test error")

        good_cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, bad_cb)
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, good_cb)

        # First publish — bad_cb raises, gets removed; good_cb runs.
        PlcConnectionEventBus.publish(PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED))
        good_cb.assert_called_once()
        self.assertEqual(PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 1)

        # Second publish — only good_cb remains.
        PlcConnectionEventBus.publish(PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED))
        self.assertEqual(good_cb.call_count, 2)

    def test_publish_all_four_event_types(self):
        """Each event type should reach its own subscriber independently."""
        callbacks = {et: Mock() for et in PlcConnectionEventType}
        for event_type, cb in callbacks.items():
            PlcConnectionEventBus.subscribe(event_type, cb)

        for event_type in PlcConnectionEventType:
            PlcConnectionEventBus.publish(PlcConnectionEvent(event_type=event_type))

        for event_type, cb in callbacks.items():
            cb.assert_called_once()
            received_type = cb.call_args[0][0].event_type
            self.assertEqual(received_type, event_type)


class TestPlcConnectionEventBusClearAndCount(unittest.TestCase):
    """clear() and get_subscriber_count() behaviour."""

    def setUp(self):
        PlcConnectionEventBus.clear()

    def tearDown(self):
        PlcConnectionEventBus.clear()

    def test_clear_removes_all_subscriptions(self):
        for event_type in PlcConnectionEventType:
            PlcConnectionEventBus.subscribe(event_type, Mock())
        PlcConnectionEventBus.clear()
        for event_type in PlcConnectionEventType:
            self.assertEqual(PlcConnectionEventBus.get_subscriber_count(event_type), 0)

    def test_get_subscriber_count_zero_for_unseen_type(self):
        self.assertEqual(
            PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.CONNECTED), 0
        )

    def test_get_subscriber_count_reflects_multiple_subscriptions(self):
        for _ in range(5):
            PlcConnectionEventBus.subscribe(PlcConnectionEventType.DISCONNECTED, Mock())
        self.assertEqual(
            PlcConnectionEventBus.get_subscriber_count(PlcConnectionEventType.DISCONNECTED), 5
        )

    def test_clear_then_subscribe_works(self):
        cb = Mock()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        PlcConnectionEventBus.clear()
        PlcConnectionEventBus.subscribe(PlcConnectionEventType.CONNECTED, cb)
        event = PlcConnectionEvent(event_type=PlcConnectionEventType.CONNECTED)
        PlcConnectionEventBus.publish(event)
        cb.assert_called_once_with(event)


if __name__ == '__main__':
    unittest.main()
