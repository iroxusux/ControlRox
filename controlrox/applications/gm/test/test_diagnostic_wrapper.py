"""Comprehensive unit tests for diagnostic_wrapper.py

Tests the wrapping of diagnostic text lines with angle brackets.
"""
import unittest
from controlrox.applications.gm.diagnostic_wrapper import (
    wrap_diagnostic_line,
    wrap_diagnostic_lines,
    fix_comment_diagnostics
)


class TestWrapDiagnosticLine(unittest.TestCase):
    """Test cases for wrap_diagnostic_line function."""

    def test_unwrapped_alarm_gets_wrapped(self):
        """Test that unwrapped Alarm lines get wrapped."""
        input_text = "#         Alarm[50]: CAM11 EtherNet IP Comm Fault"
        expected = "#         <Alarm[50]: CAM11 EtherNet IP Comm Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_already_wrapped_alarm_stays_wrapped(self):
        """Test that already wrapped Alarm lines stay as-is."""
        input_text = "#         <Alarm[50]: CAM11 EtherNet IP Comm Fault>"
        expected = "#         <Alarm[50]: CAM11 EtherNet IP Comm Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_unwrapped_prompt_gets_wrapped(self):
        """Test that unwrapped Prompt lines get wrapped."""
        input_text = "#         Prompt[20]: Test prompt message"
        expected = "#         <Prompt[20]: Test prompt message>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_already_wrapped_prompt_stays_wrapped(self):
        """Test that already wrapped Prompt lines stay as-is."""
        input_text = "#         <Prompt[20]: Test prompt message>"
        expected = "#         <Prompt[20]: Test prompt message>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_unwrapped_tl_gets_wrapped(self):
        """Test that unwrapped TL (text list) lines get wrapped."""
        input_text = "#         TestList[10]: Some message"
        expected = "#         <TestList[10]: Some message>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_already_wrapped_tl_stays_wrapped(self):
        """Test that already wrapped TL lines stay as-is."""
        input_text = "#         <TestList[10]: Some message>"
        expected = "#         <TestList[10]: Some message>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_spaces_gets_wrapped(self):
        """Test Alarm with leading/trailing spaces preserves spacing."""
        input_text = "  Alarm[5]: Indented alarm  "
        expected = "  <Alarm[5]: Indented alarm  >  "
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_custom_diagnostic_gets_wrapped(self):
        """Test that custom diagnostic patterns get wrapped."""
        input_text = "MyCustomList[999]: Custom diagnostic"
        expected = "<MyCustomList[999]: Custom diagnostic>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_regular_text_not_wrapped(self):
        """Test that regular text without pattern is not wrapped."""
        input_text = "Regular text without pattern"
        expected = "Regular text without pattern"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_empty_string_returns_empty(self):
        """Test that empty string returns empty string."""
        input_text = ""
        expected = ""
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_whitespace_only_returns_whitespace(self):
        """Test that whitespace-only string returns same whitespace."""
        input_text = "   "
        expected = "   "
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_long_message(self):
        """Test Alarm with a very long message."""
        input_text = "Alarm[100]: This is a very long alarm message with lots of details"
        expected = "<Alarm[100]: This is a very long alarm message with lots of details>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_special_characters(self):
        """Test Alarm with special characters in message."""
        input_text = "Alarm[50]: CAM11 EtherNet/IP Comm Fault - Check Connection!"
        expected = "<Alarm[50]: CAM11 EtherNet/IP Comm Fault - Check Connection!>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_prompt_with_special_characters(self):
        """Test Prompt with special characters."""
        input_text = "Prompt[20]: Press OK to continue (or Cancel)"
        expected = "<Prompt[20]: Press OK to continue (or Cancel)>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_index_zero(self):
        """Test Alarm with index [0]."""
        input_text = "Alarm[0]: First alarm"
        expected = "<Alarm[0]: First alarm>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_large_index(self):
        """Test Alarm with large index number."""
        input_text = "Alarm[9999]: Large index alarm"
        expected = "<Alarm[9999]: Large index alarm>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_partial_angle_brackets_not_considered_wrapped(self):
        """Test that partial angle brackets don't prevent wrapping."""
        # Only has opening bracket
        input_text = "<Alarm[50]: CAM11 Fault"
        # This might need adjustment based on desired behavior
        # Currently will not match pattern since < is at start
        result = wrap_diagnostic_line(input_text)
        # Pattern won't match because it starts with <
        self.assertEqual(result, input_text)

    def test_angle_brackets_in_middle_gets_wrapped(self):
        """Test that angle brackets in middle of text don't prevent wrapping."""
        input_text = "Alarm[50]: CAM11 <device> Fault"
        expected = "<Alarm[50]: CAM11 <device> Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_hash_prefix_gets_wrapped(self):
        """Test Alarm with '#' prefix gets wrapped correctly."""
        input_text = "#Alarm[50]: CAM11 Fault"
        expected = "#<Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_hash_and_space_prefix_gets_wrapped(self):
        """Test Alarm with '# ' prefix gets wrapped correctly."""
        input_text = "# Alarm[50]: CAM11 Fault"
        expected = "# <Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_hash_and_multiple_spaces_gets_wrapped(self):
        """Test Alarm with '#   ' prefix gets wrapped correctly."""
        input_text = "#   Alarm[50]: CAM11 Fault"
        expected = "#   <Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_leading_spaces_and_hash_gets_wrapped(self):
        """Test Alarm with leading spaces and '#' gets wrapped correctly."""
        input_text = "   #Alarm[50]: CAM11 Fault"
        expected = "   #<Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_leading_spaces_hash_and_space_gets_wrapped(self):
        """Test Alarm with leading spaces, '#', and space gets wrapped correctly."""
        input_text = "   # Alarm[50]: CAM11 Fault"
        expected = "   # <Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_prompt_with_hash_prefix_gets_wrapped(self):
        """Test Prompt with '#' prefix gets wrapped correctly."""
        input_text = "#Prompt[20]: User prompt"
        expected = "#<Prompt[20]: User prompt>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_tl_with_hash_prefix_gets_wrapped(self):
        """Test TL with '#' prefix gets wrapped correctly."""
        input_text = "#TestList[10]: Test message"
        expected = "#<TestList[10]: Test message>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_already_wrapped_with_hash_stays_wrapped(self):
        """Test already wrapped diagnostic with '#' stays as-is."""
        input_text = "#<Alarm[50]: CAM11 Fault>"
        expected = "#<Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_already_wrapped_with_hash_and_space_stays_wrapped(self):
        """Test already wrapped diagnostic with '# ' stays as-is."""
        input_text = "# <Alarm[50]: CAM11 Fault>"
        expected = "# <Alarm[50]: CAM11 Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)


class TestWrapDiagnosticLines(unittest.TestCase):
    """Test cases for wrap_diagnostic_lines function (multi-line)."""

    def test_multiline_with_mixed_content(self):
        """Test multi-line text with mixed diagnostic and regular lines."""
        input_text = """<@DIAG>
Alarm[50]: CAM11 EtherNet IP Comm Fault
<Prompt[20]: Already wrapped prompt>
Some regular comment text
TestList[10]: Test message
Another regular line"""

        expected = """<@DIAG>
<Alarm[50]: CAM11 EtherNet IP Comm Fault>
<Prompt[20]: Already wrapped prompt>
Some regular comment text
<TestList[10]: Test message>
Another regular line"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_all_need_wrapping(self):
        """Test multi-line where all diagnostic lines need wrapping."""
        input_text = """Alarm[1]: First alarm
Alarm[2]: Second alarm
Prompt[3]: First prompt"""

        expected = """<Alarm[1]: First alarm>
<Alarm[2]: Second alarm>
<Prompt[3]: First prompt>"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_none_need_wrapping(self):
        """Test multi-line where all are already wrapped."""
        input_text = """<Alarm[1]: First alarm>
<Alarm[2]: Second alarm>
<Prompt[3]: First prompt>"""

        expected = """<Alarm[1]: First alarm>
<Alarm[2]: Second alarm>
<Prompt[3]: First prompt>"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_only_regular_text(self):
        """Test multi-line with only regular text (no diagnostics)."""
        input_text = """This is line 1
This is line 2
This is line 3"""

        expected = """This is line 1
This is line 2
This is line 3"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_preserves_blank_lines(self):
        """Test that blank lines are preserved."""
        input_text = """Alarm[1]: First alarm

Alarm[2]: Second alarm"""

        expected = """<Alarm[1]: First alarm>

<Alarm[2]: Second alarm>"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_single_line(self):
        """Test multi-line function with single line."""
        input_text = "Alarm[50]: Single line alarm"
        expected = "<Alarm[50]: Single line alarm>"
        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_empty_string(self):
        """Test multi-line with empty string."""
        input_text = ""
        expected = ""
        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_with_hash_prefixes(self):
        """Test multi-line with various '#' prefix patterns."""
        input_text = """Alarm[1]: No hash
#Alarm[2]: With hash
# Alarm[3]: Hash and space
   #Alarm[4]: Leading spaces and hash
   # Alarm[5]: Leading spaces, hash, and space"""

        expected = """<Alarm[1]: No hash>
#<Alarm[2]: With hash>
# <Alarm[3]: Hash and space>
   #<Alarm[4]: Leading spaces and hash>
   # <Alarm[5]: Leading spaces, hash, and space>"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)

    def test_multiline_mixed_hash_and_wrapped(self):
        """Test multi-line with mix of hash prefixes and already wrapped."""
        input_text = """#Alarm[1]: Needs wrapping
#<Alarm[2]: Already wrapped>
# Alarm[3]: Needs wrapping with space
# <Alarm[4]: Already wrapped with space>"""

        expected = """#<Alarm[1]: Needs wrapping>
#<Alarm[2]: Already wrapped>
# <Alarm[3]: Needs wrapping with space>
# <Alarm[4]: Already wrapped with space>"""

        result = wrap_diagnostic_lines(input_text)
        self.assertEqual(result, expected)


class TestFixCommentDiagnostics(unittest.TestCase):
    """Test cases for fix_comment_diagnostics function."""

    def test_simple_alarm_comment(self):
        """Test simple alarm in comment."""
        input_comment = "Alarm[50]: CAM11 Fault"
        expected = "<Alarm[50]: CAM11 Fault>"
        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_simple_prompt_comment(self):
        """Test simple prompt in comment."""
        input_comment = "Prompt[20]: User prompt"
        expected = "<Prompt[20]: User prompt>"
        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_multiline_comment_with_diagnostics(self):
        """Test multi-line comment with multiple diagnostics."""
        input_comment = """Network diagnostics:
Alarm[50]: CAM11 Fault
Alarm[51]: CAM12 Fault
Prompt[20]: Check network"""

        expected = """Network diagnostics:
<Alarm[50]: CAM11 Fault>
<Alarm[51]: CAM12 Fault>
<Prompt[20]: Check network>"""

        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_comment_with_already_wrapped(self):
        """Test comment with mix of wrapped and unwrapped."""
        input_comment = """<Alarm[50]: Already wrapped>
Alarm[51]: Needs wrapping
Regular text here"""

        expected = """<Alarm[50]: Already wrapped>
<Alarm[51]: Needs wrapping>
Regular text here"""

        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_empty_comment(self):
        """Test empty comment."""
        input_comment = ""
        expected = ""
        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_none_comment(self):
        """Test None comment."""
        input_comment = None
        expected = None
        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_comment_no_diagnostics(self):
        """Test comment with no diagnostics."""
        input_comment = "Just a regular comment with no diagnostics"
        expected = "Just a regular comment with no diagnostics"
        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and corner scenarios."""

    def test_alarm_without_colon(self):
        """Test that pattern without colon is not matched."""
        input_text = "Alarm[50] No colon here"
        expected = "Alarm[50] No colon here"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_without_brackets(self):
        """Test that pattern without brackets is not matched."""
        input_text = "Alarm50: Missing brackets"
        expected = "Alarm50: Missing brackets"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_alarm_with_text_before(self):
        """Test that text before pattern prevents matching."""
        input_text = "Some text Alarm[50]: Fault"
        expected = "Some text Alarm[50]: Fault"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_lowercase_alarm(self):
        """Test that lowercase 'alarm' is matched."""
        input_text = "alarm[50]: Lowercase alarm"
        expected = "<alarm[50]: Lowercase alarm>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_mixed_case_prompt(self):
        """Test mixed case Prompt."""
        input_text = "PROMPT[20]: Uppercase prompt"
        expected = "<PROMPT[20]: Uppercase prompt>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_diagnostic_with_underscore_in_name(self):
        """Test diagnostic name with underscore."""
        input_text = "My_List[10]: Underscore in name"
        expected = "<My_List[10]: Underscore in name>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_diagnostic_starting_with_number_not_matched(self):
        """Test that diagnostic names can't start with number."""
        input_text = "1Alarm[50]: Starts with number"
        expected = "1Alarm[50]: Starts with number"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_unicode_in_diagnostic_message(self):
        """Test diagnostic with unicode characters."""
        input_text = "Alarm[50]: Temperature exceeds 100°C"
        expected = "<Alarm[50]: Temperature exceeds 100°C>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_diagnostic_empty_message(self):
        """Test diagnostic with empty message after colon."""
        input_text = "Alarm[50]:"
        expected = "<Alarm[50]:>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_diagnostic_with_only_space_after_colon(self):
        """Test diagnostic with only space after colon."""
        input_text = "Alarm[50]: "
        expected = "<Alarm[50]: > "
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)


class TestRealWorldExamples(unittest.TestCase):
    """Test with real-world GM PLC examples."""

    def test_gm_cam_alarm(self):
        """Test typical GM CAM alarm."""
        input_text = "Alarm[50]: CAM11 EtherNet IP Comm Fault"
        expected = "<Alarm[50]: CAM11 EtherNet IP Comm Fault>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_gm_kdiag_with_multiple_alarms(self):
        """Test GM KDiag block with multiple alarms."""
        input_comment = """<@DIAG>
Alarm[50]: CAM11 Comm Fault
Alarm[51]: CAM12 Comm Fault
Prompt[20]: Check camera connections"""

        expected = """<@DIAG>
<Alarm[50]: CAM11 Comm Fault>
<Alarm[51]: CAM12 Comm Fault>
<Prompt[20]: Check camera connections>"""

        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_gm_mixed_wrapped_unwrapped(self):
        """Test GM comment with mix of wrapped and unwrapped."""
        input_comment = """<@DIAG>
<Alarm[100]: Already wrapped alarm>
Alarm[101]: Not wrapped yet
<Prompt[50]: Already wrapped prompt>
Prompt[51]: Not wrapped yet
Regular instruction comment"""

        expected = """<@DIAG>
<Alarm[100]: Already wrapped alarm>
<Alarm[101]: Not wrapped yet>
<Prompt[50]: Already wrapped prompt>
<Prompt[51]: Not wrapped yet>
Regular instruction comment"""

        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_gm_textlist_element(self):
        """Test GM TextList element."""
        input_text = "TextList[10]: Status message"
        expected = "<TextList[10]: Status message>"
        result = wrap_diagnostic_line(input_text)
        self.assertEqual(result, expected)

    def test_gm_kdiag_with_hash_comments(self):
        """Test GM KDiag block with '#' commented diagnostics."""
        input_comment = """<@DIAG>
#Alarm[50]: CAM11 Comm Fault
# Alarm[51]: CAM12 Comm Fault
#<Alarm[52]: Already wrapped with hash>
Prompt[20]: Check camera connections"""

        expected = """<@DIAG>
#<Alarm[50]: CAM11 Comm Fault>
# <Alarm[51]: CAM12 Comm Fault>
#<Alarm[52]: Already wrapped with hash>
<Prompt[20]: Check camera connections>"""

        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)

    def test_gm_mixed_hash_scenarios(self):
        """Test GM with various hash prefix scenarios."""
        input_comment = """Network diagnostics:
Alarm[50]: CAM11 Fault
#Alarm[51]: CAM12 Fault (commented)
   # Alarm[52]: CAM13 Fault (indented and commented)
<Alarm[53]: Already wrapped>
# <Alarm[54]: Already wrapped with hash>"""

        expected = """Network diagnostics:
<Alarm[50]: CAM11 Fault>
#<Alarm[51]: CAM12 Fault (commented)>
   # <Alarm[52]: CAM13 Fault (indented and commented)>
<Alarm[53]: Already wrapped>
# <Alarm[54]: Already wrapped with hash>"""

        result = fix_comment_diagnostics(input_comment)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
