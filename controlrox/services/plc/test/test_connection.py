"""Unit tests for PLC connection services."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from controlrox.services.plc.connection import (
    ConnectionParameters,
    ConnectionCommandType,
    ConnectionCommand,
    WatchTableEntry,
    PlcConnectionManager,
)
from pyrox.models.network import Ipv4Address
from pylogix.lgx_response import Response


class TestConnectionParameters(unittest.TestCase):
    """Test cases for ConnectionParameters dataclass."""

    def test_default_initialization(self):
        """Test ConnectionParameters with default values."""
        params = ConnectionParameters()
        self.assertIsInstance(params.ip_address, Ipv4Address)
        self.assertEqual(str(params.ip_address), '192.168.1.2')
        self.assertEqual(params.slot, 0)
        self.assertEqual(params.rpi, 250)

    def test_custom_initialization(self):
        """Test ConnectionParameters with custom values."""
        custom_ip = Ipv4Address('10.0.0.1')
        params = ConnectionParameters(
            ip_address=custom_ip,
            slot=2,
            rpi=500
        )
        self.assertEqual(params.ip_address, custom_ip)
        self.assertEqual(params.slot, 2)
        self.assertEqual(params.rpi, 500)

    def test_ip_address_type(self):
        """Test that ip_address is an Ipv4Address instance."""
        params = ConnectionParameters()
        self.assertIsInstance(params.ip_address, Ipv4Address)

    def test_slot_value_range(self):
        """Test slot with valid integer values."""
        for slot in [0, 1, 2, 3, 4]:
            params = ConnectionParameters(slot=slot)
            self.assertEqual(params.slot, slot)

    def test_rpi_value_range(self):
        """Test rpi with valid integer values."""
        for rpi in [100, 250, 500, 1000]:
            params = ConnectionParameters(rpi=rpi)
            self.assertEqual(params.rpi, rpi)


class TestConnectionCommandType(unittest.TestCase):
    """Test cases for ConnectionCommandType enum."""

    def test_enum_values(self):
        """Test that all enum values exist."""
        self.assertEqual(ConnectionCommandType.NA.value, 0)
        self.assertEqual(ConnectionCommandType.READ.value, 1)
        self.assertEqual(ConnectionCommandType.WRITE.value, 2)

    def test_enum_members(self):
        """Test that enum has all expected members."""
        expected_members = {'NA', 'READ', 'WRITE'}
        actual_members = {member.name for member in ConnectionCommandType}
        self.assertEqual(actual_members, expected_members)

    def test_enum_comparison(self):
        """Test enum comparison operations."""
        self.assertEqual(ConnectionCommandType.READ, ConnectionCommandType.READ)
        self.assertNotEqual(ConnectionCommandType.READ, ConnectionCommandType.WRITE)


class TestWatchTableEntry(unittest.TestCase):
    """Test cases for WatchTableEntry dataclass."""

    def test_default_initialization(self):
        """Test WatchTableEntry with default values."""
        entry = WatchTableEntry(tag_name='TestTag')
        self.assertEqual(entry.tag_name, 'TestTag')
        self.assertEqual(entry.data_type, 0)
        self.assertIsNone(entry.last_value)
        self.assertIsNone(entry.last_update)
        self.assertEqual(entry.error_count, 0)
        self.assertEqual(entry.callbacks, [])

    def test_custom_initialization(self):
        """Test WatchTableEntry with custom values."""
        mock_callback = Mock()
        test_time = datetime.now()
        entry = WatchTableEntry(
            tag_name='CustomTag',
            data_type=5,
            last_value=42,
            last_update=test_time,
            error_count=3,
            callbacks=[mock_callback]
        )
        self.assertEqual(entry.tag_name, 'CustomTag')
        self.assertEqual(entry.data_type, 5)
        self.assertEqual(entry.last_value, 42)
        self.assertEqual(entry.last_update, test_time)
        self.assertEqual(entry.error_count, 3)
        self.assertIn(mock_callback, entry.callbacks)

    def test_callbacks_list_default_factory(self):
        """Test that callbacks list is independent for each instance."""
        entry1 = WatchTableEntry(tag_name='Tag1')
        entry2 = WatchTableEntry(tag_name='Tag2')

        mock_callback = Mock()
        entry1.callbacks.append(mock_callback)

        self.assertIn(mock_callback, entry1.callbacks)
        self.assertNotIn(mock_callback, entry2.callbacks)


class TestConnectionCommand(unittest.TestCase):
    """Test cases for ConnectionCommand dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_callback = Mock()

    def test_read_command_creation(self):
        """Test creating a READ command."""
        cmd = ConnectionCommand(
            type=ConnectionCommandType.READ,
            tag_name='TestTag',
            tag_value=0,
            data_type=0,
            response_cb=self.mock_callback
        )
        self.assertEqual(cmd.type, ConnectionCommandType.READ)
        self.assertEqual(cmd.tag_name, 'TestTag')
        self.assertEqual(cmd.tag_value, 0)
        self.assertEqual(cmd.data_type, 0)
        self.assertEqual(cmd.response_cb, self.mock_callback)

    def test_write_command_creation(self):
        """Test creating a WRITE command."""
        cmd = ConnectionCommand(
            type=ConnectionCommandType.WRITE,
            tag_name='OutputTag',
            tag_value=100,
            data_type=1,
            response_cb=self.mock_callback
        )
        self.assertEqual(cmd.type, ConnectionCommandType.WRITE)
        self.assertEqual(cmd.tag_name, 'OutputTag')
        self.assertEqual(cmd.tag_value, 100)
        self.assertEqual(cmd.data_type, 1)

    def test_callback_functionality(self):
        """Test that callback can be invoked."""
        cmd = ConnectionCommand(
            type=ConnectionCommandType.READ,
            tag_name='TestTag',
            tag_value=0,
            data_type=0,
            response_cb=self.mock_callback
        )
        mock_response = Mock(spec=Response)
        cmd.response_cb(mock_response)
        self.mock_callback.assert_called_once_with(mock_response)


class TestPlcConnectionManager(unittest.TestCase):
    """Test cases for PlcConnectionManager static class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the static class state before each test
        PlcConnectionManager.connection_parameters = ConnectionParameters()
        PlcConnectionManager._connected = False
        PlcConnectionManager._commands = []
        PlcConnectionManager._subscribers = []
        PlcConnectionManager._watch_table = {}
        PlcConnectionManager._timer_service.clear_all_tasks()

    def tearDown(self):
        """Clean up after tests."""
        PlcConnectionManager._connected = False
        PlcConnectionManager._commands = []
        PlcConnectionManager._subscribers = []
        PlcConnectionManager._watch_table = {}
        PlcConnectionManager._timer_service.clear_all_tasks()

    def test_cannot_instantiate(self):
        """Test that PlcConnectionManager cannot be instantiated."""
        with self.assertRaises(ValueError) as context:
            PlcConnectionManager()
        self.assertIn('static class', str(context.exception).lower())

    def test_default_connection_parameters(self):
        """Test that default connection parameters are set."""
        self.assertIsInstance(PlcConnectionManager.connection_parameters, ConnectionParameters)
        self.assertEqual(str(PlcConnectionManager.connection_parameters.ip_address), '192.168.1.2')

    def test_initial_connection_state(self):
        """Test that initial connection state is disconnected."""
        self.assertFalse(PlcConnectionManager._connected)

    def test_subscribe_to_ticks(self):
        """Test subscribing to tick events."""
        mock_callback = Mock()
        PlcConnectionManager.subscribe_to_ticks(mock_callback)
        self.assertIn(mock_callback, PlcConnectionManager._subscribers)

    def test_subscribe_invalid_callback(self):
        """Test subscribing with invalid callback raises error."""
        with self.assertRaises(ValueError) as context:
            PlcConnectionManager.subscribe_to_ticks('not_a_function')  # type: ignore
        self.assertIn('callable', str(context.exception).lower())

    def test_unsubscribe_from_ticks(self):
        """Test unsubscribing from tick events."""
        mock_callback = Mock()
        PlcConnectionManager.subscribe_to_ticks(mock_callback)
        self.assertIn(mock_callback, PlcConnectionManager._subscribers)

        PlcConnectionManager.unsubscribe_from_ticks(mock_callback)
        self.assertNotIn(mock_callback, PlcConnectionManager._subscribers)

    def test_unsubscribe_nonexistent_callback(self):
        """Test unsubscribing a callback that wasn't subscribed."""
        mock_callback = Mock()
        # Should not raise an error
        PlcConnectionManager.unsubscribe_from_ticks(mock_callback)
        self.assertNotIn(mock_callback, PlcConnectionManager._subscribers)

    @patch('controlrox.services.plc.connection.PLC')
    def test_strobe_plc_success(self, mock_plc_class):
        """Test successful PLC strobe."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.GetPLCTime.return_value.Status = 'Success'

        result = PlcConnectionManager._strobe_plc()
        self.assertTrue(result)
        mock_plc.GetPLCTime.assert_called_once()

    @patch('controlrox.services.plc.connection.PLC')
    def test_strobe_plc_failure(self, mock_plc_class):
        """Test failed PLC strobe."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.GetPLCTime.return_value.Status = 'Failed'

        result = PlcConnectionManager._strobe_plc()
        self.assertFalse(result)

    @patch('controlrox.services.plc.connection.PLC')
    def test_connect_success(self, mock_plc_class):
        """Test successful connection to PLC."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.GetPLCTime.return_value.Status = 'Success'

        PlcConnectionManager.connect()
        self.assertTrue(PlcConnectionManager._connected)

    @patch('controlrox.services.plc.connection.PLC')
    def test_connect_already_connected(self, mock_plc_class):
        """Test connecting when already connected."""
        PlcConnectionManager._connected = True
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        PlcConnectionManager.connect()
        # Should not call PLC methods if already connected
        mock_plc.GetPLCTime.assert_not_called()

    def test_disconnect(self):
        """Test disconnecting from PLC."""
        PlcConnectionManager._connected = True
        PlcConnectionManager.disconnect()
        self.assertFalse(PlcConnectionManager._connected)

    def test_disconnect_when_not_connected(self):
        """Test disconnecting when not connected."""
        PlcConnectionManager._connected = False
        # Should not raise an error
        PlcConnectionManager.disconnect()
        self.assertFalse(PlcConnectionManager._connected)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_commands_read(self, mock_plc_class):
        """Test running READ commands."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_response = Response(tag_name='TestTag', value=42, status='Success')
        mock_plc.Read.return_value = mock_response

        mock_callback = Mock()
        PlcConnectionManager._connected = True
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.READ,
                tag_name='TestTag',
                tag_value=0,
                data_type=0,
                response_cb=mock_callback
            )
        ]

        PlcConnectionManager._run_commands()
        mock_callback.assert_called_once_with(mock_response)
        self.assertEqual(len(PlcConnectionManager._commands), 0)  # Commands should be cleared

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_commands_write(self, mock_plc_class):
        """Test running WRITE commands."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_response = Response(tag_name='OutputTag', value=100, status='Success')
        mock_plc.Write.return_value = mock_response

        mock_callback = Mock()
        PlcConnectionManager._connected = True
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.WRITE,
                tag_name='OutputTag',
                tag_value=100,
                data_type=1,
                response_cb=mock_callback
            )
        ]

        PlcConnectionManager._run_commands()
        mock_callback.assert_called_once_with(mock_response)
        mock_plc.Write.assert_called_once_with('OutputTag', 100, datatype=1)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_commands_write_string_value(self, mock_plc_class):
        """Test running WRITE command with string value."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_response = Response(tag_name='StringTag', value='test', status='Success')
        mock_plc.Write.return_value = mock_response

        mock_callback = Mock()
        PlcConnectionManager._connected = True
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.WRITE,
                tag_name='StringTag',
                tag_value='test_string',  # type: ignore
                data_type=2,
                response_cb=mock_callback
            )
        ]

        PlcConnectionManager._run_commands()
        # Should keep as string if conversion to int fails
        mock_plc.Write.assert_called_once_with('StringTag', 'test_string', datatype=2)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_commands_read_error_handling(self, mock_plc_class):
        """Test error handling during READ command."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.Read.side_effect = KeyError('Tag not found')

        mock_callback = Mock()
        PlcConnectionManager._connected = True
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.READ,
                tag_name='InvalidTag',
                tag_value=0,
                data_type=0,
                response_cb=mock_callback
            )
        ]

        PlcConnectionManager._run_commands()
        # Should call callback with error response
        self.assertTrue(mock_callback.called)
        error_response = mock_callback.call_args[0][0]
        self.assertEqual(error_response.TagName, 'InvalidTag')
        self.assertIsNone(error_response.Value)
        self.assertEqual(error_response.Status, 'Error')

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_commands_write_error_handling(self, mock_plc_class):
        """Test error handling during WRITE command."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.Write.side_effect = KeyError('Tag not found')

        mock_callback = Mock()
        PlcConnectionManager._connected = True
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.WRITE,
                tag_name='InvalidTag',
                tag_value=100,
                data_type=1,
                response_cb=mock_callback
            )
        ]

        PlcConnectionManager._run_commands()
        # Should call callback with error response
        self.assertTrue(mock_callback.called)
        error_response = mock_callback.call_args[0][0]
        self.assertEqual(error_response.TagName, 'InvalidTag')
        self.assertIsNone(error_response.Value)
        self.assertEqual(error_response.Status, 'Error')

    def test_run_commands_when_disconnected(self):
        """Test that commands don't run when disconnected."""
        mock_callback = Mock()
        PlcConnectionManager._connected = False
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.READ,
                tag_name='TestTag',
                tag_value=0,
                data_type=0,
                response_cb=mock_callback
            )
        ]

        PlcConnectionManager._run_commands()
        mock_callback.assert_not_called()

    @patch('controlrox.services.plc.connection.PLC')
    def test_connection_loop_success(self, mock_plc_class):
        """Test successful connection loop."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.GetPLCTime.return_value.Status = 'Success'

        mock_subscriber = Mock()
        PlcConnectionManager.subscribe_to_ticks(mock_subscriber)

        PlcConnectionManager._connection_loop()
        self.assertTrue(PlcConnectionManager._connected)
        mock_subscriber.assert_called_once()

    @patch('controlrox.services.plc.connection.PLC')
    def test_connection_loop_failure(self, mock_plc_class):
        """Test connection loop when PLC strobe fails."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.GetPLCTime.return_value.Status = 'Failed'

        PlcConnectionManager._connection_loop()
        self.assertFalse(PlcConnectionManager._connected)

    @patch('controlrox.services.plc.connection.PLC')
    def test_connection_loop_exception_handling(self, mock_plc_class):
        """Test connection loop handles exceptions."""
        mock_plc_class.side_effect = Exception('Connection error')

        PlcConnectionManager._connection_loop()
        self.assertFalse(PlcConnectionManager._connected)

    @patch('controlrox.services.plc.connection.PLC')
    def test_multiple_subscribers(self, mock_plc_class):
        """Test multiple subscribers are called during connection loop."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.GetPLCTime.return_value.Status = 'Success'

        mock_subscriber1 = Mock()
        mock_subscriber2 = Mock()
        mock_subscriber3 = Mock()

        PlcConnectionManager.subscribe_to_ticks(mock_subscriber1)
        PlcConnectionManager.subscribe_to_ticks(mock_subscriber2)
        PlcConnectionManager.subscribe_to_ticks(mock_subscriber3)

        PlcConnectionManager._connection_loop()

        mock_subscriber1.assert_called_once()
        mock_subscriber2.assert_called_once()
        mock_subscriber3.assert_called_once()

    @patch('controlrox.services.plc.connection.PLC')
    def test_mixed_read_write_commands(self, mock_plc_class):
        """Test running mixed READ and WRITE commands."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        read_response = Response(tag_name='InputTag', value=42, status='Success')
        write_response = Response(tag_name='OutputTag', value=100, status='Success')
        mock_plc.Read.return_value = read_response
        mock_plc.Write.return_value = write_response

        read_callback = Mock()
        write_callback = Mock()

        PlcConnectionManager._connected = True
        PlcConnectionManager._commands = [
            ConnectionCommand(
                type=ConnectionCommandType.READ,
                tag_name='InputTag',
                tag_value=0,
                data_type=0,
                response_cb=read_callback
            ),
            ConnectionCommand(
                type=ConnectionCommandType.WRITE,
                tag_name='OutputTag',
                tag_value=100,
                data_type=1,
                response_cb=write_callback
            )
        ]

        PlcConnectionManager._run_commands()

        read_callback.assert_called_once_with(read_response)
        write_callback.assert_called_once_with(write_response)
        mock_plc.Read.assert_called_once()
        mock_plc.Write.assert_called_once()

    def test_schedule_when_connected(self):
        """Test that scheduling works when connected."""
        PlcConnectionManager._connected = True
        PlcConnectionManager._schedule()
        # Verify a task was scheduled (timer service should have tasks)
        # Note: This depends on TimerService implementation

    def test_schedule_when_disconnected(self):
        """Test that scheduling doesn't happen when disconnected."""
        PlcConnectionManager._connected = False
        initial_tasks = len(PlcConnectionManager._timer_service._tasks)
        PlcConnectionManager._schedule()
        final_tasks = len(PlcConnectionManager._timer_service._tasks)
        self.assertEqual(initial_tasks, final_tasks)

    def test_add_watch_tag_new(self):
        """Test adding a new tag to watch table."""
        PlcConnectionManager.add_watch_tag('TestTag', data_type=5)

        self.assertIn('TestTag', PlcConnectionManager._watch_table)
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.tag_name, 'TestTag')
        self.assertEqual(entry.data_type, 5)
        self.assertIsNone(entry.last_value)

    def test_add_watch_tag_with_callback(self):
        """Test adding a tag with a callback."""
        mock_callback = Mock()
        PlcConnectionManager.add_watch_tag('TestTag', callback=mock_callback)

        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertIn(mock_callback, entry.callbacks)

    def test_add_watch_tag_duplicate(self):
        """Test adding a tag that's already in watch table."""
        PlcConnectionManager.add_watch_tag('TestTag', data_type=5)
        PlcConnectionManager.add_watch_tag('TestTag', data_type=10)  # Different data type

        # Should keep original entry
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.data_type, 5)  # Original data type preserved

    def test_add_watch_tag_duplicate_with_new_callback(self):
        """Test adding callback to existing watched tag."""
        callback1 = Mock()
        callback2 = Mock()

        PlcConnectionManager.add_watch_tag('TestTag', callback=callback1)
        PlcConnectionManager.add_watch_tag('TestTag', callback=callback2)

        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertIn(callback1, entry.callbacks)
        self.assertIn(callback2, entry.callbacks)

    def test_remove_watch_tag_existing(self):
        """Test removing an existing watched tag."""
        PlcConnectionManager.add_watch_tag('TestTag')
        result = PlcConnectionManager.remove_watch_tag('TestTag')

        self.assertTrue(result)
        self.assertNotIn('TestTag', PlcConnectionManager._watch_table)

    def test_remove_watch_tag_nonexistent(self):
        """Test removing a tag that's not in watch table."""
        result = PlcConnectionManager.remove_watch_tag('NonexistentTag')
        self.assertFalse(result)

    def test_clear_watch_table(self):
        """Test clearing all tags from watch table."""
        PlcConnectionManager.add_watch_tag('Tag1')
        PlcConnectionManager.add_watch_tag('Tag2')
        PlcConnectionManager.add_watch_tag('Tag3')

        self.assertEqual(len(PlcConnectionManager._watch_table), 3)

        PlcConnectionManager.clear_watch_table()
        self.assertEqual(len(PlcConnectionManager._watch_table), 0)

    def test_get_watch_table(self):
        """Test getting a copy of the watch table."""
        PlcConnectionManager.add_watch_tag('Tag1')
        PlcConnectionManager.add_watch_tag('Tag2')

        watch_table = PlcConnectionManager.get_watch_table()

        self.assertEqual(len(watch_table), 2)
        self.assertIn('Tag1', watch_table)
        self.assertIn('Tag2', watch_table)

        # Verify it's a copy, not the original
        watch_table['Tag3'] = WatchTableEntry(tag_name='Tag3')
        self.assertNotIn('Tag3', PlcConnectionManager._watch_table)

    def test_get_watched_tag_value_exists(self):
        """Test getting value of watched tag."""
        PlcConnectionManager.add_watch_tag('TestTag')
        PlcConnectionManager._watch_table['TestTag'].last_value = 42

        value = PlcConnectionManager.get_watched_tag_value('TestTag')
        self.assertEqual(value, 42)

    def test_get_watched_tag_value_not_watched(self):
        """Test getting value of tag not in watch table."""
        value = PlcConnectionManager.get_watched_tag_value('NonexistentTag')
        self.assertIsNone(value)

    def test_get_watched_tag_value_no_value_yet(self):
        """Test getting value of watched tag before any reads."""
        PlcConnectionManager.add_watch_tag('TestTag')
        value = PlcConnectionManager.get_watched_tag_value('TestTag')
        self.assertIsNone(value)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_watch_table_reads_success(self, mock_plc_class):
        """Test automatic reading of watched tags."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=42, status='Success')
        mock_plc.Read.return_value = mock_response

        PlcConnectionManager.add_watch_tag('TestTag', data_type=5)
        PlcConnectionManager._connected = True

        PlcConnectionManager._run_commands()

        # Verify the tag was read
        mock_plc.Read.assert_called_with('TestTag', datatype=5)

        # Verify the entry was updated
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.last_value, 42)
        self.assertIsNotNone(entry.last_update)
        self.assertEqual(entry.error_count, 0)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_watch_table_reads_with_callback(self, mock_plc_class):
        """Test that callbacks are invoked when watched tags are read."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=100, status='Success')
        mock_plc.Read.return_value = mock_response

        mock_callback = Mock()
        PlcConnectionManager.add_watch_tag('TestTag', callback=mock_callback)
        PlcConnectionManager._connected = True

        PlcConnectionManager._run_commands()

        # Verify callback was called with response
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args[0][0]
        self.assertEqual(call_args.Value, 100)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_watch_table_reads_failure(self, mock_plc_class):
        """Test error handling when watched tag read fails."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=None, status='Failed')
        mock_plc.Read.return_value = mock_response

        PlcConnectionManager.add_watch_tag('TestTag')
        PlcConnectionManager._connected = True

        PlcConnectionManager._run_commands()

        # Verify error count was incremented
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.error_count, 1)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_watch_table_reads_exception(self, mock_plc_class):
        """Test error handling when exception occurs during watch read."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc
        mock_plc.Read.side_effect = Exception('Read error')

        PlcConnectionManager.add_watch_tag('TestTag')
        PlcConnectionManager._connected = True

        PlcConnectionManager._run_commands()

        # Verify error count was incremented
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.error_count, 1)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_watch_table_reads_list_response(self, mock_plc_class):
        """Test handling of list response from PLC read."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        # Some pylogix operations return lists
        mock_response = Response(tag_name='TestTag', value=99, status='Success')
        mock_plc.Read.return_value = [mock_response]

        PlcConnectionManager.add_watch_tag('TestTag')
        PlcConnectionManager._connected = True

        PlcConnectionManager._run_commands()

        # Verify the first response was used
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.last_value, 99)

    @patch('controlrox.services.plc.connection.PLC')
    def test_run_watch_table_reads_multiple_tags(self, mock_plc_class):
        """Test automatic reading of multiple watched tags."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        def mock_read(tag_name, datatype):
            if tag_name == 'Tag1':
                return Response(tag_name='Tag1', value=10, status='Success')
            elif tag_name == 'Tag2':
                return Response(tag_name='Tag2', value=20, status='Success')
            return Response(tag_name=tag_name, value=None, status='Error')

        mock_plc.Read.side_effect = mock_read

        PlcConnectionManager.add_watch_tag('Tag1')
        PlcConnectionManager.add_watch_tag('Tag2')
        PlcConnectionManager._connected = True

        PlcConnectionManager._run_commands()

        # Verify both tags were read
        self.assertEqual(PlcConnectionManager._watch_table['Tag1'].last_value, 10)
        self.assertEqual(PlcConnectionManager._watch_table['Tag2'].last_value, 20)

    @patch('controlrox.services.plc.connection.PLC')
    def test_write_watch_tag_new_tag(self, mock_plc_class):
        """Test writing to a tag not in watch table."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='NewTag', value=50, status='Success')
        mock_plc.Write.return_value = mock_response

        PlcConnectionManager._connected = True
        PlcConnectionManager.write_watch_tag('NewTag', 50)

        # Should add write command to buffer
        PlcConnectionManager._run_commands()

        mock_plc.Write.assert_called_once_with('NewTag', 50, datatype=0)

    @patch('controlrox.services.plc.connection.PLC')
    def test_write_watch_tag_watched_tag(self, mock_plc_class):
        """Test writing to a tag in watch table."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=75, status='Success')
        mock_plc.Write.return_value = mock_response

        PlcConnectionManager.add_watch_tag('TestTag', data_type=5)
        PlcConnectionManager._connected = True
        PlcConnectionManager.write_watch_tag('TestTag', 75)

        PlcConnectionManager._run_commands()

        # Should use data type from watch table
        mock_plc.Write.assert_called_once_with('TestTag', 75, datatype=5)

        # Should update watch table entry
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.last_value, 75)

    @patch('controlrox.services.plc.connection.PLC')
    def test_write_watch_tag_with_callback(self, mock_plc_class):
        """Test writing with custom callback."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=30, status='Success')
        mock_plc.Write.return_value = mock_response

        mock_callback = Mock()
        PlcConnectionManager._connected = True
        PlcConnectionManager.write_watch_tag('TestTag', 30, callback=mock_callback)

        PlcConnectionManager._run_commands()

        # Custom callback should be called
        mock_callback.assert_called_once()

    @patch('controlrox.services.plc.connection.PLC')
    def test_write_watch_tag_failure(self, mock_plc_class):
        """Test write failure handling."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=None, status='Failed')
        mock_plc.Write.return_value = mock_response

        PlcConnectionManager.add_watch_tag('TestTag')
        PlcConnectionManager._connected = True
        PlcConnectionManager.write_watch_tag('TestTag', 100)

        PlcConnectionManager._run_commands()

        # Watch table should not be updated on failure
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertIsNone(entry.last_value)  # Should still be None

    @patch('controlrox.services.plc.connection.PLC')
    def test_write_watch_tag_list_response(self, mock_plc_class):
        """Test handling list response from write operation."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=88, status='Success')
        mock_plc.Write.return_value = [mock_response]

        PlcConnectionManager.add_watch_tag('TestTag')
        PlcConnectionManager._connected = True
        PlcConnectionManager.write_watch_tag('TestTag', 88)

        PlcConnectionManager._run_commands()

        # Should handle list response and update watch table
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.last_value, 88)

    @patch('controlrox.services.plc.connection.PLC')
    def test_watch_callback_exception_handling(self, mock_plc_class):
        """Test that callback exceptions don't break watch reads."""
        mock_plc = MagicMock()
        mock_plc_class.return_value.__enter__.return_value = mock_plc

        mock_response = Response(tag_name='TestTag', value=123, status='Success')
        mock_plc.Read.return_value = mock_response

        # Callback that raises exception
        def bad_callback(response):
            raise RuntimeError('Callback error')

        PlcConnectionManager.add_watch_tag('TestTag', callback=bad_callback)
        PlcConnectionManager._connected = True

        # Should not raise exception
        PlcConnectionManager._run_commands()

        # Entry should still be updated despite callback error
        entry = PlcConnectionManager._watch_table['TestTag']
        self.assertEqual(entry.last_value, 123)


if __name__ == '__main__':
    unittest.main()
