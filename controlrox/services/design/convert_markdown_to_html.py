"""Convert a Markdown file to an HTML file using Pandoc.

Command-line usage:
    python docs/controls/design/convert_markdown_to_html.py \
        --input  path/to/input.md \
        --output path/to/output.html \
        [--theme github-dark|light] \
        [--title "Optional HTML Title"]

Options:
    --input   Path to the input Markdown file.
    --output  Path to the output HTML file.
    --theme   HTML theme (github-dark or light).
    --title   Optional HTML title.

Programmatic usage:
    from pathlib import Path
    from controlrox.services.design.convert_markdown_to_html import convert_markdown_to_html

    # Basic usage
    output = convert_markdown_to_html(
        input_markdown="path/to/input.md",
        output_html="path/to/output.html"
    )

    # With custom theme and title
    output = convert_markdown_to_html(
        input_markdown="my_doc.md",
        output_html="my_doc.html",
        theme="light",
        title="My Custom Title"
    )

"""
import argparse
import sys

import pypandoc


_GITHUB_DARK_CSS = """
:root {
    color-scheme: dark;
}

html, body {
    height: 100%;
}

body {
    margin: 0;
    background: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.5;
}

a { color: #58a6ff; }
a:visited { color: #8e96f0; }

.markdown-body {
    box-sizing: border-box;
    min-width: 200px;
    max-width: 980px;
    margin: 0 auto;
    padding: 32px 24px;
}

hr {
    border: 0;
    border-top: 1px solid #30363d;
}

blockquote {
    margin: 0;
    padding: 0 1em;
    color: #8b949e;
    border-left: 0.25em solid #30363d;
}

pre, code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

code {
    padding: 0.2em 0.4em;
    border-radius: 6px;
    background: rgba(110, 118, 129, 0.2);
}

pre {
    padding: 16px;
    overflow: auto;
    border-radius: 6px;
    background: #161b22;
    border: 1px solid #30363d;
}

pre code {
    padding: 0;
    background: transparent;
}

table {
    border-collapse: collapse;
    width: 100%;
}

table th, table td {
    border: 1px solid #30363d;
    padding: 6px 13px;
}

table tr:nth-child(2n) {
    background: #161b22;
}
"""


_LIGHT_CSS = """
:root {
    color-scheme: light;
}

body {
    margin: 0;
    background: #ffffff;
    color: #111111;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.5;
}

.markdown-body {
    box-sizing: border-box;
    min-width: 200px;
    max-width: 980px;
    margin: 0 auto;
    padding: 32px 24px;
}

pre, code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
"""


def _wrap_html(*, title: str, body_html: str, css: str) -> str:
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\" />\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
        f"  <title>{title}</title>\n"
        "  <style>\n"
        f"{css}\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <main class=\"markdown-body\">\n"
        f"{body_html}\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def convert_markdown_to_html(
    input_markdown: str,
    output_html: str,
    theme: str = "github-dark",
    title: str = "",
) -> str:
    """Convert a Markdown file to an HTML file using Pandoc.

    This function provides a programmatic interface to convert Markdown to HTML
    without using command-line arguments. It can be called directly from
    Python code.

    Args:
        input_markdown: Path to the input Markdown file
        output_html: Path to the output HTML file
        theme: HTML theme - "github-dark" or "light" (default: "github-dark")
        title: Optional HTML <title>. Defaults to the input filename if empty.

    Returns:
        str: The path to the output HTML file

    Raises:
        FileNotFoundError: If input Markdown file doesn't exist
        RuntimeError: If pandoc conversion fails

    Example:
        >>> from controlrox.services.design.convert_markdown_to_html import convert_markdown_to_html
        >>>
        >>> # Basic usage with default theme
        >>> output = convert_markdown_to_html(
        ...     input_markdown="docs/README.md",
        ...     output_html="docs/README.html"
        ... )
        >>> print(f"Created: {output}")
        >>>
        >>> # With light theme and custom title
        >>> output = convert_markdown_to_html(
        ...     input_markdown="my_doc.md",
        ...     output_html="my_doc.html",
        ...     theme="light",
        ...     title="My Documentation"
        ... )
    """
    from pathlib import Path

    input_path = Path(input_markdown)
    output_path = Path(output_html)

    # Validate input
    if not input_path.exists():
        raise FileNotFoundError(f"Input Markdown file not found: {input_path}")

    # Validate theme
    if theme not in ("github-dark", "light"):
        raise ValueError(f"Invalid theme '{theme}'. Must be 'github-dark' or 'light'")

    # Determine title and CSS
    page_title = title or str(input_path)
    css = _GITHUB_DARK_CSS if theme == "github-dark" else _LIGHT_CSS

    # Convert Markdown to HTML
    try:
        body_html = pypandoc.convert_file(
            str(input_path),
            to="html",
            format="md",
        )
        html = _wrap_html(title=page_title, body_html=body_html, css=css)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)

        return str(output_path)

    except Exception as exc:
        raise RuntimeError(f"Pandoc conversion failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML using Pandoc bundled in the venv.")
    parser.add_argument("--input", required=True, help="Input markdown file path")
    parser.add_argument("--output", required=True, help="Output html file path")
    parser.add_argument(
        "--theme",
        choices=("github-dark", "light"),
        default="github-dark",
        help="HTML theme. Default matches GitHub's dark markdown preview.",
    )
    parser.add_argument(
        "--title",
        default="",
        help="Optional HTML <title>. Defaults to the input filename.",
    )
    args = parser.parse_args()

    try:
        output_path = convert_markdown_to_html(
            input_markdown=args.input,
            output_html=args.output,
            theme=args.theme,
            title=args.title,
        )
        print(f"Converted: {output_path}")
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
