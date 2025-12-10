"""Unit tests for the datatype module."""

import unittest
from unittest.mock import Mock, patch

from controlrox.models.plc.rockwell.datatype import RaDatatype, RaDatatypeMember, BUILTINS
from controlrox.models.plc.rockwell import meta as plc_meta
from controlrox.models.plc.rockwell import RaController


class TestRaDatatypeMember(unittest.TestCase):
    """Test cases for RaDatatypeMember class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b

        self.mock_parent_datatype = Mock(spec=RaDatatype)

        self.sample_member_data = {
            '@Name': 'TestMember',
            '@DataType': 'BOOL',
            '@Dimension': '0',
            '@Hidden': 'false',
            'Description': 'Test member description'
        }

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_initialization(self, mock_get_controller):
        """Test RaDatatypeMember initialization."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.name, 'TestMember')
        self.assertIs(member._parent_datatype, self.mock_parent_datatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_datatype_property(self, mock_get_controller):
        """Test datatype property getter."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.datatype.name, 'BOOL')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_dimension_property(self, mock_get_controller):
        """Test dimension property getter."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.dimension, '0')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_hidden_property(self, mock_get_controller):
        """Test hidden property getter."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertFalse(member.hidden)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_hidden_property_true(self, mock_get_controller):
        """Test hidden property when set to true."""
        mock_get_controller.return_value = self.mock_controller
        member_data = self.sample_member_data.copy()
        member_data['@Hidden'] = 'true'

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertTrue(member.hidden)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    def test_is_atomic_true_for_atomic_datatype(self):
        """Test is_atomic property returns True for atomic datatypes."""
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype,
        )

        self.assertTrue(member.is_atomic())

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['DINT', 'REAL'])
    def test_is_atomic_false_for_non_atomic_datatype(self):
        """Test is_atomic property returns False for non-atomic datatypes."""
        member_data = self.sample_member_data.copy()
        member_data['@DataType'] = 'CustomDatatype'

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertFalse(member.is_atomic())

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_parent_datatype_property(self, mock_get_controller):
        """Test parent_datatype property getter."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertIs(member.parent_datatype, self.mock_parent_datatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_different_datatypes(self, mock_get_controller):
        """Test member with different datatypes."""
        datatypes = ['DINT', 'REAL', 'STRING', 'CustomType']
        mock_get_controller.return_value = self.mock_controller

        customtype = Mock(spec=RaDatatype)
        customtype.name = 'CustomType'
        self.mock_controller.datatypes['CustomType'] = customtype

        for datatype in datatypes:
            member_data = self.sample_member_data.copy()
            member_data['@DataType'] = datatype

            member = RaDatatypeMember(
                meta_data=member_data,
                parent_datatype=self.mock_parent_datatype
            )

            self.assertEqual(member.datatype.name, datatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_inheritance_from_named_plc_object(self, mock_get_controller):
        """Test that RaDatatypeMember inherits from NamedPlcObject."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertIsInstance(member, plc_meta.RaPlcObject)
        self.assertTrue(hasattr(member, 'name'))
        self.assertTrue(hasattr(member, 'description'))

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_builtin_for_atomic_datatype(self, mock_get_controller):
        """Test is_builtin returns True for built-in datatypes."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        # BOOL is a built-in datatype
        self.assertTrue(member.is_builtin())

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_builtin_for_custom_datatype(self, mock_get_controller):
        """Test is_builtin returns False for custom datatypes."""
        custom_datatype = Mock(spec=RaDatatype)
        custom_datatype.name = 'CustomType'
        custom_datatype.is_builtin.return_value = False
        self.mock_controller.datatypes['CustomType'] = custom_datatype
        mock_get_controller.return_value = self.mock_controller

        member_data = self.sample_member_data.copy()
        member_data['@DataType'] = 'CustomType'

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype,
        )

        self.assertFalse(member.is_builtin())

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_set_dimension(self, mock_get_controller):
        """Test set_dimension modifies dimension value."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.get_dimension(), '0')

        member.set_dimension('10')

        self.assertEqual(member.get_dimension(), '10')
        self.assertEqual(member['@Dimension'], '10')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_set_dimension_with_string(self, mock_get_controller):
        """Test set_dimension accepts string values."""
        mock_get_controller.return_value = self.mock_controller
        member = RaDatatypeMember(
            meta_data=self.sample_member_data,
            parent_datatype=self.mock_parent_datatype
        )

        member.set_dimension('100')

        self.assertEqual(member.get_dimension(), '100')


class TestDatatype(unittest.TestCase):
    """Test cases for Datatype class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_controller = Mock(spec=RaController)

        # Mock controller.datatypes for endpoint operand testing
        self.mock_controller.datatypes = BUILTINS

        self.sample_datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Description': 'Test datatype description',
            'Members': {
                'Member': [
                    {
                        '@Name': 'BoolMember',
                        '@DataType': 'BOOL',
                        '@Dimension': '0',
                        '@Hidden': 'false'
                    },
                    {
                        '@Name': 'IntMember',
                        '@DataType': 'DINT',
                        '@Dimension': '0',
                        '@Hidden': 'false'
                    }
                ]
            }
        }

    def test_initialization_with_members(self):
        """Test Datatype initialization with members."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        self.assertEqual(datatype.name, 'TestDatatype')
        self.assertEqual(len(datatype.members), 2)
        self.assertIsInstance(datatype.members[0], RaDatatypeMember)
        self.assertIsInstance(datatype.members[1], RaDatatypeMember)

    def test_initialization_empty_members(self):
        """Test Datatype initialization with empty members."""
        datatype_data = self.sample_datatype_data.copy()
        datatype_data['Members'] = {'Member': []}

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        self.assertEqual(len(datatype._members), 0)

    def test_initialization_no_members_key(self):
        """Test Datatype initialization without Members key."""
        datatype_data = self.sample_datatype_data.copy()
        del datatype_data['Members']

        datatype = RaDatatype(
            meta_data=datatype_data,
        )

        # Should create empty Members structure
        self.assertEqual(datatype.members, [])
        self.assertEqual(len(datatype._members), 0)

    def test_dict_key_order(self):
        """Test dict_key_order property."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data,
        )

        expected_order = [
            '@Name',
            '@Family',
            '@Class',
            'Description',
            'Members',
        ]

        self.assertEqual(datatype.dict_key_order, expected_order)

    def test_family_property(self):
        """Test family property getter."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        self.assertEqual(datatype.family, 'NoFamily')

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    def test_is_atomic_false_for_user_datatype(self):
        """Test is_atomic property returns False for user datatypes."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        self.assertFalse(datatype.is_atomic())

    def test_is_builtin_for_builtin_datatype(self):
        """Test is_builtin returns True for built-in datatypes."""
        from controlrox.models.plc.rockwell.datatype import BOOL

        self.assertTrue(BOOL.is_builtin())

    def test_is_builtin_for_user_datatype(self):
        """Test is_builtin returns False for user-defined datatypes."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        self.assertFalse(datatype.is_builtin())

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL', 'TestDatatype'])
    def test_is_atomic_true_for_atomic_datatype(self):
        """Test is_atomic property returns True for atomic datatypes."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        self.assertTrue(datatype.is_atomic())

    def test_members_property(self):
        """Test members property getter."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        members = datatype.members
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, 'BoolMember')
        self.assertEqual(members[1].name, 'IntMember')
        self.assertTrue(all(isinstance(member, RaDatatypeMember) for member in members))

    def test_raw_members_property_with_list(self):
        """Test raw_members property when Members contains a list."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        raw_members = datatype.raw_members
        self.assertIsInstance(raw_members, list)
        self.assertEqual(len(raw_members), 2)
        self.assertEqual(raw_members[0]['@Name'], 'BoolMember')
        self.assertEqual(raw_members[1]['@Name'], 'IntMember')

    def test_raw_members_property_with_single_member(self):
        """Test raw_members property when Members contains a single member."""
        datatype_data = self.sample_datatype_data.copy()
        datatype_data['Members'] = {
            'Member': {
                '@Name': 'SingleMember',
                '@DataType': 'BOOL',
                '@Dimension': '0',
                '@Hidden': 'false'
            }
        }

        datatype = RaDatatype(
            meta_data=datatype_data,
        )

        raw_members = datatype.raw_members
        self.assertIsInstance(raw_members, list)
        self.assertEqual(len(raw_members), 1)
        self.assertEqual(raw_members[0]['@Name'], 'SingleMember')

        # Verify it was converted to list in meta_data
        self.assertIsInstance(datatype['Members']['Member'], list)

    def test_raw_members_property_creates_structure_when_none(self):
        """Test raw_members property creates structure when Members is None."""
        datatype_data = self.sample_datatype_data.copy()
        datatype_data['Members'] = None

        datatype = RaDatatype(
            meta_data=datatype_data,
        )

        raw_members = datatype.raw_members
        self.assertIsInstance(raw_members, list)
        self.assertEqual(len(raw_members), 0)

        # Verify structure was created
        self.assertEqual(datatype['Members'], {'Member': []})

    def test_raw_members_property_modifiable(self):
        """Test that raw_members property returns a modifiable reference."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data,
        )

        raw_members = datatype.raw_members
        original_length = len(raw_members)

        # Add a new member
        new_member = {
            '@Name': 'NewMember',
            '@DataType': 'REAL',
            '@Dimension': '0',
            '@Hidden': 'false'
        }
        raw_members.append(new_member)

        # Verify it was added to the original structure
        self.assertEqual(len(datatype.raw_members), original_length + 1)
        self.assertEqual(datatype.raw_members[-1]['@Name'], 'NewMember')

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    def test_endpoint_operands_atomic_datatype(self):
        """Test endpoint_operands for atomic datatype."""
        # Create an atomic datatype
        atomic_data = self.sample_datatype_data.copy()
        atomic_data['@Name'] = 'BOOL'  # Make it atomic

        datatype = RaDatatype(
            meta_data=atomic_data
        )

        # Mock is_atomic to return True
        operands = datatype.endpoint_operands
        self.assertEqual(operands, [''])

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    def test_endpoint_operands_simple_members(self):
        """Test endpoint_operands for datatype with atomic members."""
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        operands = datatype.endpoint_operands
        expected = ['.BoolMember', '.IntMember']
        self.assertEqual(operands, expected)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_endpoint_operands_hidden_members_excluded(self, mock_get_controller):
        """Test endpoint_operands excludes hidden members."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = self.sample_datatype_data.copy()
        datatype_data['Members']['Member'][0]['@Hidden'] = 'true'  # Hide first member

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        operands = datatype.endpoint_operands
        expected = ['.IntMember']  # Only the non-hidden member
        self.assertEqual(operands, expected)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    def test_endpoint_operands_nested_datatypes(self):
        """Test endpoint_operands for datatype with nested custom datatypes."""
        # Create a nested datatype
        nested_datatype = Mock(spec=RaDatatype)
        nested_datatype.endpoint_operands = ['.NestedBool', '.NestedInt']

        # Set up controller to return the nested datatype
        self.mock_controller.datatypes = {'CustomType': nested_datatype}

        # Create datatype with custom member
        datatype_data = self.sample_datatype_data.copy()
        datatype_data['Members']['Member'].append({
            '@Name': 'CustomMember',
            '@DataType': 'CustomType',
            '@Dimension': '0',
            '@Hidden': 'false'
        })

        with patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller', return_value=self.mock_controller):
            datatype = RaDatatype(meta_data=datatype_data)

            operands = datatype.endpoint_operands
            expected = [
                '.BoolMember',
                '.IntMember',
                '.CustomMember.NestedBool',
                '.CustomMember.NestedInt'
            ]
            self.assertEqual(operands, expected)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_endpoint_operands_unknown_datatype(self, mock_get_controller):
        """Test endpoint_operands when member datatype is not found in controller."""
        # Create datatype with unknown member type
        datatype_data = self.sample_datatype_data.copy()
        datatype_data['Members']['Member'].append({
            '@Name': 'UnknownMember',
            '@DataType': 'UnknownType',
            '@Dimension': '0',
            '@Hidden': 'false'
        })

        # Controller doesn't have the unknown datatype
        self.mock_controller.datatypes = {}
        mock_get_controller.return_value = self.mock_controller

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        operands = datatype.endpoint_operands
        expected = ['.BoolMember', '.IntMember']  # Unknown member is skipped
        self.assertEqual(operands, expected)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_endpoint_operands_caching(self, mock_get_controller):
        """Test that endpoint_operands are cached after first calculation."""
        mock_get_controller.return_value = self.mock_controller
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        # First call should calculate
        operands1 = datatype.endpoint_operands

        # Second call should return cached result
        operands2 = datatype.endpoint_operands

        self.assertIs(operands1, operands2)  # Should be the same object (cached)
        self.assertEqual(operands1, ['.BoolMember', '.IntMember'])

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_inheritance_from_raplc_object(self, mock_get_controller):
        """Test that Datatype inherits from NamedPlcObject."""
        mock_get_controller.return_value = self.mock_controller
        datatype = RaDatatype(
            meta_data=self.sample_datatype_data
        )

        self.assertIsInstance(datatype, plc_meta.RaPlcObject)
        self.assertTrue(hasattr(datatype, 'name'))
        self.assertTrue(hasattr(datatype, 'description'))


class TestRaDatatypeMemberEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for RaDatatypeMember."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}

        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b

        self.mock_parent_datatype = Mock(spec=RaDatatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_member_with_missing_optional_fields(self, mock_get_controller):
        """Test member with missing optional fields."""
        mock_get_controller.return_value = self.mock_controller
        minimal_data = {
            '@Name': 'MinimalMember',
            '@DataType': 'BOOL'
        }

        member = RaDatatypeMember(
            meta_data=minimal_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.name, 'MinimalMember')
        self.assertEqual(member.datatype.name, 'BOOL')

        # These should NOT raise KeyError if not present
        _ = member.dimension
        _ = member.hidden

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_member_datatype_case_sensitivity(self, mock_get_controller):
        """Test that datatype property is case sensitive."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'CaseSensitiveMember',
            '@DataType': 'bool',  # lowercase
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(ValueError):
            _ = member.datatype  # 'bool' not found in controller datatypes

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_atomic_case_sensitive(self, mock_get_controller):
        """Test that is_atomic check is case sensitive."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'CaseMember',
            '@DataType': 'bool',  # lowercase, not in ATOMIC_DATATYPES
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertFalse(member.is_atomic())  # 'bool' != 'BOOL'


class TestDatatypeEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for Datatype."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_datatype_with_no_family(self, mock_get_controller):
        """Test datatype with missing family field."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'NoFamilyDatatype',
            '@Class': 'User',
            'Description': 'Test datatype',
            'Members': {'Member': []}
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )
        # Should not raise error, family defaults to None
        _ = datatype.family

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_empty_members_structure_handling(self, mock_get_controller):
        """Test various empty members structure scenarios."""
        mock_get_controller.return_value = self.mock_controller
        scenarios = [
            {'Members': None},
            {'Members': {}},
            {'Members': {'Member': None}},
            {'Members': {'Member': []}},
            {}  # No Members key at all
        ]

        for scenario in scenarios:
            datatype_data = {
                '@Name': 'EmptyDatatype',
                '@Family': 'NoFamily',
                '@Class': 'User'
            }
            datatype_data.update(scenario)

            datatype = RaDatatype(
                meta_data=datatype_data
            )

            # Should always result in empty list
            self.assertEqual(datatype.raw_members, [])
            self.assertEqual(len(datatype.members), 0)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', [])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_endpoint_operands_no_atomic_types(self, mock_get_controller):
        """Test endpoint_operands when no atomic types are defined."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {
                        '@Name': 'Member1',
                        '@DataType': 'BOOL',
                        '@Hidden': 'false'
                    }
                ]
            }
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        # No atomic types defined, so member is not atomic
        # Controller has no datatypes, so it will be skipped
        operands = datatype.endpoint_operands
        self.assertEqual(operands, [])

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_circular_reference_protection(self, mock_get_controller):
        """Test protection against circular references in nested datatypes."""
        # Create a datatype that references itself
        mock_get_controller.return_value = self.mock_controller
        circular_datatype = Mock()
        circular_datatype.endpoint_operands = ['.SelfRef']

        self.mock_controller.datatypes = {'SelfType': circular_datatype}

        datatype_data = {
            '@Name': 'SelfType',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {
                        '@Name': 'SelfMember',
                        '@DataType': 'SelfType',
                        '@Hidden': 'false'
                    }
                ]
            }
        }

        datatype = RaDatatype(meta_data=datatype_data)

        # This should work without infinite recursion
        # The mock will return a fixed value
        operands = datatype.endpoint_operands
        self.assertEqual(operands, ['.SelfMember.SelfRef'])


class TestDatatypeIntegration(unittest.TestCase):
    """Integration tests for Datatype and RaDatatypeMember."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock controller that passes isinstance check
        self.mock_controller = Mock(spec_set=RaController)
        self.mock_controller.datatypes = {}

        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b

        # Create a complex nested structure
        self.nested_datatype_data = {
            '@Name': 'NestedDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Description': 'Nested datatype',
            'Members': {
                'Member': [
                    {
                        '@Name': 'NestedBool',
                        '@DataType': 'BOOL',
                        '@Dimension': '0',
                        '@Hidden': 'false'
                    },
                    {
                        '@Name': 'NestedReal',
                        '@DataType': 'REAL',
                        '@Dimension': '0',
                        '@Hidden': 'false'
                    }
                ]
            }
        }

        self.complex_datatype_data = {
            '@Name': 'ComplexDatatype',
            '@Family': 'StringFamily',
            '@Class': 'User',
            'Description': 'Complex datatype with nested members',
            'Members': {
                'Member': [
                    {
                        '@Name': 'SimpleBool',
                        '@DataType': 'BOOL',
                        '@Dimension': '0',
                        '@Hidden': 'false',
                        'Description': 'Simple boolean member'
                    },
                    {
                        '@Name': 'HiddenInt',
                        '@DataType': 'DINT',
                        '@Dimension': '0',
                        '@Hidden': 'true',
                        'Description': 'Hidden integer member'
                    },
                    {
                        '@Name': 'NestedMember',
                        '@DataType': 'NestedDatatype',
                        '@Dimension': '0',
                        '@Hidden': 'false',
                        'Description': 'Nested custom datatype member'
                    },
                    {
                        '@Name': 'ArrayMember',
                        '@DataType': 'REAL',
                        '@Dimension': '10',
                        '@Hidden': 'false',
                        'Description': 'Array member'
                    }
                ]
            }
        }

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_complex_datatype_creation(self, mock_get_controller):
        """Test creating a complex datatype with various member types."""
        # Set up nested datatype in controller
        nested_datatype = RaDatatype(
            meta_data=self.nested_datatype_data
        )

        self.mock_controller.datatypes = {'NestedDatatype': nested_datatype}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b
        mock_get_controller.return_value = self.mock_controller

        # Create complex datatype
        complex_datatype = RaDatatype(
            meta_data=self.complex_datatype_data
        )

        # Test basic properties
        self.assertEqual(complex_datatype.name, 'ComplexDatatype')
        self.assertEqual(complex_datatype.family, 'StringFamily')
        self.assertFalse(complex_datatype.is_atomic())

        # Test members
        members = complex_datatype.members
        self.assertEqual(len(members), 4)

        # Test individual members
        self.assertEqual(members[0].name, 'SimpleBool')
        self.assertEqual(members[0].get_datatype().name, 'BOOL')
        self.assertFalse(members[0].is_hidden(),)
        self.assertTrue(members[0].is_atomic())

        self.assertEqual(members[1].name, 'HiddenInt')
        self.assertEqual(members[1].get_datatype().name, 'DINT')
        self.assertTrue(members[1].is_hidden(),)
        self.assertTrue(members[1].is_atomic())

        self.assertEqual(members[2].name, 'NestedMember')
        self.assertEqual(members[2].get_datatype().name, 'NestedDatatype')
        self.assertFalse(members[2].is_hidden(),)
        self.assertFalse(members[2].is_atomic())

        self.assertEqual(members[3].name, 'ArrayMember')
        self.assertEqual(members[3].get_datatype().name, 'REAL')
        self.assertEqual(members[3].get_dimension(), '10')

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL', 'STRING'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_complex_endpoint_operands(self, mock_get_controller):
        """Test endpoint operands for complex nested structure."""
        # Set up nested datatype
        nested_datatype = RaDatatype(
            meta_data=self.nested_datatype_data
        )

        self.mock_controller.datatypes = {'NestedDatatype': nested_datatype}
        mock_get_controller.return_value = self.mock_controller

        # Create complex datatype
        complex_datatype = RaDatatype(
            meta_data=self.complex_datatype_data
        )

        operands = complex_datatype.endpoint_operands
        expected = [
            '.SimpleBool',  # Atomic, not hidden
            # '.HiddenInt' is skipped because it's hidden
            '.NestedMember.NestedBool',  # From nested datatype
            '.NestedMember.NestedReal',  # From nested datatype
            '.ArrayMember'  # Atomic array member
        ]

        self.assertEqual(operands, expected)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_member_parent_reference(self, mock_get_controller):
        """Test that members correctly reference their parent datatype."""
        mock_get_controller.return_value = self.mock_controller
        datatype = RaDatatype(
            meta_data=self.complex_datatype_data
        )

        for member in datatype.members:
            self.assertIs(member.parent_datatype, datatype)
            self.assertIs(member.controller, datatype.controller)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_datatype_modification_through_raw_members(self, mock_get_controller):
        """Test modifying datatype structure through raw_members."""
        mock_get_controller.return_value = self.mock_controller
        datatype = RaDatatype(
            meta_data=self.complex_datatype_data
        )

        original_member_count = len(datatype.members)

        # Add a new member through raw_members
        new_member_data = {
            '@Name': 'NewMember',
            '@DataType': 'STRING',
            '@Dimension': '0',
            '@Hidden': 'false',
            'Description': 'Dynamically added member'
        }

        datatype.raw_members.append(new_member_data)

        # The _members list is created during initialization and won't update
        # automatically, but raw_members should reflect the change
        self.assertEqual(len(datatype.raw_members), original_member_count + 1)
        self.assertEqual(datatype.raw_members[-1]['@Name'], 'NewMember')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_endpoint_operands_performance_caching(self, mock_get_controller):
        """Test that endpoint operands calculation is cached for performance."""
        # Create a complex structure that would be expensive to recalculate
        nested_datatype = RaDatatype(
            meta_data=self.nested_datatype_data
        )

        self.mock_controller.datatypes = {'NestedDatatype': nested_datatype}
        mock_get_controller.return_value = self.mock_controller

        datatype = RaDatatype(
            meta_data=self.complex_datatype_data
        )

        # First call should calculate and cache
        operands1 = datatype.endpoint_operands

        # Modify the mock to return different values
        nested_datatype._endpoint_operands = ['.Modified']

        # Second call should return cached result (not recalculate)
        operands2 = datatype.endpoint_operands

        self.assertIs(operands1, operands2)  # Same object reference (cached)
        # Should not reflect the mock modification


class TestRaDatatypeMemberControllerIntegration(unittest.TestCase):
    """Test RaDatatypeMember with controller integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b
        self.mock_parent_datatype = Mock(spec=RaDatatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_get_datatype_with_controller(self, mock_get_controller):
        """Test get_datatype method with controller set."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'TestMember',
            '@DataType': 'DINT',
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        datatype = member.get_datatype()
        self.assertEqual(datatype.name, 'DINT')

    def test_get_datatype_without_controller(self):
        """Test get_datatype raises ValueError without controller."""
        member_data = {
            '@Name': 'TestMember',
            '@DataType': 'DINT',
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(ValueError) as context:
            member.get_datatype()

        self.assertIn('No controller set for this application', str(context.exception))

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_get_datatype_not_found(self, mock_get_controller):
        """Test get_datatype raises ValueError when datatype not in controller."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'TestMember',
            '@DataType': 'UnknownType',
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(ValueError) as context:
            member.get_datatype()

        self.assertIn('not found in controller', str(context.exception))

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_get_datatype_caching(self, mock_get_controller):
        """Test that get_datatype caches the result."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'TestMember',
            '@DataType': 'DINT',
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        # First call
        datatype1 = member.get_datatype()
        # Second call should return cached
        datatype2 = member.get_datatype()

        self.assertIs(datatype1, datatype2)


class TestRaDatatypeMemberGetMethods(unittest.TestCase):
    """Test RaDatatypeMember getter methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b
        self.mock_parent_datatype = Mock(spec=RaDatatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_get_dimension(self, mock_get_controller):
        """Test get_dimension method."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'ArrayMember',
            '@DataType': 'DINT',
            '@Dimension': '10',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.get_dimension(), '10')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_hidden_false(self, mock_get_controller):
        """Test is_hidden returns False for non-hidden member."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'VisibleMember',
            '@DataType': 'BOOL',
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertFalse(member.is_hidden())

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_hidden_true(self, mock_get_controller):
        """Test is_hidden returns True for hidden member."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'HiddenMember',
            '@DataType': 'BOOL',
            '@Dimension': '0',
            '@Hidden': 'true'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertTrue(member.is_hidden())

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_hidden_none(self, mock_get_controller):
        """Test is_hidden returns False when @Hidden is None."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'NoHiddenMember',
            '@DataType': 'BOOL',
            '@Dimension': '0',
            '@Hidden': None
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertFalse(member.is_hidden())

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_is_atomic_none_datatype(self, mock_get_controller):
        """Test is_atomic returns False when @DataType is None."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'NoDatatypeMember',
            '@DataType': None,
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertFalse(member.is_atomic())


class TestRaDatatypeCompileMethods(unittest.TestCase):
    """Test RaDatatype compile methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_compile_members(self, mock_get_controller):
        """Test compile_members method."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'},
                    {'@Name': 'Member2', '@DataType': 'DINT', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        # Members should be compiled during init
        self.assertEqual(len(datatype.members), 2)
        self.assertIsInstance(datatype.members[0], RaDatatypeMember)

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_compile_endpoint_operands(self, mock_get_controller):
        """Test compile_endpoint_operands method."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'},
                    {'@Name': 'Member2', '@DataType': 'DINT', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        datatype.compile_endpoint_operands()

        operands = datatype._endpoint_operands
        self.assertEqual(operands, ['.Member1', '.Member2'])

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_compile_members_clears_existing(self, mock_get_controller):
        """Test compile_members clears existing members."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        original_count = len(datatype.members)

        # Compile again
        datatype.compile_members()

        # Should have same count (cleared and re-added)
        self.assertEqual(len(datatype.members), original_count)


class TestRaDatatypeStringRepresentation(unittest.TestCase):
    """Test RaDatatype string representation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_str_representation(self, mock_get_controller):
        """Test __str__ returns datatype name."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {'Member': []}
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        result = str(datatype)

        self.assertEqual(result, 'TestDatatype')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_repr_representation(self, mock_get_controller):
        """Test __repr__ returns useful representation."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'TestDatatype',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {'Member': []}
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        result = repr(datatype)

        self.assertIsInstance(result, str)
        self.assertEqual(result, 'TestDatatype')


class TestRaDatatypeBuiltins(unittest.TestCase):
    """Test built-in datatype constants."""

    def test_builtins_defined(self):
        """Test that built-in datatypes are defined."""
        from controlrox.models.plc.rockwell.datatype import (
            BOOL, INT, DINT, TIMER, COUNTER
        )

        self.assertIsInstance(BOOL, RaDatatype)
        self.assertIsInstance(INT, RaDatatype)
        self.assertIsInstance(DINT, RaDatatype)
        self.assertIsInstance(TIMER, RaDatatype)
        self.assertIsInstance(COUNTER, RaDatatype)

    def test_builtins_list_length(self):
        """Test BUILTINS list contains expected number of types."""
        from controlrox.models.plc.rockwell.datatype import BUILTINS

        # Should have at least the basic atomic types plus TIMER, COUNTER
        self.assertGreaterEqual(len(BUILTINS), 15)

    def test_timer_has_members(self):
        """Test TIMER datatype has expected members."""
        from controlrox.models.plc.rockwell.datatype import TIMER

        self.assertEqual(TIMER.name, 'TIMER')
        self.assertEqual(len(TIMER.members), 5)
        member_names = [m.name for m in TIMER.members]
        self.assertIn('PRE', member_names)
        self.assertIn('ACC', member_names)
        self.assertIn('DN', member_names)

    def test_counter_has_members(self):
        """Test COUNTER datatype has expected members."""
        from controlrox.models.plc.rockwell.datatype import COUNTER

        self.assertEqual(COUNTER.name, 'COUNTER')
        self.assertEqual(len(COUNTER.members), 5)
        member_names = [m.name for m in COUNTER.members]
        self.assertIn('PRE', member_names)
        self.assertIn('ACC', member_names)
        self.assertIn('DN', member_names)

    def test_control_has_members(self):
        """Test CONTROL datatype has expected members."""
        from controlrox.models.plc.rockwell.datatype import CONTROL

        self.assertEqual(CONTROL.name, 'CONTROL')
        self.assertEqual(len(CONTROL.members), 10)


class TestRaDatatypeClassAttributes(unittest.TestCase):
    """Test RaDatatype class-level attributes."""

    def test_default_l5x_file_path(self):
        """Test default_l5x_file_path is set."""
        from controlrox.models.plc.rockwell.datatype import RaDatatype
        from controlrox.models.plc.rockwell.meta import PLC_DT_FILE

        self.assertEqual(RaDatatype.default_l5x_file_path, PLC_DT_FILE)

    def test_default_l5x_asset_key(self):
        """Test default_l5x_asset_key is set."""
        from controlrox.models.plc.rockwell.datatype import RaDatatype

        self.assertEqual(RaDatatype.default_l5x_asset_key, 'Datatype')


class TestRaDatatypeMemberDictAccess(unittest.TestCase):
    """Test RaDatatypeMember dictionary-style access."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b
        self.mock_parent_datatype = Mock(spec=RaDatatype)

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_dict_item_access(self, mock_get_controller):
        """Test dictionary-style item access."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'TestMember',
            '@DataType': 'BOOL',
            '@Dimension': '5',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member['@Name'], 'TestMember')
        self.assertEqual(member['@DataType'], 'BOOL')
        self.assertEqual(member['@Dimension'], '5')

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_dict_item_modification(self, mock_get_controller):
        """Test dictionary-style item modification."""
        mock_get_controller.return_value = self.mock_controller
        member_data = {
            '@Name': 'TestMember',
            '@DataType': 'BOOL',
            '@Dimension': '0',
            '@Hidden': 'false'
        }

        member = RaDatatypeMember(
            meta_data=member_data,
            parent_datatype=self.mock_parent_datatype
        )

        member['@Dimension'] = '10'

        self.assertEqual(member['@Dimension'], '10')


class TestRaDatatypeComplexScenarios(unittest.TestCase):
    """Test RaDatatype complex real-world scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.datatypes = {}
        for b in BUILTINS:
            self.mock_controller.datatypes[b.name] = b

    @patch('controlrox.models.plc.rockwell.datatype.ATOMIC_DATATYPES', ['BOOL', 'DINT', 'REAL'])
    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_deeply_nested_datatypes(self, mock_get_controller):
        """Test handling of deeply nested datatype structures."""
        mock_get_controller.return_value = self.mock_controller
        # Level 3
        level3_data = {
            '@Name': 'Level3',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'L3_Bool', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        level3 = RaDatatype(meta_data=level3_data)
        self.mock_controller.datatypes['Level3'] = level3

        # Level 2
        level2_data = {
            '@Name': 'Level2',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'L2_Nested', '@DataType': 'Level3', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        level2 = RaDatatype(meta_data=level2_data)
        self.mock_controller.datatypes['Level2'] = level2

        # Level 1
        level1_data = {
            '@Name': 'Level1',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'L1_Nested', '@DataType': 'Level2', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        level1 = RaDatatype(meta_data=level1_data)

        # Check endpoint operands traverse all levels
        operands = level1.endpoint_operands
        self.assertEqual(operands, ['.L1_Nested.L2_Nested.L3_Bool'])

    @patch('controlrox.models.plc.rockwell.datatype.ControllerInstanceManager.get_controller')
    def test_multiple_members_same_datatype(self, mock_get_controller):
        """Test datatype with multiple members of same type."""
        mock_get_controller.return_value = self.mock_controller
        datatype_data = {
            '@Name': 'MultiMember',
            '@Family': 'NoFamily',
            '@Class': 'User',
            'Members': {
                'Member': [
                    {'@Name': 'Bool1', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'},
                    {'@Name': 'Bool2', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'},
                    {'@Name': 'Bool3', '@DataType': 'BOOL', '@Dimension': '0', '@Hidden': 'false'}
                ]
            }
        }

        datatype = RaDatatype(
            meta_data=datatype_data
        )

        self.assertEqual(len(datatype.members), 3)
        self.assertEqual(datatype.members[0].name, 'Bool1')
        self.assertEqual(datatype.members[1].name, 'Bool2')
        self.assertEqual(datatype.members[2].name, 'Bool3')


if __name__ == '__main__':
    unittest.main(verbosity=2)
