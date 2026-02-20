"""Unit tests for controlrox.models.tasks.app module."""
import unittest
from unittest.mock import Mock, MagicMock, patch

from controlrox.interfaces import IController
from controlrox.models.tasks.app import ControllerApplication, ENV_LAST_OPEN_L5X


class TestControllerApplication(unittest.TestCase):
    """Test cases for ControllerApplication class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the entire Application.__init__ to avoid tkinter initialization
        self.app_init_patcher = patch('pyrox.application.Application.__init__')
        self.mock_app_init = self.app_init_patcher.start()
        self.mock_app_init.return_value = None

        # Mock ServicesRunnableMixin.__init__
        self.services_init_patcher = patch('pyrox.models.services.ServicesRunnableMixin.__init__')
        self.mock_services_init = self.services_init_patcher.start()
        self.mock_services_init.return_value = None

        # DON'T mock HasController.__init__ - let it run to set _controller properly

        # Mock GuiManager for main_window access
        self.gui_manager_patcher = patch('pyrox.services.gui.TkGuiManager')
        self.mock_gui_manager_class = self.gui_manager_patcher.start()

        # Create mock window
        self.mock_window = MagicMock()
        self.mock_window.set_title = MagicMock()

        # Create mock backend
        self.mock_backend = MagicMock()
        self.mock_backend.get_root_window.return_value = self.mock_window

        # Configure GuiManager to return our mock backend
        self.mock_gui_manager_class.unsafe_get_backend.return_value = self.mock_backend

        # Also patch it in the models.services module where it's accessed
        self.gui_manager_services_patcher = patch('pyrox.models.services.TkGuiManager')
        self.mock_gui_manager_services = self.gui_manager_services_patcher.start()
        self.mock_gui_manager_services.unsafe_get_backend.return_value = self.mock_backend

        # Mock logging service
        self.mock_logging = MagicMock()

        # Create mock controller
        self.mock_controller = Mock(spec=IController)
        self.mock_controller.name = 'TestController'
        self.mock_controller.file_location = '/path/to/controller.L5X'
        self.mock_controller.meta_data = {'@Name': 'TestController'}
        self.mock_controller.set_file_location = MagicMock()

    def tearDown(self):
        """Clean up test fixtures."""
        self.app_init_patcher.stop()
        self.services_init_patcher.stop()
        self.gui_manager_patcher.stop()
        self.gui_manager_services_patcher.stop()

    def _create_app(self):
        """Helper to create ControllerApplication with mocked services."""
        app = ControllerApplication()
        # HasController.__init__ runs and sets _controller to None
        # GuiManager and backend are accessed via service layer properties, already mocked
        return app

    def test_invalidate(self):
        """Test invalidate method."""
        app = self._create_app()

        # Test with no controller
        app.invalidate()  # Should not raise

        # Test with controller - need to set it via the setter to ensure it works
        self.mock_controller.invalidate = MagicMock()

        # Use the actual controller setter/property
        with patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller') as mock_get:
            mock_get.return_value = self.mock_controller

            # Directly set _controller since that's what HasController uses
            app._controller = self.mock_controller

            # Call invalidate - it should call controller.invalidate()
            app.invalidate()

        self.mock_controller.invalidate.assert_called_once()

    @patch('controlrox.models.tasks.app.get_env')
    @patch('controlrox.models.tasks.app.os.path.isfile')
    def test_load_last_opened_controller_file_exists(self, mock_isfile, mock_get_env):
        """Test loading last opened controller when file exists."""
        mock_get_env.return_value = '/path/to/last.L5X'
        mock_isfile.return_value = True
        app = self._create_app()

        with patch.object(app, 'load_controller') as mock_load:
            app.load_last_opened_controller()

            mock_load.assert_called_once_with('/path/to/last.L5X')

    @patch('controlrox.models.tasks.app.get_env')
    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.os.path.isfile')
    def test_load_last_opened_controller_file_not_exists(self, mock_isfile, mock_set_env, mock_get_env):
        """Test loading last opened controller when file doesn't exist."""
        mock_get_env.return_value = '/path/to/missing.L5X'
        mock_isfile.return_value = False
        app = self._create_app()

        with patch.object(app, 'load_controller') as mock_load:
            app.load_last_opened_controller()

            mock_load.assert_not_called()
            mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '')

    @patch('controlrox.models.tasks.app.get_env')
    @patch('controlrox.models.tasks.app.set_env')
    def test_load_last_opened_controller_no_file(self, mock_set_env, mock_get_env):
        """Test loading last opened controller when no file is set."""
        mock_get_env.return_value = None
        app = self._create_app()

        with patch.object(app, 'load_controller') as mock_load:
            app.load_last_opened_controller()

            mock_load.assert_not_called()
            mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '')

    @patch('controlrox.models.tasks.app.set_env')
    def test_load_controller_sets_env(self, mock_set_env):
        """Test loading a controller sets the environment variable."""
        app = self._create_app()
        app.set_app_state_busy = MagicMock()
        app.set_app_state_normal = MagicMock()

        with patch('controlrox.models.tasks.app.ControllerInstanceManager.load_controller_from_file_location') as mock_load:
            with patch.object(app, 'set_controller'):
                mock_controller = MagicMock(spec=IController)
                mock_controller.file_location = '/path/to/controller.L5X'
                mock_load.return_value = mock_controller

                app.load_controller('/path/to/controller.L5X')

                mock_load.assert_called_once_with(file_location='/path/to/controller.L5X')
                app.set_controller.assert_called_once_with(mock_controller)

    def test_new_controller(self):
        """Test new controller raises NotImplementedError."""
        app = self._create_app()

        with self.assertRaises(NotImplementedError):
            app.new_controller()

    def test_refresh(self):
        """Test refresh method."""
        app = self._create_app()
        app.set_app_state_busy = MagicMock()
        app.set_app_state_normal = MagicMock()

        with patch.object(app, 'set_app_title') as mock_set_title:
            app.refresh()

            app.set_app_state_busy.assert_called_once()
            mock_set_title.assert_called_once()
            app.set_app_state_normal.assert_called_once()

    @patch('controlrox.models.tasks.app.EnvManager.get')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_set_app_title_no_controller(self, mock_get_controller, mock_env_get):
        """Test setting app title with no controller."""
        mock_env_get.return_value = 'ControlRox'
        mock_get_controller.return_value = None
        app = self._create_app()

        app.set_app_title()

        self.mock_backend.set_title.assert_called_once_with('ControlRox')

    @patch('controlrox.models.tasks.app.EnvManager.get')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_set_app_title_with_controller(self, mock_get_controller, mock_env_get):
        """Test setting app title with controller."""
        mock_env_get.return_value = 'ControlRox'
        mock_get_controller.return_value = self.mock_controller
        app = self._create_app()

        app.set_app_title()

        expected_title = 'ControlRox - [TestController] - [/path/to/controller.L5X]'
        self.mock_backend.set_title.assert_called_once_with(expected_title)

    @patch('controlrox.models.tasks.app.EnvManager.get')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_set_app_title_with_unsaved_controller(self, mock_get_controller, mock_env_get):
        """Test setting app title with unsaved controller."""
        mock_env_get.return_value = 'ControlRox'

        mock_controller = MagicMock()
        mock_controller.name = 'UnsavedController'
        mock_controller.file_location = None
        mock_get_controller.return_value = mock_controller

        app = self._create_app()

        app.set_app_title()

        expected_title = 'ControlRox - [UnsavedController] - [Unsaved*]'
        self.mock_backend.set_title.assert_called_once_with(expected_title)

    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_valid(self, mock_set_controller, mock_set_env):
        """Test setting a valid controller."""
        app = self._create_app()

        with patch.object(app, 'invalidate'):
            with patch.object(app, 'refresh'):
                app.set_controller(self.mock_controller)

        mock_set_controller.assert_called_once_with(self.mock_controller)
        mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '/path/to/controller.L5X')

    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_none(self, mock_set_controller, mock_set_env):
        """Test setting controller to None."""
        app = self._create_app()

        with patch.object(app, 'invalidate'):
            with patch.object(app, 'refresh'):
                app.set_controller(None)

        mock_set_controller.assert_called_once_with(None)
        # Should not set env when controller is None
        mock_set_env.assert_not_called()

    def test_set_controller_invalid_type(self):
        """Test setting controller with invalid type."""
        app = self._create_app()
        invalid_controller = "not a controller"

        with self.assertRaises(TypeError):
            app.set_controller(invalid_controller)  # type: ignore

    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_no_file_location(self, mock_set_controller, mock_set_env):
        """Test setting controller without file location."""
        mock_controller = MagicMock(spec=IController)
        mock_controller.file_location = None
        app = self._create_app()

        with patch.object(app, 'invalidate'):
            with patch.object(app, 'refresh'):
                app.set_controller(mock_controller)

        mock_set_controller.assert_called_once_with(mock_controller)
        # Should not set env when no file location
        mock_set_env.assert_not_called()

    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_calls_invalidate_and_refresh(self, mock_set_controller):
        """Test that set_controller calls invalidate and refresh."""
        app = self._create_app()

        with patch.object(app, 'invalidate') as mock_invalidate:
            with patch.object(app, 'refresh') as mock_refresh:
                app.set_controller(self.mock_controller)

        mock_invalidate.assert_called_once()
        mock_refresh.assert_called_once()

    def test_env_last_open_l5x_constant(self):
        """Test that ENV_LAST_OPEN_L5X constant is defined."""
        self.assertEqual(ENV_LAST_OPEN_L5X, 'PLC_LAST_OPEN_L5X')

    def test_inheritance(self):
        """Test that ControllerApplication has correct inheritance."""
        from controlrox.interfaces import IControllerApplication
        from pyrox import Application

        app = self._create_app()

        self.assertIsInstance(app, IControllerApplication)
        self.assertIsInstance(app, Application)


if __name__ == '__main__':
    unittest.main()
