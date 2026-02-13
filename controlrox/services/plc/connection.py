"""PLC IO Application Manager.
"""
from dataclasses import dataclass
from enum import Enum
from pyrox.services.logging import log
from typing import Callable
from pylogix.lgx_response import Response
from pylogix import PLC
from pyrox.services import TimerService
from pyrox.models.network import Ipv4Address


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


class PlcConnectionManager:
    """Static Connection Manager for PLC IO Applications.
    """
    connection_parameters: ConnectionParameters = ConnectionParameters()
    _connected: bool = False
    _commands: list[ConnectionCommand] = []
    _subscribers: list[Callable] = []
    _timer_service = TimerService()

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
    def _schedule(cls) -> None:
        """Schedule the next connection loop iteration.
        """
        if not cls._connected:
            return

        cls._timer_service.schedule_task(cls._connection_loop, cls.connection_parameters.rpi)

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
