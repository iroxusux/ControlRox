"""Unit tests for controlrox.models.plc.datatype module."""
import unittest
from typing import Self
from unittest.mock import Mock

from controlrox.models.plc.datatype import (
    DatatypeProto,
    DatatypeMember,
    Datatype,
    BOOL,
    BIT,
    SINT,
    INT,
    DINT,
    LINT,
    USINT,
    UINT,
    UDINT,
    ULINT,
    REAL,
    LREAL,
    STRING,
    TIMER,
    COUNTER,
    CONTROL,
    BUILTINS,
)
from controlrox.interfaces import IController, IDatatype, IDatatypeMember


class TestDatatypeProto(unittest.TestCase):
    """Test cases for DatatypeProto class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete subclass for testing
        class ConcreteDatatypeProto(DatatypeProto):
            """Concrete implementation for testing."""

            def compile(self) -> Self:
                """Implement compile method."""
                self.compiled = True
                return self

            def invalidate(self) -> None:
                """Implement invalidate method."""
                self.invalidated = True

            @property
            def process_name(self) -> str:
                """Implement process_name property."""
                return "TestProcess"

            def is_atomic(self) -> bool:
                """Implement is_atomic method."""
                return True

            def is_builtin(self) -> bool:
                """Implement is_builtin method."""
                return False

        self.ConcreteDatatypeProto = ConcreteDatatypeProto

    def test_init_with_defaults(self):
        """Test DatatypeProto initialization with default values."""
        obj = self.ConcreteDatatypeProto()

        self.assertEqual(obj.name, '')
        self.assertEqual(obj.description, '')
        self.assertIsInstance(obj.meta_data, dict)

    def test_init_with_meta_data(self):
        """Test DatatypeProto initialization with metadata."""
        meta_data = {
            '@Name': 'TestDatatype',
            '@Description': 'Test Description'
        }
        obj = self.ConcreteDatatypeProto(meta_data=meta_data)

        self.assertEqual(obj.name, 'TestDatatype')
        self.assertEqual(obj.description, 'Test Description')

    def test_is_atomic_not_implemented(self):
        """Test that is_atomic raises NotImplementedError in base class."""
        proto = DatatypeProto(meta_data={'@Name': 'Test'})

        with self.assertRaises(NotImplementedError):
            proto.is_atomic()

    def test_is_builtin_not_implemented(self):
        """Test that is_builtin raises NotImplementedError in base class."""
        proto = DatatypeProto(meta_data={'@Name': 'Test'})

        with self.assertRaises(NotImplementedError):
            proto.is_builtin()


class TestDatatypeMember(unittest.TestCase):
    """Test cases for DatatypeMember class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=IController)
        self.mock_parent_datatype = Mock(spec=IDatatype)
        self.mock_parent_datatype.name = 'ParentDatatype'

        # Create a concrete subclass for testing
        class ConcreteDatatypeMember(DatatypeMember):
            """Concrete implementation for testing."""

            def compile(self) -> Self:
                """Implement compile method."""
                self.compiled = True
                return self

            def invalidate(self) -> None:
                """Implement invalidate method."""
                self.invalidated = True

            @property
            def process_name(self) -> str:
                """Implement process_name property."""
                return "TestProcess"

            def is_atomic(self) -> bool:
                """Implement is_atomic method."""
                return self.datatype.name in ['BOOL', 'DINT', 'REAL']

            def is_builtin(self) -> bool:
                """Implement is_builtin method."""
                return True

            def get_dimension(self) -> str:
                """Implement get_dimension method."""
                return self.meta_data.get('@Dimension', '0')

            def is_hidden(self) -> bool:
                """Implement is_hidden method."""
                return self.meta_data.get('@Hidden', 'false') == 'true'

        self.ConcreteDatatypeMember = ConcreteDatatypeMember

    def test_init_with_required_params(self):
        """Test DatatypeMember initialization with required parameters."""
        meta_data = {
            '@Name': 'TestMember',
            '@DataType': 'DINT',
            '@Dimension': '0',
            '@Hidden': 'false'
        }
        member = self.ConcreteDatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.name, 'TestMember')
        self.assertEqual(member.get_parent_datatype(), self.mock_parent_datatype)
        self.assertIsNone(member._datatype)

    def test_init_with_all_params(self):
        """Test DatatypeMember initialization with all parameters."""
        meta_data = {
            '@Name': 'TestMember',
            '@DataType': 'BOOL',
            '@Dimension': '1',
            '@Hidden': 'true'
        }
        member = self.ConcreteDatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype,
            name='OverrideName',
            description='Test Description',
        )

        self.assertEqual(member.name, 'OverrideName')
        self.assertEqual(member.description, 'Test Description')
        self.assertEqual(member.get_parent_datatype(), self.mock_parent_datatype)

    def test_get_parent_datatype(self):
        """Test get_parent_datatype returns correct parent."""
        meta_data = {'@Name': 'Member1'}
        member = self.ConcreteDatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        result = member.get_parent_datatype()

        self.assertEqual(result, self.mock_parent_datatype)

    def test_set_datatype_with_valid_datatype(self):
        """Test set_datatype with valid IDatatype instance."""
        meta_data = {'@Name': 'Member1'}
        member = self.ConcreteDatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        mock_datatype = Mock(spec=IDatatype)
        mock_datatype.name = 'CustomDatatype'

        member.set_datatype(mock_datatype)

        self.assertEqual(member.datatype, mock_datatype)

    def test_set_datatype_with_none(self):
        """Test set_datatype with None value."""
        meta_data = {'@Name': 'Member1'}
        member = self.ConcreteDatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype,
        )

        member.set_datatype(None)

        with self.assertRaises(ValueError) as context:
            member.get_datatype()
        self.assertIn("Datatype not set for this member", str(context.exception))

    def test_set_datatype_with_invalid_type(self):
        """Test set_datatype raises TypeError with invalid type."""
        meta_data = {'@Name': 'Member1'}
        member = self.ConcreteDatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(TypeError) as context:
            member.set_datatype("not_a_datatype")  # type: ignore

        self.assertIn('must be an instance of IDatatype', str(context.exception))

    def test_get_datatype_raises_with_no_datatype(self):
        """Test get datatype raises an exception if _datatype is not set."""
        meta_data = {'@Name': 'Member1'}
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(ValueError):
            member.get_datatype()

    def test_get_dimension_not_implemented(self):
        """Test get_dimension raises NotImplementedError in base class."""
        meta_data = {'@Name': 'Member1'}
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(NotImplementedError):
            member.get_dimension()

    def test_is_hidden_not_implemented(self):
        """Test is_hidden raises NotImplementedError in base class."""
        meta_data = {'@Name': 'Member1'}
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        with self.assertRaises(NotImplementedError):
            member.is_hidden()


class TestDatatype(unittest.TestCase):
    """Test cases for Datatype class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=IController)

        # Create a concrete subclass for testing
        class ConcreteDatatype(Datatype):
            """Concrete implementation for testing."""

            def invalidate(self) -> None:
                """Implement invalidate method."""
                self.invalidated = True

            @property
            def process_name(self) -> str:
                """Implement process_name property."""
                return "TestProcess"

            def is_atomic(self) -> bool:
                """Implement is_atomic method."""
                return self.name in ['BOOL', 'DINT', 'REAL', 'INT', 'SINT']

            def is_builtin(self) -> bool:
                """Implement is_builtin method."""
                return self.name in ['BOOL', 'DINT', 'REAL']

            def compile_endpoint_operands(self) -> None:
                """Implement compile_endpoint_operands method."""
                if self.is_atomic():
                    self._endpoint_operands = ['']
                else:
                    # Simplified logic for testing
                    self._endpoint_operands = [f'.{m.name}' for m in self.members if hasattr(m, 'name')]

            def compile_members(self) -> None:
                """Implement compile_members method."""
                if 'Members' in self.meta_data and self.meta_data['Members']:
                    members_data = self.meta_data['Members'].get('Member', [])
                    if not isinstance(members_data, list):
                        members_data = [members_data]

                    for member_data in members_data:
                        mock_member = Mock(spec=IDatatypeMember)
                        mock_member.name = member_data.get('@Name', '')
                        mock_member.meta_data = member_data
                        self._members.append(mock_member)

            def get_family(self) -> str:
                """Implement get_family method."""
                if self.is_atomic():
                    return 'NoFamily'
                return 'StringFamily'

        self.ConcreteDatatype = ConcreteDatatype

    def test_init_with_defaults(self):
        """Test Datatype initialization with default values."""
        dt = self.ConcreteDatatype()

        self.assertEqual(dt.name, '')
        self.assertEqual(dt.description, '')
        self.assertIsInstance(dt.meta_data, dict)
        self.assertEqual(dt._members, [])
        self.assertEqual(dt._endpoint_operands, [])

    def test_init_with_meta_data(self):
        """Test Datatype initialization with metadata."""
        meta_data = {
            '@Name': 'CustomDatatype',
            '@Description': 'Custom Description',
            '@Family': 'NoFamily'
        }
        dt = self.ConcreteDatatype(meta_data=meta_data)

        self.assertEqual(dt.name, 'CustomDatatype')
        self.assertEqual(dt.description, 'Custom Description')

    def test_init_with_all_params(self):
        """Test Datatype initialization with all parameters."""
        meta_data = {'@Name': 'TestDatatype'}
        dt = self.ConcreteDatatype(
            meta_data=meta_data,
            name='OverrideName',
            description='Override Description',
        )

        self.assertEqual(dt.name, 'OverrideName')
        self.assertEqual(dt.description, 'Override Description')

    def test_get_members_empty(self):
        """Test get_members with no members."""
        meta_data = {'@Name': 'AtomicType'}
        dt = self.ConcreteDatatype(meta_data=meta_data)

        members = dt.get_members()

        self.assertEqual(members, [])

    def test_get_members_compiles_if_empty(self):
        """Test get_members calls compile_members if members list is empty."""
        meta_data = {
            '@Name': 'ComplexType',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'DINT'},
                    {'@Name': 'Member2', '@DataType': 'BOOL'}
                ]
            }
        }
        dt = self.ConcreteDatatype(meta_data=meta_data)

        members = dt.get_members()

        self.assertEqual(len(members), 2)

    def test_get_members_returns_cached(self):
        """Test get_members returns cached members without recompiling."""
        meta_data = {
            '@Name': 'ComplexType',
            'Members': {
                'Member': [{'@Name': 'Member1', '@DataType': 'DINT'}]
            }
        }
        dt = self.ConcreteDatatype(meta_data=meta_data)

        # First call compiles
        members1 = dt.get_members()
        # Second call should return cached
        members2 = dt.get_members()

        self.assertEqual(members1, members2)
        self.assertIs(members1, members2)

    def test_compile_calls_both_compile_methods(self):
        """Test compile method calls both compile_members and compile_endpoint_operands."""
        meta_data = {
            '@Name': 'TestDatatype',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'DINT'}
                ]
            }
        }
        dt = self.ConcreteDatatype(meta_data=meta_data)

        result = dt.compile()

        self.assertIsNotNone(dt._members)
        self.assertIsNotNone(dt._endpoint_operands)
        self.assertIs(result, dt)

    def test_compile_endpoint_operands_not_implemented(self):
        """Test compile_endpoint_operands raises NotImplementedError in base class."""
        dt = Datatype(meta_data={'@Name': 'Test'})

        with self.assertRaises(NotImplementedError):
            dt.compile_endpoint_operands()

    def test_compile_members_not_implemented(self):
        """Test compile_members raises NotImplementedError in base class."""
        dt = Datatype(meta_data={'@Name': 'Test'})

        with self.assertRaises(NotImplementedError):
            dt.compile_members()

    def test_get_endpoint_operands_atomic(self):
        """Test get_endpoint_operands for atomic datatype."""
        meta_data = {'@Name': 'BOOL'}
        dt = self.ConcreteDatatype(meta_data=meta_data)

        operands = dt.get_endpoint_operands()

        self.assertEqual(operands, [''])

    def test_get_endpoint_operands_complex(self):
        """Test get_endpoint_operands for complex datatype."""
        meta_data = {
            '@Name': 'ComplexType',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'DINT'},
                    {'@Name': 'Member2', '@DataType': 'BOOL'}
                ]
            }
        }
        dt = self.ConcreteDatatype(meta_data=meta_data)

        operands = dt.get_endpoint_operands()

        self.assertIsInstance(operands, list)
        self.assertGreater(len(operands), 0)

    def test_get_endpoint_operands_compiles_if_empty(self):
        """Test get_endpoint_operands compiles if endpoint_operands is empty."""
        meta_data = {
            '@Name': 'ComplexType',
            'Members': {
                'Member': [{'@Name': 'Member1', '@DataType': 'DINT'}]
            }
        }
        dt = self.ConcreteDatatype(meta_data=meta_data)

        # Ensure _endpoint_operands is empty
        dt._endpoint_operands = []

        operands = dt.get_endpoint_operands()

        self.assertIsNotNone(operands)

    def test_get_family_not_implemented(self):
        """Test get_family raises NotImplementedError in base class."""
        dt = Datatype(meta_data={'@Name': 'Test'})

        with self.assertRaises(NotImplementedError):
            dt.get_family()


class TestBuiltinDatatypes(unittest.TestCase):
    """Test cases for built-in datatype constants."""

    def test_bool_datatype(self):
        """Test BOOL builtin datatype."""
        self.assertEqual(BOOL.name, 'BOOL')
        self.assertIsInstance(BOOL, Datatype)

    def test_bit_datatype(self):
        """Test BIT builtin datatype."""
        self.assertEqual(BIT.name, 'BIT')
        self.assertIsInstance(BIT, Datatype)

    def test_sint_datatype(self):
        """Test SINT builtin datatype."""
        self.assertEqual(SINT.name, 'SINT')
        self.assertIsInstance(SINT, Datatype)

    def test_int_datatype(self):
        """Test INT builtin datatype."""
        self.assertEqual(INT.name, 'INT')
        self.assertIsInstance(INT, Datatype)

    def test_dint_datatype(self):
        """Test DINT builtin datatype."""
        self.assertEqual(DINT.name, 'DINT')
        self.assertIsInstance(DINT, Datatype)

    def test_lint_datatype(self):
        """Test LINT builtin datatype."""
        self.assertEqual(LINT.name, 'LINT')
        self.assertIsInstance(LINT, Datatype)

    def test_usint_datatype(self):
        """Test USINT builtin datatype."""
        self.assertEqual(USINT.name, 'USINT')
        self.assertIsInstance(USINT, Datatype)

    def test_uint_datatype(self):
        """Test UINT builtin datatype."""
        self.assertEqual(UINT.name, 'UINT')
        self.assertIsInstance(UINT, Datatype)

    def test_udint_datatype(self):
        """Test UDINT builtin datatype."""
        self.assertEqual(UDINT.name, 'UDINT')
        self.assertIsInstance(UDINT, Datatype)

    def test_ulint_datatype(self):
        """Test ULINT builtin datatype."""
        self.assertEqual(ULINT.name, 'ULINT')
        self.assertIsInstance(ULINT, Datatype)

    def test_real_datatype(self):
        """Test REAL builtin datatype."""
        self.assertEqual(REAL.name, 'REAL')
        self.assertIsInstance(REAL, Datatype)

    def test_lreal_datatype(self):
        """Test LREAL builtin datatype."""
        self.assertEqual(LREAL.name, 'LREAL')
        self.assertIsInstance(LREAL, Datatype)

    def test_string_datatype(self):
        """Test STRING builtin datatype."""
        self.assertEqual(STRING.name, 'STRING')
        self.assertIsInstance(STRING, Datatype)

    def test_timer_datatype(self):
        """Test TIMER builtin datatype."""
        self.assertEqual(TIMER.name, 'TIMER')
        self.assertIsInstance(TIMER, Datatype)
        self.assertIn('Members', TIMER.meta_data)

        members = TIMER.meta_data['Members']['Member']
        self.assertEqual(len(members), 5)

        # Check expected members
        member_names = [m['@Name'] for m in members]
        self.assertIn('PRE', member_names)
        self.assertIn('ACC', member_names)
        self.assertIn('EN', member_names)
        self.assertIn('TT', member_names)
        self.assertIn('DN', member_names)

    def test_counter_datatype(self):
        """Test COUNTER builtin datatype."""
        self.assertEqual(COUNTER.name, 'COUNTER')
        self.assertIsInstance(COUNTER, Datatype)
        self.assertIn('Members', COUNTER.meta_data)

        members = COUNTER.meta_data['Members']['Member']
        self.assertEqual(len(members), 5)

        # Check expected members
        member_names = [m['@Name'] for m in members]
        self.assertIn('PRE', member_names)
        self.assertIn('ACC', member_names)
        self.assertIn('CU', member_names)
        self.assertIn('CD', member_names)
        self.assertIn('DN', member_names)

    def test_control_datatype(self):
        """Test CONTROL builtin datatype."""
        self.assertEqual(CONTROL.name, 'CONTROL')
        self.assertIsInstance(CONTROL, Datatype)
        self.assertIn('Members', CONTROL.meta_data)

        members = CONTROL.meta_data['Members']['Member']
        self.assertEqual(len(members), 10)

        # Check expected members
        member_names = [m['@Name'] for m in members]
        self.assertIn('LEN', member_names)
        self.assertIn('POS', member_names)
        self.assertIn('EN', member_names)
        self.assertIn('EU', member_names)
        self.assertIn('DN', member_names)
        self.assertIn('EM', member_names)
        self.assertIn('ER', member_names)
        self.assertIn('UL', member_names)
        self.assertIn('IN', member_names)
        self.assertIn('FD', member_names)

    def test_builtins_list(self):
        """Test BUILTINS list contains all expected datatypes."""
        self.assertEqual(len(BUILTINS), 15)

        self.assertIn(BOOL, BUILTINS)
        self.assertIn(BIT, BUILTINS)
        self.assertIn(SINT, BUILTINS)
        self.assertIn(INT, BUILTINS)
        self.assertIn(DINT, BUILTINS)
        self.assertIn(LINT, BUILTINS)
        self.assertIn(USINT, BUILTINS)
        self.assertIn(UINT, BUILTINS)
        self.assertIn(UDINT, BUILTINS)
        self.assertIn(ULINT, BUILTINS)
        self.assertIn(REAL, BUILTINS)
        self.assertIn(LREAL, BUILTINS)
        self.assertIn(STRING, BUILTINS)
        self.assertIn(TIMER, BUILTINS)
        self.assertIn(COUNTER, BUILTINS)

    def test_builtins_all_are_datatype_instances(self):
        """Test all builtins are instances of Datatype."""
        for builtin in BUILTINS:
            self.assertIsInstance(builtin, Datatype)


class TestDatatypeEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for Datatype classes."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=IController)
        self.mock_parent_datatype = Mock(spec=IDatatype)

    def test_datatype_with_empty_metadata(self):
        """Test Datatype with empty metadata dictionary."""
        dt = Datatype(meta_data={})

        self.assertEqual(dt.name, '')
        self.assertIsInstance(dt.meta_data, dict)

    def test_datatype_with_none_metadata(self):
        """Test Datatype with None metadata."""
        dt = Datatype(meta_data=None)

        self.assertIsInstance(dt.meta_data, dict)

    def test_datatypemember_with_none_controller(self):
        """Test DatatypeMember with None controller."""
        meta_data = {'@Name': 'Member1'}
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype,
        )

        self.assertEqual(member.name, 'Member1')

    def test_datatypemember_parent_datatype_required(self):
        """Test DatatypeMember requires parent_datatype."""
        meta_data = {'@Name': 'Member1'}

        # This should work without error
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        self.assertIsNotNone(member.get_parent_datatype())


class TestDatatypeIntegration(unittest.TestCase):
    """Integration tests for Datatype classes."""

    def setUp(self):
        """Set up test fixtures."""
        # Create concrete implementations for integration testing
        class TestableDatatype(Datatype):
            """Testable datatype implementation."""

            def invalidate(self) -> None:
                """Implement invalidate method."""
                pass

            @property
            def process_name(self) -> str:
                """Implement process_name property."""
                return "TestProcess"

            def is_atomic(self) -> bool:
                """Implement is_atomic method."""
                return not self._members

            def is_builtin(self) -> bool:
                """Implement is_builtin method."""
                return False

            def compile_endpoint_operands(self) -> None:
                """Implement compile_endpoint_operands method."""
                if self.is_atomic():
                    self._endpoint_operands = ['']
                else:
                    self._endpoint_operands = ['.Member1', '.Member2']

            def compile_members(self) -> None:
                """Implement compile_members method."""
                pass

            def get_family(self) -> str:
                """Implement get_family method."""
                return 'NoFamily'

        self.TestableDatatype = TestableDatatype

    def test_datatype_lifecycle(self):
        """Test complete datatype lifecycle."""
        meta_data = {
            '@Name': 'CustomDatatype',
            '@Description': 'Test datatype',
            '@Family': 'NoFamily'
        }

        dt = self.TestableDatatype(meta_data=meta_data)

        # Initial state
        self.assertEqual(dt.name, 'CustomDatatype')
        self.assertEqual(dt._members, [])
        self.assertEqual(dt._endpoint_operands, [])

        # Compile
        dt.compile()

        # Post-compile state
        self.assertIsNotNone(dt._endpoint_operands)

        # Get members
        members = dt.get_members()
        self.assertEqual(members, [])

        # Get endpoint operands
        operands = dt.get_endpoint_operands()
        self.assertIn('', operands)


class TestDatatypeMemberProperties(unittest.TestCase):
    """Test DatatypeMember property access patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_parent_datatype = Mock(spec=IDatatype)
        self.mock_parent_datatype.name = 'ParentType'

    def test_datatype_property_with_interface(self):
        """Test that datatype property works via interface."""
        meta_data = {'@Name': 'TestMember'}
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        mock_dt = Mock(spec=IDatatype)
        mock_dt.name = 'DINT'
        member.set_datatype(mock_dt)

        # Should access via property
        self.assertEqual(member.datatype, mock_dt)

    def test_parent_datatype_property(self):
        """Test parent_datatype property access."""
        meta_data = {'@Name': 'TestMember'}
        member = DatatypeMember(
            meta_data=meta_data,
            parent_datatype=self.mock_parent_datatype
        )

        # Check property access
        self.assertEqual(member.parent_datatype, self.mock_parent_datatype)


class TestDatatypePropertiesAndInterfaces(unittest.TestCase):
    """Test Datatype properties match interface definitions."""

    def setUp(self):
        """Set up test fixtures."""
        class TestableDatatype(Datatype):
            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "TestProcess"

            def is_atomic(self) -> bool:
                return True

            def is_builtin(self) -> bool:
                return True

            def compile_endpoint_operands(self) -> None:
                self._endpoint_operands = ['']

            def compile_members(self) -> None:
                pass

            def get_family(self) -> str:
                return 'NoFamily'

        self.TestableDatatype = TestableDatatype

    def test_endpoint_operands_property(self):
        """Test endpoint_operands property delegates to get_endpoint_operands."""
        dt = self.TestableDatatype(meta_data={'@Name': 'Test'})

        # Access via property
        result = dt.endpoint_operands

        # Should be same as method call
        self.assertEqual(result, dt.get_endpoint_operands())

    def test_members_property(self):
        """Test members property delegates to get_members."""
        dt = self.TestableDatatype(meta_data={'@Name': 'Test'})

        # Access via property
        result = dt.members

        # Should be same as method call
        self.assertEqual(result, dt.get_members())

    def test_interface_property_consistency(self):
        """Test that interface properties are consistent with getters."""
        dt = self.TestableDatatype(meta_data={'@Name': 'Test'})

        # Both should return the same content
        self.assertEqual(dt.endpoint_operands, dt.get_endpoint_operands())
        self.assertEqual(dt.members, dt.get_members())


class TestBuiltinDatatypeDetails(unittest.TestCase):
    """Detailed tests for built-in datatype structures."""

    def test_timer_member_datatypes(self):
        """Test TIMER has correct member datatypes."""
        members = TIMER.meta_data['Members']['Member']

        pre_member = next(m for m in members if m['@Name'] == 'PRE')
        self.assertEqual(pre_member['@DataType'], 'DINT')

        acc_member = next(m for m in members if m['@Name'] == 'ACC')
        self.assertEqual(acc_member['@DataType'], 'DINT')

        en_member = next(m for m in members if m['@Name'] == 'EN')
        self.assertEqual(en_member['@DataType'], 'BOOL')

    def test_counter_member_dimensions(self):
        """Test COUNTER members have correct dimensions."""
        members = COUNTER.meta_data['Members']['Member']

        for member in members:
            self.assertEqual(member['@Dimension'], '1')
            self.assertEqual(member['@Hidden'], 'false')

    def test_control_all_members_present(self):
        """Test CONTROL has all expected members."""
        members = CONTROL.meta_data['Members']['Member']
        member_names = {m['@Name'] for m in members}

        expected_names = {'LEN', 'POS', 'EN', 'EU', 'DN', 'EM', 'ER', 'UL', 'IN', 'FD'}
        self.assertEqual(member_names, expected_names)

    def test_atomic_datatypes_no_members(self):
        """Test atomic datatypes don't have Members in metadata."""
        atomic_types = [BOOL, BIT, SINT, INT, DINT, LINT, USINT, UINT, UDINT, ULINT, REAL, LREAL, STRING]

        for dt in atomic_types:
            self.assertNotIn('Members', dt.meta_data)

    def test_complex_datatypes_have_members(self):
        """Test complex datatypes have Members in metadata."""
        complex_types = [TIMER, COUNTER, CONTROL]

        for dt in complex_types:
            self.assertIn('Members', dt.meta_data)
            self.assertIn('Member', dt.meta_data['Members'])


class TestDatatypeValidation(unittest.TestCase):
    """Test validation and error handling in Datatype classes."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_parent_datatype = Mock(spec=IDatatype)

    def test_set_datatype_type_checking(self):
        """Test set_datatype enforces type checking."""
        member = DatatypeMember(
            meta_data={'@Name': 'Member1'},
            parent_datatype=self.mock_parent_datatype
        )

        # These should raise TypeError
        invalid_values = [123, 'string', [], {}, object()]

        for invalid_value in invalid_values:
            with self.assertRaises(TypeError):
                member.set_datatype(invalid_value)  # type: ignore

    def test_get_datatype_validates_state(self):
        """Test get_datatype validates internal state."""
        member = DatatypeMember(
            meta_data={'@Name': 'Member1'},
            parent_datatype=self.mock_parent_datatype
        )

        # Should raise ValueError when datatype not set
        with self.assertRaises(ValueError) as context:
            member.get_datatype()

        self.assertIn('Datatype not set', str(context.exception))

    def test_datatype_member_requires_parent(self):
        """Test DatatypeMember properly stores parent reference."""
        member = DatatypeMember(
            meta_data={'@Name': 'Member1'},
            parent_datatype=self.mock_parent_datatype
        )

        self.assertIsNotNone(member._parent_datatype)
        self.assertEqual(member.get_parent_datatype(), self.mock_parent_datatype)


class TestDatatypeCompilation(unittest.TestCase):
    """Test compilation process for datatypes."""

    def setUp(self):
        """Set up test fixtures."""
        class CompilableDatatype(Datatype):
            def invalidate(self) -> None:
                self.invalidated = True

            @property
            def process_name(self) -> str:
                return "TestProcess"

            def is_atomic(self) -> bool:
                return len(self._members) == 0

            def is_builtin(self) -> bool:
                return False

            def compile_endpoint_operands(self) -> None:
                self.endpoint_operands_compiled = True
                if self.is_atomic():
                    self._endpoint_operands = ['']
                else:
                    self._endpoint_operands = [f'.{m.name}' for m in self._members]

            def compile_members(self) -> None:
                self.members_compiled = True
                # Simplified member compilation
                if 'Members' in self.meta_data:
                    members_data = self.meta_data['Members'].get('Member', [])
                    if not isinstance(members_data, list):
                        members_data = [members_data]
                    for member_data in members_data:
                        mock_member = Mock(spec=IDatatypeMember)
                        mock_member.name = member_data.get('@Name', '')
                        self._members.append(mock_member)

            def get_family(self) -> str:
                return 'TestFamily'

        self.CompilableDatatype = CompilableDatatype

    def test_compile_executes_in_order(self):
        """Test compile executes sub-methods in correct order."""
        dt = self.CompilableDatatype(meta_data={'@Name': 'Test'})

        result = dt.compile()

        self.assertTrue(dt.members_compiled)
        self.assertTrue(dt.endpoint_operands_compiled)
        self.assertIs(result, dt)

    def test_compile_returns_self_for_chaining(self):
        """Test compile returns self to allow method chaining."""
        dt = self.CompilableDatatype(meta_data={'@Name': 'Test'})

        result = dt.compile()

        self.assertIs(result, dt)
        self.assertIsInstance(result, self.CompilableDatatype)

    def test_lazy_compilation_of_members(self):
        """Test members are compiled lazily on first access."""
        meta_data = {
            '@Name': 'LazyType',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'DINT'}
                ]
            }
        }
        dt = self.CompilableDatatype(meta_data=meta_data)

        # Members not compiled yet
        self.assertFalse(hasattr(dt, 'members_compiled'))

        # First access triggers compilation
        members = dt.get_members()

        self.assertTrue(dt.members_compiled)
        self.assertEqual(len(members), 1)

    def test_lazy_compilation_of_endpoint_operands(self):
        """Test endpoint operands are compiled on access."""
        meta_data = {
            '@Name': 'LazyType',
            'Members': {
                'Member': [
                    {'@Name': 'Member1', '@DataType': 'DINT'}
                ]
            }
        }
        dt = self.CompilableDatatype(meta_data=meta_data)

        # First populate members manually
        member_mock = Mock(spec=IDatatypeMember)
        member_mock.name = 'Member1'
        dt._members = [member_mock]

        # Access triggers compilation
        operands = dt.get_endpoint_operands()

        # Endpoint operands should be populated
        self.assertIsNotNone(operands)
        self.assertGreater(len(operands), 0)


class TestDatatypeSpecialCases(unittest.TestCase):
    """Test special cases and boundary conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_parent_datatype = Mock(spec=IDatatype)

    def test_datatype_with_single_member(self):
        """Test datatype metadata with single member (not in list)."""
        # Some XML parsers return single member not as list
        meta_data = {
            '@Name': 'SingleMemberType',
            'Members': {
                'Member': {'@Name': 'OnlyMember', '@DataType': 'DINT'}
            }
        }

        dt = Datatype(meta_data=meta_data)

        # Should handle both list and single dict gracefully in subclass
        self.assertIsNotNone(dt.meta_data)

    def test_datatype_member_with_empty_name(self):
        """Test member with empty name."""
        member = DatatypeMember(
            meta_data={'@Name': ''},
            parent_datatype=self.mock_parent_datatype
        )

        self.assertEqual(member.name, '')

    def test_multiple_set_datatype_calls(self):
        """Test setting datatype multiple times."""
        member = DatatypeMember(
            meta_data={'@Name': 'Member1'},
            parent_datatype=self.mock_parent_datatype
        )

        dt1 = Mock(spec=IDatatype)
        dt1.name = 'Type1'
        dt2 = Mock(spec=IDatatype)
        dt2.name = 'Type2'

        member.set_datatype(dt1)
        self.assertEqual(member.get_datatype(), dt1)

        member.set_datatype(dt2)
        self.assertEqual(member.get_datatype(), dt2)

    def test_datatype_with_complex_metadata_structure(self):
        """Test datatype with deeply nested metadata."""
        meta_data = {
            '@Name': 'ComplexType',
            '@Description': 'Complex',
            'CustomData': {
                'Nested': {
                    'DeepNested': 'Value'
                }
            },
            'Members': {
                'Member': [
                    {
                        '@Name': 'Member1',
                        '@DataType': 'DINT',
                        'CustomAttribute': 'Value'
                    }
                ]
            }
        }

        dt = Datatype(meta_data=meta_data)

        self.assertEqual(dt.name, 'ComplexType')
        self.assertEqual(dt.meta_data, meta_data)


class TestDatatypeInheritance(unittest.TestCase):
    """Test inheritance chain and mixin behavior."""

    def test_datatype_inherits_from_plcobject(self):
        """Test Datatype inherits from PlcObject."""
        dt = Datatype(meta_data={'@Name': 'Test'})

        # Should have PlcObject methods and attributes
        self.assertTrue(hasattr(dt, 'compile'))
        self.assertTrue(hasattr(dt, 'invalidate'))
        self.assertTrue(hasattr(dt, 'set_name'))
        self.assertTrue(hasattr(dt, 'set_description'))

    def test_datatypemember_inherits_from_datatypeproto(self):
        """Test DatatypeMember inherits from DatatypeProto."""
        member = DatatypeMember(
            meta_data={'@Name': 'Member1'},
            parent_datatype=Mock(spec=IDatatype)
        )

        # Should have DatatypeProto interface
        self.assertTrue(hasattr(member, 'is_atomic'))
        self.assertTrue(hasattr(member, 'is_builtin'))

    def test_datatype_implements_idatatype_interface(self):
        """Test Datatype implements IDatatype interface."""
        class TestableDatatype(Datatype):
            def invalidate(self) -> None:
                pass

            @property
            def process_name(self) -> str:
                return "Test"

            def is_atomic(self) -> bool:
                return True

            def is_builtin(self) -> bool:
                return False

            def compile_endpoint_operands(self) -> None:
                self._endpoint_operands = ['']

            def compile_members(self) -> None:
                pass

            def get_family(self) -> str:
                return 'NoFamily'

        dt = TestableDatatype(meta_data={'@Name': 'Test'})

        # Should have IDatatype methods
        self.assertTrue(hasattr(dt, 'get_endpoint_operands'))
        self.assertTrue(hasattr(dt, 'get_family'))
        self.assertTrue(hasattr(dt, 'get_members'))
        self.assertTrue(hasattr(dt, 'endpoint_operands'))
        self.assertTrue(hasattr(dt, 'members'))


class TestBuiltinDatatypeImmutability(unittest.TestCase):
    """Test that built-in datatypes maintain integrity."""

    def test_builtin_names_are_correct(self):
        """Test all built-in datatype names match expected values."""
        expected_names = {
            'BOOL', 'BIT', 'SINT', 'INT', 'DINT', 'LINT',
            'USINT', 'UINT', 'UDINT', 'ULINT', 'REAL', 'LREAL',
            'STRING', 'TIMER', 'COUNTER'
        }

        builtin_names = {dt.name for dt in BUILTINS}

        self.assertEqual(builtin_names, expected_names)

    def test_builtins_list_length_matches_constants(self):
        """Test BUILTINS list contains expected number of items."""
        # Count individual datatype constants
        individual_constants = [
            BOOL, BIT, SINT, INT, DINT, LINT, USINT, UINT, UDINT, ULINT,
            REAL, LREAL, STRING, TIMER, COUNTER
        ]

        self.assertEqual(len(BUILTINS), len(individual_constants))

    def test_control_not_in_builtins(self):
        """Test CONTROL is defined but not in BUILTINS list."""
        self.assertEqual(CONTROL.name, 'CONTROL')
        self.assertNotIn(CONTROL, BUILTINS)

    def test_builtin_metadata_structure(self):
        """Test all builtins have proper metadata structure."""
        for dt in BUILTINS:
            self.assertIsInstance(dt.meta_data, dict)
            self.assertIn('@Name', dt.meta_data)
            self.assertIsInstance(dt.meta_data['@Name'], str)
            self.assertGreater(len(dt.meta_data['@Name']), 0)


class TestDatatypeStringRepresentation(unittest.TestCase):
    """Test string representation of datatypes."""

    def test_datatype_str(self):
        """Test __str__ returns name."""
        dt = Datatype(meta_data={'@Name': 'TestType'})

        self.assertEqual(str(dt), 'TestType')

    def test_datatype_repr(self):
        """Test __repr__ returns name."""
        dt = Datatype(meta_data={'@Name': 'TestType'})

        self.assertEqual(repr(dt), 'TestType')

    def test_datatypemember_str(self):
        """Test member __str__ returns name."""
        member = DatatypeMember(
            meta_data={'@Name': 'TestMember'},
            parent_datatype=Mock(spec=IDatatype)
        )

        self.assertEqual(str(member), 'TestMember')


if __name__ == '__main__':
    unittest.main(verbosity=2)
