"""Unit tests for controlrox.models.plc.rockwell.rung module."""

import unittest
from unittest.mock import Mock

from controlrox.models.plc.rockwell.rung import RaRung
from controlrox.models.plc.rockwell import RaController, RaRoutine


class TestRaRungInit(unittest.TestCase):
    """Test RaRung initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_controller.name = "TestController"

        self.mock_routine = Mock(spec=RaRoutine)
        self.mock_routine.name = "TestRoutine"

        self.basic_rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': 'Test rung comment'
        }

        self.empty_rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': '',
            'Comment': ''
        }

    def test_init_with_meta_data(self):
        """Test RaRung initialization with provided meta_data."""
        rung = RaRung(
            meta_data=self.basic_rung_meta,

            routine=self.mock_routine
        )

        self.assertEqual(rung['@Number'], '0')
        self.assertEqual(rung.routine, self.mock_routine)

    def test_init_without_meta_data(self):
        """Test RaRung initialization without meta_data loads from file."""
        rung = RaRung()
        self.assertEqual(rung['@Number'], 0)

    def test_init_with_parameters(self):
        """Test RaRung initialization with direct parameters."""
        rung = RaRung(
            meta_data=self.basic_rung_meta,
            routine=self.mock_routine,
            rung_number=5,
            rung_text="XIC(Test)OTE(Output);",
            comment="Custom comment"
        )

        self.assertEqual(rung.number, 5)
        self.assertEqual(rung.text, "XIC(Test)OTE(Output);")
        self.assertEqual(rung.comment, "Custom comment")

    def test_init_sets_private_attributes(self):
        """Test that initialization properly sets private attributes."""
        rung = RaRung(
            meta_data=self.basic_rung_meta,

        )

        self.assertIsInstance(rung._instructions, list)
        self.assertIsInstance(rung._sequence, list)
        self.assertIsInstance(rung._branches, dict)

    def test_init_with_empty_text(self):
        """Test initialization with empty text."""
        rung = RaRung(
            meta_data=self.empty_rung_meta,

        )

        self.assertEqual(rung.text, '')
        self.assertEqual(len(rung._instructions), 0)


class TestRaRungEquality(unittest.TestCase):
    """Test RaRung equality methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': 'Test comment'
        }

    def test_equality_same_text(self):
        """Test equality when rungs have same text."""
        rung1 = RaRung(meta_data=self.rung_meta, )
        rung2 = RaRung(meta_data=self.rung_meta.copy(), )

        self.assertEqual(rung1, rung2)

    def test_equality_different_text(self):
        """Test inequality when rungs have different text."""
        rung1 = RaRung(meta_data=self.rung_meta, )

        different_meta = self.rung_meta.copy()
        different_meta['Text'] = 'XIO(Input2)OTL(Output2);'
        rung2 = RaRung(meta_data=different_meta, )

        self.assertNotEqual(rung1, rung2)

    def test_equality_different_type(self):
        """Test inequality when comparing with different type."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertNotEqual(rung, "not a rung")
        self.assertNotEqual(rung, 123)
        self.assertNotEqual(rung, None)


class TestRaRungProperties(unittest.TestCase):
    """Test RaRung properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_routine = Mock(spec=RaRoutine)

        self.rung_meta = {
            '@Number': '5',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': 'Test rung comment'
        }

    def test_dict_key_order(self):
        """Test dict_key_order property."""
        rung = RaRung(meta_data=self.rung_meta, )

        expected_order = ['@Number', '@Type', 'Comment', 'Text']
        self.assertEqual(rung.dict_key_order, expected_order)

    def test_comment_property(self):
        """Test comment property getter and setter."""
        rung = RaRung(meta_data=self.rung_meta)

        self.assertEqual(rung.comment, 'Test rung comment')

        rung.set_comment('New comment')
        self.assertEqual(rung.comment, 'New comment')
        self.assertEqual(rung['Comment'], 'New comment')

    def test_number_property(self):
        """Test number property getter and setter."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.number, 5)

        rung.set_number(10)
        self.assertEqual(rung.number, 10)

        rung.set_number(15)
        self.assertEqual(rung.number, 15)

    def test_text_property(self):
        """Test text property getter and setter."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.text, 'XIC(Input1)OTE(Output1);')

        rung.set_text('XIO(Input2)OTL(Output2);')
        self.assertEqual(rung.text, 'XIO(Input2)OTL(Output2);')

    def test_text_property_empty(self):
        """Test text property with empty text."""
        meta = self.rung_meta.copy()
        meta['Text'] = ''
        rung = RaRung(meta_data=meta, )

        self.assertEqual(rung.text, '')

    def test_routine_property(self):
        """Test routine property getter."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertIsNone(rung.routine)

        rung_with_routine = RaRung(meta_data=self.rung_meta,  routine=self.mock_routine)
        self.assertEqual(rung_with_routine.routine, self.mock_routine)

    def test_container_property(self):
        """Test type property."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.type, 'N')


if __name__ == '__main__':
    unittest.main()
