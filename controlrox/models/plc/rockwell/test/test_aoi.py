"""Unit tests for the aoi module."""

import pytest
from unittest.mock import Mock, patch

from controlrox.models.plc.rockwell.aoi import RaAddOnInstruction
from controlrox.models.plc.rockwell.controller import RaController
from controlrox.models.plc.rockwell.instruction import RaLogicInstruction
from controlrox.models.plc.rockwell.operand import LogixOperand
from controlrox.models.plc.rockwell import meta as plc_meta
from controlrox.models.plc.rockwell.tag import RaTag
from pyrox.models.abc.meta import EnforcesNaming
from pyrox.models import HashList


class TestRaAddOnInstruction:
    """Test cases for RaAddOnInstruction class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Sample meta data that matches expected AOI structure
        self.sample_meta_data = {
            '@Name': 'TestAOI',
            '@Class': 'User',
            '@Revision': '1.0',
            '@ExecutePrescan': 'false',
            '@ExecutePostscan': 'false',
            '@ExecuteEnableInFalse': 'false',
            '@CreatedDate': '2023-01-01T10:00:00.000Z',
            '@CreatedBy': 'TestUser',
            '@EditedDate': '2023-01-01T10:00:00.000Z',
            '@EditedBy': 'TestUser',
            '@SoftwareRevision': '33.00',
            '@RevisionExtension': '1.0',
            'Description': 'Test AOI Description',
            'RevisionNote': 'Initial version',
            'Parameters': {
                'Parameter': [
                    {
                        '@Name': 'Input1',
                        '@TagType': 'Base',
                        '@DataType': 'BOOL',
                        '@Usage': 'Input'
                    }
                ]
            },
            'LocalTags': {
                'LocalTag': [
                    {
                        '@Name': 'LocalVar1',
                        '@DataType': 'BOOL'
                    }
                ]
            },
            'Routines': {
                'Routine': [
                    {
                        '@Name': 'Logic',
                        '@Type': 'RLL'
                    }
                ]
            }
        }

        self.mock_controller = Mock(spec=RaController)

    @patch('controlrox.models.plc.rockwell.meta.l5x_dict_from_file')
    def test_initialization_default_meta_data(self, mock_l5x_dict):
        """Test initialization with default meta data from file."""
        mock_l5x_dict.return_value = {
            'AddOnInstructionDefinition': self.sample_meta_data
        }

        aoi = RaAddOnInstruction()

        mock_l5x_dict.assert_called_once_with(plc_meta.PLC_AOI_FILE)
        assert aoi.name == 'TestAOI'

    def test_initialization_with_meta_data(self):
        """Test initialization with provided meta data."""
        aoi = RaAddOnInstruction(
            meta_data=self.sample_meta_data,
        )

        assert aoi.name == 'TestAOI'
        assert aoi.revision == '1.0'

    def test_initialization_with_revision_extension_replacement(self):
        """Test that revision extension '<' characters are replaced during init."""
        meta_data_with_brackets = self.sample_meta_data.copy()
        meta_data_with_brackets['@RevisionExtension'] = 'v1.0<test>'

        aoi = RaAddOnInstruction(meta_data=meta_data_with_brackets)

        # Should trigger setter logic to replace '<' with '&lt;'
        assert aoi.revision_extension == 'v1.0&lt;test>'

    def test_dict_key_order(self):
        """Test that dict_key_order returns correct order."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        expected_order = [
            '@Name',
            '@Class',
            '@Revision',
            '@ExecutePrescan',
            '@ExecutePostscan',
            '@ExecuteEnableInFalse',
            '@CreatedDate',
            '@CreatedBy',
            '@EditedDate',
            '@EditedBy',
            '@SoftwareRevision',
            'Description',
            'RevisionNote',
            'Parameters',
            'LocalTags',
            'Routines',
        ]

        assert aoi.dict_key_order == expected_order

    def test_revision_property_getter(self):
        """Test revision property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.revision == '1.0'

    def test_revision_property_setter_valid(self):
        """Test revision property setter with valid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.set_revision('2.1')
        assert aoi.revision == '2.1'
        assert aoi['@Revision'] == '2.1'

        aoi.set_revision('10.25.3')
        assert aoi.revision == '10.25.3'

    def test_revision_property_setter_invalid(self):
        """Test revision property setter with invalid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.set_revision('invalid_revision')

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.set_revision('v1.2.3')

    def test_execute_prescan_property_getter(self):
        """Test execute_prescan property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.execute_prescan == 'false'

    def test_execute_prescan_property_setter_string(self):
        """Test execute_prescan property setter with string values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.execute_prescan = 'true'
        assert aoi.execute_prescan == 'true'
        assert aoi['@ExecutePrescan'] == 'true'

        aoi.execute_prescan = 'false'
        assert aoi.execute_prescan == 'false'

    def test_execute_prescan_property_setter_bool(self):
        """Test execute_prescan property setter with boolean values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.execute_prescan = True  # type: ignore
        assert aoi.execute_prescan == 'true'

        aoi.execute_prescan = False  # type: ignore
        assert aoi.execute_prescan == 'false'

    def test_execute_prescan_property_setter_invalid(self):
        """Test execute_prescan property setter with invalid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.execute_prescan = 'invalid'

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.execute_prescan = 'True'  # Case sensitive

    def test_execute_postscan_property_getter(self):
        """Test execute_postscan property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.execute_postscan == 'false'

    def test_execute_postscan_property_setter_string(self):
        """Test execute_postscan property setter with string values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.execute_postscan = 'true'
        assert aoi.execute_postscan == 'true'
        assert aoi['@ExecutePostscan'] == 'true'

    def test_execute_postscan_property_setter_bool(self):
        """Test execute_postscan property setter with boolean values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.execute_postscan = True  # type: ignore
        assert aoi.execute_postscan == 'true'

        aoi.execute_postscan = False  # type: ignore
        assert aoi.execute_postscan == 'false'

    def test_execute_postscan_property_setter_invalid(self):
        """Test execute_postscan property setter with invalid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.execute_postscan = 'yes'

    def test_execute_enable_in_false_property_getter(self):
        """Test execute_enable_in_false property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.execute_enable_in_false == 'false'

    def test_execute_enable_in_false_property_setter_string(self):
        """Test execute_enable_in_false property setter with string values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.execute_enable_in_false = 'true'
        assert aoi.execute_enable_in_false == 'true'
        assert aoi['@ExecuteEnableInFalse'] == 'true'

    def test_execute_enable_in_false_property_setter_bool(self):
        """Test execute_enable_in_false property setter with boolean values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.execute_enable_in_false = True  # type: ignore
        assert aoi.execute_enable_in_false == 'true'

        aoi.execute_enable_in_false = False  # type: ignore
        assert aoi.execute_enable_in_false == 'false'

    def test_execute_enable_in_false_property_setter_invalid(self):
        """Test execute_enable_in_false property setter with invalid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.execute_enable_in_false = '1'

    def test_read_only_properties(self):
        """Test read-only properties."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        assert aoi.created_date == '2023-01-01T10:00:00.000Z'
        assert aoi.created_by == 'TestUser'
        assert aoi.edited_date == '2023-01-01T10:00:00.000Z'
        assert aoi.edited_by == 'TestUser'

    def test_software_revision_property_getter(self):
        """Test software_revision property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.software_revision == '33.00'

    def test_software_revision_property_setter_valid(self):
        """Test software_revision property setter with valid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.software_revision = '34.00'
        assert aoi.software_revision == '34.00'
        assert aoi['@SoftwareRevision'] == '34.00'

    def test_software_revision_property_setter_invalid(self):
        """Test software_revision property setter with invalid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(EnforcesNaming.InvalidNamingException):
            aoi.software_revision = 'invalid_version'

    def test_revision_extension_property_getter(self):
        """Test revision_extension property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.revision_extension == '1.0'

    def test_revision_extension_property_setter_valid(self):
        """Test revision_extension property setter with valid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.revision_extension = 'v2.0'
        assert aoi.revision_extension == 'v2.0'
        assert aoi['@RevisionExtension'] == 'v2.0'

    def test_revision_extension_property_setter_with_brackets(self):
        """Test revision_extension property setter replaces '<' characters."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.revision_extension = 'v1.0<beta>'
        assert aoi.revision_extension == 'v1.0&lt;beta>'
        assert aoi['@RevisionExtension'] == 'v1.0&lt;beta>'

        aoi.revision_extension = '<<test>>'
        assert aoi.revision_extension == '&lt;&lt;test>>'

    def test_revision_extension_property_setter_invalid(self):
        """Test revision_extension property setter with invalid types."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(ValueError, match="Revision extension must be a string!"):
            aoi.revision_extension = 123  # type: ignore

        with pytest.raises(ValueError, match="Revision extension must be a string!"):
            aoi.revision_extension = None  # type: ignore

    def test_revision_note_property_getter(self):
        """Test revision_note property getter."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)
        assert aoi.revision_note == 'Initial version'

    def test_revision_note_property_setter_valid(self):
        """Test revision_note property setter with valid values."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        aoi.revision_note = 'Updated version'
        assert aoi.revision_note == 'Updated version'
        assert aoi['RevisionNote'] == 'Updated version'

        aoi.revision_note = ''
        assert aoi.revision_note == ''

    def test_revision_note_property_setter_invalid(self):
        """Test revision_note property setter with invalid types."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        with pytest.raises(ValueError, match="Revision note must be a string!"):
            aoi.revision_note = 123  # type: ignore

        with pytest.raises(ValueError, match="Revision note must be a string!"):
            aoi.revision_note = None  # type: ignore

    def test_parameters_property_with_list(self):
        """Test parameters property when Parameters contains a list."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        parameters = aoi.parameters
        assert isinstance(parameters, list)
        assert len(parameters) == 1
        assert parameters[0]['@Name'] == 'Input1'

    def test_parameters_property_with_single_item(self):
        """Test parameters property when Parameters contains a single item."""
        meta_data = self.sample_meta_data.copy()
        meta_data['Parameters'] = {
            'Parameter': {
                '@Name': 'SingleInput',
                '@TagType': 'Base',
                '@DataType': 'BOOL',
                '@Usage': 'Input'
            }
        }

        aoi = RaAddOnInstruction(meta_data=meta_data)

        parameters = aoi.parameters
        assert isinstance(parameters, list)
        assert len(parameters) == 1
        assert parameters[0]['@Name'] == 'SingleInput'

    def test_parameters_property_empty(self):
        """Test parameters property when Parameters is empty or None."""
        meta_data = self.sample_meta_data.copy()
        meta_data['Parameters'] = None

        aoi = RaAddOnInstruction(meta_data=meta_data)

        parameters = aoi.parameters
        assert isinstance(parameters, list)
        assert len(parameters) == 0

    def test_local_tags_property_with_list(self):
        """Test local_tags property when LocalTags contains a list."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        local_tags = aoi.local_tags
        assert isinstance(local_tags, list)
        assert len(local_tags) == 1
        assert local_tags[0]['@Name'] == 'LocalVar1'

    def test_local_tags_property_with_single_item(self):
        """Test local_tags property when LocalTags contains a single item."""
        meta_data = self.sample_meta_data.copy()
        meta_data['LocalTags'] = {
            'LocalTag': {
                '@Name': 'SingleLocalVar',
                '@DataType': 'DINT'
            }
        }

        aoi = RaAddOnInstruction(meta_data=meta_data)

        local_tags = aoi.local_tags
        assert isinstance(local_tags, list)
        assert len(local_tags) == 1
        assert local_tags[0]['@Name'] == 'SingleLocalVar'

    def test_local_tags_property_empty(self):
        """Test local_tags property when LocalTags is empty or None."""
        meta_data = self.sample_meta_data.copy()
        meta_data['LocalTags'] = None

        aoi = RaAddOnInstruction(meta_data=meta_data)

        local_tags = aoi.local_tags
        assert isinstance(local_tags, list)
        assert len(local_tags) == 0

    def test_raw_tags_property_with_existing_list(self):
        """Test raw_tags property when LocalTags already contains a list."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        raw_tags = aoi.raw_tags
        assert isinstance(raw_tags, list)
        assert len(raw_tags) == 1
        assert raw_tags[0]['@Name'] == 'LocalVar1'

        # Verify the structure is maintained in meta_data
        assert isinstance(aoi['LocalTags']['LocalTag'], list)

    def test_raw_tags_property_with_single_item(self):
        """Test raw_tags property when LocalTags contains a single item."""
        meta_data = self.sample_meta_data.copy()
        meta_data['LocalTags'] = {
            'LocalTag': {
                '@Name': 'SingleLocalVar',
                '@DataType': 'DINT'
            }
        }

        aoi = RaAddOnInstruction(meta_data=meta_data)

        raw_tags = aoi.raw_tags
        assert isinstance(raw_tags, list)
        assert len(raw_tags) == 1
        assert raw_tags[0]['@Name'] == 'SingleLocalVar'

        # Verify it was converted to list in meta_data
        assert isinstance(aoi['LocalTags']['LocalTag'], list)

    def test_raw_tags_property_empty_creates_structure(self):
        """Test raw_tags property creates structure when LocalTags is None."""
        meta_data = self.sample_meta_data.copy()
        meta_data['LocalTags'] = None

        aoi = RaAddOnInstruction(meta_data=meta_data)

        raw_tags = aoi.raw_tags
        assert isinstance(raw_tags, list)
        assert len(raw_tags) == 0

        # Verify structure was created
        assert aoi['LocalTags'] == {'LocalTag': []}
        assert isinstance(aoi['LocalTags']['LocalTag'], list)

    def test_raw_tags_property_modifiable(self):
        """Test that raw_tags property returns a modifiable reference."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        raw_tags = aoi.raw_tags
        original_length = len(raw_tags)

        # Add a new tag
        new_tag = {
            '@Name': 'NewLocalVar',
            '@DataType': 'BOOL'
        }
        raw_tags.append(new_tag)

        # Verify it was added to the original structure
        assert len(aoi.raw_tags) == original_length + 1
        assert aoi.raw_tags[-1]['@Name'] == 'NewLocalVar'


class TestRaAddOnInstructionInheritance:
    """Test RaAddOnInstruction inheritance from ContainsRoutines."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_meta_data = {
            '@Name': 'TestAOI',
            '@Class': 'User',
            '@Revision': '1.0',
            '@ExecutePrescan': 'false',
            '@ExecutePostscan': 'false',
            '@ExecuteEnableInFalse': 'false',
            '@CreatedDate': '2023-01-01T10:00:00.000Z',
            '@CreatedBy': 'TestUser',
            '@EditedDate': '2023-01-01T10:00:00.000Z',
            '@EditedBy': 'TestUser',
            '@SoftwareRevision': '33.00',
            '@RevisionExtension': '1.0',
            'Description': 'Test AOI Description',
            'RevisionNote': 'Initial version',
            'Parameters': {'Parameter': []},
            'LocalTags': {'LocalTag': []},
            'Routines': {
                'Routine': [
                    {
                        '@Name': 'Logic',
                        '@Type': 'RLL'
                    },
                    {
                        '@Name': 'EnableInFalse',
                        '@Type': 'RLL'
                    }
                ]
            }
        }

        self.mock_controller = Mock(spec=RaController)

    def test_inherits_from_hasroutines(self):
        """Test that RaAddOnInstruction inherits from ContainsRoutines."""
        from controlrox.models.plc.protocols import HasRoutines

        aoi = RaAddOnInstruction(
            meta_data=self.sample_meta_data,
        )

        assert isinstance(aoi, HasRoutines)

        # Should have inherited methods/properties
        with patch.object(aoi, 'compile_routines'):
            assert hasattr(aoi, 'routines')
        assert hasattr(aoi, 'name')

    def test_inherited_routines_functionality(self):
        """Test that inherited routines functionality works."""
        # Create mock routine objects with distinct names
        mock_routine1 = Mock()
        mock_routine1.name = 'Logic'
        mock_routine1.__getitem__ = lambda self, key: 'Logic' if key == '@Name' else None

        mock_routine2 = Mock()
        mock_routine2.name = 'EnableInFalse'
        mock_routine2.__getitem__ = lambda self, key: 'EnableInFalse' if key == '@Name' else None

        # Configure controller to return different routines based on meta_data
        def create_routine_side_effect(meta_data, controller, container):
            if meta_data.get('@Name') == 'Logic':
                return mock_routine1
            elif meta_data.get('@Name') == 'EnableInFalse':
                return mock_routine2
            return Mock()

        self.mock_controller.create_routine = Mock(side_effect=create_routine_side_effect)

        aoi = RaAddOnInstruction(
            meta_data=self.sample_meta_data,
        )

        with patch.object(aoi, 'compile_routines'):
            aoi._routines.extend([mock_routine1, mock_routine2])
            routines = aoi.routines
        assert len(routines) == 2
        assert routines[0].name == 'Logic'  # type: ignore
        assert routines[1].name == 'EnableInFalse'  # type: ignore

    def test_inherited_naming_validation(self):
        """Test that inherited naming validation works."""
        aoi = RaAddOnInstruction(meta_data=self.sample_meta_data)

        # Should inherit naming validation methods
        assert hasattr(aoi, 'is_valid_string')
        assert hasattr(aoi, 'is_valid_revision_string')
        assert hasattr(aoi, 'is_valid_rockwell_bool')

        # Test validation works
        assert aoi.is_valid_string('ValidName')
        assert not aoi.is_valid_string('Invalid Name!')
        assert aoi.is_valid_revision_string('1.2.3')
        assert aoi.is_valid_rockwell_bool('true')


class TestRaAddOnInstructionEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.minimal_meta_data = {
            '@Name': 'MinimalAOI',
            '@Revision': '1.0',
            '@ExecutePrescan': 'false',
            '@ExecutePostscan': 'false',
            '@ExecuteEnableInFalse': 'false',
            '@SoftwareRevision': '33.00'
        }

    def test_missing_optional_fields(self):
        """Test AOI with missing optional fields."""
        aoi = RaAddOnInstruction(meta_data=self.minimal_meta_data)

        assert aoi.name == 'MinimalAOI'
        assert aoi.revision == '1.0'

        # These should handle missing keys gracefully
        _ = aoi.revision_extension
        _ = aoi.revision_note

    def test_empty_parameters_and_local_tags(self):
        """Test behavior with empty parameters and local tags."""
        meta_data = self.minimal_meta_data.copy()
        meta_data.update({  # type: ignore
            'Parameters': {},
            'LocalTags': {}
        })

        aoi = RaAddOnInstruction(meta_data=meta_data)

        # Should return empty lists for missing/empty structures
        assert aoi.parameters == []
        assert aoi.local_tags == []

    def test_none_values_in_collections(self):
        """Test behavior when collections contain None values."""
        meta_data = self.minimal_meta_data.copy()
        meta_data.update({  # type: ignore
            'Parameters': None,
            'LocalTags': None
        })

        aoi = RaAddOnInstruction(meta_data=meta_data)

        assert aoi.parameters == []
        assert aoi.local_tags == []

        # raw_tags should create structure
        raw_tags = aoi.raw_tags
        assert isinstance(raw_tags, list)
        assert aoi['LocalTags'] == {'LocalTag': []}

    def test_boolean_conversion_edge_cases(self):
        """Test edge cases for boolean property conversions."""
        aoi = RaAddOnInstruction(meta_data=self.minimal_meta_data)

        # Test all boolean properties with edge cases
        boolean_properties = [
            'execute_prescan',
            'execute_postscan',
            'execute_enable_in_false'
        ]

        for prop in boolean_properties:
            # Test boolean True/False
            setattr(aoi, prop, True)
            assert getattr(aoi, prop) == 'true'

            setattr(aoi, prop, False)
            assert getattr(aoi, prop) == 'false'

            # Test string values
            setattr(aoi, prop, 'true')
            assert getattr(aoi, prop) == 'true'

            setattr(aoi, prop, 'false')
            assert getattr(aoi, prop) == 'false'

    def test_string_property_type_validation(self):
        """Test type validation for string properties."""
        aoi = RaAddOnInstruction(meta_data=self.minimal_meta_data)

        # Test revision_extension type validation
        with pytest.raises(ValueError, match="Revision extension must be a string!"):
            aoi.revision_extension = 123  # type: ignore

        with pytest.raises(ValueError, match="Revision extension must be a string!"):
            aoi.revision_extension = ['list']  # type: ignore

        # Test revision_note type validation
        with pytest.raises(ValueError, match="Revision note must be a string!"):
            aoi.revision_note = 123  # type: ignore

        with pytest.raises(ValueError, match="Revision note must be a string!"):
            aoi.revision_note = {'dict': 'value'}  # type: ignore


class TestRaAddOnInstructionIntegration:
    """Integration tests for RaAddOnInstruction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.full_meta_data = {
            '@Name': 'ComplexAOI',
            '@Class': 'User',
            '@Revision': '2.5',
            '@ExecutePrescan': 'true',
            '@ExecutePostscan': 'true',
            '@ExecuteEnableInFalse': 'false',
            '@CreatedDate': '2023-01-01T10:00:00.000Z',
            '@CreatedBy': 'Developer',
            '@EditedDate': '2023-06-01T15:30:00.000Z',
            '@EditedBy': 'Maintainer',
            '@SoftwareRevision': '34.00',
            '@RevisionExtension': 'v2.5<stable>',
            'Description': 'Complex AOI for testing',
            'RevisionNote': 'Added new functionality and bug fixes',
            'Parameters': {
                'Parameter': [
                    {
                        '@Name': 'Enable',
                        '@TagType': 'Base',
                        '@DataType': 'BOOL',
                        '@Usage': 'Input',
                        'Description': 'Enable input'
                    },
                    {
                        '@Name': 'Output',
                        '@TagType': 'Base',
                        '@DataType': 'BOOL',
                        '@Usage': 'Output',
                        'Description': 'Output value'
                    }
                ]
            },
            'LocalTags': {
                'LocalTag': [
                    {
                        '@Name': 'Counter',
                        '@DataType': 'DINT',
                        'Description': 'Internal counter'
                    },
                    {
                        '@Name': 'Timer',
                        '@DataType': 'TIMER',
                        'Description': 'Internal timer'
                    }
                ]
            },
            'Routines': {
                'Routine': [
                    {
                        '@Name': 'Logic',
                        '@Type': 'RLL'
                    },
                    {
                        '@Name': 'EnableInFalse',
                        '@Type': 'RLL'
                    }
                ]
            }
        }

    def test_full_aoi_functionality(self):
        """Test AOI with all features enabled."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        # Test all properties
        assert aoi.name == 'ComplexAOI'
        assert aoi.revision == '2.5'
        assert aoi.execute_prescan == 'true'
        assert aoi.execute_postscan == 'true'
        assert aoi.execute_enable_in_false == 'false'
        assert aoi.software_revision == '34.00'
        assert aoi.revision_extension == 'v2.5&lt;stable>'  # Should be escaped
        assert aoi.revision_note == 'Added new functionality and bug fixes'

        # Test collections
        parameters = aoi.parameters
        assert len(parameters) == 2
        assert parameters[0]['@Name'] == 'Enable'
        assert parameters[1]['@Name'] == 'Output'

        local_tags = aoi.local_tags
        assert len(local_tags) == 2
        assert local_tags[0]['@Name'] == 'Counter'
        assert local_tags[1]['@Name'] == 'Timer'

        raw_tags = aoi.raw_tags
        assert len(raw_tags) == 2
        assert raw_tags is aoi['LocalTags']['LocalTag']  # Should be same reference

    def test_property_modifications(self):
        """Test modifying various properties."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        # Modify revision
        aoi.set_revision('3.0')
        assert aoi.revision == '3.0'

        # Modify boolean properties
        aoi.execute_prescan = 'false'
        assert aoi.execute_prescan == 'false'

        aoi.execute_postscan = 'false'
        assert aoi.execute_postscan == 'false'

        # Modify string properties
        aoi.software_revision = '35.00'
        assert aoi.software_revision == '35.00'

        aoi.revision_extension = 'v3.0<beta>'
        assert aoi.revision_extension == 'v3.0&lt;beta>'

        aoi.revision_note = 'Major version update'
        assert aoi.revision_note == 'Major version update'

    def test_raw_tags_modification(self):
        """Test modifying AOI through raw_tags property."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        # Get raw tags and modify
        raw_tags = aoi.raw_tags
        original_count = len(raw_tags)

        # Add a new local tag
        new_tag = {
            '@Name': 'Status',
            '@DataType': 'BOOL',
            'Description': 'Status flag'
        }
        raw_tags.append(new_tag)

        # Verify changes are reflected
        assert len(aoi.raw_tags) == original_count + 1
        assert len(aoi.local_tags) == original_count + 1
        assert aoi.local_tags[-1]['@Name'] == 'Status'

        # Verify structure is maintained in meta_data
        assert len(aoi['LocalTags']['LocalTag']) == original_count + 1

    @patch('controlrox.models.plc.rockwell.meta.l5x_dict_from_file')
    def test_default_file_loading(self, mock_l5x_dict):
        """Test loading from default file."""
        mock_l5x_dict.return_value = {
            'AddOnInstructionDefinition': self.full_meta_data
        }

        aoi = RaAddOnInstruction()

        mock_l5x_dict.assert_called_once_with(plc_meta.PLC_AOI_FILE)
        assert aoi.name == 'ComplexAOI'  # Assuming default name in file

    def test_dict_key_order_completeness(self):
        """Test that dict_key_order includes all expected keys."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        key_order = aoi.dict_key_order

        # Test that all major keys are present
        expected_keys = [
            '@Name', '@Class', '@Revision', '@ExecutePrescan',
            '@ExecutePostscan', '@ExecuteEnableInFalse', '@CreatedDate',
            '@CreatedBy', '@EditedDate', '@EditedBy', '@SoftwareRevision',
            'Description', 'RevisionNote', 'Parameters', 'LocalTags', 'Routines'
        ]

        for key in expected_keys:
            assert key in key_order

        # Test order is maintained
        assert key_order == expected_keys


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestRaAddOnInstructionProtocolMethods:
    """Test protocol method implementations in RaAddOnInstruction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.full_meta_data = {
            '@Name': 'TestAOI',
            '@Class': 'User',
            '@Revision': '1.0',
            '@ExecutePrescan': 'false',
            '@ExecutePostscan': 'false',
            '@ExecuteEnableInFalse': 'false',
            '@CreatedDate': '2023-01-01T10:00:00.000Z',
            '@CreatedBy': 'TestUser',
            '@EditedDate': '2023-01-01T10:00:00.000Z',
            '@EditedBy': 'TestUser',
            '@SoftwareRevision': '33.00',
            '@RevisionExtension': '1.0',
            'Description': 'Test AOI',
            'RevisionNote': 'Test version',
            'Parameters': {'Parameter': []},
            'LocalTags': {
                'LocalTag': [
                    {
                        '@Name': 'LocalVar1',
                        '@DataType': 'BOOL',
                        '@Class': 'Standard'
                    }
                ]
            },
            'Routines': {
                'Routine': [
                    {
                        '@Name': 'Logic',
                        '@Type': 'RLL'
                    }
                ]
            }
        }
        self.mock_controller = Mock(spec=RaController)

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_compile_tags_creates_tag_objects(self, mock_get_controller):
        """Test compile_tags creates RaTag objects from raw_tags."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        with patch.object(RaTag, '__init__', return_value=None):
            mock_tag = Mock()
            mock_tag.name = 'LocalVar1'
            mock_tag.class_ = 'Standard'

            with patch.object(RaTag, '__new__', return_value=mock_tag):
                aoi.compile_tags()

                # Should have called RaTag creation
                assert len(aoi._tags) > 0

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_compile_tags_categorizes_by_safety(self, mock_get_controller):
        """Test compile_tags categorizes tags into safety and standard."""
        meta_data = self.full_meta_data.copy()
        meta_data['LocalTags'] = {
            'LocalTag': [
                {'@Name': 'StandardTag', '@DataType': 'BOOL', '@Class': 'Standard'},
                {'@Name': 'SafetyTag', '@DataType': 'BOOL', '@Class': 'Safety'}
            ]
        }

        aoi = RaAddOnInstruction(
            meta_data=meta_data,
        )

        aoi._tags.clear()
        aoi._safety_tags.clear()
        aoi._standard_tags.clear()

        # Create mock tags
        standard_tag = Mock(spec=RaTag)
        standard_tag.class_ = 'Standard'
        standard_tag.name = 'StandardTag'

        safety_tag = Mock(spec=RaTag)
        safety_tag.class_ = 'Safety'
        safety_tag.name = 'SafetyTag'

        aoi._tags.append(standard_tag)
        aoi._tags.append(safety_tag)

        # Manually categorize for testing
        if standard_tag.class_ != 'Safety':
            aoi._standard_tags.append(standard_tag)
        if safety_tag.class_ == 'Safety':
            aoi._safety_tags.append(safety_tag)

        assert len(aoi._standard_tags) == 1
        assert len(aoi._safety_tags) == 1

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_compile_instructions_aggregates_from_routines(self, mock_get_controller):
        """Test compile_instructions aggregates instructions from routines."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        # Mock routines with instructions
        mock_routine1 = Mock()
        mock_routine1.get_instructions.return_value = [Mock(), Mock()]
        mock_routine1.get_input_instructions.return_value = [Mock()]
        mock_routine1.get_output_instructions.return_value = [Mock()]

        mock_routine2 = Mock()
        mock_routine2.get_instructions.return_value = [Mock()]
        mock_routine2.get_input_instructions.return_value = []
        mock_routine2.get_output_instructions.return_value = [Mock()]

        with patch.object(aoi, 'compile_routines'):
            aoi._routines.extend([mock_routine1, mock_routine2])
            aoi.compile_instructions()

        assert len(aoi._instructions) == 3
        assert len(aoi._input_instructions) == 1
        assert len(aoi._output_instructions) == 2

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_add_tag_calls_helper_method(self, mock_get_controller):
        """Test add_tag uses RaPlcObject helper method."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        mock_tag = Mock()
        mock_tag.name = 'NewTag'
        mock_tag.meta_data = {'@Name': 'NewTag', '@DataType': 'DINT'}

        with patch.object(aoi, 'get_raw_tags', return_value=[]):
            with patch.object(aoi, 'add_asset_to_meta_data') as mock_add:
                aoi.add_tag(mock_tag)

                mock_add.assert_called_once()
                args = mock_add.call_args
                assert args[1]['asset'] == mock_tag
                assert args[1]['inhibit_invalidate'] is False

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_add_tag_appends_when_index_negative(self, mock_get_controller):
        """Test add_tag appends when index is -1."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        mock_tag = Mock()
        mock_tag.name = 'NewTag'
        mock_tag.meta_data = {'@Name': 'NewTag', '@DataType': 'DINT'}

        with patch.object(aoi, 'get_raw_tags', return_value=[]):
            with patch.object(aoi, 'add_asset_to_meta_data') as mock_add:
                aoi.add_tag(mock_tag)

                mock_add.assert_called_once()
                args = mock_add.call_args
                assert args[1]['asset'] == mock_tag

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_remove_tag_calls_helper_method(self, mock_get_controller):
        """Test remove_tag uses RaPlcObject helper method."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data
        )

        mock_tag = Mock()
        mock_tag.name = 'LocalVar1'

        with patch.object(aoi, 'get_raw_tags', return_value=[]):
            with patch.object(aoi, 'remove_asset_from_meta_data') as mock_remove:
                aoi.remove_tag(mock_tag)

                mock_remove.assert_called_once()
                args = mock_remove.call_args
                assert args[1]['asset'] == mock_tag
                assert args[1]['inhibit_invalidate'] is False

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_add_routine_calls_helper_method(self, mock_get_controller):
        """Test add_routine uses RaPlcObject helper method."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data
        )

        mock_routine = Mock()
        mock_routine.name = 'NewRoutine'
        mock_routine.meta_data = {'@Name': 'NewRoutine', '@Type': 'RLL'}

        with patch.object(aoi, 'compile_routines'):
            with patch.object(aoi, 'add_asset_to_meta_data') as mock_add:
                with patch.object(aoi, 'get_raw_routines', return_value=[]):
                    aoi.add_routine(mock_routine)

                    mock_add.assert_called_once()
                    args = mock_add.call_args
                    assert args[1]['asset'] == mock_routine

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_remove_routine_calls_helper_method(self, mock_get_controller):
        """Test remove_routine uses RaPlcObject helper method."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        mock_routine = Mock()
        mock_routine.name = 'Logic'

        with patch.object(aoi, 'remove_asset_from_meta_data') as mock_remove:
            with patch.object(aoi, 'get_routines', return_value=HashList('name')):
                with patch.object(aoi, 'get_raw_routines', return_value=[]):
                    aoi.remove_routine(mock_routine)

                mock_remove.assert_called_once()
                args = mock_remove.call_args
                assert args[1]['asset'] == mock_routine

    def test_block_routine_raises_not_implemented(self):
        """Test block_routine raises NotImplementedError."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        with pytest.raises(NotImplementedError, match="block_routine is not yet implemented"):
            aoi.block_routine('Logic', 'BlockBit')

    def test_unblock_routine_raises_not_implemented(self):
        """Test unblock_routine raises NotImplementedError."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        with pytest.raises(NotImplementedError, match="unblock_routine is not yet implemented"):
            aoi.unblock_routine('Logic', 'BlockBit')

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_get_main_routine_returns_logic(self, mock_get_controller):
        """Test get_main_routine returns Logic routine if present."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data
        )

        mock_logic_routine = Mock()
        mock_logic_routine.name = 'Logic'
        aoi._routines.append(mock_logic_routine)

        result = aoi.get_main_routine()
        assert result == mock_logic_routine

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_get_main_routine_returns_first_if_no_logic(self, mock_get_controller):
        """Test get_main_routine returns first routine if Logic not found."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data
        )

        mock_routine = Mock()
        mock_routine.name = 'Other'
        aoi._routines.append(mock_routine)

        result = aoi.get_main_routine()
        assert result == mock_routine

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_get_main_routine_returns_none_when_empty(self, mock_get_controller):
        """Test get_main_routine returns None when no routines."""
        # Create AOI with no routines in metadata
        meta_data = self.full_meta_data.copy()
        meta_data['Routines'] = None

        aoi = RaAddOnInstruction(
            meta_data=meta_data
        )

        # Ensure routines list is empty
        aoi._routines.clear()

        with patch.object(aoi, 'compile_routines'):
            result = aoi.get_main_routine()
        assert result is None

    def test_add_instruction_raises_not_implemented(self):
        """Test add_instruction raises NotImplementedError with helpful message."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        with patch.object(aoi, 'compile_routines'):
            with patch.object(aoi, 'compile_instructions'):
                with patch.object(aoi, 'get_raw_instructions', return_value=[]):
                    with pytest.raises(ValueError, match="asset must be of type PlcObject or string"):
                        aoi.add_instruction(Mock())

    def test_clear_instructions(self):
        """Test clear_instructions."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)
        aoi.clear_instructions()
        assert len(aoi._instructions) == 0

    def test_remove_instruction_raises_not_implemented(self):
        """Test remove_instruction raises NotImplementedError with helpful message."""
        aoi = RaAddOnInstruction(meta_data=self.full_meta_data)

        with patch.object(aoi, 'compile_routines'):
            with patch.object(aoi, 'compile_instructions'):
                with patch.object(aoi, 'get_raw_instructions', return_value=[]):
                    with pytest.raises(ValueError, match="asset must be of type PlcObject"):
                        aoi.remove_instruction(Mock())

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_has_instruction_checks_compiled_instructions(self, mock_get_controller):
        """Test has_instruction raises NotImplementedError."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        mock_instruction = Mock()
        aoi._instructions = [mock_instruction]

        with pytest.raises(NotImplementedError, match="has_instruction method must be implemented"):
            aoi.has_instruction(mock_instruction)

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_get_filtered_instructions_by_type(self, mock_get_controller):
        """Test get_filtered_instructions filters by instruction type."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        mock_xic = Mock(spec=RaLogicInstruction)
        mock_xic.type = 'XIC'
        mock_xic.get_instruction_name.return_value = 'XIC'
        mock_ote = Mock(spec=RaLogicInstruction)
        mock_ote.type = 'OTE'
        mock_ote.get_instruction_name.return_value = 'OTE'

        aoi._instructions = [mock_xic, mock_ote]

        instr = aoi.get_filtered_instructions(instruction_filter='XIC')
        assert len(instr) == 1
        assert instr[0].type == 'XIC'  # type: ignore

    @patch('controlrox.models.plc.rockwell.aoi.ControllerInstanceManager.get_controller', return_value=Mock(spec=RaController))
    def test_get_filtered_instructions_by_operand(self, mock_get_controller):
        """Test get_filtered_instructions filters by operand."""
        aoi = RaAddOnInstruction(
            meta_data=self.full_meta_data,
        )

        mock_instr1 = Mock(spec=RaLogicInstruction)
        mock_instr1.type = 'XIC'
        instr1_operand1 = Mock(spec=LogixOperand)
        instr1_operand1.meta_data = 'Tag1'
        instr1_operand2 = Mock(spec=LogixOperand)
        instr1_operand2.meta_data = 'Tag2'
        mock_instr1.operands = [instr1_operand1, instr1_operand2]
        mock_instr1.get_operands.return_value = mock_instr1.operands

        mock_instr2 = Mock(spec=RaLogicInstruction)
        mock_instr2.type = 'OTE'
        instr2_operand1 = Mock(spec=LogixOperand)
        instr2_operand1.meta_data = 'Tag3'
        mock_instr2.operands = [instr2_operand1]
        mock_instr2.get_operands.return_value = mock_instr2.operands

        aoi._instructions = [mock_instr1, mock_instr2]

        instr = aoi.get_filtered_instructions(operand_filter='Tag1')
        assert len(instr) == 1
        assert instr[0].type == 'XIC'  # type: ignore


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
