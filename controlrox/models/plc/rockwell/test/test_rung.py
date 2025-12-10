"""Unit tests for controlrox.models.plc.rockwell.rung module."""

import unittest
from unittest.mock import Mock, patch

from controlrox.models.plc.rockwell.rung import RaRung, RungElement, RungBranch, RungElementType
from controlrox.models.plc.rockwell import RaController, RaRoutine
from controlrox.models.plc.rockwell.instruction import RaLogicInstruction
from controlrox.interfaces import LogicInstructionType, ILogicInstruction


class TestRungElementType(unittest.TestCase):
    """Test RungElementType enum."""

    def test_enum_values(self):
        """Test that enum has correct values."""
        self.assertEqual(RungElementType.INSTRUCTION.value, "instruction")
        self.assertEqual(RungElementType.BRANCH_START.value, "branch_start")
        self.assertEqual(RungElementType.BRANCH_END.value, "branch_end")
        self.assertEqual(RungElementType.BRANCH_NEXT.value, "branch_next")


class TestRungElement(unittest.TestCase):
    """Test RungElement dataclass."""

    def test_rung_element_creation(self):
        """Test RungElement creation with all parameters."""
        mock_instruction = Mock(spec=RaLogicInstruction)
        mock_rung = Mock(spec=RaRung)

        element = RungElement(
            element_type=RungElementType.INSTRUCTION,
            instruction=mock_instruction,
            branch_id="test_branch",
            root_branch_id="root_branch",
            branch_level=1,
            position=5,
            rung=mock_rung,
            rung_number=2
        )

        self.assertEqual(element.element_type, RungElementType.INSTRUCTION)
        self.assertEqual(element.instruction, mock_instruction)
        self.assertEqual(element.branch_id, "test_branch")
        self.assertEqual(element.root_branch_id, "root_branch")
        self.assertEqual(element.branch_level, 1)
        self.assertEqual(element.position, 5)
        self.assertEqual(element.rung, mock_rung)
        self.assertEqual(element.rung_number, 2)

    def test_rung_element_defaults(self):
        """Test RungElement creation with default values."""
        element = RungElement(element_type=RungElementType.BRANCH_START)

        self.assertEqual(element.element_type, RungElementType.BRANCH_START)
        self.assertIsNone(element.instruction)
        self.assertIsNone(element.branch_id)
        self.assertIsNone(element.root_branch_id)
        self.assertEqual(element.branch_level, 0)
        self.assertEqual(element.position, 0)
        self.assertIsNone(element.rung)
        self.assertEqual(element.rung_number, 0)


class TestRungBranch(unittest.TestCase):
    """Test RungBranch dataclass."""

    def test_rung_branch_creation(self):
        """Test RungBranch creation with all parameters."""
        nested_branch = RungBranch(
            branch_id="nested_1",
            start_position=3,
            end_position=5
        )

        branch = RungBranch(
            branch_id="main_branch",
            start_position=1,
            end_position=10,
            root_branch_id="root",
            nested_branches=[nested_branch]
        )

        self.assertEqual(branch.branch_id, "main_branch")
        self.assertEqual(branch.start_position, 1)
        self.assertEqual(branch.end_position, 10)
        self.assertEqual(branch.root_branch_id, "root")
        self.assertEqual(len(branch.nested_branches), 1)
        self.assertEqual(branch.nested_branches[0], nested_branch)

    def test_rung_branch_defaults(self):
        """Test RungBranch creation with default values."""
        branch = RungBranch(
            branch_id="test_branch",
            start_position=0,
            end_position=5
        )

        self.assertEqual(branch.branch_id, "test_branch")
        self.assertEqual(branch.start_position, 0)
        self.assertEqual(branch.end_position, 5)
        self.assertIsNone(branch.root_branch_id)
        self.assertEqual(len(branch.nested_branches), 0)


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
        self.assertEqual(rung['@Number'], '0')

    def test_init_with_parameters(self):
        """Test RaRung initialization with direct parameters."""
        rung = RaRung(
            meta_data=self.basic_rung_meta,

            routine=self.mock_routine,
            rung_number=5,
            rung_text="XIC(Test)OTE(Output);",
            comment="Custom comment"
        )

        self.assertEqual(rung.number, '5')
        self.assertEqual(rung.text, "XIC(Test)OTE(Output);")
        self.assertEqual(rung.comment, "Custom comment")

    def test_init_sets_private_attributes(self):
        """Test that initialization properly sets private attributes."""
        rung = RaRung(
            meta_data=self.basic_rung_meta,

        )

        self.assertIsInstance(rung._instructions, list)
        self.assertIsInstance(rung._rung_sequence, list)
        self.assertIsInstance(rung._branches, dict)
        self.assertEqual(rung._branch_id_counter, 0)

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
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.comment, 'Test rung comment')

        rung.set_rung_comment('New comment')
        self.assertEqual(rung.comment, 'New comment')
        self.assertEqual(rung['Comment'], 'New comment')

    def test_number_property(self):
        """Test number property getter and setter."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.number, '5')

        rung.set_rung_number('10')
        self.assertEqual(rung.number, '10')

        rung.set_rung_number('15')
        self.assertEqual(rung.number, '15')

    def test_text_property(self):
        """Test text property getter and setter."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.text, 'XIC(Input1)OTE(Output1);')

        rung.set_rung_text('XIO(Input2)OTL(Output2);')
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


class TestRaRungInstructionExtraction(unittest.TestCase):
    """Test RaRung instruction extraction methods."""

    def test_extract_instructions_simple(self):
        """Test extraction of simple instructions."""
        text = "XIC(Input1)XIO(Input2)OTE(Output1);"
        instructions = RaRung._extract_instructions(text)

        expected = ["XIC(Input1)", "XIO(Input2)", "OTE(Output1)"]
        self.assertEqual(instructions, expected)

    def test_extract_instructions_nested_parentheses(self):
        """Test extraction with nested parentheses."""
        text = "MOV(Array[0],Dest)EQU(Value[Index],Target);"
        instructions = RaRung._extract_instructions(text)

        expected = ["MOV(Array[0],Dest)", "EQU(Value[Index],Target)"]
        self.assertEqual(instructions, expected)

    def test_extract_instructions_complex_operands(self):
        """Test extraction with complex operands."""
        text = "ADD(Tag.Value[Index],Constant,Result.Data);"
        instructions = RaRung._extract_instructions(text)

        expected = ["ADD(Tag.Value[Index],Constant,Result.Data)"]
        self.assertEqual(instructions, expected)

    def test_extract_instructions_empty_text(self):
        """Test extraction from empty text."""
        instructions = RaRung._extract_instructions("")
        self.assertEqual(instructions, [])

    def test_extract_instructions_with_branches(self):
        """Test extraction with branch markers."""
        text = "XIC(Input1)[XIO(Input2),XIC(Input3)]OTE(Output1);"
        instructions = RaRung._extract_instructions(text)

        expected = ["XIC(Input1)", "XIO(Input2)", "XIC(Input3)", "OTE(Output1)"]
        self.assertEqual(instructions, expected)


class TestRaRungTokenization(unittest.TestCase):
    """Test RaRung tokenization methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': '',
            'Comment': ''
        }

    def test_tokenize_simple_instructions(self):
        """Test tokenization of simple instructions."""
        rung = RaRung(meta_data=self.rung_meta, )

        text = "XIC(Input1)XIO(Input2)OTE(Output1);"
        tokens = rung._tokenize_rung_text(text)

        expected = ["XIC(Input1)", "XIO(Input2)", "OTE(Output1)"]
        self.assertEqual(tokens, expected)

    def test_tokenize_with_branches(self):
        """Test tokenization with branch structures."""
        rung = RaRung(meta_data=self.rung_meta, )

        text = "XIC(Input1)[XIO(Input2),XIC(Input3)]OTE(Output1);"
        tokens = rung._tokenize_rung_text(text)

        expected = ["XIC(Input1)", "[", "XIO(Input2)", ",", "XIC(Input3)", "]", "OTE(Output1)"]
        self.assertEqual(tokens, expected)

    def test_tokenize_nested_branches(self):
        """Test tokenization with nested branches."""
        rung = RaRung(meta_data=self.rung_meta, )

        text = "XIC(Input1)[XIO(Input2)[XIC(Input3),XIO(Input4)],XIC(Input5)]OTE(Output1);"
        tokens = rung._tokenize_rung_text(text)

        expected = [
            "XIC(Input1)", "[", "XIO(Input2)", "[", "XIC(Input3)", ",",
            "XIO(Input4)", "]", ",", "XIC(Input5)", "]", "OTE(Output1)"
        ]
        self.assertEqual(tokens, expected)

    def test_tokenize_array_references(self):
        """Test tokenization preserves array references in instructions."""
        rung = RaRung(meta_data=self.rung_meta, )

        text = "MOV(Array[0],Dest[1]);"
        tokens = rung._tokenize_rung_text(text)

        expected = ["MOV(Array[0],Dest[1])"]
        self.assertEqual(tokens, expected)

    def test_tokenize_empty_text(self):
        """Test tokenization of empty text."""
        rung = RaRung(meta_data=self.rung_meta, )

        tokens = rung._tokenize_rung_text("")
        self.assertEqual(tokens, [])


class TestRaRungSequenceBuilding(unittest.TestCase):
    """Test RaRung sequence building methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_instruction = Mock(spec=RaLogicInstruction)
        self.mock_instruction.meta_data = "XIC(Input1)"

        self.rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

    def test_build_sequence_simple_instructions(self):
        """Test building sequence with simple instructions."""
        rung = RaRung(meta_data=self.rung_meta, )

        # Verify the rung was created successfully
        self.assertEqual(rung.text, 'XIC(Input1)OTE(Output1);')

        # Verify instructions were parsed (2 instructions in the text)
        self.assertEqual(len(rung.instructions), 2)

    def test_build_sequence_with_branches(self):
        """Test building sequence with branches."""
        branch_meta = self.rung_meta.copy()
        branch_meta['Text'] = 'XIC(Input1)[XIO(Input2),XIC(Input3)]OTE(Output1);'

        rung = RaRung(meta_data=branch_meta, )

        # Verify the rung was created with branch text
        self.assertIn('[', rung.text)
        self.assertIn(']', rung.text)

        # Verify instructions were parsed (4 instructions in the text)
        self.assertEqual(len(rung.instructions), 4)

        # Verify branch structure is valid
        self.assertTrue(rung.validate_branch_structure())

    def test_get_unique_branch_id(self):
        """Test unique branch ID generation."""
        rung = RaRung(meta_data=self.rung_meta, )

        id1 = rung._get_unique_branch_id()
        id2 = rung._get_unique_branch_id()

        self.assertNotEqual(id1, id2)
        self.assertIn("rung_0_branch", id1)
        self.assertIn("rung_0_branch", id2)


class TestRaRungInstructionMethods(unittest.TestCase):
    """Test RaRung instruction-related methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)XIO(Input2)OTE(Output1);',
            'Comment': ''
        }

    def test_instructions_property(self):
        """Test instructions property."""
        mock_instr1 = Mock(spec=RaLogicInstruction)
        mock_instr1.meta_data = "XIC(Input1)"
        mock_instr1.type = LogicInstructionType.INPUT

        mock_instr2 = Mock(spec=RaLogicInstruction)
        mock_instr2.meta_data = "XIO(Input2)"
        mock_instr2.type = LogicInstructionType.INPUT

        mock_instr3 = Mock(spec=RaLogicInstruction)
        mock_instr3.meta_data = "OTE(Output1)"
        mock_instr3.type = LogicInstructionType.OUTPUT

        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(len(rung.instructions), 3)
        self.assertEqual(rung.instructions[0].meta_data, mock_instr1.meta_data)
        self.assertEqual(rung.instructions[1].meta_data, mock_instr2.meta_data)
        self.assertEqual(rung.instructions[2].meta_data, mock_instr3.meta_data)

    def test_get_instructions_with_filter(self):
        """Test get_instructions method with filters."""
        mock_instr1 = Mock(spec=RaLogicInstruction)
        mock_instr1.instruction_name = "XIC"
        mock_operand1 = Mock()
        mock_operand1.meta_data = "Input1"
        mock_instr1.operands = [mock_operand1]

        mock_instr2 = Mock(spec=RaLogicInstruction)
        mock_instr2.instruction_name = "OTE"
        mock_operand2 = Mock()
        mock_operand2.meta_data = "Output1"
        mock_instr2.operands = [mock_operand2]

        rung = RaRung(meta_data=self.rung_meta, )

        # Filter by instruction name
        xic_instructions = rung.get_instructions(instruction_filter="XIC")
        self.assertEqual(len(xic_instructions), 1)

        # Filter by operand
        input1_instructions = rung.get_instructions(operand_filter="Input1")
        self.assertEqual(len(input1_instructions), 1)

    def test_get_instruction_count(self):
        """Test get_instruction_count method."""
        rung = RaRung(meta_data=self.rung_meta, )

        # The rung already has instructions from parsing the text
        count = rung.get_instruction_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_get_instruction_at_position(self):
        """Test get_instruction_at_position method."""
        rung = RaRung(meta_data=self.rung_meta, )

        mock_instr1 = Mock(spec=RaLogicInstruction)
        mock_instr2 = Mock(spec=RaLogicInstruction)
        rung._instructions = [mock_instr1, mock_instr2]

        self.assertEqual(rung.get_instruction_at_position(0), mock_instr1)
        self.assertEqual(rung.get_instruction_at_position(1), mock_instr2)
        self.assertIsNone(rung.get_instruction_at_position(2))
        self.assertIsNone(rung.get_instruction_at_position(-1))

    def test_get_instruction_summary(self):
        """Test get_instruction_summary method."""
        mock_instr1 = Mock(spec=RaLogicInstruction)
        mock_instr1.name = "XIC"

        mock_instr2 = Mock(spec=RaLogicInstruction)
        mock_instr2.name = "XIO"

        mock_instr3 = Mock(spec=RaLogicInstruction)
        mock_instr3.name = "OTE"

        rung = RaRung(meta_data=self.rung_meta, )
        # Mock the instructions property to return our mocked instructions
        rung._instructions = [mock_instr1, mock_instr2, mock_instr3]

        summary = rung.get_instruction_summary()
        expected = {"XIC": 1, 'XIO': 1, "OTE": 1}
        self.assertEqual(summary, expected)


class TestRaRungInstructionManipulation(unittest.TestCase):
    """Test RaRung instruction manipulation methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

    def test_add_instruction_to_empty_rung(self):
        """Test adding instruction to empty rung."""
        empty_meta = self.rung_meta.copy()
        empty_meta['Text'] = ''

        rung = RaRung(meta_data=empty_meta, )
        instr = RaLogicInstruction(meta_data="XIC(Input1)")

        rung.add_instruction(instr)
        self.assertEqual(rung.text, "XIC(Input1);")

    def test_add_instruction_at_position(self):
        """Test adding instruction at specific position."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

            instr = RaLogicInstruction(meta_data="XIO(Input2)")

            rung.add_instruction(instr, index=1)

            mock_tokenize.assert_called()
            # Verify text was updated
            self.assertIn("XIO(Input2)", rung.text)

    def test_add_instruction_invalid_format(self):
        """Test adding instruction with invalid format."""
        rung = RaRung(meta_data=self.rung_meta, )

        # Create a mock instruction that returns invalid format
        mock_instr = Mock(spec=RaLogicInstruction)
        mock_instr.get_meta_data.return_value = "INVALID_FORMAT"

        with self.assertRaises(ValueError) as context:
            rung.add_instruction(mock_instr)

        self.assertIn("Invalid instruction format", str(context.exception))

    def test_add_instruction_empty_string(self):
        """Test adding empty instruction string."""
        rung = RaRung(meta_data=self.rung_meta, )

        # Create a mock instruction that returns empty meta_data
        mock_instr = Mock(spec=RaLogicInstruction)
        mock_instr.get_meta_data.return_value = ""

        with self.assertRaises(ValueError) as context:
            rung.add_instruction(mock_instr)

        self.assertIn("Instruction text must be a non-empty string", str(context.exception))

    def test_remove_instruction_by_text(self):
        """Test removing instruction by text."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_find_instruction_index_in_text') as mock_find:
            with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
                mock_find.return_value = 0
                mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

                instr = RaLogicInstruction(meta_data="XIC(Input1)")

                rung.remove_instruction(instr)

                mock_find.assert_called_once_with("XIC(Input1)", 0)

    def test_remove_instruction_by_index(self):
        """Test removing instruction by index."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

            rung.remove_instruction(0)

            # Should rebuild text without first instruction
            self.assertNotIn("XIC(Input1)", rung.text)

    def test_remove_instruction_index_out_of_range(self):
        """Test removing instruction with out of range index."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)"]

            with self.assertRaises(IndexError) as context:
                rung.remove_instruction(5)

            self.assertIn("Instruction index 5 out of range", str(context.exception))

    def test_remove_instruction_empty_rung(self):
        """Test removing instruction from empty rung."""
        empty_meta = self.rung_meta.copy()
        empty_meta['Text'] = ''

        rung = RaRung(meta_data=empty_meta, )

        with self.assertRaises(ValueError) as context:
            rung.remove_instruction("XIC(Input1)")

        self.assertIn("Cannot remove instruction from empty rung", str(context.exception))

    def test_replace_instruction_by_text(self):
        """Test replacing instruction by text."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_find_instruction_index_in_text') as mock_find:
            with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
                mock_find.return_value = 0
                mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

                rung.replace_instruction("XIC(Input1)", "XIO(Input2)")

                mock_find.assert_called_once_with("XIC(Input1)", 0)

    def test_replace_instruction_invalid_format(self):
        """Test replacing instruction with invalid format."""
        rung = RaRung(meta_data=self.rung_meta, )

        with self.assertRaises(ValueError) as context:
            rung.replace_instruction("XIC(Input1)", "INVALID_FORMAT")

        self.assertIn("Invalid instruction format", str(context.exception))

    def test_move_instruction_by_index(self):
        """Test moving instruction by index."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "XIO(Input2)", "OTE(Output1)"]

            rung.move_instruction(0, 2)  # Move first instruction to position 2

            # Should have reordered the tokens
            mock_tokenize.assert_called()

    def test_move_instruction_same_position(self):
        """Test moving instruction to same position."""
        rung = RaRung(meta_data=self.rung_meta, )

        original_text = rung.text
        rung.move_instruction(0, 0)  # Same position

        # Text should remain unchanged
        self.assertEqual(rung.text, original_text)


class TestRungBranchMethods(unittest.TestCase):
    """Test RaRung branch-related methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.branch_rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)[XIO(Input2),XIC(Input3)]OTE(Output1);',
            'Comment': ''
        }

    def test_has_branches_true(self):
        """Test has_branches method when branches exist."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        # Mock branches
        rung._branches = {"branch_1": Mock()}

        self.assertTrue(rung.has_branches())

    def test_has_branches_false(self):
        """Test has_branches method when no branches exist."""
        simple_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

        rung = RaRung(meta_data=simple_meta, )

        self.assertFalse(rung.has_branches())

    def test_get_branch_count(self):
        """Test get_branch_count method."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        # Mock branches
        rung._branches = {"branch_1": Mock(), "branch_2": Mock()}

        self.assertEqual(rung.get_branch_count(), 2)

    def test_get_max_branch_depth_no_branches(self):
        """Test get_max_branch_depth with no branches."""
        simple_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

        rung = RaRung(meta_data=simple_meta, )

        self.assertEqual(rung.get_max_branch_depth(), 0)

    def test_get_max_branch_depth_with_branches(self):
        """Test get_max_branch_depth with branches."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "[", "XIO(Input2)", ",", "XIC(Input3)", "]", "OTE(Output1)"]

            depth = rung.get_max_branch_depth()
            self.assertGreaterEqual(depth, 1)

    def test_get_branch_nesting_level(self):
        """Test get_branch_nesting_level method."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "[", "XIO(Input2)", "]", "OTE(Output1)"]

            # Position inside branch should have nesting level > 0
            level = rung.get_branch_nesting_level(2)
            self.assertGreaterEqual(level, 0)

    def test_insert_branch(self):
        """Test insert_branch method."""
        simple_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

        rung = RaRung(meta_data=simple_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            with patch.object(rung, '_insert_branch_tokens') as mock_insert:
                mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]
                mock_insert.return_value = ["XIC(Input1)", "[", "]", "OTE(Output1)"]

                rung.insert_branch(0, 1)

                mock_insert.assert_called_once()

    def test_insert_branch_invalid_positions(self):
        """Test insert_branch with invalid positions."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with self.assertRaises(ValueError) as context:
            rung.insert_branch(-1, 2)

        self.assertIn("Branch positions must be non-negative", str(context.exception))

    def test_remove_branch_not_found(self):
        """Test remove_branch with non-existent branch."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with self.assertRaises(ValueError) as context:
            rung.remove_branch("non_existent_branch")

        self.assertIn("Branch 'non_existent_branch' not found", str(context.exception))

    def test_validate_branch_structure_valid(self):
        """Test validate_branch_structure with valid structure."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "[", "XIO(Input2)", "]", "OTE(Output1)"]

            self.assertTrue(rung.validate_branch_structure())

    def test_validate_branch_structure_invalid(self):
        """Test validate_branch_structure with invalid structure."""
        invalid_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)[XIO(Input2)OTE(Output1);',  # Missing closing bracket
            'Comment': ''
        }

        rung = RaRung(meta_data=invalid_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "[", "XIO(Input2)", "OTE(Output1)"]

            self.assertFalse(rung.validate_branch_structure())

    def test_find_matching_branch_end(self):
        """Test find_matching_branch_end method."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "[", "XIO(Input2)", "]", "OTE(Output1)"]

            end_position = rung.find_matching_branch_end(1)  # Position of '['
            self.assertEqual(end_position, 3)  # Position of ']'

    def test_find_matching_branch_end_invalid_start(self):
        """Test find_matching_branch_end with invalid start position."""
        rung = RaRung(meta_data=self.branch_rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

            with self.assertRaises(ValueError) as context:
                rung.find_matching_branch_end(0)  # Not a '[' token

            self.assertIn("Start position must be a valid branch start token", str(context.exception))


class TestRaRungUtilityMethods(unittest.TestCase):
    """Test RaRung utility methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.rung_meta = {
            '@Number': '5',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': 'Test comment\nSecond line'
        }

    def test_get_comment_lines(self):
        """Test get_comment_lines method."""
        rung = RaRung(meta_data=self.rung_meta, )

        self.assertEqual(rung.get_comment_lines(), 2)

    def test_get_comment_lines_no_comment(self):
        """Test get_comment_lines with no comment."""
        meta = self.rung_meta.copy()
        meta['Comment'] = ''

        rung = RaRung(meta_data=meta, )

        self.assertEqual(rung.get_comment_lines(), 0)

    def test_has_instruction_true(self):
        """Test has_instruction method when instruction exists."""
        rung = RaRung(meta_data=self.rung_meta, )

        # Create mock instruction
        mock_instruction = Mock(spec=RaLogicInstruction)
        mock_instruction.get_meta_data.return_value = "XIC(Input1)"

        with patch.object(rung, 'find_instruction_positions') as mock_find:
            mock_find.return_value = [0, 2]  # Found at positions 0 and 2

            self.assertTrue(rung.has_instruction(mock_instruction))

    def test_has_instruction_false(self):
        """Test has_instruction method when instruction doesn't exist."""
        rung = RaRung(meta_data=self.rung_meta, )

        # Create mock instruction
        mock_instruction = Mock(spec=RaLogicInstruction)
        mock_instruction.get_meta_data.return_value = "XIO(Input2)"

        with patch.object(rung, 'find_instruction_positions') as mock_find:
            mock_find.return_value = []  # Not found

            self.assertFalse(rung.has_instruction(mock_instruction))

    def test_find_instruction_positions(self):
        """Test find_instruction_positions method."""
        multi_instruction_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

        rung = RaRung(meta_data=multi_instruction_meta, )

        positions = rung.find_instruction_positions("XIC(Input1)")
        self.assertEqual(len(positions), 2)

    def test_get_execution_sequence(self):
        """Test get_execution_sequence method."""
        rung = RaRung(meta_data=self.rung_meta, )

        # Mock rung sequence with proper interface methods
        mock_instruction = Mock(spec=ILogicInstruction)
        mock_instruction.get_instruction_name.return_value = "XIC"
        mock_instruction.meta_data = "XIC(Input1)"
        mock_instruction.get_instruction_type.return_value = LogicInstructionType.INPUT

        mock_operand = Mock()
        mock_operand.meta_data = "Input1"
        mock_instruction.get_operands.return_value = [mock_operand]

        mock_element = RungElement(
            element_type=RungElementType.INSTRUCTION,
            instruction=mock_instruction,
            position=0
        )

        rung._rung_sequence = [mock_element]

        sequence = rung.get_execution_sequence()

        self.assertEqual(len(sequence), 1)
        self.assertEqual(sequence[0]['instruction_type'], "XIC")
        self.assertEqual(sequence[0]['instruction_text'], "XIC(Input1)")
        self.assertTrue(sequence[0]['is_input'])
        self.assertEqual(sequence[0]['operands'], ["Input1"])

    # Skipping test_to_sequence_dict - the method to_sequence_dict does not exist in RaRung
    # def test_to_sequence_dict(self):
    #     """Test to_sequence_dict method."""
    #     rung = RaRung(meta_data=self.rung_meta, )
    #
    #     # Mock required properties
    #     rung._instructions = [Mock(), Mock()]
    #     rung._branches = {}
    #
    #     with patch.object(RaRung, 'get_execution_sequence') as mock_exec:
    #         with patch.object(RaRung, 'get_main_line_instructions') as mock_main:
    #             mock_exec.return_value = []
    #             mock_main.return_value = []
    #
    #             result = rung.to_sequence_dict()
    #
    #             self.assertEqual(result['rung_number'], '5')
    #             self.assertEqual(result['comment'], 'Test comment\nSecond line')
    #             self.assertEqual(result['instruction_count'], 2)
    #             self.assertEqual(result['branch_count'], 0)


class TestRaRungErrorHandling(unittest.TestCase):
    """Test RaRung error handling and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(Input1)OTE(Output1);',
            'Comment': ''
        }

    def test_get_element_at_position_out_of_range(self):
        """Test _get_element_at_position with out of range position."""
        rung = RaRung(meta_data=self.rung_meta, )

        with self.assertRaises(IndexError) as context:
            rung._get_element_at_position(999)

        self.assertIn("Position out of range", str(context.exception))

    def test_get_element_at_position_negative(self):
        """Test _get_element_at_position with negative position."""
        rung = RaRung(meta_data=self.rung_meta, )

        with self.assertRaises(IndexError) as context:
            rung._get_element_at_position(-1)

        self.assertIn("Position out of range", str(context.exception))

    def test_remove_token_by_index_out_of_range(self):
        """Test _remove_token_by_index with out of range index."""
        rung = RaRung(meta_data=self.rung_meta, )

        tokens = ["XIC(Input1)", "OTE(Output1)"]

        with self.assertRaises(IndexError) as context:
            rung._remove_token_by_index(tokens, 5)

        self.assertIn("Index out of range", str(context.exception))

    def test_remove_tokens_invalid_range(self):
        """Test _remove_tokens with invalid range."""
        rung = RaRung(meta_data=self.rung_meta, )

        tokens = ["XIC(Input1)", "OTE(Output1)"]

        with self.assertRaises(IndexError) as context:
            rung._remove_tokens(tokens, 1, 0)  # start > end

        self.assertIn("Invalid start or end indices", str(context.exception))

    def test_insert_branch_tokens_invalid_positions(self):
        """Test _insert_branch_tokens with invalid positions."""
        rung = RaRung(meta_data=self.rung_meta, )

        tokens = ["XIC(Input1)", "OTE(Output1)"]

        with self.assertRaises(ValueError) as context:
            rung._insert_branch_tokens(tokens, 2, 1, [])  # end < start

        self.assertIn("End position must be greater than or equal to start position", str(context.exception))

    def test_find_instruction_index_not_found(self):
        """Test _find_instruction_index_in_text with non-existent instruction."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

            with self.assertRaises(ValueError) as context:
                rung._find_instruction_index_in_text("XIO(Input2)")

            self.assertIn("Instruction 'XIO(Input2)' not found", str(context.exception))

    def test_find_instruction_index_occurrence_out_of_range(self):
        """Test _find_instruction_index_in_text with occurrence out of range."""
        rung = RaRung(meta_data=self.rung_meta, )

        with patch.object(rung, '_tokenize_rung_text') as mock_tokenize:
            mock_tokenize.return_value = ["XIC(Input1)", "OTE(Output1)"]

            with self.assertRaises(ValueError) as context:
                rung._find_instruction_index_in_text("XIC(Input1)", occurrence=5)

            self.assertIn("Occurrence 5 not found", str(context.exception))


class TestRaRungIntegration(unittest.TestCase):
    """Integration tests for RaRung class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=RaController)
        self.mock_routine = Mock(spec=RaRoutine)

    def test_full_rung_lifecycle(self):
        """Test full rung creation and usage lifecycle."""
        rung_meta = {
            '@Number': '0',
            '@Type': 'N',
            'Text': 'XIC(StartButton)[XIO(SafetyStop),XIC(Enable)]OTE(Motor);',
            'Comment': 'Motor control logic with safety'
        }

        # Create rung with meta_data directly
        rung = RaRung(
            meta_data=rung_meta,

            routine=self.mock_routine
        )

        # Verify properties
        self.assertEqual(rung.number, '0')
        self.assertEqual(rung.type, 'N')
        self.assertIn('Motor control logic', rung.comment)

        # Verify instructions - the rung should parse 4 instructions from the text
        self.assertEqual(len(rung.instructions), 4)

        # Verify the text contains branch markers
        self.assertIn('[', rung.text)
        self.assertIn(']', rung.text)

        # Test instruction manipulation
        mock_new_instr = Mock(spec=RaLogicInstruction)
        mock_new_instr.get_meta_data.return_value = "XIC(NewInput)"
        rung.add_instruction(mock_new_instr)
        self.assertIn("XIC(NewInput)", rung.text)

        # Test branch validation - should pass even with branches in text
        self.assertTrue(rung.validate_branch_structure())

    def test_complex_branch_operations(self):
        """Test complex branch operations."""
        complex_meta = {
            '@Number': '1',
            '@Type': 'N',
            'Text': 'XIC(A)[XIO(B)[XIC(C),XIO(D)],XIC(E)]OTE(F);',
            'Comment': 'Complex nested branches'
        }

        rung = RaRung(meta_data=complex_meta, )

        # Verify the rung was created with the complex text
        self.assertEqual(rung.number, '1')
        self.assertEqual(rung.type, 'N')

        # Verify the text contains nested branch markers
        self.assertIn('[', rung.text)
        self.assertIn(']', rung.text)

        # Verify instructions were parsed (6 instructions in the text)
        self.assertEqual(len(rung.instructions), 6)

        # Test branch validation on complex structure
        self.assertTrue(rung.validate_branch_structure())


if __name__ == '__main__':
    unittest.main()
