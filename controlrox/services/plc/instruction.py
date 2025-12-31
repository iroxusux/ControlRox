import re
from pyrox.models.abc.factory import MetaFactory


class InstructionFactory(MetaFactory):
    pass


def extract_instruction_strings(
    text
) -> list[str]:
    """Extract instructions with properly balanced parentheses.

    Args:
        text (str): The rung text to extract instructions from.

    Returns:
        List[str]: A list of extracted instructions.
    """
    instructions = []

    # Find instruction starts
    starts = list(re.finditer(r'[A-Za-z0-9_]+\(', text))

    for match in starts:
        start_pos = match.start()
        paren_pos = match.end() - 1  # Position of opening parenthesis

        # Find matching closing parenthesis
        paren_count = 1
        pos = paren_pos + 1

        while pos < len(text) and paren_count > 0:
            if text[pos] == '(':
                paren_count += 1
            elif text[pos] == ')':
                paren_count -= 1
            pos += 1

        if paren_count == 0:  # Found matching closing parenthesis
            instruction = text[start_pos:pos]
            instructions.append(instruction)

    return instructions
