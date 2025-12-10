# Module Configuration System

This system provides a hybrid approach to defining introspective PLC modules using JSON configuration files that generate Python classes.

## Overview

Instead of manually writing Python classes for each module type, you can now:
1. Define modules in simple JSON configuration files
2. Validate the configurations
3. Generate Python classes automatically
4. Use the generated modules with the existing factory system

## Directory Structure

```
controlrox/applications/mod/
├── config/                          # JSON configuration files
│   ├── module_config_schema.json   # JSON schema definition
│   ├── ab_1732es_ib8xobv4.json    # Example: Simple module config
│   ├── ab_1734ib8s.json           # Example: Complex module with tags/rungs
│   └── ab_1734_aent.json          # Example: Ethernet module
├── generated/                       # Auto-generated Python classes
│   ├── __init__.py                 # Auto-generated exports
│   ├── ab_1732es_ib8xobv4.py
│   ├── ab_1734ib8s.py
│   └── ab_1734aent.py
├── generate_modules.py              # Generator script
└── validate_configs.py              # Configuration validator
```

## Quick Start

### 1. Create a Module Configuration

Create a new JSON file in `config/` directory:

**Simple Example** (`config/my_module.json`):
```json
{
  "catalog_number": "1756-EN2T",
  "class_name": "AB_1756EN2T",
  "parent_class": "AllenBradleyModule",
  "controls_type": "ETHERNET",
  "metadata": {
    "vendor": "Allen Bradley",
    "description": "1756-EN2T Ethernet Communication Module"
  }
}
```

**Complex Example with Tags and Rungs**:
```json
{
  "catalog_number": "1734-IB8S",
  "class_name": "AB_1734IB8S",
  "parent_class": "AllenBradleyGenericSafetyBlock",
  "controls_type": "SAFETY_INPUT_BLOCK",
  "required_imports": [
    {
      "path": "docs\\controls\\emu\\Demo3D_HMI_IN_DataType.L5X",
      "elements": ["DataTypes"]
    }
  ],
  "tag_name_methods": {
    "safety_input": "sz_Demo3D_{module.parent_module}_I",
    "standard_input": "zz_Demo3D_{module.parent_module}_I"
  },
  "tags": [
    {
      "name_method": "get_safety_input_tag_name",
      "datatype": "Demo3D_HMI_IN",
      "tag_class": "Safety",
      "description": "Safety input tag"
    }
  ],
  "rungs": {
    "safety": [
      {
        "text_template": "COP(sz_Demo3D_{module.parent_module}_I,{module.parent_module}:1:I,1);",
        "comment": "Copy input data to safety card"
      }
    ]
  }
}
```

### 2. Validate Configuration

```bash
python validate_configs.py
```

Output:
```
✓ ab_1732es_ib16.json
✓ ab_1734ib8s.json
✓ my_module.json

✓ All 3 configuration(s) are valid
```

### 3. Generate Modules

```bash
python generate_modules.py
```

Output:
```
Generating modules...
✓ Generated: generated\ab_1732es_ib16.py
✓ Generated: generated\ab_1734ib8s.py
✓ Generated: generated\my_module.py

✓ Generated: generated\__init__.py
✓ Successfully generated 3 module(s)
```

### 4. Use Generated Modules

```python
from controlrox.applications.mod.generated import AB_1756EN2T

# The generated class works exactly like hand-written classes
module = AB_1756EN2T.create_from_module(base_module)
print(module.catalog_number)  # "1756-EN2T"
print(module.controls_type)   # ModuleControlsType.ETHERNET
```

## Configuration Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `catalog_number` | string | Module catalog number (e.g., "1732ES-IB8XOBV4") |
| `class_name` | string | Python class name to generate (must start with uppercase) |
| `controls_type` | enum | Type of controls (see Control Types below) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `parent_class` | string | Parent class to inherit from (default: "AllenBradleyModule") |
| `required_imports` | array | List of L5X files to import datatypes from |
| `tags` | array | Required tags for this module |
| `tag_name_methods` | object | Templates for tag name getter methods |
| `rungs` | object | Safety and standard program rungs |
| `connection_points` | object | Input/output/config connection points |
| `connection_sizes` | object | Connection sizes in bytes |
| `metadata` | object | Additional metadata (vendor, description, etc.) |

### Control Types

- `SAFETY_INPUT_OUTPUT_BLOCK`
- `SAFETY_INPUT_BLOCK`
- `SAFETY_OUTPUT_BLOCK`
- `SAFETY_BLOCK`
- `POINT_IO`
- `ETHERNET`
- `RACK_COMM_CARD`
- `PLC`
- `DRIVE`
- `HMI`

### Template Variables

Use these placeholders in `text_template` and `name_template` fields:

| Variable | Description | Example |
|----------|-------------|---------|
| `{module.name}` | Module instance name | "Local_IB8" |
| `{module.parent_module}` | Parent module name | "Local" |
| `{controller.process_name}` | Controller process name | "Paint" |

## Parent Classes

Choose the appropriate parent class based on your module type:

| Parent Class | Use For |
|--------------|---------|
| `AllenBradleyModule` | Basic Allen Bradley modules |
| `AllenBradleyGenericSafetyBlock` | Safety modules with common safety logic |
| `AB_1732Es` | 1732ES series safety blocks |

## Advanced Features

### Custom Tag Name Methods

Define reusable tag name templates:

```json
{
  "tag_name_methods": {
    "safety_input": "sz_Demo3D_{module.parent_module}_I",
    "standard_output": "zz_Demo3D_{module.name}_O"
  }
}
```

Then reference them in tags:

```json
{
  "tags": [
    {
      "name_method": "get_safety_input_tag_name",
      "datatype": "Demo3D_HMI_IN"
    }
  ]
}
```

### Required Imports

Specify L5X files to import datatypes from:

```json
{
  "required_imports": [
    {
      "path": "docs\\controls\\emu\\Demo3D_WDint_DataType.L5X",
      "elements": ["DataTypes"]
    }
  ]
}
```

### Safety and Standard Rungs

Define ladder logic rungs for safety and standard programs:

```json
{
  "rungs": {
    "safety": [
      {
        "text_template": "COP(sz_Input,{module.name}:I,1);",
        "comment": "Copy input data"
      }
    ],
    "standard": [
      {
        "text_template": "COP({module.name}:O,zz_Output,1);",
        "comment": "Copy output data"
      }
    ]
  }
}
```

## Benefits of This Approach

### ✅ Advantages

1. **Type Safety** - Generated classes are real Python with full type hints
2. **IDE Support** - Full autocomplete and IntelliSense
3. **Version Control** - Both configs and generated code can be tracked
4. **UI-Friendly** - JSON configs are easy to edit programmatically
5. **Validation** - Configs are validated before generation
6. **Flexibility** - Can still hand-write complex modules when needed
7. **Factory Compatible** - Generated classes work with existing metaclass registration

### 🎯 Use Cases

- **UI Module Creator** - Build a GUI to edit JSON configs
- **Batch Creation** - Define many similar modules quickly
- **Standardization** - Ensure consistent module definitions
- **Documentation** - JSON configs are self-documenting
- **Migration** - Gradually migrate existing hand-written modules

## Workflow Integration

### Option 1: Manual Workflow

1. Edit JSON config files manually
2. Run `validate_configs.py`
3. Run `generate_modules.py`
4. Import from `generated` package

### Option 2: Build Integration

Add to your build process:

```bash
# In your build script
python validate_configs.py || exit 1
python generate_modules.py
```

### Option 3: Watch Mode (Future)

Create a file watcher that auto-regenerates on config changes:

```python
# Future enhancement
python watch_and_generate.py  # Auto-regenerates on JSON changes
```

### Option 4: UI Integration

Build a GUI that:
1. Loads JSON configs
2. Provides forms for editing
3. Validates on save
4. Auto-regenerates Python classes

## Migrating Existing Modules

To convert an existing hand-written module to config-driven:

1. **Create JSON config** with the same properties
2. **Generate the class** using `generate_modules.py`
3. **Compare** generated vs. hand-written code
4. **Test** to ensure behavior is identical
5. **Switch imports** to use generated version
6. **Delete** old hand-written file (or keep as reference)

Example migration:

```python
# Old import
from controlrox.applications.mod.ab import AB_1734IB8S

# New import
from controlrox.applications.mod.generated import AB_1734IB8S
```

## Troubleshooting

### Validation Errors

If validation fails:
1. Check the error message for specific field
2. Refer to `module_config_schema.json` for field requirements
3. Check examples in `config/` directory
4. Ensure all required fields are present

### Generation Errors

If generation fails:
1. Run validation first to catch config errors
2. Check that parent class imports are correct
3. Verify template variables are valid
4. Check for syntax errors in templates

### Runtime Errors

If generated modules don't work:
1. Verify parent class is correct
2. Check that template variables resolve correctly
3. Ensure controller/module properties exist
4. Compare with working hand-written modules

## Future Enhancements

Potential improvements to this system:

- [ ] JSON Schema validation using `jsonschema` library
- [ ] GUI config editor with forms
- [ ] Watch mode for auto-regeneration
- [ ] Config inheritance (module extends another config)
- [ ] Macro expansion for common patterns
- [ ] Export existing modules to JSON configs
- [ ] Unit test generation for modules
- [ ] Visual studio code extension for editing configs

## Examples

See the `config/` directory for working examples:

- **ab_1734_aent.json** - Simple Ethernet module
- **ab_1732es_ib16.json** - Safety block inheriting from AB_1732Es
- **ab_1734ib8s.json** - Complex module with tags, rungs, and imports

## Support

For issues or questions:
1. Check this README
2. Review example configs in `config/`
3. Examine generated code in `generated/`
4. Compare with hand-written modules in `ab.py`
