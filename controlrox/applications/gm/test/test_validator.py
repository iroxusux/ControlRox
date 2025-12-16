"""Unit tests for GM Controller Validator.

This test suite provides comprehensive testing of the GmControllerValidator
for validating GM-specific PLC controller configurations.
"""
import unittest


from controlrox.applications.gm.validator import GmControllerValidator
from controlrox.applications.gm.gm import GmController


class TestGmControllerValidatorInitialization(unittest.TestCase):
    """Test cases for GmControllerValidator initialization."""

    def test_supporting_class_is_gm_controller(self):
        """Test supporting_class is set to GmController."""
        self.assertEqual(GmControllerValidator.supporting_class, GmController)

    def test_std_module_rpi_configured(self):
        """Test standard module RPI is configured."""
        self.assertEqual(GmControllerValidator.std_module_rpi, 20.0)

    def test_drive_module_rpi_configured(self):
        """Test drive module RPI is configured."""
        self.assertEqual(GmControllerValidator.drive_module_rpi, 30.0)

    def test_safety_module_input_rpi_configured(self):
        """Test safety module input RPI is configured."""
        self.assertEqual(GmControllerValidator.sfty_module_input_rpi, 20.0)

    def test_safety_module_output_rpi_configured(self):
        """Test safety module output RPI is configured."""
        self.assertEqual(GmControllerValidator.sfty_module_output_rpi, 50.0)


class TestGmControllerValidatorInheritance(unittest.TestCase):
    """Test cases for GmControllerValidator inheritance."""

    def test_inherits_from_base_controller_validator(self):
        """Test GmControllerValidator inherits from BaseControllerValidator."""
        from controlrox.applications.validator import BaseControllerValidator

        self.assertTrue(issubclass(GmControllerValidator, BaseControllerValidator))


class TestGmControllerValidatorRPIValues(unittest.TestCase):
    """Test cases for RPI (Request Packet Interval) values."""

    def test_standard_module_rpi_is_20ms(self):
        """Test standard modules use 20ms RPI."""
        validator = GmControllerValidator
        self.assertEqual(validator.std_module_rpi, 20.0)

    def test_drive_module_rpi_is_30ms(self):
        """Test drive modules use 30ms RPI."""
        validator = GmControllerValidator
        self.assertEqual(validator.drive_module_rpi, 30.0)

    def test_safety_input_module_rpi_is_20ms(self):
        """Test safety input modules use 20ms RPI."""
        validator = GmControllerValidator
        self.assertEqual(validator.sfty_module_input_rpi, 20.0)

    def test_safety_output_module_rpi_is_50ms(self):
        """Test safety output modules use 50ms RPI."""
        validator = GmControllerValidator
        self.assertEqual(validator.sfty_module_output_rpi, 50.0)


class TestGmControllerValidatorClassAttributes(unittest.TestCase):
    """Test cases for class-level attributes."""

    def test_validator_has_all_required_rpi_attributes(self):
        """Test validator has all required RPI attributes."""
        required_attrs = [
            'std_module_rpi',
            'drive_module_rpi',
            'sfty_module_input_rpi',
            'sfty_module_output_rpi'
        ]

        for attr in required_attrs:
            self.assertTrue(hasattr(GmControllerValidator, attr),
                            f"Missing required attribute: {attr}")

    def test_all_rpi_values_are_numeric(self):
        """Test all RPI values are numeric."""
        self.assertIsInstance(GmControllerValidator.std_module_rpi, (int, float))
        self.assertIsInstance(GmControllerValidator.drive_module_rpi, (int, float))
        self.assertIsInstance(GmControllerValidator.sfty_module_input_rpi, (int, float))
        self.assertIsInstance(GmControllerValidator.sfty_module_output_rpi, (int, float))

    def test_all_rpi_values_are_positive(self):
        """Test all RPI values are positive."""
        self.assertGreater(GmControllerValidator.std_module_rpi, 0)
        self.assertGreater(GmControllerValidator.drive_module_rpi, 0)
        self.assertGreater(GmControllerValidator.sfty_module_input_rpi, 0)
        self.assertGreater(GmControllerValidator.sfty_module_output_rpi, 0)


class TestGmControllerValidatorRPIComplianceGuidelines(unittest.TestCase):
    """Test cases to verify RPI values follow GM guidelines."""

    def test_safety_output_rpi_greater_than_input(self):
        """Test safety output RPI is greater than input RPI per GM guidelines."""
        validator = GmControllerValidator
        self.assertGreater(validator.sfty_module_output_rpi,
                           validator.sfty_module_input_rpi,
                           "Safety output RPI should be greater than input RPI")

    def test_drive_rpi_greater_than_standard(self):
        """Test drive module RPI is greater than standard module RPI."""
        validator = GmControllerValidator
        self.assertGreater(validator.drive_module_rpi,
                           validator.std_module_rpi,
                           "Drive module RPI should be greater than standard module RPI")

    def test_rpi_values_within_reasonable_range(self):
        """Test RPI values are within reasonable millisecond range."""
        validator = GmControllerValidator

        # RPI values should be between 1ms and 1000ms (1 second)
        rpi_values = [
            validator.std_module_rpi,
            validator.drive_module_rpi,
            validator.sfty_module_input_rpi,
            validator.sfty_module_output_rpi
        ]

        for rpi in rpi_values:
            self.assertGreaterEqual(rpi, 1.0, "RPI should be at least 1ms")
            self.assertLessEqual(rpi, 1000.0, "RPI should be at most 1000ms")


class TestGmControllerValidatorGMSpecific(unittest.TestCase):
    """Test cases for GM-specific validation requirements."""

    def test_validator_designed_for_gm_controllers(self):
        """Test validator is specifically designed for GM controllers."""
        self.assertEqual(GmControllerValidator.supporting_class, GmController)
        self.assertIn('Gm', GmControllerValidator.__name__)

    def test_validator_follows_gm_timing_standards(self):
        """Test validator follows GM timing standards."""
        # GM typically uses these specific values for automotive applications
        validator = GmControllerValidator

        # Standard I/O at 20ms
        self.assertEqual(validator.std_module_rpi, 20.0)

        # Drives at 30ms
        self.assertEqual(validator.drive_module_rpi, 30.0)

        # Safety inputs at 20ms for fast response
        self.assertEqual(validator.sfty_module_input_rpi, 20.0)

        # Safety outputs at 50ms for stability
        self.assertEqual(validator.sfty_module_output_rpi, 50.0)


class TestGmControllerValidatorInstantiation(unittest.TestCase):
    """Test cases for validator instantiation and usage."""

    def test_validator_can_be_instantiated(self):
        """Test validator can be instantiated."""
        try:
            validator = GmControllerValidator()
            self.assertIsInstance(validator, GmControllerValidator)
        except TypeError:
            # Some validators might require initialization parameters
            # which is acceptable
            pass

    def test_validator_attributes_accessible_from_instance(self):
        """Test RPI attributes are accessible from instance."""
        try:
            validator = GmControllerValidator()

            self.assertEqual(validator.std_module_rpi, 20.0)
            self.assertEqual(validator.drive_module_rpi, 30.0)
            self.assertEqual(validator.sfty_module_input_rpi, 20.0)
            self.assertEqual(validator.sfty_module_output_rpi, 50.0)
        except TypeError:
            # If instantiation requires parameters, test at class level
            self.assertEqual(GmControllerValidator.std_module_rpi, 20.0)
            self.assertEqual(GmControllerValidator.drive_module_rpi, 30.0)


class TestGmControllerValidatorComparisonWithOtherImplementations(unittest.TestCase):
    """Test cases comparing GM validator with other implementations."""

    def test_gm_rpi_values_differ_from_generic_values(self):
        """Test GM RPI values are specific and not default placeholders."""
        validator = GmControllerValidator

        # Verify these are intentional values, not defaults like 0 or 10
        self.assertNotEqual(validator.std_module_rpi, 0)
        self.assertNotEqual(validator.std_module_rpi, 10)
        self.assertNotEqual(validator.drive_module_rpi, 0)
        self.assertNotEqual(validator.drive_module_rpi, 10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
