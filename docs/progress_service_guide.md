# ControlRox Progress Service & Loading Bar Integration Guide

This guide explains how to add loading progress indicators to ControlRox operations without coupling your model logic to GUI code.

## Architecture Overview

The solution uses a **Progress Service Pattern** that provides clean separation between:
- **Model Operations**: Report progress without knowing about GUI
- **Progress Service**: Centralized progress tracking and event distribution  
- **GUI Components**: Display progress updates from the service

## Key Components

### 1. ProgressService (`controlrox.services.progress`)
- Singleton service that tracks multiple concurrent operations
- Thread-safe operation management
- Observer pattern for progress updates
- No GUI dependencies

### 2. ProgressBarController & LoadingBarManager (`controlrox.services.progress_gui`)
- Bridges ProgressService to PyroxLoadingBar widgets
- Automatic loading bar updates based on progress events
- Factory methods for common loading scenarios

### 3. Enhanced Controller Loading (`controlrox.services.plc`)
- Modified `load_controller_from_file_location()` with optional progress reporting
- Step-by-step progress tracking through L5X parsing and object creation

## Basic Usage

### Adding Progress to Model Operations

```python
from controlrox.services.progress import ProgressService

def your_model_operation():
    # Start tracking progress
    progress_service = ProgressService.get_instance()
    progress = progress_service.start_operation(
        "my_operation",
        "Starting operation...",
        total_steps=3  # Optional: enables automatic step-based progress
    )
    
    try:
        # Step 1
        progress.next_step("Loading data...")
        # ... do work ...
        
        # Step 2  
        progress.next_step("Processing...")
        # ... do work ...
        
        # Manual progress updates
        progress.update(75.0, "Almost finished...")
        # ... do work ...
        
        # Complete
        progress.complete("Operation finished successfully!")
        
    except Exception as e:
        progress.error(f"Operation failed: {e}")
        raise
```

### Displaying Progress in GUI

#### Option 1: Popup Loading Window
```python
from controlrox.services.progress_gui import show_controller_loading_progress

# Show loading window for controller operations
window, controller = show_controller_loading_progress(parent=main_window)

# Your model operation runs and reports progress automatically
# Window will auto-close when operation completes

# Clean up
controller.disconnect()
window.destroy()
```

#### Option 2: Embedded Loading Bar
```python
from controlrox.services.progress_gui import LoadingBarManager

# Create embedded loading bar
progress_controller = LoadingBarManager.create_embedded_progress_bar(
    parent_widget,
    operation_id="my_operation"  # Filter for specific operation
)

# The bar will automatically update when operations with matching ID report progress
```

#### Option 3: Generic Loading Window
```python
from controlrox.services.progress_gui import LoadingBarManager

window, controller = LoadingBarManager.create_progress_window(
    title="Processing...",
    operation_id=None,  # Show all operations
    parent=main_window
)
```

## Advanced Usage

### Multiple Concurrent Operations
```python
# The service automatically handles multiple operations
progress1 = ProgressService.get_instance().start_operation("task_1", "Task 1...")  
progress2 = ProgressService.get_instance().start_operation("task_2", "Task 2...")

# Each reports progress independently
progress1.update(50.0, "Task 1 halfway done")
progress2.update(25.0, "Task 2 quarter done")
```

### Custom Progress Updates
```python
progress = ProgressService.get_instance().start_operation("custom_op", "Starting...")

# Update with metadata
progress.update(
    progress=30.0,
    message="Processing items...",
    current_step="Validating data",
    metadata={"items_processed": 150, "total_items": 500}
)
```

### Error Handling
```python
try:
    # ... operation code ...
    progress.complete("Success!")
except Exception as e:
    progress.error(
        f"Operation failed: {e}",
        metadata={"error_type": type(e).__name__, "retry_possible": True}
    )
```

## Integration Examples

### Existing Controller Loading
The controller loading has already been enhanced:

```python
# In controlrox.applications.app.App.load_controller()
from controlrox.services.progress_gui import show_controller_loading_progress

def load_controller(self, file_location):
    # Show progress window
    progress_window, progress_controller = show_controller_loading_progress(
        parent=self.root_window.get_window()
    )
    
    try:
        # This now reports progress automatically
        controller = load_controller_from_file_location(file_location, report_progress=True)
        self.controller = controller
    finally:
        progress_controller.disconnect()
        progress_window.destroy()
```

### Adding Progress to Import Operations
```python
def import_assets_with_progress(self, file_location, asset_types):
    progress = ProgressService.get_instance().start_operation(
        "import_assets",
        f"Importing from {Path(file_location).name}...",
        total_steps=len(asset_types)
    )
    
    try:
        for i, asset_type in enumerate(asset_types):
            progress.next_step(f"Importing {asset_type}...")
            self.import_specific_asset_type(asset_type, file_location)
            
        progress.complete("All assets imported successfully!")
        
    except Exception as e:
        progress.error(f"Import failed: {e}")
        raise
```

## Customization

### Custom Loading Bar Appearance
```python
from pyrox.models.gui.loadingbar import LoadingConfig, LoadingMode

config = LoadingConfig(
    mode=LoadingMode.DETERMINATE,
    show_percentage=True,
    show_text=True,
    show_time=True,
    animate=True,
    color_scheme='success',  # 'default', 'success', 'warning', 'error', 'info'
    height=30,
    gradient=True,
    striped=True
)

window, controller = LoadingBarManager.create_progress_window(
    title="Custom Loading...",
    config=config,
    parent=main_window
)
```

### Custom Progress Callbacks
```python
def on_progress_update(update):
    print(f"Operation {update.operation_id}: {update.progress:.1f}% - {update.message}")
    
    if update.status == ProgressStatus.COMPLETED:
        print("✓ Operation completed!")
    elif update.status == ProgressStatus.ERROR:
        print("✗ Operation failed!")

# Subscribe to all progress updates
ProgressService.get_instance().subscribe(on_progress_update)
```

## Benefits of This Approach

1. **Clean Separation**: Models don't know about GUI, GUI doesn't know about model internals
2. **Reusable**: Same progress service works with any GUI framework  
3. **Flexible**: Support for determinate/indeterminate progress, multiple concurrent operations
4. **Consistent**: Uniform progress reporting across the application
5. **Testable**: Easy to test models without GUI dependencies
6. **Extensible**: Easy to add progress to existing operations

## Migration Guide

To add progress to an existing operation:

1. **Add progress reporting to your model method:**
   ```python
   # Before
   def load_data(self):
       # ... existing code ...
   
   # After  
   def load_data(self, report_progress=False):
       progress = None
       if report_progress:
           progress = ProgressService.get_instance().start_operation("load_data", "Loading...")
       
       try:
           # ... existing code with progress.update() calls ...
           if progress:
               progress.complete("Data loaded!")
       except Exception as e:
           if progress:
               progress.error(f"Failed: {e}")
           raise
   ```

2. **Update GUI calls to show progress:**
   ```python
   # Before
   def on_load_button_click(self):
       self.model.load_data()
   
   # After
   def on_load_button_click(self):
       window, controller = show_generic_loading_progress("Loading Data...", self.root)
       try:
           self.model.load_data(report_progress=True)
       finally:
           controller.disconnect()
           window.destroy()
   ```

## Running the Demo

A comprehensive demo is provided in `demo_progress.py`:

```bash
python demo_progress.py
```

This shows examples of:
- Controller loading progress
- Multi-step operations  
- Indeterminate progress
- Embedded progress bars
- Multiple concurrent operations
- Error handling

The demo provides a complete working example you can use as a reference for implementing progress in your own operations.