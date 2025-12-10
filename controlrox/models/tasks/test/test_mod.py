"""Unit tests for controlrox.models.tasks.mod module."""
import unittest
from unittest.mock import Mock, patch

from pyrox.models.abc.list import HashList
from controlrox.interfaces import ITag, IRoutine, IRung
from controlrox.models import Controller, ControllerModificationSchema


class TestControllerModificationSchema(unittest.TestCase):
    """Test cases for ControllerModificationSchema class."""

    @patch('controlrox.models.tasks.mod.ControllerInstanceManager.get_controller')
    def setUp(self, mock_get_controller):
        """Set up test fixtures."""

        self.source_controller = Mock(spec=Controller)
        self.destination_controller = Mock(spec=Controller)

        # Set up hash lists for destination controller
        self.destination_controller.programs = HashList('name')
        self.destination_controller.tags = HashList('name')
        self.destination_controller.datatypes = HashList('name')

        # Set up hash lists for source controller
        self.source_controller.programs = HashList('name')
        self.source_controller.tags = HashList('name')
        self.source_controller.datatypes = HashList('name')

        mock_get_controller.return_value = self.destination_controller
        self.schema = ControllerModificationSchema()

    def test_initialization(self):
        """Test ControllerModificationSchema initialization."""
        self.assertEqual(self.schema.destination, self.destination_controller)
        self.assertEqual(self.schema.actions, [])

    def test_add_controller_tag_migration(self):
        """Test add_controller_tag_migration method."""
        self.schema.add_controller_tag_migration('TestTag')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'migrate_controller_tag')
        self.assertEqual(action['name'], 'TestTag')
        self.assertEqual(action['method'], self.schema._execute_controller_tag_migration)

    def test_add_datatype_migration(self):
        """Test add_datatype_migration method."""
        self.schema.add_datatype_migration('TestDatatype')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'migrate_datatype')
        self.assertEqual(action['name'], 'TestDatatype')
        self.assertEqual(action['method'], self.schema._execute_datatype_migration)

    def test_add_controller_tag(self):
        """Test add_controller_tag method."""
        mock_tag = Mock(spec=ITag)
        mock_tag.meta_data = {'@Name': 'TestTag', '@DataType': 'DINT'}

        result = self.schema.add_controller_tag(mock_tag)

        self.assertEqual(result, mock_tag)
        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'add_controller_tag')
        self.assertEqual(action['asset'], mock_tag.meta_data)
        self.assertEqual(action['method'], self.schema._execute_add_controller_tag)

    def test_add_controller_tag_invalid_type(self):
        """Test add_controller_tag method with invalid tag type."""
        with self.assertRaises(ValueError) as context:
            self.schema.add_controller_tag("invalid_tag")  # type: ignore
        self.assertIn("Tag must be an instance of Tag class", str(context.exception))

    def test_add_program_tag(self):
        """Test add_program_tag method."""
        mock_tag = Mock(spec=ITag)
        mock_tag.meta_data = {'@Name': 'ProgramTag', '@DataType': 'BOOL'}

        result = self.schema.add_program_tag('MainProgram', mock_tag)

        self.assertEqual(result, mock_tag)
        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'add_program_tag')
        self.assertEqual(action['program'], 'MainProgram')
        self.assertEqual(action['asset'], mock_tag.meta_data)
        self.assertEqual(action['method'], self.schema._execute_add_program_tag)

    def test_add_program_tag_invalid_type(self):
        """Test add_program_tag with invalid tag type."""
        with self.assertRaises(ValueError) as context:
            self.schema.add_program_tag('MainProgram', "not_a_tag")  # type: ignore
        self.assertIn("Tag must be an instance of Tag class", str(context.exception))

    def test_add_routine(self):
        """Test add_routine method."""
        mock_routine = Mock(spec=IRoutine)
        mock_routine.meta_data = {'@Name': 'TestRoutine', '@Type': 'RLL'}

        result = self.schema.add_routine('MainProgram', mock_routine)

        self.assertEqual(result, mock_routine)
        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'add_routine')
        self.assertEqual(action['program'], 'MainProgram')
        self.assertEqual(action['routine'], mock_routine.meta_data)
        self.assertEqual(action['method'], self.schema._execute_add_routine)

    def test_add_routine_invalid_type(self):
        """Test add_routine with invalid routine type."""
        with self.assertRaises(ValueError) as context:
            self.schema.add_routine('MainProgram', "not_a_routine")  # type: ignore
        self.assertIn("Routine must be an instance of Routine class", str(context.exception))

    def test_add_routine_migration(self):
        """Test add_routine_migration method."""
        self.schema.add_routine_migration(
            source_program_name='SourceProgram',
            routine_name='TestRoutine',
            destination_program_name='DestProgram',
            rung_updates={'1': 'new_rung'}
        )

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'migrate_routine')
        self.assertEqual(action['source_program'], 'SourceProgram')
        self.assertEqual(action['routine'], 'TestRoutine')
        self.assertEqual(action['destination_program'], 'DestProgram')
        self.assertEqual(action['rung_updates'], {'1': 'new_rung'})
        self.assertEqual(action['method'], self.schema._execute_routine_migration)

    def test_add_routine_migration_default_destination(self):
        """Test add_routine_migration method with default destination program."""
        self.schema.add_routine_migration(
            source_program_name='SourceProgram',
            routine_name='TestRoutine'
        )

        action = self.schema.actions[0]
        self.assertEqual(action['destination_program'], 'SourceProgram')
        self.assertEqual(action['rung_updates'], {})

    def test_add_rung(self):
        """Test add_rung method."""
        mock_rung = Mock(spec=IRung)
        mock_rung.meta_data = {'@Number': '5', 'Text': 'NOP();'}

        result = self.schema.add_rung('MainProgram', 'MainRoutine', mock_rung, rung_number=5)

        self.assertEqual(result, mock_rung)
        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'add_rung')
        self.assertEqual(action['program'], 'MainProgram')
        self.assertEqual(action['routine'], 'MainRoutine')
        self.assertEqual(action['rung_number'], 5)
        self.assertEqual(action['new_rung'], mock_rung.meta_data)
        self.assertEqual(action['method'], self.schema._execute_add_rung)

    def test_add_rung_invalid_type(self):
        """Test add_rung with invalid rung type."""
        with self.assertRaises(ValueError) as context:
            self.schema.add_rung('MainProgram', 'MainRoutine', "not_a_rung")  # type: ignore
        self.assertIn("Rung must be an instance of Rung class", str(context.exception))

    def test_add_import_from_file(self):
        """Test add_import_from_file method."""
        self.schema.add_import_from_file('test.L5X', ['Tags', 'DataTypes'])

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'import_from_file')
        self.assertEqual(action['file'], 'test.L5X')
        self.assertEqual(action['asset_types'], ['Tags', 'DataTypes'])
        self.assertEqual(action['method'], self.schema._execute_import_assets_from_file)

    def test_add_import_from_file_all_assets(self):
        """Test add_import_from_file with all asset types."""
        self.schema.add_import_from_file('test.L5X', None)

        action = self.schema.actions[0]
        self.assertIsNone(action['asset_types'])

    def test_add_safety_tag_mapping(self):
        """Test add_safety_tag_mapping method."""
        self.schema.add_safety_tag_mapping('StandardTag', 'SafetyTag')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'safety_tag_mapping')
        self.assertEqual(action['standard'], 'StandardTag')
        self.assertEqual(action['safety'], 'SafetyTag')
        self.assertEqual(action['method'], self.schema._execute_add_safety_tag_mapping)

    def test_add_safety_tag_mapping_invalid_types(self):
        """Test add_safety_tag_mapping method with invalid types."""
        with self.assertRaises(ValueError) as context:
            self.schema.add_safety_tag_mapping(123, 'SafetyTag')  # type: ignore
        self.assertIn("Source and destination tags must be strings", str(context.exception))

    def test_remove_controller_tag(self):
        """Test remove_controller_tag method."""
        self.schema.remove_controller_tag('TagToRemove')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'remove_controller_tag')
        self.assertEqual(action['name'], 'TagToRemove')
        self.assertEqual(action['method'], self.schema._execute_remove_controller_tag)

    def test_remove_datatype(self):
        """Test remove_datatype method."""
        self.schema.remove_datatype('DatatypeToRemove')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'remove_datatype')
        self.assertEqual(action['name'], 'DatatypeToRemove')
        self.assertEqual(action['method'], self.schema._execute_remove_datatype)

    def test_remove_program_tag(self):
        """Test remove_program_tag method."""
        self.schema.remove_program_tag('MainProgram', 'TagToRemove')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'remove_program_tag')
        self.assertEqual(action['program'], 'MainProgram')
        self.assertEqual(action['name'], 'TagToRemove')
        self.assertEqual(action['method'], self.schema._execute_remove_program_tag)

    def test_remove_routine(self):
        """Test remove_routine method."""
        self.schema.remove_routine('TestProgram', 'RoutineToRemove')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'remove_routine')
        self.assertEqual(action['program'], 'TestProgram')
        self.assertEqual(action['name'], 'RoutineToRemove')
        self.assertEqual(action['method'], self.schema._execute_remove_routine)

    def test_remove_safety_tag_mapping(self):
        """Test remove_safety_tag_mapping method."""
        self.schema.remove_safety_tag_mapping('StandardTag', 'SafetyTag')

        self.assertEqual(len(self.schema.actions), 1)
        action = self.schema.actions[0]
        self.assertEqual(action['type'], 'remove_safety_tag_mapping')
        self.assertEqual(action['standard'], 'StandardTag')
        self.assertEqual(action['safety'], 'SafetyTag')
        self.assertEqual(action['method'], self.schema._execute_remove_safety_tag_mapping)

    def test_safe_register_action(self):
        """Test _safe_register_action method."""
        action1 = {'type': 'test_action', 'data': 'test'}
        action2 = {'type': 'test_action', 'data': 'test'}  # Duplicate
        action3 = {'type': 'different_action', 'data': 'test'}

        self.schema._safe_register_action(action1)
        self.schema._safe_register_action(action2)  # Should not be added (duplicate)
        self.schema._safe_register_action(action3)

        self.assertEqual(len(self.schema.actions), 2)
        self.assertIn(action1, self.schema.actions)
        self.assertIn(action3, self.schema.actions)

    def test_execute_with_valid_methods(self):
        """Test execute method with valid action methods."""
        self.destination_controller.compile = Mock()

        # Create actions with mock methods
        mock_method1 = Mock()
        mock_method2 = Mock()

        self.schema.actions = [
            {'type': 'test1', 'method': mock_method1, 'data': 'test1'},
            {'type': 'test2', 'method': mock_method2, 'data': 'test2'}
        ]

        self.schema.execute()

        # Verify methods were called with correct actions
        mock_method1.assert_called_once_with({'type': 'test1', 'method': mock_method1, 'data': 'test1'})
        mock_method2.assert_called_once_with({'type': 'test2', 'method': mock_method2, 'data': 'test2'})
        self.destination_controller.compile.assert_called_once()

    def test_execute_with_invalid_method(self):
        """Test execute method with invalid action method."""
        self.destination_controller.compile = Mock()

        self.schema.actions = [
            {'type': 'test', 'method': 'not_callable'}
        ]

        self.schema.execute()

        # Should not raise error, just log warning and call compile
        self.destination_controller.compile.assert_called_once()

    def test_execute_controller_tag_migration_tag_not_found(self):
        """Test _execute_controller_tag_migration when tag doesn't exist."""
        self.destination_controller.compile = Mock()

        action = {
            'type': 'migrate_controller_tag',
            'name': 'NonExistentTag',
            'method': self.schema._execute_controller_tag_migration
        }

        # Should not raise error, just log warning
        self.schema._execute_controller_tag_migration(action)

    def test_execute_controller_tag_migration_no_source(self):
        """Test _execute_controller_tag_migration with no source controller."""
        self.schema.source = None
        self.destination_controller.compile = Mock()

        action = {
            'type': 'migrate_controller_tag',
            'name': 'TestTag',
            'method': self.schema._execute_controller_tag_migration
        }

        # Should not raise error, just log warning
        self.schema._execute_controller_tag_migration(action)

    def test_execute_add_controller_tag(self):
        """Test _execute_add_controller_tag method."""
        tag_data = {'@Name': 'NewTag', '@DataType': 'DINT'}

        # Set up destination methods
        mock_tag = Mock(spec=ITag)
        mock_tag.name = 'NewTag'
        self.destination_controller.create_tag = Mock(return_value=mock_tag)
        self.destination_controller.add_tag = Mock()
        self.destination_controller.compile = Mock()

        action = {
            'type': 'add_controller_tag',
            'asset': tag_data,
            'method': self.schema._execute_add_controller_tag
        }

        self.schema._execute_add_controller_tag(action)

        # Verify tag was created and added
        self.destination_controller.create_tag.assert_called_once()
        self.destination_controller.add_tag.assert_called_once_with(mock_tag)

    def test_execute_add_controller_tag_no_data(self):
        """Test _execute_add_controller_tag with no tag data."""
        self.destination_controller.compile = Mock()

        action = {
            'type': 'add_controller_tag',
            'method': self.schema._execute_add_controller_tag
        }

        # Should not raise error, just log warning
        self.schema._execute_add_controller_tag(action)

    def test_execute_import_assets_from_file(self):
        """Test _execute_import_assets_from_file method."""
        self.destination_controller.import_assets_from_file = Mock()
        self.destination_controller.compile = Mock()

        action = {
            'type': 'import_from_file',
            'file': 'test.L5X',
            'asset_types': ['Tags', 'DataTypes'],
            'method': self.schema._execute_import_assets_from_file
        }

        self.schema._execute_import_assets_from_file(action)

        # Verify import was called
        self.destination_controller.import_assets_from_file.assert_called_once_with(
            'test.L5X',
            ['Tags', 'DataTypes']
        )

    def test_execute_import_assets_from_file_no_location(self):
        """Test _execute_import_assets_from_file with no file location."""
        self.destination_controller.compile = Mock()

        action = {
            'type': 'import_from_file',
            'asset_types': ['Tags'],
            'method': self.schema._execute_import_assets_from_file
        }

        # Should not raise error, just log warning
        self.schema._execute_import_assets_from_file(action)

    def test_execute_remove_controller_tag(self):
        """Test _execute_remove_controller_tag method."""
        mock_tag = Mock(spec=ITag)
        mock_tag.name = 'TagToRemove'
        self.destination_controller.tags.append(mock_tag)

        self.destination_controller.remove_tag = Mock()
        self.destination_controller.compile = Mock()

        action = {
            'type': 'remove_controller_tag',
            'name': 'TagToRemove',
            'method': self.schema._execute_remove_controller_tag
        }

        self.schema._execute_remove_controller_tag(action)

        # Verify tag was removed
        self.destination_controller.remove_tag.assert_called_once_with(mock_tag)

    def test_execute_remove_controller_tag_not_found(self):
        """Test _execute_remove_controller_tag when tag doesn't exist."""
        self.destination_controller.compile = Mock()

        action = {
            'type': 'remove_controller_tag',
            'name': 'NonExistentTag',
            'method': self.schema._execute_remove_controller_tag
        }

        # Should not raise error, just log warning
        self.schema._execute_remove_controller_tag(action)

    def test_execute_remove_datatype(self):
        """Test _execute_remove_datatype method."""
        mock_datatype = Mock()
        mock_datatype.name = 'DatatypeToRemove'
        self.destination_controller.datatypes.append(mock_datatype)

        self.destination_controller.remove_datatype = Mock()
        self.destination_controller.compile = Mock()

        action = {
            'type': 'remove_datatype',
            'name': 'DatatypeToRemove',
            'method': self.schema._execute_remove_datatype
        }

        self.schema._execute_remove_datatype(action)

        # Verify datatype was removed
        self.destination_controller.remove_datatype.assert_called_once_with(mock_datatype)

    def test_execute_add_safety_tag_mapping(self):
        """Test _execute_add_safety_tag_mapping method."""
        mock_safety_info = Mock()
        mock_safety_info.add_safety_tag_mapping = Mock()
        self.destination_controller.safety_info = mock_safety_info
        self.destination_controller.compile = Mock()

        action = {
            'type': 'safety_tag_mapping',
            'standard': 'StandardTag',
            'safety': 'SafetyTag',
            'method': self.schema._execute_add_safety_tag_mapping
        }

        self.schema._execute_add_safety_tag_mapping(action)

        # Verify mapping was added
        mock_safety_info.add_safety_tag_mapping.assert_called_once_with('StandardTag', 'SafetyTag')

    def test_execute_add_safety_tag_mapping_missing_tags(self):
        """Test _execute_add_safety_tag_mapping with missing tag data."""
        self.destination_controller.compile = Mock()

        action = {
            'type': 'safety_tag_mapping',
            'standard': 'StandardTag',
            'method': self.schema._execute_add_safety_tag_mapping
        }

        # Should not raise error, just log warning
        self.schema._execute_add_safety_tag_mapping(action)

    def test_multiple_actions_chaining(self):
        """Test that multiple actions can be chained together."""
        self.schema.add_controller_tag_migration('Tag1')
        self.schema.add_datatype_migration('Datatype1')
        self.schema.remove_controller_tag('Tag2')
        self.schema.add_import_from_file('test.L5X', ['Programs'])

        self.assertEqual(len(self.schema.actions), 4)
        self.assertEqual(self.schema.actions[0]['type'], 'migrate_controller_tag')
        self.assertEqual(self.schema.actions[1]['type'], 'migrate_datatype')
        self.assertEqual(self.schema.actions[2]['type'], 'remove_controller_tag')
        self.assertEqual(self.schema.actions[3]['type'], 'import_from_file')


class TestControllerModificationSchemaIntegration(unittest.TestCase):
    """Integration tests for ControllerModificationSchema with realistic scenarios."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.source_controller = Mock(spec=Controller)
        self.destination_controller = Mock(spec=Controller)

        # Set up hash lists
        self.source_controller.programs = HashList('name')
        self.source_controller.tags = HashList('name')
        self.source_controller.datatypes = HashList('name')
        self.destination_controller.programs = HashList('name')
        self.destination_controller.tags = HashList('name')
        self.destination_controller.datatypes = HashList('name')

        self.schema = ControllerModificationSchema()

    def test_complete_migration_workflow(self):
        """Test complete migration workflow with multiple operations."""
        # Add multiple actions
        self.schema.add_controller_tag_migration('ProcessValue')
        self.schema.add_datatype_migration('CustomStruct')
        self.schema.add_import_from_file('additions.L5X', ['Programs'])
        self.schema.remove_controller_tag('ObsoleteTag')

        # Verify all actions were registered
        self.assertEqual(len(self.schema.actions), 4)

        # Verify action types
        types = [action['type'] for action in self.schema.actions]
        self.assertIn('migrate_controller_tag', types)
        self.assertIn('migrate_datatype', types)
        self.assertIn('import_from_file', types)
        self.assertIn('remove_controller_tag', types)

    def test_action_order_preservation(self):
        """Test that actions maintain their registration order."""
        self.schema.add_controller_tag_migration('Tag1')
        self.schema.add_datatype_migration('DT1')
        self.schema.add_controller_tag_migration('Tag2')
        self.schema.add_datatype_migration('DT2')

        # Verify order is preserved
        self.assertEqual(self.schema.actions[0]['name'], 'Tag1')
        self.assertEqual(self.schema.actions[1]['name'], 'DT1')
        self.assertEqual(self.schema.actions[2]['name'], 'Tag2')
        self.assertEqual(self.schema.actions[3]['name'], 'DT2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
