"""Unit tests for controlrox.models.simulation.devices module."""
import unittest

from controlrox.models.simulation.devices import Motor, Sensor, Valve
from controlrox.models.simulation import DeviceState, Tag, TagType


class TestMotor(unittest.TestCase):
    """Test cases for Motor device."""

    def setUp(self):
        """Set up test fixtures."""
        self.motor = Motor(
            id="motor_001",
            device_type="Motor",
            name="TestMotor"
        )

    def test_init_with_defaults(self):
        """Test Motor initialization sets default properties."""
        motor = Motor(
            id="motor_002",
            device_type="Motor",
            name="DefaultMotor"
        )

        self.assertIn("rpm", motor.properties)
        self.assertIn("max_rpm", motor.properties)
        self.assertIn("acceleration", motor.properties)
        self.assertEqual(motor.properties["rpm"], 0.0)
        self.assertEqual(motor.properties["max_rpm"], 1800.0)
        self.assertEqual(motor.properties["acceleration"], 100.0)

    def test_init_with_custom_properties(self):
        """Test Motor initialization with custom properties."""
        motor = Motor(
            id="motor_003",
            device_type="Motor",
            name="CustomMotor",
            properties={
                "rpm": 100.0,
                "max_rpm": 3600.0,
                "acceleration": 200.0
            }
        )

        self.assertEqual(motor.properties["rpm"], 100.0)
        self.assertEqual(motor.properties["max_rpm"], 3600.0)
        self.assertEqual(motor.properties["acceleration"], 200.0)

    def test_update_accelerates_when_running(self):
        """Test that motor accelerates when run command is true."""
        self.motor.add_tag(Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.motor.add_tag(Tag(
            name="TestMotor_Speed",
            tag_type=TagType.REAL,
            value=0.0
        ))

        initial_rpm = self.motor.properties["rpm"]

        self.motor.update(0.5)

        # Should have accelerated
        self.assertGreater(self.motor.properties["rpm"], initial_rpm)
        self.assertEqual(self.motor.state, DeviceState.RUNNING)

    def test_update_decelerates_when_stopped(self):
        """Test that motor decelerates when run command is false."""
        self.motor.add_tag(Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=False
        ))
        self.motor.add_tag(Tag(
            name="TestMotor_Speed",
            tag_type=TagType.REAL,
            value=0.0
        ))

        # Set initial speed
        self.motor.properties["rpm"] = 1000.0

        self.motor.update(0.5)

        # Should have decelerated
        self.assertLess(self.motor.properties["rpm"], 1000.0)

    def test_update_reaches_max_rpm(self):
        """Test that motor doesn't exceed max_rpm."""
        self.motor.add_tag(Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.motor.add_tag(Tag(
            name="TestMotor_Speed",
            tag_type=TagType.REAL,
            value=0.0
        ))

        # Update for a long time
        for _ in range(100):
            self.motor.update(1.0)

        # Should not exceed max_rpm
        self.assertLessEqual(
            self.motor.properties["rpm"],
            self.motor.properties["max_rpm"]
        )

    def test_update_stops_at_zero(self):
        """Test that motor stops at zero RPM."""
        self.motor.add_tag(Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=False
        ))
        self.motor.add_tag(Tag(
            name="TestMotor_Speed",
            tag_type=TagType.REAL,
            value=0.0
        ))

        self.motor.properties["rpm"] = 10.0

        # Update for a long time
        for _ in range(100):
            self.motor.update(1.0)

        # Should not go below zero
        self.assertGreaterEqual(self.motor.properties["rpm"], 0.0)

    def test_update_without_tags(self):
        """Test that update handles missing tags gracefully."""
        # Should not raise an error
        self.motor.update(0.1)

    def test_state_changes(self):
        """Test that motor state changes appropriately."""
        self.motor.add_tag(Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.motor.add_tag(Tag(
            name="TestMotor_Speed",
            tag_type=TagType.REAL,
            value=0.0
        ))

        # Start from stopped
        self.motor.properties["rpm"] = 0.0
        self.motor.update(0.1)
        self.assertIn(self.motor.state, [DeviceState.RUNNING, DeviceState.IDLE])

        # Run at speed
        self.motor.properties["rpm"] = 1000.0
        self.motor.update(0.1)
        self.assertEqual(self.motor.state, DeviceState.RUNNING)

    def test_read_inputs(self):
        """Test Motor.read_inputs() method."""
        run_tag = Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=True
        )
        self.motor.add_tag(run_tag)

        inputs = self.motor.read_inputs()

        self.assertIn("TestMotor_Run", inputs)
        self.assertEqual(inputs["TestMotor_Run"], True)

    def test_write_outputs(self):
        """Test Motor.write_outputs() method."""
        speed_tag = Tag(
            name="TestMotor_Speed",
            tag_type=TagType.REAL,
            value=0.0
        )
        self.motor.add_tag(speed_tag)
        self.motor.properties["rpm"] = 1234.5

        outputs = self.motor.write_outputs()

        self.assertIn("TestMotor_Speed", outputs)
        self.assertEqual(outputs["TestMotor_Speed"], 1234.5)

    def test_serialization_roundtrip(self):
        """Test that motor can be serialized and deserialized."""
        self.motor.properties["rpm"] = 500.0
        self.motor.add_tag(Tag(
            name="TestMotor_Run",
            tag_type=TagType.BOOL,
            value=True
        ))

        data = self.motor.to_dict()
        restored = Motor.from_dict(data)

        self.assertEqual(restored.id, self.motor.id)
        self.assertEqual(restored.name, self.motor.name)
        self.assertEqual(restored.properties["rpm"], 500.0)
        self.assertEqual(len(restored.tags), 1)


class TestSensor(unittest.TestCase):
    """Test cases for Sensor device."""

    def setUp(self):
        """Set up test fixtures."""
        self.sensor = Sensor(
            id="sensor_001",
            device_type="Sensor",
            name="TestSensor"
        )

    def test_init_with_defaults(self):
        """Test Sensor initialization sets default properties."""
        sensor = Sensor(
            id="sensor_002",
            device_type="Sensor",
            name="DefaultSensor"
        )

        self.assertIn("value", sensor.properties)
        self.assertIn("min_value", sensor.properties)
        self.assertIn("max_value", sensor.properties)
        self.assertIn("noise", sensor.properties)
        self.assertEqual(sensor.properties["value"], 0.0)
        self.assertEqual(sensor.properties["min_value"], 0.0)
        self.assertEqual(sensor.properties["max_value"], 100.0)
        self.assertEqual(sensor.properties["noise"], 0.0)

    def test_init_with_custom_properties(self):
        """Test Sensor initialization with custom properties."""
        sensor = Sensor(
            id="sensor_003",
            device_type="Sensor",
            name="CustomSensor",
            properties={
                "value": 50.0,
                "min_value": -100.0,
                "max_value": 200.0,
                "noise": 5.0
            }
        )

        self.assertEqual(sensor.properties["value"], 50.0)
        self.assertEqual(sensor.properties["min_value"], -100.0)
        self.assertEqual(sensor.properties["max_value"], 200.0)
        self.assertEqual(sensor.properties["noise"], 5.0)

    def test_update_without_noise(self):
        """Test sensor update without noise."""
        self.sensor.add_tag(Tag(
            name="TestSensor_Value",
            tag_type=TagType.REAL,
            value=0.0
        ))
        self.sensor.properties["value"] = 42.0
        self.sensor.properties["noise"] = 0.0

        self.sensor.update(0.1)

        value_tag = self.sensor.get_tag("TestSensor_Value")
        self.assertEqual(value_tag.value, 42.0)
        self.assertEqual(self.sensor.state, DeviceState.RUNNING)

    def test_update_with_noise(self):
        """Test sensor update with noise."""
        self.sensor.add_tag(Tag(
            name="TestSensor_Value",
            tag_type=TagType.REAL,
            value=0.0
        ))
        self.sensor.properties["value"] = 50.0
        self.sensor.properties["noise"] = 5.0

        self.sensor.update(0.1)

        value_tag = self.sensor.get_tag("TestSensor_Value")

        # Value should be within noise range
        self.assertGreaterEqual(value_tag.value, 45.0)
        self.assertLessEqual(value_tag.value, 55.0)

    def test_update_respects_min_value(self):
        """Test that sensor respects minimum value."""
        self.sensor.add_tag(Tag(
            name="TestSensor_Value",
            tag_type=TagType.REAL,
            value=0.0
        ))
        self.sensor.properties["value"] = 5.0
        self.sensor.properties["min_value"] = 0.0
        self.sensor.properties["max_value"] = 100.0
        self.sensor.properties["noise"] = 20.0  # Large noise

        # Update multiple times to test randomness
        for _ in range(100):
            self.sensor.update(0.1)
            value_tag = self.sensor.get_tag("TestSensor_Value")
            self.assertGreaterEqual(value_tag.value, 0.0)

    def test_update_respects_max_value(self):
        """Test that sensor respects maximum value."""
        self.sensor.add_tag(Tag(
            name="TestSensor_Value",
            tag_type=TagType.REAL,
            value=0.0
        ))
        self.sensor.properties["value"] = 95.0
        self.sensor.properties["min_value"] = 0.0
        self.sensor.properties["max_value"] = 100.0
        self.sensor.properties["noise"] = 20.0  # Large noise

        # Update multiple times to test randomness
        for _ in range(100):
            self.sensor.update(0.1)
            value_tag = self.sensor.get_tag("TestSensor_Value")
            self.assertLessEqual(value_tag.value, 100.0)

    def test_update_without_tag(self):
        """Test that update handles missing tag gracefully."""
        # Should not raise an error
        self.sensor.update(0.1)

    def test_set_value(self):
        """Test Sensor.set_value() method."""
        self.sensor.set_value(75.5)

        self.assertEqual(self.sensor.properties["value"], 75.5)

    def test_set_value_clamps_to_min(self):
        """Test that set_value clamps to minimum."""
        self.sensor.properties["min_value"] = 0.0
        self.sensor.properties["max_value"] = 100.0

        self.sensor.set_value(-50.0)

        self.assertEqual(self.sensor.properties["value"], 0.0)

    def test_set_value_clamps_to_max(self):
        """Test that set_value clamps to maximum."""
        self.sensor.properties["min_value"] = 0.0
        self.sensor.properties["max_value"] = 100.0

        self.sensor.set_value(150.0)

        self.assertEqual(self.sensor.properties["value"], 100.0)

    def test_read_inputs(self):
        """Test Sensor.read_inputs() method."""
        inputs = self.sensor.read_inputs()

        # Sensors don't typically read inputs
        self.assertEqual(inputs, {})

    def test_write_outputs(self):
        """Test Sensor.write_outputs() method."""
        value_tag = Tag(
            name="TestSensor_Value",
            tag_type=TagType.REAL,
            value=99.9
        )
        self.sensor.add_tag(value_tag)

        outputs = self.sensor.write_outputs()

        self.assertIn("TestSensor_Value", outputs)
        self.assertEqual(outputs["TestSensor_Value"], 99.9)

    def test_serialization_roundtrip(self):
        """Test that sensor can be serialized and deserialized."""
        self.sensor.properties["value"] = 66.6
        self.sensor.properties["noise"] = 3.0

        data = self.sensor.to_dict()
        restored = Sensor.from_dict(data)

        self.assertEqual(restored.id, self.sensor.id)
        self.assertEqual(restored.name, self.sensor.name)
        self.assertEqual(restored.properties["value"], 66.6)
        self.assertEqual(restored.properties["noise"], 3.0)


class TestValve(unittest.TestCase):
    """Test cases for Valve device."""

    def setUp(self):
        """Set up test fixtures."""
        self.valve = Valve(
            id="valve_001",
            device_type="Valve",
            name="TestValve"
        )

    def test_init_with_defaults(self):
        """Test Valve initialization sets default properties."""
        valve = Valve(
            id="valve_002",
            device_type="Valve",
            name="DefaultValve"
        )

        self.assertIn("is_open", valve.properties)
        self.assertIn("position", valve.properties)
        self.assertIn("speed", valve.properties)
        self.assertEqual(valve.properties["is_open"], False)
        self.assertEqual(valve.properties["position"], 0.0)
        self.assertEqual(valve.properties["speed"], 1.0)

    def test_init_with_custom_properties(self):
        """Test Valve initialization with custom properties."""
        valve = Valve(
            id="valve_003",
            device_type="Valve",
            name="CustomValve",
            properties={
                "is_open": True,
                "position": 0.5,
                "speed": 2.0
            }
        )

        self.assertEqual(valve.properties["is_open"], True)
        self.assertEqual(valve.properties["position"], 0.5)
        self.assertEqual(valve.properties["speed"], 2.0)

    def test_update_opens_valve(self):
        """Test that valve opens when commanded."""
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.valve.add_tag(Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=0.0
        ))

        initial_position = self.valve.properties["position"]

        self.valve.update(0.5)

        # Should have moved toward open
        self.assertGreater(self.valve.properties["position"], initial_position)

    def test_update_closes_valve(self):
        """Test that valve closes when commanded."""
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=False
        ))
        self.valve.add_tag(Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=1.0
        ))

        self.valve.properties["position"] = 1.0

        self.valve.update(0.5)

        # Should have moved toward closed
        self.assertLess(self.valve.properties["position"], 1.0)

    def test_update_reaches_fully_open(self):
        """Test that valve reaches fully open position."""
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.valve.add_tag(Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=0.0
        ))
        self.valve.add_tag(Tag(
            name="TestValve_IsOpen",
            tag_type=TagType.BOOL,
            value=False
        ))

        # Update for sufficient time
        for _ in range(20):
            self.valve.update(0.1)

        # Should be fully open
        self.assertGreaterEqual(self.valve.properties["position"], 0.99)
        self.assertTrue(self.valve.properties["is_open"])

    def test_update_reaches_fully_closed(self):
        """Test that valve reaches fully closed position."""
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=False
        ))
        self.valve.add_tag(Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=1.0
        ))

        self.valve.properties["position"] = 1.0

        # Update for sufficient time
        for _ in range(20):
            self.valve.update(0.1)

        # Should be fully closed
        self.assertLessEqual(self.valve.properties["position"], 0.01)
        self.assertFalse(self.valve.properties["is_open"])

    def test_is_open_flag(self):
        """Test that is_open flag is set correctly."""
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.valve.add_tag(Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=0.0
        ))
        self.valve.add_tag(Tag(
            name="TestValve_IsOpen",
            tag_type=TagType.BOOL,
            value=False
        ))

        # Start with closed valve
        self.assertFalse(self.valve.properties["is_open"])

        # Open it
        for _ in range(20):
            self.valve.update(0.1)

        # Should be marked as open
        self.assertTrue(self.valve.properties["is_open"])

    def test_state_changes(self):
        """Test that valve state changes appropriately."""
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=True
        ))
        self.valve.add_tag(Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=0.0
        ))

        # Closed state
        self.valve.properties["position"] = 0.0
        self.valve.update(0.1)
        # State should be RUNNING (opening) or STOPPED

        # Fully open
        self.valve.properties["position"] = 1.0
        self.valve.update(0.1)
        self.assertEqual(self.valve.state, DeviceState.RUNNING)

    def test_update_without_tags(self):
        """Test that update handles missing tags gracefully."""
        # Should not raise an error
        self.valve.update(0.1)

    def test_read_inputs(self):
        """Test Valve.read_inputs() method."""
        open_cmd_tag = Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=True
        )
        self.valve.add_tag(open_cmd_tag)

        inputs = self.valve.read_inputs()

        self.assertIn("TestValve_OpenCmd", inputs)
        self.assertEqual(inputs["TestValve_OpenCmd"], True)

    def test_write_outputs(self):
        """Test Valve.write_outputs() method."""
        position_tag = Tag(
            name="TestValve_Position",
            tag_type=TagType.REAL,
            value=0.0
        )
        is_open_tag = Tag(
            name="TestValve_IsOpen",
            tag_type=TagType.BOOL,
            value=False
        )
        self.valve.add_tag(position_tag)
        self.valve.add_tag(is_open_tag)

        self.valve.properties["position"] = 0.75
        self.valve.properties["is_open"] = False

        outputs = self.valve.write_outputs()

        self.assertIn("TestValve_Position", outputs)
        self.assertIn("TestValve_IsOpen", outputs)
        self.assertEqual(outputs["TestValve_Position"], 0.75)
        self.assertEqual(outputs["TestValve_IsOpen"], False)

    def test_serialization_roundtrip(self):
        """Test that valve can be serialized and deserialized."""
        self.valve.properties["position"] = 0.5
        self.valve.properties["is_open"] = True
        self.valve.add_tag(Tag(
            name="TestValve_OpenCmd",
            tag_type=TagType.BOOL,
            value=True
        ))

        data = self.valve.to_dict()
        restored = Valve.from_dict(data)

        self.assertEqual(restored.id, self.valve.id)
        self.assertEqual(restored.name, self.valve.name)
        self.assertEqual(restored.properties["position"], 0.5)
        self.assertEqual(restored.properties["is_open"], True)
        self.assertEqual(len(restored.tags), 1)


class TestDeviceIntegration(unittest.TestCase):
    """Integration tests for device interactions."""

    def test_multiple_devices_independent(self):
        """Test that multiple devices operate independently."""
        motor = Motor(
            id="motor_001",
            device_type="Motor",
            name="Motor1"
        )
        sensor = Sensor(
            id="sensor_001",
            device_type="Sensor",
            name="Sensor1"
        )
        valve = Valve(
            id="valve_001",
            device_type="Valve",
            name="Valve1"
        )

        # Set up tags
        motor.add_tag(Tag(name="Motor1_Run", tag_type=TagType.BOOL, value=True))
        motor.add_tag(Tag(name="Motor1_Speed", tag_type=TagType.REAL, value=0.0))
        sensor.add_tag(Tag(name="Sensor1_Value", tag_type=TagType.REAL, value=0.0))
        valve.add_tag(Tag(name="Valve1_OpenCmd", tag_type=TagType.BOOL, value=True))
        valve.add_tag(Tag(name="Valve1_Position", tag_type=TagType.REAL, value=0.0))

        # Update all
        motor.update(0.1)
        sensor.update(0.1)
        valve.update(0.1)

        # Each should have updated independently
        self.assertGreater(motor.properties["rpm"], 0)
        self.assertEqual(sensor.state, DeviceState.RUNNING)
        self.assertGreater(valve.properties["position"], 0)


if __name__ == '__main__':
    unittest.main()
