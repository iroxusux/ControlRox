"""
Example field device implementations.
"""
from typing import Any, Dict
from ..simulation import Device, DeviceState, register_device


@register_device("Motor")
class Motor(Device):
    """
    A simple motor device with run/stop control.

    Properties:
        rpm: Current motor speed in RPM
        max_rpm: Maximum motor speed
        acceleration: RPM increase per second
    """

    def __post_init__(self):
        """Initialize motor-specific defaults."""
        if "rpm" not in self.properties:
            self.properties["rpm"] = 0.0
        if "max_rpm" not in self.properties:
            self.properties["max_rpm"] = 1800.0
        if "acceleration" not in self.properties:
            self.properties["acceleration"] = 100.0  # RPM per second

    def update(self, delta_time: float) -> None:
        """Update motor speed based on run command."""
        run_tag = self.get_tag(f"{self.name}_Run")
        speed_tag = self.get_tag(f"{self.name}_Speed")

        if not run_tag or not speed_tag:
            return

        current_rpm = self.properties["rpm"]
        target_rpm = self.properties["max_rpm"] if run_tag.value else 0.0
        acceleration = self.properties["acceleration"]

        # Ramp speed up or down
        if current_rpm < target_rpm:
            current_rpm = min(current_rpm + acceleration * delta_time, target_rpm)
            self.state = DeviceState.RUNNING
        elif current_rpm > target_rpm:
            current_rpm = max(current_rpm - acceleration * delta_time, target_rpm)
            self.state = DeviceState.RUNNING if current_rpm > 0 else DeviceState.STOPPED
        else:
            self.state = DeviceState.RUNNING if current_rpm > 0 else DeviceState.IDLE

        self.properties["rpm"] = current_rpm
        speed_tag.update_value(current_rpm)

    def read_inputs(self) -> Dict[str, Any]:
        """Read run command from PLC."""
        run_tag = self.get_tag(f"{self.name}_Run")
        if run_tag:
            return {run_tag.name: run_tag.value}
        return {}

    def write_outputs(self) -> Dict[str, Any]:
        """Write motor speed to PLC."""
        speed_tag = self.get_tag(f"{self.name}_Speed")
        if speed_tag:
            return {speed_tag.name: self.properties["rpm"]}
        return {}


@register_device("Sensor")
class Sensor(Device):
    """
    A generic sensor device that provides a reading.

    Properties:
        value: Current sensor reading
        min_value: Minimum possible value
        max_value: Maximum possible value
        noise: Amount of random noise to add
    """

    def __post_init__(self):
        """Initialize sensor-specific defaults."""
        import random
        self._random = random.Random()

        if "value" not in self.properties:
            self.properties["value"] = 0.0
        if "min_value" not in self.properties:
            self.properties["min_value"] = 0.0
        if "max_value" not in self.properties:
            self.properties["max_value"] = 100.0
        if "noise" not in self.properties:
            self.properties["noise"] = 0.0

    def update(self, delta_time: float) -> None:
        """Update sensor reading with optional noise."""
        value_tag = self.get_tag(f"{self.name}_Value")

        if not value_tag:
            return

        # Add noise if configured
        noise = self.properties["noise"]
        if noise > 0:
            base_value = self.properties["value"]
            noise_offset = self._random.uniform(-noise, noise)
            noisy_value = max(
                self.properties["min_value"],
                min(self.properties["max_value"], base_value + noise_offset)
            )
            value_tag.update_value(noisy_value)
        else:
            value_tag.update_value(self.properties["value"])

        self.state = DeviceState.RUNNING

    def read_inputs(self) -> Dict[str, Any]:
        """Sensors typically don't read inputs."""
        return {}

    def write_outputs(self) -> Dict[str, Any]:
        """Write sensor value to PLC."""
        value_tag = self.get_tag(f"{self.name}_Value")
        if value_tag:
            return {value_tag.name: value_tag.value}
        return {}

    def set_value(self, value: float) -> None:
        """Set the sensor's base value."""
        self.properties["value"] = max(
            self.properties["min_value"],
            min(self.properties["max_value"], value)
        )


@register_device("Valve")
class Valve(Device):
    """
    A valve device with open/close control.

    Properties:
        is_open: Whether valve is fully open
        position: Current position (0.0 = closed, 1.0 = open)
        speed: Position change per second
    """

    def __post_init__(self):
        """Initialize valve-specific defaults."""
        if "is_open" not in self.properties:
            self.properties["is_open"] = False
        if "position" not in self.properties:
            self.properties["position"] = 0.0
        if "speed" not in self.properties:
            self.properties["speed"] = 1.0  # Fully open/close in 1 second

    def update(self, delta_time: float) -> None:
        """Update valve position based on command."""
        open_cmd_tag = self.get_tag(f"{self.name}_OpenCmd")
        position_tag = self.get_tag(f"{self.name}_Position")
        is_open_tag = self.get_tag(f"{self.name}_IsOpen")

        if not open_cmd_tag or not position_tag:
            return

        current_position = self.properties["position"]
        target_position = 1.0 if open_cmd_tag.value else 0.0
        speed = self.properties["speed"]

        # Move valve position
        if current_position < target_position:
            current_position = min(current_position + speed * delta_time, target_position)
        elif current_position > target_position:
            current_position = max(current_position - speed * delta_time, target_position)

        self.properties["position"] = current_position
        self.properties["is_open"] = current_position >= 0.99

        # Update state
        if current_position >= 0.99:
            self.state = DeviceState.RUNNING
        elif current_position <= 0.01:
            self.state = DeviceState.STOPPED
        else:
            self.state = DeviceState.RUNNING

        # Update tags
        position_tag.update_value(current_position)
        if is_open_tag:
            is_open_tag.update_value(self.properties["is_open"])

    def read_inputs(self) -> Dict[str, Any]:
        """Read open command from PLC."""
        open_cmd_tag = self.get_tag(f"{self.name}_OpenCmd")
        if open_cmd_tag:
            return {open_cmd_tag.name: open_cmd_tag.value}
        return {}

    def write_outputs(self) -> Dict[str, Any]:
        """Write valve position and status to PLC."""
        outputs = {}

        position_tag = self.get_tag(f"{self.name}_Position")
        if position_tag:
            outputs[position_tag.name] = self.properties["position"]

        is_open_tag = self.get_tag(f"{self.name}_IsOpen")
        if is_open_tag:
            outputs[is_open_tag.name] = self.properties["is_open"]

        return outputs
