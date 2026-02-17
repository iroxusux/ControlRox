"""PLC IO Application Manager.
"""
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any

from pylogix.lgx_response import Response
from pylogix import PLC
from pyrox.services import log, EnvManager, TimerService
from pyrox.models.network import Ipv4Address

from controlrox.interfaces import ControlRoxEnvironmentKeys


@dataclass
class ConnectionParameters:
    """Connection Parameters for a PLC
    """
    ip_address: Ipv4Address = Ipv4Address('192.168.1.2')
    slot: int = 0
    rpi: int = 250


class ConnectionCommandType(Enum):
    NA = 0
    READ = 1
    WRITE = 2


@dataclass
class ConnectionCommand:
    """Connection Command for a PLC
    """
    type: ConnectionCommandType
    tag_name: str
    tag_value: int
    data_type: int
    response_cb: Callable[[Response | list[Response]], None]


@dataclass
class WatchTableEntry:
    """Watch Table Entry for monitoring PLC tags.
    """
    tag_name: str
    data_type: int = 0
    last_value: Any = None
    last_update: datetime | None = None
    error_count: int = 0
    callbacks: list[Callable[[Response | list[Response]], None]] = field(default_factory=list)


class PlcConnectionManager:
    """Static Connection Manager for PLC IO Applications.
    """
    connection_parameters: ConnectionParameters = ConnectionParameters()
    _connected: bool = False
    _commands: list[ConnectionCommand] = []
    _subscribers: list[Callable] = []
    _timer_service = TimerService()
    _watch_table: dict[str, WatchTableEntry] = {}

    def __init__(self) -> None:
        raise ValueError('PlcConnectionManager is a static class and cannot be instantiated.')

    @classmethod
    def _connection_loop(cls) -> None:
        """Main connection loop for the PLC.
        """
        try:
            if not cls._strobe_plc():
                cls._connected = False
                log(cls).warning('Failed to strobe PLC at %s', cls.connection_parameters.ip_address)
                return
            if not cls._connected:
                log(cls).info('Connected to PLC at %s', cls.connection_parameters.ip_address)
                cls._connected = True
        except Exception:
            log(cls).error('Error connecting to PLC at %s', cls.connection_parameters.ip_address)
            cls._connected = False
            return

        [callback() for callback in cls._subscribers]
        cls._run_commands()
        cls._schedule()

    @classmethod
    def _strobe_plc(cls) -> bool:
        with PLC(
            ip_address=str(cls.connection_parameters.ip_address),
            slot=cls.connection_parameters.slot
        ) as comm:
            return comm.GetPLCTime().Status == 'Success'

    @classmethod
    def _run_commands(cls):
        if not cls._connected:
            return

        with PLC(
            ip_address=str(cls.connection_parameters.ip_address),
            slot=cls.connection_parameters.slot
        ) as comm:
            cls._run_commands_read(comm)
            cls._run_commands_write(comm)
            cls._run_watch_table_reads(comm)
        cls._commands.clear()

    @classmethod
    def _run_commands_read(
        cls,
        comm: PLC
    ) -> None:
        """Run read commands from the command buffer.
        """
        read_commands = [cmd for cmd in cls._commands if cmd.type == ConnectionCommandType.READ]
        for command in read_commands:
            try:
                response = comm.Read(
                    command.tag_name,
                    datatype=command.data_type
                )
                command.response_cb(response)
            except KeyError:
                command.response_cb(
                    Response(
                        tag_name=command.tag_name,
                        value=None,
                        status='Error'
                    )
                )

    @classmethod
    def _run_commands_write(cls, comm: PLC):
        """Run write commands from the command buffer.
        """
        write_commands = [cmd for cmd in cls._commands if cmd.type == ConnectionCommandType.WRITE]
        for command in write_commands:
            try:
                try:
                    tag_value = int(command.tag_value)
                except (ValueError, TypeError):
                    tag_value = command.tag_value  # keep as string if conversion fails
                response = comm.Write(
                    command.tag_name,
                    tag_value,
                    datatype=command.data_type
                )
                command.response_cb(response)
            except KeyError:
                command.response_cb(
                    Response(
                        tag_name=command.tag_name,
                        value=None,
                        status='Error')
                )

    @classmethod
    def _run_watch_table_reads(cls, comm: PLC) -> None:
        """Automatically read all tags in the watch table.
        """
        for tag_name, entry in cls._watch_table.items():
            try:
                response = comm.Read(tag_name, datatype=entry.data_type)

                # Handle both single Response and list[Response]
                if isinstance(response, list):
                    response = response[0] if response else Response(tag_name, None, 'Error')

                if response.Status == 'Success':
                    entry.last_value = response.Value
                    entry.last_update = datetime.now()
                    entry.error_count = 0
                else:
                    entry.error_count += 1
                    log(cls).warning('Failed to read watched tag %s: %s', tag_name, response.Status)

                # Call any registered callbacks for this tag
                for callback in entry.callbacks:
                    try:
                        callback(response)
                    except Exception as e:
                        log(cls).error('Error in watch callback for %s: %s', tag_name, e)
            except Exception as e:
                entry.error_count += 1
                log(cls).error('Error reading watched tag %s: %s', tag_name, e)

    @classmethod
    def _schedule(cls) -> None:
        """Schedule the next connection loop iteration.
        """
        if not cls._connected:
            return

        # Convert RPI from milliseconds to seconds for timer service
        cls._timer_service.schedule_task(cls._connection_loop, cls.connection_parameters.rpi / 1000.0)

    @classmethod
    def connect(cls) -> None:
        """Connect to the PLC.
        """
        if cls._connected:
            return
        if not cls.connection_parameters:
            log(cls).warning('No connection parameters provided, using default values')
            cls.connection_parameters = ConnectionParameters()
        log(cls).info('Connecting to PLC at %s...', cls.connection_parameters.ip_address)
        cls.save_connection_parameters()
        cls._connection_loop()

    @classmethod
    def disconnect(cls) -> None:
        """Disconnect from the PLC.
        """
        if not cls._connected:
            return
        log(cls).info('Disconnecting from PLC at %s...', cls.connection_parameters.ip_address)
        cls._connected = False
        cls._timer_service.clear_all_tasks()

    @classmethod
    def subscribe_to_ticks(cls, callback: Callable) -> None:
        """Subscribe to tick events.

        Args:
            callback: Function to call on each tick
        """
        if not callable(callback):
            raise ValueError('Callback must be callable')
        cls._subscribers.append(callback)

    @classmethod
    def unsubscribe_from_ticks(cls, callback: Callable) -> None:
        """Unsubscribe from tick events.

        Args:
            callback: Function to remove from subscribers
        """
        if callback in cls._subscribers:
            cls._subscribers.remove(callback)

    @classmethod
    def read_plc_tag_table(
        cls,
        all_tags: bool = True
    ) -> Response:
        """Read the entire PLC tag table.

        Args:
            all_tags: Whether to read all tags or just top-level tags (not including program tags)

        Returns:
            Response: A response object containing the tag table data or an error status
        """
        with PLC(
            ip_address=str(cls.connection_parameters.ip_address),
            slot=cls.connection_parameters.slot
        ) as comm:
            return comm.GetTagList(allTags=all_tags)

    @classmethod
    def add_watch_tag(
        cls,
        tag_name: str,
        data_type: int = 0,
        callback: Callable[[Response | list[Response]], None] | None = None
    ) -> None:
        """Add a tag to the watch table for automatic monitoring.

        Args:
            tag_name: Name of the PLC tag to watch
            data_type: PyLogix data type code (0 for auto-detect)
            callback: Optional callback function to call when tag value updates
        """
        if tag_name in cls._watch_table:
            log(cls).debug('Tag %s already in watch table', tag_name)
            if callback and callback not in cls._watch_table[tag_name].callbacks:
                cls._watch_table[tag_name].callbacks.append(callback)
        else:
            callbacks = [callback] if callback else []
            cls._watch_table[tag_name] = WatchTableEntry(
                tag_name=tag_name,
                data_type=data_type,
                callbacks=callbacks
            )
            log(cls).info('Added tag %s to watch table', tag_name)

    @classmethod
    def remove_watch_tag(cls, tag_name: str) -> bool:
        """Remove a tag from the watch table.

        Args:
            tag_name: Name of the PLC tag to stop watching

        Returns:
            bool: True if tag was removed, False if not found
        """
        if tag_name in cls._watch_table:
            del cls._watch_table[tag_name]
            log(cls).info('Removed tag %s from watch table', tag_name)
            return True
        return False

    @classmethod
    def clear_watch_table(cls) -> None:
        """Clear all tags from the watch table."""
        cls._watch_table.clear()
        log(cls).info('Cleared watch table')

    @classmethod
    def get_watch_table(cls) -> dict[str, WatchTableEntry]:
        """Get the current watch table.

        Returns:
            dict: Dictionary of tag names to WatchTableEntry objects
        """
        return cls._watch_table.copy()

    @classmethod
    def get_watched_tag_value(cls, tag_name: str) -> Any | None:
        """Get the last known value of a watched tag.

        Args:
            tag_name: Name of the tag

        Returns:
            The last known value or None if tag not watched or no value yet
        """
        entry = cls._watch_table.get(tag_name)
        return entry.last_value if entry else None

    @classmethod
    def write_watch_tag(
        cls,
        tag_name: str,
        value: Any,
        callback: Callable[[Response | list[Response]], None] | None = None
    ) -> None:
        """Write a value to a watched tag (or any tag).

        This method is designed for GUI integration to allow editing tag values.
        If the tag is in the watch table, it uses the stored data type.

        Args:
            tag_name: Name of the PLC tag to write
            value: Value to write to the tag
            callback: Optional callback to handle the write response
        """
        # Get data type from watch table if available
        data_type = 0
        if tag_name in cls._watch_table:
            data_type = cls._watch_table[tag_name].data_type

        # Create default callback if none provided
        def default_callback(response: Response | list[Response]) -> None:
            # Handle both single Response and list[Response]
            if isinstance(response, list):
                response = response[0] if response else Response(tag_name, None, 'Error')

            if response.Status == 'Success':
                log(cls).debug('Successfully wrote %s to tag %s', value, tag_name)
                # Update watch table entry if tag is watched
                if tag_name in cls._watch_table:
                    cls._watch_table[tag_name].last_value = value
                    cls._watch_table[tag_name].last_update = datetime.now()
            else:
                log(cls).warning('Failed to write to tag %s: %s', tag_name, response.Status)

        response_cb = callback if callback else default_callback

        # Add write command to command buffer
        cls._commands.append(
            ConnectionCommand(
                type=ConnectionCommandType.WRITE,
                tag_name=tag_name,
                tag_value=value,
                data_type=data_type,
                response_cb=response_cb
            )
        )

    @classmethod
    def save_connection_parameters(cls) -> None:
        """Save connection parameters and reconnect.

        Args:
            params: ConnectionParameters object containing new settings
        """
        EnvManager.set(
            ControlRoxEnvironmentKeys.plc.PLC_DEFAULT_IP,
            str(cls.connection_parameters.ip_address)
        )
        EnvManager.set(
            ControlRoxEnvironmentKeys.plc.PLC_DEFAULT_SLOT,
            str(cls.connection_parameters.slot)
        )
        EnvManager.set(
            ControlRoxEnvironmentKeys.plc.PLC_DEFAULT_RPI,
            str(cls.connection_parameters.rpi)
        )
        log(cls).info('Saved new connection parameters: %s', cls.connection_parameters)

    @classmethod
    def load_connection_parameters(cls) -> None:
        """Load connection parameters from environment variables.
        """
        ip_str = EnvManager.get(
            ControlRoxEnvironmentKeys.plc.PLC_DEFAULT_IP,
            cast_type=str,
            default=str(cls.connection_parameters.ip_address)
        )
        slot = EnvManager.get(
            ControlRoxEnvironmentKeys.plc.PLC_DEFAULT_SLOT,
            cast_type=int,
            default=cls.connection_parameters.slot
        )
        rpi = EnvManager.get(
            ControlRoxEnvironmentKeys.plc.PLC_DEFAULT_RPI,
            cast_type=int,
            default=cls.connection_parameters.rpi
        )
        cls.connection_parameters = ConnectionParameters(
            ip_address=Ipv4Address(ip_str),
            slot=slot,
            rpi=rpi
        )
