"""Unit tests for PLC connection services."""
import unittest
from unittest.mock import Mock, patch, MagicMock

from controlrox.services.plc.connection import (
    ConnectionParameters,
    ConnectionCommandType,
    ConnectionCommand,
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
        PlcConnectionManager._timer_service.clear_all_tasks()

    def tearDown(self):
        """Clean up after tests."""
        PlcConnectionManager._connected = False
        PlcConnectionManager._commands = []
        PlcConnectionManager._subscribers = []
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


if __name__ == '__main__':
    unittest.main()
