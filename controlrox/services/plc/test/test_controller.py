"""Unit tests for controlrox.services.plc.controller module."""
import unittest
from unittest.mock import Mock, patch
from typing import List, Type

from controlrox.interfaces import IController
from controlrox.services.plc.controller import (
    ControllerMatcher,
    ControllerMatcherFactory,
    ControllerFactory,
    ControllerInstanceManager,
)


class ConcreteControllerMatcher(ControllerMatcher):
    """Concrete implementation of ControllerMatcher for testing."""

    @staticmethod
    def get_datatype_patterns() -> List[str]:
        """List of patterns to identify the controller by datatype."""
        return ['TestDatatype*', 'CustomType*']

    @staticmethod
    def get_module_patterns() -> List[str]:
        """List of patterns to identify the controller by module."""
        return ['TestModule*', '1756-*']

    @staticmethod
    def get_program_patterns() -> List[str]:
        """List of patterns to identify the controller by program."""
        return ['MainProgram', 'TestProgram*']

    @staticmethod
    def get_safety_program_patterns() -> List[str]:
        """List of patterns to identify the controller by safety program."""
        return ['SafetyProgram*', 'Safe*']

    @staticmethod
    def get_tag_patterns() -> List[str]:
        """List of patterns to identify the controller by tag."""
        return ['GlobalTag*', 'TestTag*']

    @classmethod
    def get_controller_constructor(cls) -> Type[IController]:
        """Get the appropriate controller constructor for this matcher."""
        # Return Mock type instead of actual controller
        return Mock  # type: ignore


class EmptyPatternMatcher(ControllerMatcher):
    """Matcher with empty patterns for testing."""

    @staticmethod
    def get_datatype_patterns() -> List[str]:
        return []

    @staticmethod
    def get_module_patterns() -> List[str]:
        return []

    @staticmethod
    def get_program_patterns() -> List[str]:
        return []

    @staticmethod
    def get_safety_program_patterns() -> List[str]:
        return []

    @staticmethod
    def get_tag_patterns() -> List[str]:
        return []

    @classmethod
    def get_controller_constructor(cls) -> Type[IController]:
        return Mock  # type: ignore


class TestControllerMatcher(unittest.TestCase):
    """Test cases for ControllerMatcher class."""

    def setUp(self):
        """Set up test fixtures."""
        self.matcher = ConcreteControllerMatcher
        self.sample_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController',
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'TestDatatype1'},
                            {'@Name': 'CustomType2'},
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'TestModule1'},
                            {'@Name': '1756-EN2T'},
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {'@Name': 'MainProgram', '@Class': 'Standard'},
                            {'@Name': 'SafetyProgram1', '@Class': 'Safety'},
                        ]
                    },
                    'Tags': {
                        'Tag': [
                            {'@Name': 'GlobalTag1'},
                            {'@Name': 'TestTag1'},
                        ]
                    }
                }
            }
        }

    def test_get_datatype_patterns(self):
        """Test get_datatype_patterns returns correct patterns."""
        patterns = self.matcher.get_datatype_patterns()
        self.assertIsInstance(patterns, list)
        self.assertIn('TestDatatype*', patterns)
        self.assertIn('CustomType*', patterns)

    def test_get_module_patterns(self):
        """Test get_module_patterns returns correct patterns."""
        patterns = self.matcher.get_module_patterns()
        self.assertIsInstance(patterns, list)
        self.assertIn('TestModule*', patterns)
        self.assertIn('1756-*', patterns)

    def test_get_program_patterns(self):
        """Test get_program_patterns returns correct patterns."""
        patterns = self.matcher.get_program_patterns()
        self.assertIsInstance(patterns, list)
        self.assertIn('MainProgram', patterns)
        self.assertIn('TestProgram*', patterns)

    def test_get_safety_program_patterns(self):
        """Test get_safety_program_patterns returns correct patterns."""
        patterns = self.matcher.get_safety_program_patterns()
        self.assertIsInstance(patterns, list)
        self.assertIn('SafetyProgram*', patterns)
        self.assertIn('Safe*', patterns)

    def test_get_tag_patterns(self):
        """Test get_tag_patterns returns correct patterns."""
        patterns = self.matcher.get_tag_patterns()
        self.assertIsInstance(patterns, list)
        self.assertIn('GlobalTag*', patterns)
        self.assertIn('TestTag*', patterns)

    def test_calculate_score_perfect_match(self):
        """Test calculate_score with perfect match returns 1.0."""
        with patch.object(self.matcher, 'check_controller_datatypes', return_value=True), \
                patch.object(self.matcher, 'check_controller_modules', return_value=True), \
                patch.object(self.matcher, 'check_controller_programs', return_value=True), \
                patch.object(self.matcher, 'check_controller_safety_programs', return_value=True), \
                patch.object(self.matcher, 'check_controller_tags', return_value=True):

            score = self.matcher.calculate_score(self.sample_controller_data)
            self.assertEqual(score, 1.0)

    def test_calculate_score_partial_match(self):
        """Test calculate_score with partial match returns correct score."""
        with patch.object(self.matcher, 'check_controller_datatypes', return_value=True), \
                patch.object(self.matcher, 'check_controller_modules', return_value=True), \
                patch.object(self.matcher, 'check_controller_programs', return_value=False), \
                patch.object(self.matcher, 'check_controller_safety_programs', return_value=False), \
                patch.object(self.matcher, 'check_controller_tags', return_value=True):

            score = self.matcher.calculate_score(self.sample_controller_data)
            self.assertAlmostEqual(score, 0.6)  # 3 out of 5 checks passed

    def test_calculate_score_no_match(self):
        """Test calculate_score with no match returns 0.0."""
        with patch.object(self.matcher, 'check_controller_datatypes', return_value=False), \
                patch.object(self.matcher, 'check_controller_modules', return_value=False), \
                patch.object(self.matcher, 'check_controller_programs', return_value=False), \
                patch.object(self.matcher, 'check_controller_safety_programs', return_value=False), \
                patch.object(self.matcher, 'check_controller_tags', return_value=False):

            score = self.matcher.calculate_score(self.sample_controller_data)
            self.assertEqual(score, 0.0)

    def test_can_match_returns_false(self):
        """Test can_match returns False by default."""
        result = self.matcher.can_match()
        self.assertFalse(result)

    def test_get_class_returns_correct_class(self):
        """Test get_class returns the matcher class."""
        result = self.matcher.get_class()
        self.assertEqual(result, self.matcher)

    def test_get_factory_returns_correct_factory(self):
        """Test get_factory returns ControllerMatcherFactory."""
        result = self.matcher.get_factory()
        self.assertEqual(result, ControllerMatcherFactory)

    def test_get_controller_constructor_returns_controller_type(self):
        """Test get_controller_constructor returns correct controller type."""
        result = self.matcher.get_controller_constructor()
        self.assertEqual(result, Mock)

    def test_check_controller_datatypes_with_matching_patterns(self):
        """Test check_controller_datatypes with matching patterns."""
        with patch.object(self.matcher, 'check_dict_list_for_patterns', return_value=True) as mock_check:
            result = self.matcher.check_controller_datatypes(self.sample_controller_data)
            self.assertTrue(result)
            mock_check.assert_called_once()

    def test_check_controller_modules_with_matching_patterns(self):
        """Test check_controller_modules with matching patterns."""
        with patch.object(self.matcher, 'check_dict_list_for_patterns', return_value=True) as mock_check:
            result = self.matcher.check_controller_modules(self.sample_controller_data)
            self.assertTrue(result)
            mock_check.assert_called_once()

    def test_check_controller_programs_with_matching_patterns(self):
        """Test check_controller_programs with matching patterns."""
        with patch.object(self.matcher, 'check_dict_list_for_patterns', return_value=True) as mock_check:
            result = self.matcher.check_controller_programs(self.sample_controller_data)
            self.assertTrue(result)
            mock_check.assert_called_once()

    def test_check_controller_safety_programs_filters_safety_class(self):
        """Test check_controller_safety_programs filters by safety class."""
        with patch.object(self.matcher, 'check_dict_list_for_patterns', return_value=True) as mock_check:
            result = self.matcher.check_controller_safety_programs(self.sample_controller_data)
            self.assertTrue(result)
            # Verify it was called with filtered safety programs
            mock_check.assert_called_once()
            args = mock_check.call_args[0]
            # Should only include safety programs
            self.assertEqual(len(args[0]), 1)
            self.assertEqual(args[0][0]['@Name'], 'SafetyProgram1')

    def test_check_controller_tags_with_matching_patterns(self):
        """Test check_controller_tags with matching patterns."""
        with patch.object(self.matcher, 'check_dict_list_for_patterns', return_value=True) as mock_check:
            result = self.matcher.check_controller_tags(self.sample_controller_data)
            self.assertTrue(result)
            mock_check.assert_called_once()

    def test_check_dict_list_for_patterns_with_match(self):
        """Test check_dict_list_for_patterns with matching patterns."""
        dict_list = [
            {'@Name': 'TestDatatype1'},
            {'@Name': 'OtherType'},
        ]
        patterns = ['TestDatatype*']

        with patch('controlrox.services.plc.controller.check_wildcard_patterns', return_value=True) as mock_check:
            result = self.matcher.check_dict_list_for_patterns(dict_list, '@Name', patterns)
            self.assertTrue(result)
            mock_check.assert_called_once_with(['TestDatatype1', 'OtherType'], patterns)

    def test_check_dict_list_for_patterns_with_empty_patterns(self):
        """Test check_dict_list_for_patterns with empty patterns."""
        dict_list = [{'@Name': 'TestDatatype1'}]
        patterns = []

        result = self.matcher.check_dict_list_for_patterns(dict_list, '@Name', patterns)
        self.assertFalse(result)

    def test_check_dict_list_for_patterns_with_missing_key(self):
        """Test check_dict_list_for_patterns with missing key in dict."""
        dict_list = [
            {'@Name': 'TestDatatype1'},
            {'@Other': 'NoName'},
        ]
        patterns = ['Test*']

        with patch('controlrox.services.plc.controller.check_wildcard_patterns', return_value=True) as mock_check:
            result = self.matcher.check_dict_list_for_patterns(dict_list, '@Name', patterns)
            self.assertTrue(result)
            # Missing key should result in empty string
            mock_check.assert_called_once_with(['TestDatatype1', ''], patterns)

    def test_get_controller_meta_with_valid_data(self):
        """Test get_controller_meta extracts controller dictionary."""
        result = self.matcher.get_controller_meta(self.sample_controller_data)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['@Name'], 'TestController')

    def test_get_controller_meta_with_empty_data(self):
        """Test get_controller_meta raises ValueError with empty data."""
        with self.assertRaises(ValueError) as context:
            self.matcher.get_controller_meta({})
        self.assertIn('No controller data provided', str(context.exception))

    def test_get_controller_meta_with_none_logix_content(self):
        """Test get_controller_meta with None RSLogix5000Content."""
        data = {'RSLogix5000Content': None}
        result = self.matcher.get_controller_meta(data)
        self.assertEqual(result, {})

    def test_get_controller_meta_with_none_controller(self):
        """Test get_controller_meta with None Controller."""
        data = {
            'RSLogix5000Content': {
                'Controller': None
            }
        }
        result = self.matcher.get_controller_meta(data)
        self.assertEqual(result, {})

    def test_get_controller_data_list_with_valid_data(self):
        """Test get_controller_data_list extracts correct list."""
        result = self.matcher.get_controller_data_list(
            self.sample_controller_data,
            'DataType'
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['@Name'], 'TestDatatype1')

    def test_get_controller_data_list_with_single_item(self):
        """Test get_controller_data_list converts single dict to list."""
        data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {
                        'DataType': {'@Name': 'SingleType'}
                    }
                }
            }
        }
        result = self.matcher.get_controller_data_list(data, 'DataType')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['@Name'], 'SingleType')

    def test_get_controller_data_list_with_none_container(self):
        """Test get_controller_data_list with None container."""
        data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': None
                }
            }
        }
        result = self.matcher.get_controller_data_list(data, 'DataType')
        self.assertEqual(result, [])

    def test_get_controller_data_list_with_none_list(self):
        """Test get_controller_data_list with None list."""
        data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {
                        'DataType': None
                    }
                }
            }
        }
        result = self.matcher.get_controller_data_list(data, 'DataType')
        self.assertEqual(result, [])

    def test_get_controller_data_list_with_missing_key(self):
        """Test get_controller_data_list with missing key."""
        data = {
            'RSLogix5000Content': {
                'Controller': {}
            }
        }
        result = self.matcher.get_controller_data_list(data, 'DataType')
        self.assertEqual(result, [])

    def test_supports_registering_subclass(self):
        """Test that subclasses have supports_registering set to True."""
        self.assertTrue(ConcreteControllerMatcher.supports_registering)

    def test_supports_registering_base_class(self):
        """Test that base class has supports_registering set to False."""
        self.assertFalse(ControllerMatcher.supports_registering)


class TestControllerMatcherFactory(unittest.TestCase):
    """Test cases for ControllerMatcherFactory class."""

    def test_factory_is_meta_factory(self):
        """Test that ControllerMatcherFactory is a MetaFactory."""
        from pyrox.models.factory import MetaFactory
        self.assertTrue(issubclass(ControllerMatcherFactory, type(MetaFactory)))


class TestControllerFactory(unittest.TestCase):
    """Test cases for ControllerFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController',
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'TestDatatype1'},
                        ]
                    }
                }
            }
        }

    def test_get_best_match_with_valid_data(self):
        """Test get_best_match returns best matching controller type."""
        mock_controller_class = Mock(spec=IController)
        mock_controller_class.__name__ = 'MockController1'
        mock_matcher1 = Mock(spec=ControllerMatcher)
        mock_matcher1.calculate_score.return_value = 0.5
        mock_matcher1.get_controller_constructor.return_value = mock_controller_class
        mock_matcher1.__name__ = 'Matcher1'

        mock_controller_class2 = Mock(spec=IController)
        mock_controller_class2.__name__ = 'MockController2'
        mock_matcher2 = Mock(spec=ControllerMatcher)
        mock_matcher2.calculate_score.return_value = 0.8
        mock_matcher2.get_controller_constructor.return_value = mock_controller_class2
        mock_matcher2.__name__ = 'Matcher2'

        with patch.object(
            ControllerMatcherFactory,
            'get_registered_types',
            return_value={'matcher1': mock_matcher1, 'matcher2': mock_matcher2}
        ):
            result = ControllerFactory.get_best_match(self.sample_controller_data)
            self.assertEqual(result, mock_controller_class2)
            mock_matcher1.calculate_score.assert_called_once()
            mock_matcher2.calculate_score.assert_called_once()

    def test_get_best_match_with_no_matches_above_min_score(self):
        """Test get_best_match returns None when no matches above min_score."""
        mock_controller_class = Mock(spec=IController)
        mock_controller_class.__name__ = 'MockController'
        mock_matcher = Mock()
        mock_matcher.calculate_score.return_value = 0.2
        mock_matcher.get_controller_constructor.return_value = mock_controller_class

        with patch.object(
            ControllerMatcherFactory,
            'get_registered_types',
            return_value={'matcher': mock_matcher}
        ):
            result = ControllerFactory.get_best_match(
                self.sample_controller_data,
                min_score=0.3
            )
            self.assertIsNone(result)

    def test_get_best_match_with_empty_controller_data(self):
        """Test get_best_match returns None with empty controller data."""
        result = ControllerFactory.get_best_match({})
        self.assertIsNone(result)

    def test_get_best_match_with_none_controller_data(self):
        """Test get_best_match returns None with None controller data."""
        result = ControllerFactory.get_best_match(None)  # type: ignore
        self.assertIsNone(result)

    def test_get_best_match_with_no_registered_matchers(self):
        """Test get_best_match returns None with no registered matchers."""
        with patch.object(
            ControllerMatcherFactory,
            'get_registered_types',
            return_value={}
        ):
            result = ControllerFactory.get_best_match(self.sample_controller_data)
            self.assertIsNone(result)

    def test_get_best_match_with_custom_min_score(self):
        """Test get_best_match with custom min_score."""
        mock_controller_class = Mock(spec=IController)
        mock_controller_class.__name__ = 'MockController'
        mock_matcher = Mock()
        mock_matcher.calculate_score.return_value = 0.5
        mock_matcher.get_controller_constructor.return_value = mock_controller_class

        with patch.object(
            ControllerMatcherFactory,
            'get_registered_types',
            return_value={'matcher': mock_matcher}
        ):
            result = ControllerFactory.get_best_match(
                self.sample_controller_data,
                min_score=0.4
            )
            self.assertEqual(result, mock_controller_class)

            result_none = ControllerFactory.get_best_match(
                self.sample_controller_data,
                min_score=0.6
            )
            self.assertIsNone(result_none)

    def test_get_best_match_sorts_by_highest_score(self):
        """Test get_best_match returns highest scoring match."""
        mock_controller1 = Mock(spec=IController)
        mock_controller1.__name__ = 'MockController1'
        mock_matcher1 = Mock()
        mock_matcher1.calculate_score.return_value = 0.7
        mock_matcher1.get_controller_constructor.return_value = mock_controller1

        mock_controller2 = Mock(spec=IController)
        mock_controller2.__name__ = 'MockController2'
        mock_matcher2 = Mock()
        mock_matcher2.calculate_score.return_value = 0.9
        mock_matcher2.get_controller_constructor.return_value = mock_controller2

        mock_controller3 = Mock(spec=IController)
        mock_controller3.__name__ = 'MockController3'
        mock_matcher3 = Mock()
        mock_matcher3.calculate_score.return_value = 0.5
        mock_matcher3.get_controller_constructor.return_value = mock_controller3

        with patch.object(
            ControllerMatcherFactory,
            'get_registered_types',
            return_value={
                'matcher1': mock_matcher1,
                'matcher2': mock_matcher2,
                'matcher3': mock_matcher3
            }
        ):
            result = ControllerFactory.get_best_match(self.sample_controller_data)
            self.assertEqual(result, mock_controller2)

    def test_create_controller_with_valid_match(self):
        """Test create_controller creates instance with valid match."""
        mock_controller_instance = Mock(spec=IController)
        mock_controller_class = Mock(return_value=mock_controller_instance)

        with patch.object(
            ControllerFactory,
            'get_best_match',
            return_value=mock_controller_class
        ):
            result = ControllerFactory.create_controller(
                self.sample_controller_data,
                file_location='/test/path.L5X'
            )

            self.assertIsNotNone(result)
            mock_controller_class.assert_called_once_with(
                meta_data=self.sample_controller_data,
                file_location='/test/path.L5X'
            )

    def test_create_controller_with_no_match(self):
        """Test create_controller returns Default Controller with no match."""
        with patch.object(
            ControllerFactory,
            'get_best_match',
            return_value=None
        ):
            result = ControllerFactory.create_controller(self.sample_controller_data)
            self.assertIsNotNone(result)

    def test_create_controller_passes_kwargs(self):
        """Test create_controller passes additional kwargs."""
        mock_controller_instance = Mock(spec=IController)
        mock_controller_class = Mock(return_value=mock_controller_instance)

        with patch.object(
            ControllerFactory,
            'get_best_match',
            return_value=mock_controller_class
        ):
            ControllerFactory.create_controller(
                self.sample_controller_data,
                file_location='/test/path.L5X',
                comms_path='1,0',
                slot=2
            )

            mock_controller_class.assert_called_once_with(
                meta_data=self.sample_controller_data,
                file_location='/test/path.L5X',
                comms_path='1,0',
                slot=2
            )


class TestControllerInstanceManager(unittest.TestCase):
    """Test cases for ControllerInstanceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the controller instance before each test
        ControllerInstanceManager._controller = None

    def tearDown(self):
        """Clean up test fixtures."""
        # Reset the controller instance after each test
        ControllerInstanceManager._controller = None

    def test_cannot_instantiate(self):
        """Test that ControllerInstanceManager cannot be instantiated."""
        with self.assertRaises(RuntimeError) as context:
            ControllerInstanceManager()
        self.assertIn('static class', str(context.exception))

    def test_get_controller_returns_none_initially(self):
        """Test get_controller returns None when not set."""
        result = ControllerInstanceManager.get_controller()
        self.assertIsNone(result)

    def test_set_controller_with_valid_controller(self):
        """Test set_controller with valid IController instance."""
        mock_controller = Mock(spec=IController)
        ControllerInstanceManager.set_controller(mock_controller)
        result = ControllerInstanceManager.get_controller()
        self.assertEqual(result, mock_controller)

    def test_set_controller_with_none(self):
        """Test set_controller with None doesn't raise an error."""
        ControllerInstanceManager.set_controller(None)  # type: ignore
        result = ControllerInstanceManager.get_controller()
        self.assertIsNone(result)

    def test_set_controller_with_invalid_type_raises_error(self):
        """Test set_controller with non-IController raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ControllerInstanceManager.set_controller("not a controller")  # type: ignore
        self.assertIn('must be a valid IController object', str(context.exception))

    def test_load_controller_from_file_location_success(self):
        """Test load_controller_from_file_location with valid file."""
        file_location = '/test/path/controller.L5X'
        mock_controller_data = {'RSLogix5000Content': {'Controller': {}}}
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        with patch('controlrox.services.plc.controller.l5x_dict_from_file', return_value=mock_controller_data), \
                patch.object(ControllerFactory, 'create_controller', return_value=mock_controller):

            result = ControllerInstanceManager.load_controller_from_file_location(file_location)

            self.assertIsNotNone(result)
            self.assertEqual(result, mock_controller)
            self.assertEqual(ControllerInstanceManager.get_controller(), mock_controller)

    def test_load_controller_from_file_location_with_path_object(self):
        """Test load_controller_from_file_location with Path object."""
        from pathlib import Path
        file_location = Path('/test/path/controller.L5X')
        mock_controller_data = {'RSLogix5000Content': {'Controller': {}}}
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        with patch('controlrox.services.plc.controller.l5x_dict_from_file', return_value=mock_controller_data), \
                patch.object(ControllerFactory, 'create_controller', return_value=mock_controller):

            result = ControllerInstanceManager.load_controller_from_file_location(file_location)

            self.assertIsNotNone(result)
            self.assertEqual(result, mock_controller)

    def test_load_controller_from_file_location_with_empty_file_location(self):
        """Test load_controller_from_file_location with empty file location."""
        result = ControllerInstanceManager.load_controller_from_file_location('')
        self.assertIsNone(result)

    def test_load_controller_from_file_location_with_none_file_location(self):
        """Test load_controller_from_file_location with None file location."""
        result = ControllerInstanceManager.load_controller_from_file_location(None)  # type: ignore
        self.assertIsNone(result)

    def test_load_controller_from_file_location_with_no_meta_data(self):
        """Test load_controller_from_file_location when meta data fails to load."""
        file_location = '/test/path/controller.L5X'

        with patch('controlrox.services.plc.controller.l5x_dict_from_file', return_value=None):
            result = ControllerInstanceManager.load_controller_from_file_location(file_location)
            self.assertIsNone(result)

    def test_load_controller_from_file_location_with_no_matching_controller(self):
        """Test load_controller_from_file_location when no suitable controller found."""
        file_location = '/test/path/controller.L5X'
        mock_controller_data = {'RSLogix5000Content': {'Controller': {}}}

        with patch('controlrox.services.plc.controller.l5x_dict_from_file', return_value=mock_controller_data), \
                patch.object(ControllerFactory, 'create_controller', return_value=None):

            result = ControllerInstanceManager.load_controller_from_file_location(file_location)
            self.assertIsNone(result)

    def test_load_controller_from_file_location_handles_exception(self):
        """Test load_controller_from_file_location handles exceptions gracefully."""
        file_location = '/test/path/controller.L5X'

        with patch('controlrox.services.plc.controller.l5x_dict_from_file', side_effect=Exception('Test error')):
            result = ControllerInstanceManager.load_controller_from_file_location(file_location)
            self.assertIsNone(result)

    def test_save_controller_to_file_location_success(self):
        """Test save_controller_to_file_location with valid controller."""
        file_location = '/test/path/controller.L5X'
        mock_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController'
                }
            }
        }
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        with patch('controlrox.services.plc.controller.dict_to_l5x_file') as mock_dict_to_l5x, \
                patch('controlrox.services.plc.controller.remove_none_values_inplace'):

            ControllerInstanceManager.save_controller_to_file_location(
                mock_controller,
                file_location
            )

            mock_dict_to_l5x.assert_called_once()

    def test_save_controller_to_file_location_adds_extension(self):
        """Test save_controller_to_file_location adds .L5X extension if missing."""
        file_location = '/test/path/controller'
        mock_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController'
                }
            }
        }
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        with patch('controlrox.services.plc.controller.dict_to_l5x_file') as mock_dict_to_l5x, \
                patch('controlrox.services.plc.controller.remove_none_values_inplace'):

            ControllerInstanceManager.save_controller_to_file_location(
                mock_controller,
                file_location
            )

            # Check that the file location was modified
            call_args = mock_dict_to_l5x.call_args[0]
            self.assertTrue(call_args[1].endswith('.L5X'))

    def test_save_controller_to_file_location_with_path_object(self):
        """Test save_controller_to_file_location with Path object."""
        from pathlib import Path
        file_location = Path('/test/path/controller.L5X')
        mock_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController'
                }
            }
        }
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        with patch('controlrox.services.plc.controller.dict_to_l5x_file') as mock_dict_to_l5x, \
                patch('controlrox.services.plc.controller.remove_none_values_inplace'):

            ControllerInstanceManager.save_controller_to_file_location(
                mock_controller,
                file_location
            )

            mock_dict_to_l5x.assert_called_once()

    def test_save_controller_to_file_location_with_invalid_controller(self):
        """Test save_controller_to_file_location with invalid controller."""
        file_location = '/test/path/controller.L5X'

        with self.assertRaises(ValueError) as context:
            ControllerInstanceManager.save_controller_to_file_location(
                "not a controller",  # type: ignore
                file_location
            )
        self.assertIn('must be a valid Controller object', str(context.exception))

    def test_save_controller_to_file_location_with_none_controller(self):
        """Test save_controller_to_file_location with None controller."""
        file_location = '/test/path/controller.L5X'

        with self.assertRaises(ValueError) as context:
            ControllerInstanceManager.save_controller_to_file_location(
                None,  # type: ignore
                file_location
            )
        self.assertIn('must be a valid Controller object', str(context.exception))

    def test_save_controller_to_file_location_with_invalid_meta_data(self):
        """Test save_controller_to_file_location with invalid meta data."""
        file_location = '/test/path/controller.L5X'
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = {}

        with self.assertRaises(ValueError) as context:
            ControllerInstanceManager.save_controller_to_file_location(
                mock_controller,
                file_location
            )
        self.assertIn('RSLogix5000Content', str(context.exception))

    def test_save_controller_to_file_location_with_extra_keys_in_meta_data(self):
        """Test save_controller_to_file_location filters out extra keys in meta data."""
        file_location = '/test/path/controller.L5X'
        mock_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    '@Name': 'TestController'
                }
            },
            'ExtraKey': 'ShouldNotBeHere'
        }
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        # Extra keys should be filtered out and not cause an error
        with patch('controlrox.services.plc.controller.dict_to_l5x_file') as mock_dict_to_l5x, \
                patch('controlrox.services.plc.controller.remove_none_values_inplace'):

            ControllerInstanceManager.save_controller_to_file_location(
                mock_controller,
                file_location
            )

            # Verify the call was made successfully (extra keys were filtered)
            mock_dict_to_l5x.assert_called_once()
            # Verify only RSLogix5000Content was saved (not the extra key)
            call_args = mock_dict_to_l5x.call_args[0]
            saved_dict = call_args[0]
            self.assertIn('RSLogix5000Content', saved_dict)
            self.assertNotIn('ExtraKey', saved_dict)
            self.assertEqual(len(saved_dict.keys()), 1)

    def test_save_controller_to_file_location_with_invalid_rslogix_content(self):
        """Test save_controller_to_file_location with non-dict RSLogix5000Content."""
        file_location = '/test/path/controller.L5X'
        mock_controller_data = {
            'RSLogix5000Content': 'NotADict'
        }
        mock_controller = Mock(spec=IController)
        mock_controller.get_meta_data.return_value = mock_controller_data

        with self.assertRaises(ValueError) as context:
            ControllerInstanceManager.save_controller_to_file_location(
                mock_controller,
                file_location
            )
        self.assertIn('valid "RSLogix5000Content" dictionary', str(context.exception))

    def test_new_controller_creates_generic_controller(self):
        """Test new_controller creates a generic controller instance."""
        ControllerInstanceManager.set_controller(None)  # Reset any existing controller
        result = ControllerInstanceManager.new_controller()
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
