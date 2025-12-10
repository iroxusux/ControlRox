"""Comprehensive unit tests for matcher.py module."""
import unittest
from unittest.mock import Mock, patch

from controlrox.services import (
    ControllerMatcher,
    ControllerMatcherFactory
)
from controlrox.models.plc.rockwell.controller import RaController
from pyrox.models.abc.meta import PyroxObject
from pyrox.models.abc.factory import FactoryTypeMeta, MetaFactory


class TestControllerMatcherFactory(unittest.TestCase):
    """Test cases for ControllerMatcherFactory class."""

    def test_inheritance(self):
        """Test that ControllerMatcherFactory inherits from MetaFactory."""
        self.assertTrue(issubclass(ControllerMatcherFactory, MetaFactory))


class TestControllerMatcher(unittest.TestCase):
    """Test cases for ControllerMatcher class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestMatcher(ControllerMatcher):
            @staticmethod
            def get_datatype_patterns():
                return ['*TestDataType*', 'CustomType']

            @staticmethod
            def get_module_patterns():
                return ['*TestModule*', 'IO_Module']

            @staticmethod
            def get_program_patterns():
                return ['*TestProgram*', 'MainProgram']

            @staticmethod
            def get_safety_program_patterns():
                return ['*SafetyProgram*', 'SafeTest']

            @staticmethod
            def get_tag_patterns():
                return ['*TestTag*', 'GlobalTag']

            @classmethod
            def get_controller_constructor(cls):
                return RaController

        self.test_matcher = TestMatcher

        # Sample controller data for testing
        self.sample_controller_data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'TestDataType1'},
                            {'@Name': 'StandardType'},
                            {'@Name': 'CustomType'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'TestModule1'},
                            {'@Name': 'StandardModule'},
                            {'@Name': 'IO_Module'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {'@Name': 'TestProgram1', '@Class': 'Standard'},
                            {'@Name': 'MainProgram', '@Class': 'Standard'},
                            {'@Name': 'SafetyProgram1', '@Class': 'Safety'},
                            {'@Name': 'SafeTest', '@Class': 'Safety'}
                        ]
                    },
                    'Tags': {
                        'Tag': [
                            {'@Name': 'TestTag1'},
                            {'@Name': 'StandardTag'},
                            {'@Name': 'GlobalTag'}
                        ]
                    }
                }
            }
        }

        self.empty_controller_data = {
            'RSLogix5000Content': {
                'Controller': {}
            }
        }

    def test_metaclass(self):
        """Test that ControllerMatcher uses the correct metaclass."""
        # The metaclass should be FactoryTypeMeta
        self.assertIsInstance(ControllerMatcher.__class__, type(FactoryTypeMeta))

    def test_supports_registering_base_class(self):
        """Test that base ControllerMatcher class cannot be registered."""
        self.assertFalse(ControllerMatcher.supports_registering)

    def test_supports_registering_subclass(self):
        """Test that subclasses can be registered."""
        self.assertTrue(self.test_matcher.supports_registering)

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise NotImplementedError in base class."""
        with self.assertRaises(NotImplementedError):
            ControllerMatcher.get_datatype_patterns()

        with self.assertRaises(NotImplementedError):
            ControllerMatcher.get_module_patterns()

        with self.assertRaises(NotImplementedError):
            ControllerMatcher.get_program_patterns()

        with self.assertRaises(NotImplementedError):
            ControllerMatcher.get_safety_program_patterns()

        with self.assertRaises(NotImplementedError):
            ControllerMatcher.get_tag_patterns()

        with self.assertRaises(NotImplementedError):
            ControllerMatcher.get_controller_constructor()

    def test_concrete_methods_implemented(self):
        """Test that concrete subclass implements abstract methods."""
        self.assertEqual(self.test_matcher.get_datatype_patterns(), ['*TestDataType*', 'CustomType'])
        self.assertEqual(self.test_matcher.get_module_patterns(), ['*TestModule*', 'IO_Module'])
        self.assertEqual(self.test_matcher.get_program_patterns(), ['*TestProgram*', 'MainProgram'])
        self.assertEqual(self.test_matcher.get_safety_program_patterns(), ['*SafetyProgram*', 'SafeTest'])
        self.assertEqual(self.test_matcher.get_tag_patterns(), ['*TestTag*', 'GlobalTag'])
        self.assertEqual(self.test_matcher.get_controller_constructor(), RaController)

    def test_calculate_score_perfect_match(self):
        """Test calculate_score with perfect match (all patterns match)."""
        score = self.test_matcher.calculate_score(self.sample_controller_data)
        self.assertEqual(score, 1.0)  # All 5 categories match (0.2 each)

    def test_calculate_score_partial_match(self):
        """Test calculate_score with partial match."""
        # Create data that only matches some patterns
        partial_data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'TestDataType1'}  # Matches datatype pattern
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {'@Name': 'TestProgram1', '@Class': 'Standard'}  # Matches program pattern
                        ]
                    }
                    # Missing modules, tags, and safety programs
                }
            }
        }
        score = self.test_matcher.calculate_score(partial_data)
        self.assertEqual(score, 0.4)  # 2 out of 5 categories match

    def test_calculate_score_no_match(self):
        """Test calculate_score with no matches."""
        no_match_data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {
                        'DataType': [
                            {'@Name': 'NoMatchType'}
                        ]
                    },
                    'Modules': {
                        'Module': [
                            {'@Name': 'NoMatchModule'}
                        ]
                    },
                    'Programs': {
                        'Program': [
                            {'@Name': 'NoMatchProgram', '@Class': 'Standard'}
                        ]
                    },
                    'Tags': {
                        'Tag': [
                            {'@Name': 'NoMatchTag'}
                        ]
                    }
                }
            }
        }
        score = self.test_matcher.calculate_score(no_match_data)
        self.assertEqual(score, 0.0)

    def test_can_match_base_class(self):
        """Test that base ControllerMatcher cannot match."""
        self.assertFalse(ControllerMatcher.can_match())

    def test_get_class(self):
        """Test get_class method returns the class itself."""
        self.assertEqual(self.test_matcher.get_class(), self.test_matcher)

    def test_get_factory(self):
        """Test get_factory method returns ControllerMatcherFactory."""
        self.assertEqual(self.test_matcher.get_factory(), ControllerMatcherFactory)

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_controller_datatypes(self, mock_check_patterns):
        """Test check_controller_datatypes method."""
        mock_check_patterns.return_value = True

        result = self.test_matcher.check_controller_datatypes(self.sample_controller_data)

        self.assertTrue(result)
        mock_check_patterns.assert_called_once_with(
            ['TestDataType1', 'StandardType', 'CustomType'],
            ['*TestDataType*', 'CustomType']
        )

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_controller_modules(self, mock_check_patterns):
        """Test check_controller_modules method."""
        mock_check_patterns.return_value = True

        result = self.test_matcher.check_controller_modules(self.sample_controller_data)

        self.assertTrue(result)
        mock_check_patterns.assert_called_once_with(
            ['TestModule1', 'StandardModule', 'IO_Module'],
            ['*TestModule*', 'IO_Module']
        )

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_controller_programs(self, mock_check_patterns):
        """Test check_controller_programs method."""
        mock_check_patterns.return_value = True

        result = self.test_matcher.check_controller_programs(self.sample_controller_data)

        self.assertTrue(result)
        mock_check_patterns.assert_called_once_with(
            ['TestProgram1', 'MainProgram', 'SafetyProgram1', 'SafeTest'],
            ['*TestProgram*', 'MainProgram']
        )

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_controller_safety_programs(self, mock_check_patterns):
        """Test check_controller_safety_programs method."""
        mock_check_patterns.return_value = True

        result = self.test_matcher.check_controller_safety_programs(self.sample_controller_data)

        self.assertTrue(result)
        mock_check_patterns.assert_called_once_with(
            ['SafetyProgram1', 'SafeTest'],  # Only safety programs
            ['*SafetyProgram*', 'SafeTest']
        )

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_controller_tags(self, mock_check_patterns):
        """Test check_controller_tags method."""
        mock_check_patterns.return_value = True

        result = self.test_matcher.check_controller_tags(self.sample_controller_data)

        self.assertTrue(result)
        mock_check_patterns.assert_called_once_with(
            ['TestTag1', 'StandardTag', 'GlobalTag'],
            ['*TestTag*', 'GlobalTag']
        )

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_dict_list_for_patterns_empty_patterns(self, mock_check_patterns):
        """Test check_dict_list_for_patterns with empty patterns."""
        dict_list = [{'@Name': 'Test'}]
        result = self.test_matcher.check_dict_list_for_patterns(dict_list, '@Name', [])

        self.assertFalse(result)
        mock_check_patterns.assert_not_called()

    @patch('controlrox.services.plc.controller.check_wildcard_patterns')
    def test_check_dict_list_for_patterns_valid(self, mock_check_patterns):
        """Test check_dict_list_for_patterns with valid input."""
        mock_check_patterns.return_value = True
        dict_list = [
            {'@Name': 'Test1'},
            {'@Name': 'Test2'},
            {'@Other': 'Value'}
        ]
        patterns = ['Test*']

        result = self.test_matcher.check_dict_list_for_patterns(dict_list, '@Name', patterns)

        self.assertTrue(result)
        mock_check_patterns.assert_called_once_with(['Test1', 'Test2', ''], patterns)

    def test_get_controller_meta_valid_data(self):
        """Test get_controller_meta with valid controller data."""
        meta = self.test_matcher.get_controller_meta(self.sample_controller_data)
        expected = self.sample_controller_data['RSLogix5000Content']['Controller']
        self.assertEqual(meta, expected)

    def test_get_controller_meta_empty_data(self):
        """Test get_controller_meta with empty controller data."""
        with self.assertRaises(ValueError) as context:
            self.test_matcher.get_controller_meta({})
        self.assertIn("No controller data provided", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.test_matcher.get_controller_meta(None)  # type: ignore
        self.assertIn("No controller data provided", str(context.exception))

    def test_get_controller_data_list_valid(self):
        """Test get_controller_data_list with valid data."""
        result = self.test_matcher.get_controller_data_list(self.sample_controller_data, 'DataType')
        expected = [
            {'@Name': 'TestDataType1'},
            {'@Name': 'StandardType'},
            {'@Name': 'CustomType'}
        ]
        self.assertEqual(result, expected)

    def test_get_controller_data_list_single_item(self):
        """Test get_controller_data_list when single item is returned as dict."""
        single_item_data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {
                        'DataType': {'@Name': 'SingleType'}  # Single dict, not list
                    }
                }
            }
        }
        result = self.test_matcher.get_controller_data_list(single_item_data, 'DataType')
        expected = [{'@Name': 'SingleType'}]
        self.assertEqual(result, expected)

    def test_get_controller_data_list_missing_data(self):
        """Test get_controller_data_list with missing data sections."""
        result = self.test_matcher.get_controller_data_list(self.empty_controller_data, 'DataType')
        self.assertEqual(result, [])

    def test_get_controller_data_list_no_controller_meta(self):
        """Test get_controller_data_list when controller meta is None."""
        invalid_data = {'RSLogix5000Content': {}}
        result = self.test_matcher.get_controller_data_list(invalid_data, 'DataType')
        self.assertEqual(result, [])


class TestControllerMatcherEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for ControllerMatcher."""

    def setUp(self):
        """Set up test fixtures for edge case testing."""
        class EdgeCaseMatcher(ControllerMatcher):
            @staticmethod
            def get_datatype_patterns():
                return []

            @staticmethod
            def get_module_patterns():
                return []

            @staticmethod
            def get_program_patterns():
                return []

            @staticmethod
            def get_safety_program_patterns():
                return []

            @staticmethod
            def get_tag_patterns():
                return []

            @classmethod
            def get_controller_constructor(cls):
                return RaController

        self.edge_matcher = EdgeCaseMatcher

    def test_malformed_controller_data(self):
        """Test behavior with malformed controller data."""
        malformed_data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': 'not_a_dict',  # Invalid structure
                    'Programs': {
                        'Program': 'not_a_list'  # Invalid structure
                    }
                }
            }
        }

        # The current implementation will fail on malformed data
        # This test documents the current behavior
        with self.assertRaises(AttributeError):
            self.edge_matcher.get_controller_data_list(malformed_data, 'DataType')

    def test_missing_rslogix_content(self):
        """Test behavior when RSLogix5000Content is missing."""
        invalid_data = {'SomeOtherContent': {}}

        result = self.edge_matcher.get_controller_data_list(invalid_data, 'DataType')
        self.assertEqual(result, [])

    def test_empty_pattern_lists(self):
        """Test behavior when all pattern lists are empty."""
        sample_data = {
            'RSLogix5000Content': {
                'Controller': {
                    'DataTypes': {'DataType': [{'@Name': 'Test'}]}
                }
            }
        }

        score = self.edge_matcher.calculate_score(sample_data)
        self.assertEqual(score, 0.0)  # No patterns to match


if __name__ == '__main__':
    unittest.main()
