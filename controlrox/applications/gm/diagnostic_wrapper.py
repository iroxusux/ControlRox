"""Utility function to wrap diagnostic text lines with angle brackets.

This script provides a function to ensure that Alarm, Prompt, and TL (Text List)
diagnostic lines are properly wrapped with angle brackets (< >).
"""
import re


def wrap_diagnostic_line(text: str) -> str:
    """Wrap diagnostic lines with angle brackets if not already wrapped.

    Handles Alarm, Prompt, and TL (Text List) patterns. If a line contains
    these patterns but is not already wrapped with < >, adds them.

    Lines may start with optional whitespace and/or a '#' character.
    Only the diagnostic portion (Alarm/Prompt/TL) is wrapped.

    Args:
        text: The text line to process

    Returns:
        The text with proper angle bracket wrapping

    Examples:
        >>> wrap_diagnostic_line("Alarm[50]: CAM11 EtherNet IP Comm Fault")
        '<Alarm[50]: CAM11 EtherNet IP Comm Fault>'

        >>> wrap_diagnostic_line("#Alarm[50]: CAM11 Fault")
        '#<Alarm[50]: CAM11 Fault>'

        >>> wrap_diagnostic_line("# Alarm[50]: CAM11 Fault")
        '# <Alarm[50]: CAM11 Fault>'

        >>> wrap_diagnostic_line("<Alarm[50]: CAM11 EtherNet IP Comm Fault>")
        '<Alarm[50]: CAM11 EtherNet IP Comm Fault>'

        >>> wrap_diagnostic_line("Prompt[20]: Test prompt message")
        '<Prompt[20]: Test prompt message>'

        >>> wrap_diagnostic_line("TestList[10]: Some message")
        '<TestList[10]: Some message>'
    """
    if not text or not text.strip():
        return text

    # Pattern to match optional leading whitespace, optional '#', optional spaces,
    # then the diagnostic pattern: Word[number]: text
    # Groups: (leading_ws)(#)(spaces_after_hash)(diagnostic_pattern)
    pattern = r'^(\s*)(#?)(\s*)([A-Za-z_][A-Za-z0-9_]*\[\d+\]:.*)$'

    match = re.match(pattern, text)

    if not match:
        # Not a diagnostic line, return as-is
        return text

    leading_ws = match.group(1)
    hash_char = match.group(2)
    spaces_after_hash = match.group(3)
    diagnostic_text = match.group(4)

    # Check if the diagnostic portion is already wrapped with angle brackets
    if diagnostic_text.startswith('<') and diagnostic_text.endswith('>'):
        # Already wrapped, return as-is
        return text

    # Preserve trailing whitespace
    trailing_space = text[len(text.rstrip()):]

    # Wrap only the diagnostic text, preserve prefix
    return f"{leading_ws}{hash_char}{spaces_after_hash}<{diagnostic_text}>{trailing_space}"


def wrap_diagnostic_lines(text: str) -> str:
    """Process multiple lines and wrap diagnostic lines as needed.

    Takes a multi-line string and wraps any diagnostic lines that need it.

    Args:
        text: Multi-line text to process

    Returns:
        Text with all diagnostic lines properly wrapped

    Example:
        >>> text = '''Line 1
        ... Alarm[50]: CAM11 Fault
        ... <Prompt[20]: Already wrapped>
        ... Regular line
        ... TestList[10]: Test message'''
        >>> print(wrap_diagnostic_lines(text))
        Line 1
        <Alarm[50]: CAM11 Fault>
        <Prompt[20]: Already wrapped>
        Regular line
        <TestList[10]: Test message>
    """
    lines = text.splitlines(keepends=True)
    result_lines = [wrap_diagnostic_line(line.rstrip('\n\r')) +
                    (line[len(line.rstrip('\n\r')):] if line else '')
                    for line in lines]
    return ''.join(result_lines)


def fix_comment_diagnostics(comment: str) -> str:
    """Fix diagnostic formatting in PLC rung comments.

    This is a specialized function for PLC comments that may contain
    multiple diagnostic lines mixed with other text.

    Args:
        comment: The comment text from a PLC rung

    Returns:
        Comment with properly formatted diagnostic lines
    """
    if not comment:
        return comment

    return wrap_diagnostic_lines(comment)


# Example usage and tests
if __name__ == '__main__':
    print("=== Testing wrap_diagnostic_line ===\n")

    test_cases = [
        # (input, expected_output)
        ("Alarm[50]: CAM11 EtherNet IP Comm Fault",
         "<Alarm[50]: CAM11 EtherNet IP Comm Fault>"),

        ("<Alarm[50]: CAM11 EtherNet IP Comm Fault>",
         "<Alarm[50]: CAM11 EtherNet IP Comm Fault>"),

        ("Prompt[20]: Test prompt message",
         "<Prompt[20]: Test prompt message>"),

        ("<Prompt[20]: Test prompt message>",
         "<Prompt[20]: Test prompt message>"),

        ("TestList[10]: Some message",
         "<TestList[10]: Some message>"),

        ("Regular text without pattern",
         "Regular text without pattern"),

        ("  Alarm[5]: Indented alarm  ",
         "  <Alarm[5]: Indented alarm>  "),

        ("MyCustomList[999]: Custom diagnostic",
         "<MyCustomList[999]: Custom diagnostic>"),
    ]

    all_passed = True
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = wrap_diagnostic_line(input_text)
        passed = result == expected
        all_passed = all_passed and passed

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        print()

    print("=== Testing wrap_diagnostic_lines (multi-line) ===\n")

    multiline_test = """<@DIAG>
Alarm[50]: CAM11 EtherNet IP Comm Fault
<Prompt[20]: Already wrapped prompt>
Some regular comment text
TestList[10]: Test message
Another regular line"""

    expected_multiline = """<@DIAG>
<Alarm[50]: CAM11 EtherNet IP Comm Fault>
<Prompt[20]: Already wrapped prompt>
Some regular comment text
<TestList[10]: Test message>
Another regular line"""

    result_multiline = wrap_diagnostic_lines(multiline_test)
    multiline_passed = result_multiline == expected_multiline
    all_passed = all_passed and multiline_passed

    print(f"Multi-line test: {'✓ PASS' if multiline_passed else '✗ FAIL'}")
    print("Input:")
    print(multiline_test)
    print("\nExpected:")
    print(expected_multiline)
    print("\nGot:")
    print(result_multiline)
    print()

    print("=== Summary ===")
    print(f"All tests {'PASSED ✓' if all_passed else 'FAILED ✗'}")

    # Example of how to use with GM rung comments
    print("\n=== Example GM Integration ===")
    print("# In your GM code, you can use it like this:")
    print("""
# For a single rung comment:
rung_comment = "Alarm[50]: CAM11 Fault"
fixed_comment = fix_comment_diagnostics(rung_comment)

# Or for a GmRung object:
class GmRung:
    def fix_comment_formatting(self):
        if self.comment:
            self.comment = fix_comment_diagnostics(self.comment)

# Or process all rungs in a routine:
def fix_routine_comments(routine):
    for rung in routine.rungs:
        if rung.comment:
            rung.comment = fix_comment_diagnostics(rung.comment)
""")
