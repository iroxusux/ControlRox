"""Unit tests for controlrox.models.tasks.app module."""
import unittest
from unittest.mock import Mock, MagicMock, patch

from controlrox.interfaces import IController
from controlrox.models.tasks.app import ControllerApplication, ENV_LAST_OPEN_L5X


class TestControllerApplication(unittest.TestCase):
    """Test cases for ControllerApplication class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock GUI Manager to avoid tkinter initialization
        self.gui_manager_patcher = patch('pyrox.services.gui.GuiManager')
        self.mock_gui_manager = self.gui_manager_patcher.start()

        # Create mock backend with complete window mocking
        mock_backend = MagicMock()
        mock_menu = MagicMock()
        mock_menu.get_file_menu = MagicMock(return_value=MagicMock())
        mock_backend.get_root_application_gui_menu.return_value = mock_menu

        # Mock window with set_title method
        self.mock_window = MagicMock()
        self.mock_window.set_title = MagicMock()
        mock_backend.get_root_gui_window.return_value = self.mock_window

        self.mock_gui_manager.unsafe_get_backend.return_value = mock_backend
        self.mock_gui_manager.is_gui_available.return_value = True

        # Mock environment variable for GUI - handle all parameter variations
        self.env_patcher = patch('pyrox.models.application.get_env')
        self.mock_get_env = self.env_patcher.start()

        def mock_get_env_impl(*args, **kwargs):  # type: ignore
            key = args[0] if args else kwargs.get('key')
            if key == 'UI_ICON_PATH':
                return ''
            elif key in ('is_gui_enabled', 'UI_AUTO_INIT'):
                return False
            return kwargs.get('default', args[1] if len(args) > 1 else None)

        self.mock_get_env.side_effect = mock_get_env_impl

        # Create mock controller
        self.mock_controller = Mock(spec=IController)
        self.mock_controller.name = 'TestController'
        self.mock_controller.file_location = '/path/to/controller.L5X'
        self.mock_controller.meta_data = {'@Name': 'TestController'}
        self.mock_controller.set_file_location = MagicMock()
        # Mocks are truthy by default, no need to explicitly set __bool__

    def tearDown(self):
        """Clean up test fixtures."""
        self.gui_manager_patcher.stop()
        self.env_patcher.stop()

    @patch('controlrox.models.tasks.app.ApplicationTaskFactory.build_tasks')
    def test_build(self, mock_build_tasks):
        """Test build method."""
        with patch.object(ControllerApplication, 'load_last_opened_controller'):
            with patch('pyrox.models.application.Application.build'):  # Skip parent build to avoid GUI
                app = ControllerApplication()  # type: ignore
                app.build()

                mock_build_tasks.assert_called_once_with(app)

    @patch('controlrox.models.tasks.app.ApplicationTaskFactory.build_tasks')
    @patch('controlrox.models.tasks.app.get_env')
    def test_build_calls_load_last_opened_controller(self, mock_get_env, mock_build_tasks):
        """Test that build calls load_last_opened_controller."""
        mock_get_env.return_value = None

        with patch.object(ControllerApplication, 'load_last_opened_controller') as mock_load:
            with patch('pyrox.models.application.Application.build'):  # Skip parent build to avoid GUI
                app = ControllerApplication()  # type: ignore
                app.build()

                mock_load.assert_called_once()

    def test_invalidate(self):
        """Test invalidate method."""
        app = ControllerApplication()  # type: ignore

        # Should complete without errors
        app.invalidate()

    @patch('controlrox.models.tasks.app.get_env')
    @patch('controlrox.models.tasks.app.os.path.isfile')
    def test_load_last_opened_controller_file_exists(self, mock_isfile, mock_get_env):
        """Test loading last opened controller when file exists."""
        mock_get_env.return_value = '/path/to/last.L5X'
        mock_isfile.return_value = True
        app = ControllerApplication()  # type: ignore

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
        app = ControllerApplication()  # type: ignore

        with patch.object(app, 'load_controller') as mock_load:
            app.load_last_opened_controller()

            mock_load.assert_not_called()
            mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '')

    @patch('controlrox.models.tasks.app.get_env')
    @patch('controlrox.models.tasks.app.set_env')
    def test_load_last_opened_controller_no_file(self, mock_set_env, mock_get_env):
        """Test loading last opened controller when no file is set."""
        mock_get_env.return_value = None
        app = ControllerApplication()  # type: ignore

        with patch.object(app, 'load_controller') as mock_load:
            app.load_last_opened_controller()

            mock_load.assert_not_called()
            mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '')

    @patch('controlrox.models.tasks.app.set_env')
    def test_load_controller_sets_env(self, mock_set_env):
        """Test loading a controller sets the environment variable."""
        app = ControllerApplication()  # type: ignore

        with patch('controlrox.models.tasks.app.ControllerInstanceManager.load_controller_from_file_location') as mock_load:
            with patch.object(app, 'invalidate'):
                with patch.object(app, 'refresh'):
                    mock_controller = MagicMock(spec=IController)
                    mock_controller.file_location = '/path/to/controller.L5X'
                    mock_load.return_value = mock_controller

                    app.load_controller('/path/to/controller.L5X')

            mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '/path/to/controller.L5X')

    def test_new_controller(self):
        """Test new controller raises NotImplementedError."""
        app = ControllerApplication()  # type: ignore

        with self.assertRaises(NotImplementedError):
            app.new_controller()

    def test_refresh(self):
        """Test refresh method."""
        app = ControllerApplication()  # type: ignore

        with patch.object(app, 'set_app_title') as mock_set_title:
            app.refresh()

            mock_set_title.assert_called_once()

    @patch('controlrox.models.tasks.app.EnvManager.get')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_set_app_title_no_controller(self, mock_get_controller, mock_env_get):
        """Test setting app title with no controller."""
        mock_env_get.return_value = 'ControlRox'
        mock_get_controller.return_value = None
        app = ControllerApplication()  # type: ignore

        # Patch the window property to return our mock
        mock_window = MagicMock()
        with patch.object(type(app), 'window', new_callable=lambda: property(lambda self: mock_window)):
            app.set_app_title()

        mock_window.set_title.assert_called_once_with('ControlRox')

    @patch('controlrox.models.tasks.app.EnvManager.get')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_set_app_title_with_controller(self, mock_get_controller, mock_env_get):
        """Test setting app title with controller."""
        mock_env_get.return_value = 'ControlRox'
        mock_get_controller.return_value = self.mock_controller
        app = ControllerApplication()  # type: ignore
        object.__setattr__(app, '_controller', self.mock_controller)

        # Patch window property to return our mock
        with patch.object(ControllerApplication, 'window', new_callable=lambda: property(lambda self: self._test_mock_window)):
            object.__setattr__(app, '_test_mock_window', self.mock_window)
            app.set_app_title()

        expected_title = 'ControlRox - [TestController] - [/path/to/controller.L5X]'
        self.mock_window.set_title.assert_called_once_with(expected_title)

    @patch('controlrox.models.tasks.app.EnvManager.get')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.get_controller')
    def test_set_app_title_with_unsaved_controller(self, mock_get_controller, mock_env_get):
        """Test setting app title with unsaved controller."""
        mock_env_get.return_value = 'ControlRox'

        mock_controller = MagicMock()
        mock_controller.name = 'UnsavedController'
        mock_controller.file_location = None
        mock_get_controller.return_value = mock_controller

        app = ControllerApplication()  # type: ignore
        object.__setattr__(app, '_controller', mock_controller)

        # Patch window property to return our mock
        with patch.object(ControllerApplication, 'window', new_callable=lambda: property(lambda self: self._test_mock_window)):
            object.__setattr__(app, '_test_mock_window', self.mock_window)
            app.set_app_title()

        expected_title = 'ControlRox - [UnsavedController] - [Unsaved*]'
        self.mock_window.set_title.assert_called_once_with(expected_title)

    @patch('controlrox.models.tasks.app.HasController.set_controller')
    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_valid(self, mock_set_controller, mock_set_env, mock_has_controller_set):
        """Test setting a valid controller."""
        app = ControllerApplication()  # type: ignore

        with patch.object(app, 'invalidate'):
            with patch.object(app, 'refresh'):
                app.set_controller(self.mock_controller)

        mock_set_controller.assert_called_once_with(self.mock_controller)
        mock_set_env.assert_called_once_with(ENV_LAST_OPEN_L5X, '/path/to/controller.L5X')

    @patch('controlrox.models.tasks.app.HasController.set_controller')
    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_none(self, mock_set_controller, mock_set_env, mock_has_controller_set):
        """Test setting controller to None."""
        app = ControllerApplication()  # type: ignore

        with patch.object(app, 'invalidate'):
            with patch.object(app, 'refresh'):
                app.set_controller(None)

        mock_set_controller.assert_called_once_with(None)
        # Should not set env when controller is None
        mock_set_env.assert_not_called()

    @patch('controlrox.models.tasks.app.HasController.set_controller')
    def test_set_controller_invalid_type(self, mock_has_controller_set):
        """Test setting controller with invalid type."""
        app = ControllerApplication()  # type: ignore
        invalid_controller = "not a controller"

        with self.assertRaises(TypeError):
            app.set_controller(invalid_controller)  # type: ignore

        mock_has_controller_set.assert_not_called()

    @patch('controlrox.models.tasks.app.HasController.set_controller')
    @patch('controlrox.models.tasks.app.set_env')
    @patch('controlrox.models.tasks.app.ControllerInstanceManager.set_controller')
    def test_set_controller_no_file_location(self, mock_set_controller, mock_set_env, mock_has_controller_set):
        """Test setting controller without file location."""
        mock_controller = MagicMock(spec=IController)
        mock_controller.file_location = None
        app = ControllerApplication()  # type: ignore

        with patch.object(app, 'invalidate'):
            with patch.object(app, 'refresh'):
                app.set_controller(mock_controller)

        mock_set_controller.assert_called_once_with(mock_controller)
        # Should not set env when no file location
        mock_set_env.assert_not_called()

    @patch('controlrox.models.tasks.app.HasController.set_controller')
    def test_set_controller_calls_invalidate_and_refresh(self, mock_has_controller_set):
        """Test that set_controller calls invalidate and refresh."""
        app = ControllerApplication()  # type: ignore

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
        from pyrox.models import Application

        app = ControllerApplication()  # type: ignore

        self.assertIsInstance(app, IControllerApplication)
        self.assertIsInstance(app, Application)


if __name__ == '__main__':
    unittest.main()
