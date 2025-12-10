"""Unit tests for operand.py module."""

import unittest
from controlrox.models.plc.rockwell.operand import LogixOperand


class TestLogixOperand(unittest.TestCase):
    """Test cases for LogixOperand class."""

    def test_init_valid_string_meta_data(self):
        """Test LogixOperand initialization with valid string metadata."""
        operand = LogixOperand(meta_data='TestTag.Value', arg_position=0)

        self.assertEqual(operand.meta_data, 'TestTag.Value')
        self.assertEqual(operand._arg_position, 0)

    def test_init_invalid_meta_data_type(self):
        """Test LogixOperand initialization with invalid metadata type."""
        with self.assertRaises(TypeError) as context:
            LogixOperand(meta_data={'not': 'string'}, arg_position=0)  # type: ignore

        self.assertIn("Meta data must be a string!", str(context.exception))

    def test_get_argument_position(self):
        """Test get_argument_position method."""
        operand = LogixOperand('TestTag', 2)
        self.assertEqual(operand.get_argument_position(), 2)

    def test_get_base_name_simple(self):
        """Test get_base_name with simple tag name."""
        operand = LogixOperand('SimpleTag', 0)
        self.assertEqual(operand.get_base_name(), 'SimpleTag')

    def test_get_base_name_complex(self):
        """Test get_base_name with complex tag name."""
        operand = LogixOperand('ComplexTag.Member.SubMember', 0)
        self.assertEqual(operand.get_base_name(), 'ComplexTag')

    def test_get_base_name_cached(self):
        """Test get_base_name caching."""
        operand = LogixOperand('TestTag.Value', 0)

        # First access
        first_result = operand.get_base_name()
        self.assertEqual(first_result, 'TestTag')

        # Cached access
        operand._base_name = 'CachedName'
        second_result = operand.get_base_name()
        self.assertEqual(second_result, 'CachedName')

    def test_parents_property_simple_tag(self):
        """Test parents property with simple tag."""
        operand = LogixOperand('SimpleTag', 0)
        self.assertEqual(operand.get_all_parent_operands(), ['SimpleTag'])

    def test_parents_property_complex_tag(self):
        """Test parents property with complex tag."""
        operand = LogixOperand('Tag.Member.SubMember', 0)
        expected_parents = ['Tag.Member.SubMember', 'Tag.Member', 'Tag']
        self.assertEqual(operand.get_all_parent_operands(), expected_parents)

    def test_parents_property_cached(self):
        """Test parents property caching."""
        operand = LogixOperand('Tag.Member', 0)

        # First access
        _ = operand.get_all_parent_operands()

        # Cached access
        operand._parents = ['Cached']
        self.assertEqual(operand.get_all_parent_operands(), ['Cached'])

    def test_trailing_name_simple_tag(self):
        """Test trailing_name property with simple tag."""
        operand = LogixOperand('SimpleTag', 0)
        self.assertEqual(operand.trailing_name, '')

    def test_trailing_name_complex_tag(self):
        """Test trailing_name property with complex tag."""
        operand = LogixOperand('Tag.Member.SubMember', 0)
        self.assertEqual(operand.trailing_name, '.Member.SubMember')

    def test_trailing_name_empty_meta_data(self):
        """Test trailing_name property with empty metadata."""
        operand = LogixOperand('', 0)
        name = operand.get_trailing_name()
        self.assertEqual(name, '')

    def test_invalidate(self):
        """Test invalidate method raises NotImplementedError."""
        operand = LogixOperand('TestTag', 0)
        with self.assertRaises(NotImplementedError):
            operand.invalidate()


class TestLogixOperandEdgeCases(unittest.TestCase):
    """Test edge cases for LogixOperand."""

    def test_empty_meta_data(self):
        """Test operand with empty string metadata."""
        operand = LogixOperand('', 0)
        self.assertEqual(operand.meta_data, '')
        self.assertEqual(operand.get_base_name(), '')
        self.assertEqual(operand.get_all_parent_operands(), [''])

    def test_single_character_meta_data(self):
        """Test operand with single character metadata."""
        operand = LogixOperand('T', 0)
        self.assertEqual(operand.get_base_name(), 'T')
        self.assertEqual(operand.get_all_parent_operands(), ['T'])
        self.assertEqual(operand.get_trailing_name(), '')

    def test_meta_data_with_multiple_dots(self):
        """Test operand with metadata containing multiple consecutive dots."""
        operand = LogixOperand('Tag..Member...Sub', 0)
        self.assertEqual(operand.get_base_name(), 'Tag')
        self.assertEqual(operand.trailing_name, '..Member...Sub')

    def test_meta_data_starting_with_dot(self):
        """Test operand with metadata starting with dot."""
        operand = LogixOperand('.Tag.Member', 0)
        self.assertEqual(operand.get_base_name(), '')
        self.assertEqual(operand.trailing_name, '.Tag.Member')

    def test_meta_data_ending_with_dot(self):
        """Test operand with metadata ending with dot."""
        operand = LogixOperand('Tag.Member.', 0)
        self.assertEqual(operand.get_base_name(), 'Tag')
        self.assertEqual(operand.trailing_name, '.Member.')


if __name__ == '__main__':
    unittest.main(verbosity=2)
