# ControlRox

<div align="center">

**A comprehensive Python-based ladder logic editor and PLC management toolset**

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/iroxusux/ControlRox)
![Version](https://img.shields.io/badge/version-2.3.013-blue.svg)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Architecture](#%EF%B8%8F-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Architecture](#%EF%B8%8F-architecture)
- [Project Structure](#-project-structure)
- [Usage Examples](#-usage-examples)
- [Testing](#-testing)
- [Development](#%EF%B8%8F-development)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**ControlRox** is a professional-grade toolset designed for controls engineers working with programmable logic controllers (PLCs). Built on the robust [Pyrox framework](https://github.com/iroxusux/Pyrox), ControlRox provides powerful capabilities for:

- **Loading, editing, and managing Rockwell Automation L5X files**
- **Visual ladder logic editing** with an intuitive GUI interface
- **Controller type detection** using intelligent pattern-matching algorithms
- **Multi-vendor support** for industrial automation equipment (Allen-Bradley, Siemens, SEW, Turck, Red Lion)
- **Project validation** for end customer logic manufacturing standards
- **EPLAN integration** for electrical design validation
- **Emulation Injection** for quick assembly and disassembly of code to emulate projects with Emulate3D

**Perfect for:**

- Controls Engineers managing large automation projects
- System Integrators working with multiple PLC platforms
- Manufacturing Engineers validating control systems
- Automation Developers building custom tooling

---

## ✨ Features

### 🔧 Core Capabilities

#### **PLC File Management**

- ✅ Load and parse Rockwell Automation `.L5X` files (RSLogix 5000/Studio 5000)
- ✅ Save modified controllers back to `.L5X` format
- ✅ Automatic controller type detection (CompactLogix, ControlLogix, GuardLogix)
- ✅ Vendor-specific controller matching (Ford, GM, etc)

#### **Ladder Logic Editor**

- ✅ Visual ladder logic editing interface
- ✅ Rung creation, modification, and deletion
- ✅ Instruction browsing (XIC, XIO, OTE, JSR, etc.)
- ✅ Context-aware right-click menus
- ✅ Real-time instruction validation

#### **Program Analysis**

- ✅ Tag inspection and management
- ✅ Datatype browsing with member details
- ✅ Program and routine navigation
- ✅ Add-On Instruction (AOI) support
- ✅ Module configuration viewing

#### **GUI Features**

- ✅ Modern Tkinter-based interface
- ✅ Treeview navigation for controller objects
- ✅ Command bar for quick access to common operations
- ✅ Workspace management with dockable panels
- ✅ Status bar with real-time feedback

### 🏭 Industry-Specific Tools

#### **Manufacturing Standards Support**

- **Ford**: Custom controller validation and emulation injection with Ford-specific types
- **GM**: Custom controller validation and emulation injection with GM-specific types

#### **Module Management**

- **Allen-Bradley**: Native support for all 1756/1769 modules
- **Siemens**: ET200 and S7 module integration
- **SEW**: Drive module configuration (MOVIMOT, MOVIDRIVE)
- **Turck**: I/O module support with tag generation
- **Red Lion**: HMI and communication module support

#### **EPLAN Integration**

- Project file parsing (`.epj` format)
- Device validation against controller configuration
- Cross-reference checking between electrical design and PLC program

---

## 📦 Installation

### Prerequisites

- **Python 3.13+** (Required)
- **Pyrox Framework** (Included as dependency)
- **Windows OS** (Primary support; Linux/macOS experimental)

### Option 1: Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/iroxusux/ControlRox.git
cd ControlRox

# Run the installation script
./install.sh

# Or manually install
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -e .
```

### Option 2: Install from Local Directory

```bash
# Install dependencies
pip install pyrox debugpy

# Install ControlRox in development mode
pip install -e path/to/ControlRox
```

### Verify Installation

```bash
# Test the installation
python -c "import controlrox; print(controlrox.__version__)"

# Run the application
python -m controlrox
```

---

## 🚀 Quick Start

### Basic Usage

```python
from controlrox.applications import App

# Launch the ControlRox application
app = App()
app.start()
```

### Load and Inspect a Controller

```python
from controlrox.services import ControllerInstanceManager

# Load a controller from an L5X file
controller = ControllerInstanceManager.load_controller_from_file_location(
    'path/to/controller.L5X'
)

# Access controller properties
print(f"Controller Name: {controller.name}")
print(f"Controller Type: {controller.processor_type}")
print(f"Number of Programs: {len(controller.programs)}")

# Browse tags
for tag in controller.tags:
    print(f"Tag: {tag.name}, Type: {tag.datatype}")
```

### Create and Modify Ladder Logic

```python
from controlrox.models import Routine

# Get a routine from a program
program = controller.programs['MainProgram']
routine = program.routines['MainRoutine']

# Access rungs
for rung in routine.rungs:
    print(f"Rung {rung.number}: {rung.text}")

# Get instructions
instructions = routine.get_instructions('XIC')  # Get all XIC instructions
print(f"Found {len(instructions)} XIC instructions")
```

### Controller Type Detection

```python
from controlrox.services.plc import ControllerFactory

# Automatically detect controller type from L5X data
controller_data = {...}  # Parsed L5X data
best_match = ControllerFactory.get_best_match(controller_data)
print(f"Detected controller type: {best_match.__name__}")

# Create controller instance
controller = ControllerFactory.create_controller(
    controller_data,
    file_location='path/to/controller.L5X'
)
```

---

## 🏗️ Architecture

ControlRox follows a clean, layered architecture built on SOLID principles:

```python
┌─────────────────────────────────────────┐
│         Applications Layer              │
│  (GUI, Task Management, Workflows)      │
├─────────────────────────────────────────┤
│           Services Layer                │
│  (Business Logic, File I/O, Matching)   │
├─────────────────────────────────────────┤
│            Models Layer                 │
│  (PLC Objects, Data Structures)         │
├─────────────────────────────────────────┤
│          Interfaces Layer               │
│  (Abstract Protocols, Type Definitions) │
└─────────────────────────────────────────┘
```

### Key Design Patterns

#### **Factory Pattern**

Intelligent controller type detection using scoring-based matching:

```python
class ControllerMatcher:
    @classmethod
    def calculate_score(cls, controller_data: dict) -> float:
        """Score based on datatypes, modules, programs, tags"""
        score = 0.0
        score += 0.2 if cls.check_controller_datatypes(controller_data) else 0
        score += 0.2 if cls.check_controller_modules(controller_data) else 0
        # ... more checks
        return score
```

#### **Singleton Pattern**

Centralized controller state management:

```python
class ControllerInstanceManager:
    _controller: Optional[IController] = None
    _lock = threading.Lock()
    
    @classmethod
    def get_controller(cls) -> Optional[IController]:
        return cls._controller
```

#### **Observer Pattern**

Event-driven GUI updates:

```python
self.controller_treeview.subscribe_to_selection(
    self._handle_treeview_selection
)
```

#### **Strategy Pattern**

Pluggable controller matchers for different vendors:

```python
class FordControllerMatcher(ControllerMatcher):
    @staticmethod
    def get_datatype_patterns() -> list[str]:
        return ['Fudc_*', 'Fudf_*', 'Fudh_*']
```

---

## 📁 Project Structure

```bash
ControlRox/
├── controlrox/                 # Main package
│   ├── __init__.py
│   ├── __main__.py            # Entry point
│   │
│   ├── applications/          # Application layer
│   │   ├── app.py            # Main GUI application
│   │   ├── constants.py      # Application constants
│   │   ├── ladder.py         # Ladder logic editor
│   │   ├── ford/             # Ford-specific applications
│   │   ├── gm/               # GM-specific applications
│   │   ├── default/          # default applications
│   │   └── mod/              # Module vendor applications
│   │       ├── ab/           # Allen-Bradley modules
│   │       ├── siemens/      # Siemens modules
│   │       ├── sew/          # SEW drive modules
│   │       ├── turck/        # Turck I/O modules
│   │       └── redlion/      # Red Lion modules
│   │
│   ├── interfaces/            # Interface definitions
│   │   └── plc/              # PLC-related interfaces
│   │       ├── controller.py # IController interface
│   │       ├── datatype.py   # IDatatype interface
│   │       ├── tag.py        # ITag interface
│   │       └── ...
│   │
│   ├── models/                # Data models
│   │   ├── eplan/            # EPLAN project models
│   │   ├── gui/              # GUI component models
│   │   ├── plc/              # PLC object models
│   │   │   ├── controller.py
│   │   │   ├── datatype.py
│   │   │   ├── instruction.py
│   │   │   ├── program.py
│   │   │   ├── routine.py
│   │   │   ├── rung.py
│   │   │   ├── tag.py
│   │   │   └── rockwell/    # Rockwell-specific implementations
│   │   └── tasks/           # Task models
│   │
│   ├── services/             # Business logic
│   │   ├── plc/             # PLC services
│   │   │   ├── controller.py  # Controller management
│   │   │   ├── datatype.py    # Datatype factory
│   │   │   ├── instruction.py # Instruction factory
│   │   │   ├── emu/           # Emulation services
│   │   │   └── ...
│   │   ├── l5x.py           # L5X file parsing
│   │   ├── checklist.py     # Validation checklists
│   │   └── debug.py         # Debug utilities
│   │
│   ├── tasks/                # Application tasks
│   │   ├── builtin/         # Built-in tasks
│   │   └── tools/           # Tool tasks
│   │
│   └── ui/                   # UI assets
│       ├── icons/           # Application icons
│       └── splash/          # Splash screen images
│
├── docs/                     # Documentation
│   ├── controls/            # Example L5X files
│   └── progress_service_guide.md
│
├── hooks/                    # Git hooks
│   └── pre-commit
│
├── utils/                    # Utility scripts
│   ├── check_version_increment.py
│   ├── setup_hooks.py
│   ├── sync_readme.py
│   └── utils.sh
│
├── pyproject.toml           # Project configuration
├── LICENSE                  # MIT License
├── README.md               # This file
└── install.sh              # Installation script
```

---

## 💡 Usage Examples

### Example 1: Batch Process Controllers

```python
from pathlib import Path
from controlrox.services import ControllerInstanceManager

# Process multiple L5X files
l5x_files = Path('controllers/').glob('*.L5X')

for file in l5x_files:
    controller = ControllerInstanceManager.load_controller_from_file_location(file)
    
    if controller:
        print(f"Processing: {controller.name}")
        
        # Perform operations
        tag_count = len(controller.tags)
        program_count = len(controller.programs)
        
        print(f"  Tags: {tag_count}, Programs: {program_count}")
```

### Example 2: Find All JSR Instructions

```python
# Find all Jump to Subroutine instructions
for program in controller.programs:
    for routine in program.routines:
        jsr_instructions = routine.get_instructions('JSR')
        
        for jsr in jsr_instructions:
            target_routine = jsr.operands[0]
            print(f"JSR to {target_routine} in {routine.name}")
```

### Example 3: Validate Controller Against EPLAN

```python
from controlrox.models.eplan import EplanProject

# Load EPLAN project
eplan = EplanProject(file_location='project.epj')

# Load controller
controller = ControllerInstanceManager.load_controller_from_file_location('controller.L5X')

# Validate devices match
for device in eplan.devices:
    matching_module = None
    for module in controller.modules:
        if device.article_number == module.catalog_number:
            matching_module = module
            break
    
    if matching_module:
        print(f"✓ {device.name} matches {matching_module.name}")
    else:
        print(f"✗ {device.name} not found in controller")
```

### Example 4: Custom Controller Matcher

```python
from controlrox.services.plc import ControllerMatcher

class CustomPlantMatcher(ControllerMatcher):
    """Custom matcher for plant-specific controllers."""
    
    @staticmethod
    def get_datatype_patterns() -> list[str]:
        return ['Plant_*', 'Custom_*']
    
    @staticmethod
    def get_module_patterns() -> list[str]:
        return ['Plant_IO_*']
    
    @staticmethod
    def get_program_patterns() -> list[str]:
        return ['PlantControl', 'PlantSafety']
    
    @staticmethod
    def get_safety_program_patterns() -> list[str]:
        return ['PlantSafety_*']
    
    @staticmethod
    def get_tag_patterns() -> list[str]:
        return ['Plant_*']
    
    @classmethod
    def get_controller_constructor(cls):
        return CustomPlantController

# The matcher auto-registers and will be used for scoring
```

---

## 🧪 Testing

ControlRox includes comprehensive test coverage across all modules.

### Run All Tests

```bash
# Using pytest
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=controlrox --cov-report=html
```

### Run Specific Tests

```bash
# Test a specific module
pytest controlrox/services/plc/test/test_controller.py

# Test a specific class
pytest controlrox/models/plc/test/test_datatype.py::TestRaDatatype

# Test a specific method
pytest controlrox/models/plc/test/test_routine.py::TestRaRoutine::test_compile_rungs
```

### Test Structure

```bash
controlrox/
├── applications/test/       # Application layer tests
├── models/
│   ├── plc/test/           # PLC model tests
│   ├── eplan/test/         # EPLAN model tests
│   └── tasks/test/         # Task model tests
└── services/
    ├── plc/test/           # PLC service tests
    └── test/               # General service tests
```

---

## 🛠️ Development

### Development Setup

```bash
# Clone with submodules (if Pyrox is a submodule)
git clone --recurse-submodules https://github.com/iroxusux/ControlRox.git

# Create development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
python utils/setup_hooks.py
```

### Code Style

- **Python 3.13+** type hints required
- **PEP 8** style guidelines
- **Docstrings** for all public methods (Google style)
- **Type checking** with mypy (when available)

### Pre-commit Hooks

```bash
# Hooks automatically:
# - Check version increment
# - Sync README
# - Validate imports
# - Run linting
```

### Adding a New Controller Matcher

1. Create matcher class in `applications/[vendor]/plc/matcher.py`
2. Implement pattern methods
3. Auto-registration via `FactoryTypeMeta` metaclass
4. Add tests in `applications/[vendor]/test/`

```python
class NewVendorMatcher(ControllerMatcher):
    @staticmethod
    def get_datatype_patterns() -> list[str]:
        return ['Vendor_*']
    
    @classmethod
    def get_controller_constructor(cls):
        return NewVendorController
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Reporting Issues

- Use the [GitHub Issues](https://github.com/iroxusux/ControlRox/issues) page
- Include Python version, OS, and steps to reproduce
- Provide sample L5X files (if applicable and non-confidential)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Message Convention

```bash
feat: Add support for new module type
fix: Resolve tag parsing issue
docs: Update installation instructions
test: Add tests for controller matching
refactor: Improve error handling
```

---

## 📚 Documentation

### Additional Resources

- **[Pyrox Framework Documentation](https://github.com/iroxusux/Pyrox)** - Core framework
- **[Progress Service Guide](docs/progress_service_guide.md)** - Progress tracking implementation
- **API Documentation** - (Coming soon)
- **Tutorial Videos** - (Coming soon)

### Related Projects

- **[Pyrox](https://github.com/iroxusux/Pyrox)** - Core application framework
- **[RSLogix L5X Documentation](https://literature.rockwellautomation.com/)** - Rockwell file format specs

---

## 🙏 Acknowledgments

- **Pyrox Framework** for providing the robust application foundation
- **Rockwell Automation** for L5X file format documentation
- All contributors and controls engineers who provided feedback

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```bash
MIT License

Copyright (c) 2025 Brian LaFond

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 📧 Contact

**Brian LaFond**

- Email: [Brian.L.LaFond@Gmail.com](Brian.L.LaFond@gmail.com)
- GitHub: [@iroxusux](https://github.com/iroxusux)
- Project Link: [https://github.com/iroxusux/ControlRox](https://github.com/iroxusux/ControlRox)

---

## 🗺️ Roadmap

### Current Version: 2.2.007 (Beta)

### Upcoming Features

- [ ] **Enhanced Ladder Logic Editor**
  - Drag-and-drop instruction placement
  - Inline rung editing
  - Instruction palette

- [ ] **Advanced Search & Replace**
  - Cross-project tag search
  - Batch tag renaming
  - Instruction pattern matching

- [ ] **Export Capabilities**
  - PDF reports of programs
  - Excel tag documentation
  - HTML documentation generation

- [ ] **Additional Vendor Support**
  - Schneider Electric support
  - ABB controller support
  - Mitsubishi PLC support

- [ ] **Cloud Integration**
  - Version control integration
  - Collaborative editing
  - Cloud backup

---

<div align="center">

**Built with ❤️ for Controls Engineers**

⭐ Star this repo if you find it helpful!

</div>
