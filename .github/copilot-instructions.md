# ControlRox AI Coding Guidelines

## Architecture Overview

ControlRox is a PLC management and ladder logic editing toolset built on the [Pyrox framework](https://github.com/iroxusux/Pyrox). It specializes in **Rockwell Automation L5X files** (RSLogix 5000/Studio 5000) with multi-vendor industrial automation support.

### Domain Model

**PLC Object Hierarchy**:
```
Controller (IController)
├── Programs (HasPrograms)
│   └── Routines (HasRoutines)
│       └── Rungs (HasRungs)
│           └── Instructions (HasInstructions)
├── Tags (HasTags)
├── Datatypes
├── Modules (Allen-Bradley, Siemens, etc.)
└── AddOnInstructions (AOIs)
```

All PLC objects inherit from `PlcObject` base class and implement protocol interfaces.

### Key Applications

Located in `controlrox/applications/`:
- **app.py**: Main `App` class extending `ControllerApplication` with treeview navigation
- **plcio.py**: PLC I/O communications manager (pylogix-based)
- **ladder.py**: Visual ladder logic editor task
- **validator.py**: Custom validation rules (Ford/GM standards)
- **generator.py**: Emulation code injection (Emulate3D integration)
- **eplan.py**: EPLAN electrical design validation

### Service Layer

**Key services** (`controlrox/services/`):
- `plc_gui_introspection`: Inspect and display PLC objects in GUI
- `design/`: HTML/Markdown reporting for control design checklists

## Development Workflows

### Installation
```bash
./install.sh  # Installs Pyrox as git dependency + ControlRox deps
```

### Dependencies
- **pyrox**: Core framework (git dependency from main branch)
- **debugpy**: Remote debugging support
- **pypandoc-binary**: Document conversion (markdown → HTML)
- **pyyaml**: YAML processing for design checklists
- **jinja2**: Template rendering for reports

### Key Workflows

**Load L5X file**:
```python
controller = Controller.from_file('path/to/file.L5X')
# Controller auto-parses XML into object hierarchy
```

**Navigate structure**:
```python
for program in controller.programs:
    for routine in program.routines:
        for rung in routine.rungs:
            print(rung.text)  # XML ladder logic text
```

**Save modifications**:
```python
controller.save('output.L5X')  # Writes back to L5X XML format
```

## Critical Patterns

### Protocol-Based Contracts
Use `Has*` protocols for polymorphic access:
```python
def process_programs(obj: HasPrograms):
    for program in obj.programs:
        # Works on Controller or any object with programs
```

### Controller Type Detection
Controllers have vendor-specific types (Ford, GM, etc.):
```python
controller.controller_type  # 'CompactLogix', 'ControlLogix', 'GuardLogix'
controller.is_ford_controller()  # Vendor-specific type checking
```

### Treeview Navigation
`App` class uses command bar for view modes:
```python
self.treeview_commandbar.add_button(
    id='view_programs',
    command=lambda: self._display_common_list_in_treeview(
        item_attr_name='programs',
        tab_to_select=TreeViewMode.PROGRAMS
    )
)
```

### Application Task Pattern
Extend from Pyrox's `IApplicationTask` for modular features:
```python
class LadderEditorApplicationTask(ControllerApplicationTask):
    def inject(self):
        # Add ladder editor to application workspace
    def run(self):
        # Execute ladder editing logic
```

## L5X File Format

Rockwell L5X files are XML-based:
- **Parsed via lxml**: `controller.xml_root` provides ElementTree access
- **Tags**: `<Tag Name="..." DataType="..." />`
- **Routines**: RLL, FBD, SFC, or ST types
- **Rungs**: `<Rung Number="X"><Text>XIC(Tag)OTE(Output);</Text></Rung>`
- **Instructions**: Text representation (e.g., `XIC(Input)`, `OTE(Output)`)

### Common Instructions
- **XIC**: Examine If Closed (normally open contact)
- **XIO**: Examine If Open (normally closed contact)
- **OTE**: Output Energize (coil)
- **JSR**: Jump to Subroutine
- **TON**: Timer On Delay
- **CTU**: Count Up

## File Organization

```
controlrox/
├── applications/          # Main application types
│   ├── app.py            # Primary GUI application
│   ├── plcio.py          # PLC communications
│   ├── ladder.py         # Ladder logic editor task
│   ├── validator.py      # Custom validation logic
│   ├── ford/             # Ford-specific implementations
│   └── gm/               # GM-specific implementations
├── models/
│   ├── plc/              # PLC object models (Controller, Tag, Rung, etc.)
│   │   └── rockwell/     # Rockwell-specific implementations
│   ├── eplan/            # EPLAN data models
│   └── gui/              # GUI-specific models
├── services/
│   ├── plc_gui_introspection.py  # PLC object display logic
│   └── design/           # Design checklist rendering
└── interfaces/
    ├── plc/              # PLC interface contracts
    └── tasks/            # Task interfaces
```

## Testing

Place tests adjacent to implementation:
- `controlrox/applications/test/`
- `controlrox/models/plc/test/`

Use pytest with Pyrox's test infrastructure.

## Vendor-Specific Code

### Ford Integration
- Located in `applications/ford/`
- Custom controller types and emulation injection
- Validation against Ford manufacturing standards

### GM Integration
- Located in `applications/gm/`
- GM-specific controller logic
- Custom validation rules

### Module Support
- **Allen-Bradley**: 1756/1769 series (native)
- **Siemens**: ET200/S7 modules
- **SEW, Turck, Red Lion**: Via introspective module system

## Common Gotchas

1. **L5X Namespace**: Rockwell XML uses namespaces - strip or handle appropriately
2. **Rung Text Format**: Follows specific syntax - don't modify without understanding grammar
3. **Tag Scope**: Tags can be controller-scoped or program-scoped
4. **AOI Definitions**: Add-On Instructions have both definition and instances
5. **Module Configuration**: Requires correct slot/addressing for pylogix communications

## GUI Conventions

- **Treeview**: Left sidebar for controller hierarchy navigation
- **Command Bar**: Top bar with view mode buttons (Properties, Tags, Programs, AOIs, Datatypes)
- **Context Menus**: Right-click menus for object-specific actions
- **Workspace**: Dockable panels via Pyrox workspace management

## PLC Communications

Via `plcio.py` using pylogix:
```python
connection = ControllerConnection(
    parameters=ConnectionParameters(
        Ipv4Address('192.168.1.1'),
        slot=0,
        rpi=500
    )
)
connection.connect()
# Read/write tags to/from physical PLC
```

## Design Checklist Workflow

Located in `services/design/`:
1. **YAML input**: Define control requirements in structured YAML
2. **Jinja2 templates**: Render to markdown
3. **Pandoc conversion**: Generate HTML reports
4. **Example**: See `docs/controls/design/CONTROLS_DESIGN_CHECKLIST.filled.example.yaml`

## Extension Points

1. **New controller type**: Add to `models/plc/` implementing `IController`
2. **New vendor support**: Create module recognizer in `models/plc/modules/`
3. **Custom validation**: Extend `ControllerValidator` and register in factory
4. **New application**: Subclass `ControllerApplication` in `applications/`
5. **Ladder instruction**: Parse in `LogicInstruction` class with proper text handling

## Version Compatibility

- **Python**: 3.13+ required (matches Pyrox)
- **Pyrox**: Tracks main branch via git dependency
- **L5X**: Supports RSLogix 5000 v16-v32, Studio 5000 all versions

## When You See These Imports

```python
from pyrox.models import Application  # Base application framework
from pyrox.services.logging import log  # Logging service
from controlrox.models import Controller  # PLC controller model
from controlrox.interfaces.plc.controller import IController  # Controller contract
```

These indicate you're working with the layered architecture: Pyrox (framework) → ControlRox (domain logic).
