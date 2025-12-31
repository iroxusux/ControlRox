"""Render a filled Controls Design Checklist Markdown from a YAML file.

Command-line usage (from repo root or anywhere):
  python docs/controls/design/render_controls_design_checklist.py \
    --input  path/to/filled_checklist.yaml \
    --output path/to/filled_checklist.md

Optional:
  --template docs/controls/design/controls_design_checklist.report.md.j2
  --strict   (fail on missing YAML fields for validation)

Programmatic usage:
  from pathlib import Path
  from controlrox.services.design.render_controls_design_checklist import render_checklist

  # Basic usage
  output = render_checklist(
      input_yaml="path/to/filled_checklist.yaml",
      output_markdown="path/to/filled_checklist.md"
  )

  # With custom template and strict validation
  output = render_checklist(
      input_yaml="my_checklist.yaml",
      output_markdown="my_checklist.md",
      template="my_custom_template.md.j2",
      strict=True
  )

Notes:
- This script does NOT modify the Markdown template checklist.
- It renders a report-style Markdown from YAML using Jinja2.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


DEFAULT_TEMPLATE = Path(__file__).with_name("controls_design_checklist.report.md.j2")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: PyYAML. Install with: pip install pyyaml"
        ) from exc

    data = yaml.safe_load(_read_text(path))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SystemExit(f"YAML root must be a mapping/object: {path}")
    return data


def _render(template_path: Path, context: dict[str, Any]) -> str:
    try:
        from jinja2 import ChainableUndefined, Environment, FileSystemLoader  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: Jinja2. Install with: pip install jinja2"
        ) from exc

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        undefined=ChainableUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def _yn(value: Any) -> str:
        return "☑" if bool(value) else "☐"

    def _val(value: Any, default: str = "") -> str:
        if value is None:
            return default
        if isinstance(value, str) and value.strip() == "":
            return default
        return str(value)

    def _mdlink(value: Any, label: str | None = None) -> str:
        """Render a value as a Markdown link when possible.

        Supported inputs:
        - "https://..." -> <https://...>
        - {label: "X", url: "https://..."} -> [X](https://...)
        - {label: "X", link: "https://..."} -> [X](https://...)
        - {url: "https://..."} -> <https://...>
        - Any other value -> string value
        """

        if value is None:
            return ""

        if isinstance(value, dict):
            url_value = (
                value.get("url")
                or value.get("link")
                or value.get("href")
                or value.get("uri")
            )
            label_value = (
                label
                or value.get("label")
                or value.get("name")
                or value.get("title")
            )
            url_text = str(url_value).strip() if url_value is not None else ""
            label_text = str(label_value).strip() if label_value is not None else ""

            if url_text:
                if label_text:
                    return f"[{label_text}]({url_text})"
                return f"<{url_text}>"

            return label_text

        if isinstance(value, str):
            text = value.strip()
            if not text:
                return ""
            if "://" in text:
                return f"<{text}>" if label is None else f"[{label}]({text})"
            return text

        return str(value)

    env.filters["yn"] = _yn
    env.filters["val"] = _val
    env.filters["mdlink"] = _mdlink

    template = env.get_template(template_path.name)
    return template.render(**context)


def _render_strict(template_path: Path, context: dict[str, Any]) -> str:
    """Render with strict undefined behavior to catch missing fields."""
    try:
        from jinja2 import Environment, FileSystemLoader, StrictUndefined  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: Jinja2. Install with: pip install jinja2"
        ) from exc

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def _yn(value: Any) -> str:
        return "☑" if bool(value) else "☐"

    def _val(value: Any, default: str = "") -> str:
        if value is None:
            return default
        if isinstance(value, str) and value.strip() == "":
            return default
        return str(value)

    def _mdlink(value: Any, label: str | None = None) -> str:
        if value is None:
            return ""

        if isinstance(value, dict):
            url_value = (
                value.get("url")
                or value.get("link")
                or value.get("href")
                or value.get("uri")
            )
            label_value = (
                label
                or value.get("label")
                or value.get("name")
                or value.get("title")
            )
            url_text = str(url_value).strip() if url_value is not None else ""
            label_text = str(label_value).strip() if label_value is not None else ""

            if url_text:
                if label_text:
                    return f"[{label_text}]({url_text})"
                return f"<{url_text}>"
            return label_text

        if isinstance(value, str):
            text = value.strip()
            if not text:
                return ""
            if "://" in text:
                return f"<{text}>" if label is None else f"[{label}]({text})"
            return text

        return str(value)

    env.filters["yn"] = _yn
    env.filters["val"] = _val
    env.filters["mdlink"] = _mdlink

    template = env.get_template(template_path.name)
    return template.render(**context)


def render_checklist(
    input_yaml: Path | str,
    output_markdown: Path | str,
    template: Path | str | None = None,
    strict: bool = False,
) -> Path:
    """Render a Controls Design Checklist Markdown from a YAML file.

    This function provides a programmatic interface to render checklists
    without using command-line arguments. It can be called directly from
    Python code.

    Args:
        input_yaml: Path to filled YAML file (based on controls_design_checklist.template.yaml)
        output_markdown: Path to write rendered Markdown report
        template: Path to Jinja2 Markdown template (default: controls_design_checklist.report.md.j2)
        strict: If True, fail on missing YAML fields (useful for validating completeness)

    Returns:
        Path: The path to the rendered output file

    Raises:
        FileNotFoundError: If input YAML or template file doesn't exist
        SystemExit: If dependencies are missing or YAML is invalid

    Example:
        >>> from pathlib import Path
        >>> from controlrox.services.design.render_controls_design_checklist import render_checklist
        >>>
        >>> # Basic usage
        >>> output = render_checklist(
        ...     input_yaml="docs/controls/design/CONTROLS_DESIGN_CHECKLIST.filled.example.yaml",
        ...     output_markdown="docs/controls/design/CONTROLS_DESIGN_CHECKLIST.filled.example.md"
        ... )
        >>> print(f"Rendered: {output}")
        >>>
        >>> # With custom template and strict mode
        >>> output = render_checklist(
        ...     input_yaml="my_checklist.yaml",
        ...     output_markdown="my_checklist.md",
        ...     template="my_template.md.j2",
        ...     strict=True
        ... )
    """
    # Convert to Path objects
    input_path = Path(input_yaml)
    output_path = Path(output_markdown)
    template_path = Path(template) if template is not None else DEFAULT_TEMPLATE

    # Validate inputs
    if not input_path.exists():
        raise FileNotFoundError(f"Input YAML not found: {input_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Load YAML data
    context = _load_yaml(input_path)

    # Render with appropriate mode
    if strict:
        rendered = _render_strict(template_path, context)
    else:
        rendered = _render(template_path, context)

    # Write output
    _write_text(output_path, rendered)

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render checklist Markdown from YAML")
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to filled YAML (based on controls_design_checklist.template.yaml)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to write rendered Markdown report",
    )
    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE,
        type=Path,
        help=f"Jinja2 Markdown template (default: {DEFAULT_TEMPLATE})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing YAML fields (useful for validating completeness)",
    )

    args = parser.parse_args()

    try:
        output_path = render_checklist(
            input_yaml=args.input,
            output_markdown=args.output,
            template=args.template,
            strict=args.strict,
        )
        print(f"Rendered: {output_path}")
        return 0
    except FileNotFoundError as e:
        raise SystemExit(str(e)) from e


if __name__ == "__main__":
    raise SystemExit(main())
