"""Unit tests for controlrox.models.plc.operand module."""
import unittest

from controlrox.models.plc.operand import LogicOperand


class TestLogixOperand(unittest.TestCase):
    """Test cases for LogixOperand class."""

    def test_init_with_simple_operand(self):
        """Test initialization with simple operand string."""
        operand = LogicOperand('TagName', 0)

        self.assertEqual(operand.meta_data, 'TagName')
        self.assertEqual(operand._arg_position, 0)

    def test_init_with_nested_operand(self):
        """Test initialization with nested operand string."""
        operand = LogicOperand('Tag.Member.SubMember', 1)

        self.assertEqual(operand.meta_data, 'Tag.Member.SubMember')
        self.assertEqual(operand._arg_position, 1)

    def test_meta_data_accepts_string(self):
        """Test meta_data accepts valid string."""
        operand = LogicOperand('TestTag', 0)

        operand.set_meta_data('NewTag')

        self.assertEqual(operand.meta_data, 'NewTag')

    def test_meta_data_accepts_complex_string(self):
        """Test meta_data accepts complex string with dots."""
        operand = LogicOperand('Simple', 0)

        operand.set_meta_data('Complex.Tag.Name')

        self.assertEqual(operand.meta_data, 'Complex.Tag.Name')

    def test_meta_data_can_be_updated(self):
        """Test meta_data can be updated after initialization."""
        operand = LogicOperand('Original', 0)

        operand.meta_data = 'Updated'

        self.assertEqual(operand.meta_data, 'Updated')

    def test_argument_position_property(self):
        """Test argument_position property."""
        operand = LogicOperand('TestTag', 5)

        self.assertEqual(operand.argument_position, 5)

    def test_get_argument_position(self):
        """Test get_argument_position method."""
        operand = LogicOperand('TestTag', 3)

        self.assertEqual(operand.get_argument_position(), 3)

    def test_base_name_simple_operand(self):
        """Test base_name property for simple operand."""
        operand = LogicOperand('SimpleTag', 0)

        self.assertEqual(operand.base_name, 'SimpleTag')

    def test_base_name_nested_operand(self):
        """Test base_name property for nested operand."""
        operand = LogicOperand('Parent.Child.GrandChild', 0)

        self.assertEqual(operand.base_name, 'Parent')

    def test_get_base_name_caching(self):
        """Test get_base_name caches the result."""
        operand = LogicOperand('Tag.Member', 0)

        # First call
        base_name1 = operand.get_base_name()
        # Second call should return cached value
        base_name2 = operand.get_base_name()

        self.assertEqual(base_name1, 'Tag')
        self.assertEqual(base_name2, 'Tag')
        self.assertEqual(operand._base_name, 'Tag')

    def test_trailing_name_simple_operand(self):
        """Test trailing_name property for simple operand."""
        operand = LogicOperand('SimpleTag', 0)

        self.assertEqual(operand.trailing_name, '')

    def test_trailing_name_nested_operand(self):
        """Test trailing_name property for nested operand."""
        operand = LogicOperand('Parent.Child.GrandChild', 0)

        self.assertEqual(operand.trailing_name, '.Child.GrandChild')

    def test_trailing_name_two_level_operand(self):
        """Test trailing_name property for two-level operand."""
        operand = LogicOperand('Parent.Child', 0)

        self.assertEqual(operand.trailing_name, '.Child')

    def test_get_trailing_name(self):
        """Test get_trailing_name method."""
        operand = LogicOperand('A.B.C.D', 0)

        self.assertEqual(operand.get_trailing_name(), '.B.C.D')

    def test_all_parent_operands_simple(self):
        """Test all_parent_operands property for simple operand."""
        operand = LogicOperand('SimpleTag', 0)

        parents = operand.all_parent_operands

        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0], 'SimpleTag')

    def test_all_parent_operands_nested(self):
        """Test all_parent_operands property for nested operand."""
        operand = LogicOperand('A.B.C', 0)

        parents = operand.all_parent_operands

        self.assertEqual(len(parents), 3)
        self.assertEqual(parents[0], 'A.B.C')
        self.assertEqual(parents[1], 'A.B')
        self.assertEqual(parents[2], 'A')

    def test_all_parent_operands_deeply_nested(self):
        """Test all_parent_operands property for deeply nested operand."""
        operand = LogicOperand('Root.Level1.Level2.Level3', 0)

        parents = operand.all_parent_operands

        self.assertEqual(len(parents), 4)
        self.assertEqual(parents[0], 'Root.Level1.Level2.Level3')
        self.assertEqual(parents[1], 'Root.Level1.Level2')
        self.assertEqual(parents[2], 'Root.Level1')
        self.assertEqual(parents[3], 'Root')

    def test_get_all_parent_operands_caching(self):
        """Test get_all_parent_operands caches the result."""
        operand = LogicOperand('A.B.C', 0)

        # First call
        parents1 = operand.get_all_parent_operands()
        # Second call should return cached value
        parents2 = operand.get_all_parent_operands()

        self.assertIs(parents1, parents2)
        self.assertIs(parents1, operand._parents)

    def test_cached_values_initialization(self):
        """Test cached values are initialized empty."""
        operand = LogicOperand('Test', 0)

        self.assertEqual(operand._base_name, '')
        self.assertEqual(operand._parents, [])
        self.assertEqual(operand._trailing_name, '')

    def test_operand_with_array_index(self):
        """Test operand with array index notation."""
        operand = LogicOperand('ArrayTag[5]', 0)

        self.assertEqual(operand.base_name, 'ArrayTag[5]')
        self.assertEqual(operand.trailing_name, '')

    def test_operand_with_array_and_member(self):
        """Test operand with array index and member."""
        operand = LogicOperand('ArrayTag[5].Member', 0)

        self.assertEqual(operand.base_name, 'ArrayTag[5]')
        self.assertEqual(operand.trailing_name, '.Member')

    def test_multiple_property_accesses(self):
        """Test multiple accesses to properties return consistent results."""
        operand = LogicOperand('Parent.Child', 0)

        # Access multiple times
        base1 = operand.base_name
        base2 = operand.base_name
        trail1 = operand.trailing_name
        trail2 = operand.trailing_name

        self.assertEqual(base1, base2)
        self.assertEqual(trail1, trail2)


class TestLogixOperandEdgeCases(unittest.TestCase):
    """Test edge cases for LogixOperand class."""

    def test_empty_string_operand(self):
        """Test operand with empty string."""
        operand = LogicOperand('', 0)

        self.assertEqual(operand.base_name, '')
        self.assertEqual(operand.trailing_name, '')

    def test_operand_with_single_dot(self):
        """Test operand with single trailing dot."""
        operand = LogicOperand('Tag.', 0)

        self.assertEqual(operand.base_name, 'Tag')
        self.assertEqual(operand.trailing_name, '.')

    def test_operand_with_leading_dot(self):
        """Test operand with leading dot."""
        operand = LogicOperand('.Tag', 0)

        self.assertEqual(operand.base_name, '')
        self.assertEqual(operand.trailing_name, '.Tag')

    def test_operand_with_multiple_consecutive_dots(self):
        """Test operand with multiple consecutive dots."""
        operand = LogicOperand('Tag..Member', 0)

        self.assertEqual(operand.base_name, 'Tag')
        # Empty string between dots creates empty element
        self.assertIn('..Member', operand.trailing_name)

    def test_operand_with_special_characters(self):
        """Test operand with special characters."""
        operand = LogicOperand('Tag_123.Member$Name', 0)

        self.assertEqual(operand.base_name, 'Tag_123')
        self.assertEqual(operand.trailing_name, '.Member$Name')

    def test_operand_with_spaces(self):
        """Test operand with spaces."""
        operand = LogicOperand('Tag Name.Member', 0)

        self.assertEqual(operand.base_name, 'Tag Name')
        self.assertEqual(operand.trailing_name, '.Member')

    def test_large_argument_position(self):
        """Test operand with large argument position."""
        operand = LogicOperand('Tag', 9999)

        self.assertEqual(operand.argument_position, 9999)

    def test_negative_argument_position(self):
        """Test operand with negative argument position."""
        operand = LogicOperand('Tag', -1)

        self.assertEqual(operand.argument_position, -1)

    def test_zero_argument_position(self):
        """Test operand with zero argument position."""
        operand = LogicOperand('Tag', 0)

        self.assertEqual(operand.argument_position, 0)


class TestLogixOperandInheritance(unittest.TestCase):
    """Test LogixOperand inheritance and interface compliance."""

    def test_inherits_from_plc_object(self):
        """Test LogixOperand inherits from PlcObject."""
        from controlrox.models.plc.meta import PlcObject

        operand = LogicOperand('Test', 0)

        self.assertIsInstance(operand, PlcObject)

    def test_implements_ilogic_operand(self):
        """Test LogixOperand implements ILogicOperand."""
        from controlrox.interfaces import ILogicOperand

        operand = LogicOperand('Test', 0)

        self.assertIsInstance(operand, ILogicOperand)

    def test_has_name_property_from_plc_object(self):
        """Test LogixOperand has name property from PlcObject."""
        operand = LogicOperand('TestTag', 0)

        # Should have name property from PlcObject
        self.assertTrue(hasattr(operand, 'name'))

    def test_meta_data_stored_correctly(self):
        """Test meta_data is stored and accessible."""
        operand = LogicOperand('StoredTag', 2)

        self.assertEqual(operand.meta_data, 'StoredTag')
        self.assertEqual(str(operand.meta_data), 'StoredTag')


class TestLogicOperandWithController(unittest.TestCase):
    """Test LogicOperand with controller integration."""

    def test_initialization_with_controller(self):
        """Test operand can be initialized with controller context."""
        from unittest.mock import Mock
        from controlrox.interfaces import IController

        controller = Mock(spec=IController)
        operand = LogicOperand('Tag.Member', 0)
        operand._controller = controller

        self.assertIsNotNone(operand._controller)
        self.assertEqual(operand.meta_data, 'Tag.Member')

    def test_operand_without_controller(self):
        """Test operand works without controller."""
        operand = LogicOperand('Tag.Member', 0)

        self.assertEqual(operand.base_name, 'Tag')
        self.assertEqual(operand.trailing_name, '.Member')

    def test_controller_access_methods(self):
        """Test operand methods work regardless of controller presence."""
        operand = LogicOperand('A.B.C', 1)

        self.assertEqual(operand.get_base_name(), 'A')
        self.assertEqual(operand.get_argument_position(), 1)
        self.assertEqual(len(operand.get_all_parent_operands()), 3)


class TestLogicOperandMetaData(unittest.TestCase):
    """Test LogicOperand metadata handling."""

    def test_meta_data_string_type(self):
        """Test meta_data is stored as string."""
        operand = LogicOperand('TestOperand', 0)

        self.assertIsInstance(operand.meta_data, str)
        self.assertEqual(operand.meta_data, 'TestOperand')

    def test_meta_data_empty_string(self):
        """Test meta_data with empty string."""
        operand = LogicOperand('', 0)

        self.assertEqual(operand.meta_data, '')
        self.assertEqual(operand.base_name, '')

    def test_meta_data_with_special_characters(self):
        """Test meta_data with special characters."""
        operand = LogicOperand('Tag_123$ABC.Member[5]', 0)

        self.assertEqual(operand.meta_data, 'Tag_123$ABC.Member[5]')
        self.assertEqual(operand.base_name, 'Tag_123$ABC')

    def test_meta_data_long_string(self):
        """Test meta_data with very long string."""
        long_name = 'A' * 1000
        operand = LogicOperand(long_name, 0)

        self.assertEqual(len(operand.meta_data), 1000)
        self.assertEqual(operand.base_name, long_name)


class TestLogicOperandArgumentPosition(unittest.TestCase):
    """Test LogicOperand argument position handling."""

    def test_argument_position_zero(self):
        """Test argument position of zero."""
        operand = LogicOperand('Tag', 0)

        self.assertEqual(operand.argument_position, 0)
        self.assertEqual(operand.get_argument_position(), 0)

    def test_argument_position_positive(self):
        """Test positive argument position."""
        operand = LogicOperand('Tag', 5)

        self.assertEqual(operand.argument_position, 5)

    def test_argument_position_negative(self):
        """Test negative argument position."""
        operand = LogicOperand('Tag', -1)

        self.assertEqual(operand.argument_position, -1)

    def test_argument_position_large_value(self):
        """Test large argument position value."""
        operand = LogicOperand('Tag', 999999)

        self.assertEqual(operand.argument_position, 999999)

    def test_argument_position_immutable(self):
        """Test argument position is stored correctly."""
        operand = LogicOperand('Tag', 3)

        self.assertEqual(operand._arg_position, 3)
        self.assertEqual(operand.get_argument_position(), 3)


class TestLogicOperandBaseNameExtended(unittest.TestCase):
    """Test LogicOperand base name extraction - extended cases."""

    def test_base_name_caching_behavior(self):
        """Test base_name caching works correctly."""
        operand = LogicOperand('Root.Branch.Leaf', 0)

        # First access triggers computation
        base1 = operand.get_base_name()
        # Verify cached
        self.assertEqual(operand._base_name, 'Root')
        # Second access uses cache
        base2 = operand.get_base_name()

        self.assertEqual(base1, base2)
        self.assertEqual(base1, 'Root')

    def test_base_name_property_vs_method(self):
        """Test base_name property and get_base_name method consistency."""
        operand = LogicOperand('Tag.Member', 0)

        prop_result = operand.base_name
        method_result = operand.get_base_name()

        self.assertEqual(prop_result, method_result)
        self.assertEqual(prop_result, 'Tag')

    def test_base_name_with_array_notation(self):
        """Test base_name with array notation."""
        operand = LogicOperand('Array[10].Member', 0)

        self.assertEqual(operand.base_name, 'Array[10]')

    def test_base_name_with_multidimensional_array(self):
        """Test base_name with multidimensional array."""
        operand = LogicOperand('Array[5,10].Member', 0)

        self.assertEqual(operand.base_name, 'Array[5,10]')


class TestLogicOperandTrailingNameExtended(unittest.TestCase):
    """Test LogicOperand trailing name extraction - extended cases."""

    def test_trailing_name_single_level(self):
        """Test trailing_name with single level nesting."""
        operand = LogicOperand('Parent.Child', 0)

        self.assertEqual(operand.trailing_name, '.Child')

    def test_trailing_name_multiple_levels(self):
        """Test trailing_name with multiple levels."""
        operand = LogicOperand('A.B.C.D.E', 0)

        self.assertEqual(operand.trailing_name, '.B.C.D.E')

    def test_trailing_name_no_nesting(self):
        """Test trailing_name with no nesting."""
        operand = LogicOperand('SimpleTag', 0)

        self.assertEqual(operand.trailing_name, '')
        self.assertEqual(operand.get_trailing_name(), '')

    def test_trailing_name_with_array(self):
        """Test trailing_name with array in trailing part."""
        operand = LogicOperand('Tag.Member[5]', 0)

        self.assertEqual(operand.trailing_name, '.Member[5]')


class TestLogicOperandParentOperandsExtended(unittest.TestCase):
    """Test LogicOperand parent operands extraction - extended cases."""

    def test_parent_operands_caching(self):
        """Test parent operands list is cached."""
        operand = LogicOperand('A.B.C.D', 0)

        parents1 = operand.get_all_parent_operands()
        parents2 = operand.get_all_parent_operands()

        # Should be the same list object (cached)
        self.assertIs(parents1, parents2)

    def test_parent_operands_order(self):
        """Test parent operands are in correct order (full to base)."""
        operand = LogicOperand('Root.Level1.Level2', 0)

        parents = operand.all_parent_operands

        self.assertEqual(parents[0], 'Root.Level1.Level2')
        self.assertEqual(parents[1], 'Root.Level1')
        self.assertEqual(parents[2], 'Root')

    def test_parent_operands_single_tag(self):
        """Test parent operands for non-nested tag."""
        operand = LogicOperand('SingleTag', 0)

        parents = operand.get_all_parent_operands()

        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0], 'SingleTag')

    def test_parent_operands_property_vs_method(self):
        """Test all_parent_operands property matches method."""
        operand = LogicOperand('A.B.C', 0)

        prop_result = operand.all_parent_operands
        method_result = operand.get_all_parent_operands()

        self.assertEqual(prop_result, method_result)


class TestLogicOperandCachingBehavior(unittest.TestCase):
    """Test LogicOperand caching behavior comprehensively."""

    def test_all_caches_initialized_empty(self):
        """Test all cache values start empty."""
        operand = LogicOperand('Test.Tag', 0)

        self.assertEqual(operand._base_name, '')
        self.assertEqual(operand._parents, [])
        self.assertEqual(operand._trailing_name, '')

    def test_base_name_cache_persistence(self):
        """Test base_name cache persists after first access."""
        operand = LogicOperand('Tag.Member', 0)

        # Access to populate cache
        _ = operand.base_name

        self.assertEqual(operand._base_name, 'Tag')

    def test_parents_cache_persistence(self):
        """Test parents cache persists after first access."""
        operand = LogicOperand('A.B', 0)

        # Access to populate cache
        _ = operand.all_parent_operands

        self.assertEqual(len(operand._parents), 2)
        self.assertIsInstance(operand._parents, list)

    def test_multiple_cache_accesses(self):
        """Test multiple accesses use cached values."""
        operand = LogicOperand('Root.Branch.Leaf', 0)

        # First accesses
        base1 = operand.base_name
        parents1 = operand.all_parent_operands

        # Second accesses should use cache
        base2 = operand.base_name
        parents2 = operand.all_parent_operands

        self.assertEqual(base1, base2)
        self.assertIs(parents1, parents2)


class TestLogicOperandStringRepresentation(unittest.TestCase):
    """Test LogicOperand string representation."""

    def test_str_representation(self):
        """Test __str__ returns name from PlcObject."""
        operand = LogicOperand('TestTag.Member', 2)

        result = str(operand)

        # PlcObject's __str__ returns name, which may be empty for operands
        self.assertIsInstance(result, str)

    def test_repr_representation(self):
        """Test __repr__ returns useful representation."""
        operand = LogicOperand('Tag', 0)

        result = repr(operand)

        self.assertIsInstance(result, str)

    def test_name_property_from_plc_object(self):
        """Test name property inherited from PlcObject."""
        operand = LogicOperand('Tag', 0)

        # PlcObject provides name property
        self.assertTrue(hasattr(operand, 'name'))
        self.assertIsInstance(operand.name, str)


class TestLogicOperandComplexScenarios(unittest.TestCase):
    """Test LogicOperand complex real-world scenarios."""

    def test_udt_member_access(self):
        """Test UDT member access pattern."""
        operand = LogicOperand('MyUDT.Member1.SubMember', 0)

        self.assertEqual(operand.base_name, 'MyUDT')
        self.assertEqual(operand.trailing_name, '.Member1.SubMember')
        self.assertEqual(len(operand.all_parent_operands), 3)

    def test_array_of_udt(self):
        """Test array of UDT pattern."""
        operand = LogicOperand('UDTArray[5].Member', 0)

        self.assertEqual(operand.base_name, 'UDTArray[5]')
        self.assertEqual(operand.trailing_name, '.Member')

    def test_deeply_nested_structure(self):
        """Test deeply nested structure."""
        operand = LogicOperand('Root.L1.L2.L3.L4.L5', 0)

        parents = operand.all_parent_operands

        self.assertEqual(len(parents), 6)
        self.assertEqual(parents[0], 'Root.L1.L2.L3.L4.L5')
        self.assertEqual(parents[-1], 'Root')

    def test_mixed_array_and_members(self):
        """Test mixed array indices and member access."""
        operand = LogicOperand('Array[1].Member[2].Value', 1)

        self.assertEqual(operand.base_name, 'Array[1]')
        self.assertEqual(operand.argument_position, 1)


class TestLogicOperandEdgeCasesExtended(unittest.TestCase):
    """Test LogicOperand additional edge cases."""

    def test_operand_only_dots(self):
        """Test operand with only dots."""
        operand = LogicOperand('...', 0)

        base = operand.base_name
        trail = operand.trailing_name

        self.assertEqual(base, '')
        self.assertIn('..', trail)

    def test_operand_unicode_characters(self):
        """Test operand with unicode characters."""
        operand = LogicOperand('Tägñame.Mëmber', 0)

        self.assertEqual(operand.base_name, 'Tägñame')
        self.assertEqual(operand.trailing_name, '.Mëmber')

    def test_very_long_nested_operand(self):
        """Test very long nested operand path."""
        parts = [f'Level{i}' for i in range(50)]
        long_operand = '.'.join(parts)
        operand = LogicOperand(long_operand, 0)

        parents = operand.all_parent_operands

        self.assertEqual(len(parents), 50)
        self.assertEqual(operand.base_name, 'Level0')

    def test_operand_with_whitespace(self):
        """Test operand with various whitespace."""
        operand = LogicOperand('Tag Name With Spaces.Member', 0)

        self.assertEqual(operand.base_name, 'Tag Name With Spaces')

    def test_operand_method_consistency(self):
        """Test all methods return consistent results."""
        operand = LogicOperand('Consistent.Tag.Name', 5)

        # Multiple calls should be consistent
        for _ in range(3):
            self.assertEqual(operand.base_name, 'Consistent')
            self.assertEqual(operand.trailing_name, '.Tag.Name')
            self.assertEqual(operand.argument_position, 5)
            self.assertEqual(len(operand.all_parent_operands), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
