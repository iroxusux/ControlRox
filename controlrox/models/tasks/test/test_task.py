"""Unit tests for controlrox.models.tasks.task module."""
import unittest
from unittest.mock import MagicMock

from controlrox.interfaces import IController
from controlrox.models.tasks.task import ControllerApplicationTask
from controlrox.models.tasks.app import ControllerApplication


class TestControllerApplicationTask(unittest.TestCase):
    """Test cases for ControllerApplicationTask class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the ControllerApplication
        self.mock_application = MagicMock(spec=ControllerApplication)
        self.mock_controller = MagicMock(spec=IController)
        self.mock_controller.name = 'TestController'

        # Create task instance
        self.task = ControllerApplicationTask(self.mock_application)

    def test_init(self):
        """Test initialization of ControllerApplicationTask."""
        task = ControllerApplicationTask(self.mock_application)

        self.assertEqual(task._application, self.mock_application)
        self.assertEqual(task.application, self.mock_application)

    def test_inject(self):
        """Test inject method returns None."""
        result = self.task.inject()

        self.assertIsNone(result)

    def test_inject_no_side_effects(self):
        """Test inject method has no side effects."""
        # Set up initial state
        self.mock_application.controller = self.mock_controller
        initial_controller = self.mock_application.controller

        # Call inject
        self.task.inject()

        # Verify no changes
        self.assertEqual(self.mock_application.controller, initial_controller)

    def test_application_property_inherited(self):
        """Test that application property is accessible from parent class."""
        # ApplicationTask should provide an application property
        self.assertEqual(self.task.application, self.mock_application)


if __name__ == '__main__':
    unittest.main()
