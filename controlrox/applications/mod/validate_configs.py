"""Configuration validator for module configs.

Validates JSON configuration files against the schema and checks for logical errors.
"""
import json
from pathlib import Path


class ConfigValidator:
    """Validates module configuration files."""

    def __init__(self, schema_path: str):
        """Initialize validator with schema.

        Args:
            schema_path: Path to the JSON schema file
        """
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    def validate_config(self, config_path: Path) -> tuple[bool, list[str]]:
        """Validate a configuration file.

        Args:
            config_path: Path to the config file to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"JSON parse error: {e}"]

        # Check required fields
        required_fields = self.schema.get('required', [])
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate catalog_number
        if 'catalog_number' in config:
            if not isinstance(config['catalog_number'], str) or not config['catalog_number']:
                errors.append("catalog_number must be a non-empty string")

        # Validate class_name
        if 'class_name' in config:
            class_name = config['class_name']
            if not isinstance(class_name, str):
                errors.append("class_name must be a string")
            elif not class_name[0].isupper():
                errors.append("class_name must start with an uppercase letter")
            elif not all(c.isalnum() or c == '_' for c in class_name):
                errors.append("class_name must contain only alphanumeric characters and underscores")

        # Validate controls_type
        valid_controls_types = [
            "SAFETY_INPUT_OUTPUT_BLOCK",
            "SAFETY_INPUT_BLOCK",
            "SAFETY_OUTPUT_BLOCK",
            "SAFETY_BLOCK",
            "POINT_IO",
            "ETHERNET",
            "RACK_COMM_CARD",
            "PLC",
            "DRIVE",
            "HMI"
        ]
        if 'controls_type' in config:
            if config['controls_type'] not in valid_controls_types:
                errors.append(f"Invalid controls_type. Must be one of: {', '.join(valid_controls_types)}")

        # Validate required_imports
        if 'required_imports' in config:
            if not isinstance(config['required_imports'], list):
                errors.append("required_imports must be a list")
            else:
                for i, imp in enumerate(config['required_imports']):
                    if not isinstance(imp, dict):
                        errors.append(f"required_imports[{i}] must be an object")
                        continue
                    if 'path' not in imp:
                        errors.append(f"required_imports[{i}] missing 'path' field")
                    if 'elements' not in imp:
                        errors.append(f"required_imports[{i}] missing 'elements' field")
                    elif not isinstance(imp['elements'], list):
                        errors.append(f"required_imports[{i}].elements must be a list")

        # Validate tags
        if 'tags' in config:
            if not isinstance(config['tags'], list):
                errors.append("tags must be a list")
            else:
                for i, tag in enumerate(config['tags']):
                    if not isinstance(tag, dict):
                        errors.append(f"tags[{i}] must be an object")
                        continue

                    # Must have either name_template or name_method
                    if 'name_template' not in tag and 'name_method' not in tag:
                        errors.append(f"tags[{i}] must have either 'name_template' or 'name_method'")

                    if 'datatype' not in tag:
                        errors.append(f"tags[{i}] missing required 'datatype' field")

                    if 'tag_class' in tag and tag['tag_class'] not in ['Safety', 'Standard']:
                        errors.append(f"tags[{i}].tag_class must be 'Safety' or 'Standard'")

        # Validate rungs
        if 'rungs' in config:
            if not isinstance(config['rungs'], dict):
                errors.append("rungs must be an object")
            else:
                for rung_type in ['safety', 'standard']:
                    if rung_type in config['rungs']:
                        rungs_list = config['rungs'][rung_type]
                        if not isinstance(rungs_list, list):
                            errors.append(f"rungs.{rung_type} must be a list")
                            continue

                        for i, rung in enumerate(rungs_list):
                            if not isinstance(rung, dict):
                                errors.append(f"rungs.{rung_type}[{i}] must be an object")
                                continue
                            if 'text_template' not in rung:
                                errors.append(f"rungs.{rung_type}[{i}] missing 'text_template'")
                            if 'comment' not in rung:
                                errors.append(f"rungs.{rung_type}[{i}] missing 'comment'")

        # Validate tag_name_methods
        if 'tag_name_methods' in config:
            if not isinstance(config['tag_name_methods'], dict):
                errors.append("tag_name_methods must be an object")
            else:
                valid_method_keys = ['safety_input', 'safety_output', 'standard_input', 'standard_output']
                for key in config['tag_name_methods']:
                    if key not in valid_method_keys:
                        errors.append(f"Invalid tag_name_methods key: {key}")

        return len(errors) == 0, errors

    def validate_all(self, config_dir: Path) -> dict[str, tuple[bool, list[str]]]:
        """Validate all config files in a directory.

        Args:
            config_dir: Directory containing config files

        Returns:
            Dictionary mapping config file names to validation results
        """
        results = {}
        for config_file in config_dir.glob('*.json'):
            if config_file.name == 'module_config_schema.json':
                continue

            is_valid, errors = self.validate_config(config_file)
            results[config_file.name] = (is_valid, errors)

        return results


def main():
    """Main entry point for validation."""
    script_dir = Path(__file__).parent
    schema_path = script_dir / 'config' / 'module_config_schema.json'
    config_dir = script_dir / 'config'

    print(f"Schema: {schema_path}")
    print(f"Config directory: {config_dir}")
    print('')

    validator = ConfigValidator(str(schema_path))
    results = validator.validate_all(config_dir)

    all_valid = True
    for config_name, (is_valid, errors) in results.items():
        if is_valid:
            print(f"✓ {config_name}")
        else:
            print(f"✗ {config_name}")
            for error in errors:
                print(f"  - {error}")
            all_valid = False

    print('')
    if all_valid:
        print(f"✓ All {len(results)} configuration(s) are valid")
    else:
        invalid_count = sum(1 for is_valid, _ in results.values() if not is_valid)
        print(f"✗ {invalid_count} configuration(s) have errors")


if __name__ == '__main__':
    main()
