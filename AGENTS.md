# AGENTS.md

This file provides guidelines for agentic coding agents working in the RainingKeysPython repository.

## Build & Development Commands

### Running the Application
```bash
python main.py
```

### Building Executable
```bash
python build.py
```
This creates both release and debug builds:
- `RainingKeysPython.zip` - Release build (no console)
- `RainingKeysPython-debug.zip` - Debug build (with console)

The build script automatically:
1. Cleans previous build artifacts
2. Creates release build with PyInstaller
3. Creates debug build with console enabled
4. Copies config.ini to dist directories
5. Packages both builds into zip files

### Manual PyInstaller Build
```bash
pyinstaller RainingKeysPython.spec
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Project Overview

RainingKeysPython is a high-performance, external rhythm game input visualizer built with:
- **Python 3.10+**
- **PySide6 (Qt)** - GUI and rendering
- **pynput** - Global keyboard monitoring
- **pywin32** - Windows API for transparency/click-through

## Code Style Guidelines

### Imports
- Import standard library modules first
- Import third-party modules second
- Import local modules last
- Use relative imports within the core package (e.g., `from .configuration import AppConfig`)
- Group imports by type with blank lines between sections

```python
import time
from collections import deque

from PySide6.QtWidgets import QWidget
from pynput import keyboard

from .configuration import AppConfig
```

### Type Hints
- Use type hints for function signatures, especially for public methods
- Use dataclasses for configuration objects
- Type hint complex structures with `typing.Dict`, `typing.List`, etc.

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class VisualSettings:
    scroll_speed: int = 800
    bar_color_str: str = "0,255,255,200"
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `BarPool`, `RainingKeysOverlay`)
- **Functions/Methods**: snake_case (e.g., `update_canvas`, `handle_input`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_BARS`, `FADE_START_Y`)
- **Private methods**: Leading underscore (e.g., `_init_key_counts`)
- **Instance variables**: snake_case (e.g., `active_bars`, `config`)

### Class Design
- Use dataclasses for configuration objects
- Use `__slots__` for performance-critical classes with many instances
- Inherit from Qt classes (QWidget, QObject) appropriately
- Use Qt's Signal/Slot pattern for inter-object communication

```python
@dataclass
class AppConfig:
    MAX_BARS: int = 300

class Bar:
    __slots__ = ['lane_index', 'press_time', 'release_time', 'active']
```

### Error Handling
- Use try/except with print statements for debugging (not logging module)
- Provide fallback values for error conditions
- Check for module availability with ImportError handling

```python
try:
    import win32gui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: pywin32 not found.")
```

### Qt/PySide6 Specifics
- Initialize UI in `init_ui()` method
- Use `super().__init__()` for all custom Qt widgets
- Connect signals in constructor or init methods
- Use `blockSignals(True/False)` when programmatically updating UI controls
- Set window flags for overlay: `FramelessWindowHint | WindowStaysOnTopHint | Tool | WindowTransparentForInput`

### Performance Optimization
- Use object pooling for frequently created/destroyed objects (see `BarPool` class)
- Use `deque` for active/inactive object collections
- Cache geometry calculations that don't change frequently
- Use `time.perf_counter()` for high-precision timing

### Configuration Management
- All config flows through `SettingsManager` and `AppConfig` dataclasses
- Settings are persisted to `config.ini` using ConfigParser
- Emit `settings_changed` Signal after any config modifications
- Always save config after changes using `settings.save()`

### Thread Safety
- Input monitoring runs in separate QThread (`InputMonitor`)
- Use Qt Signals for thread communication (key_pressed, key_released)
- Worker objects use `active_keys` set to filter autorepeat events

## Architecture Notes

### Core Components
- `main.py` - Application entry point, initializes all components
- `core/configuration.py` - Dataclasses for all config
- `core/settings_manager.py` - Loads/saves config, emits change signals
- `core/input_mon.py` - Global keyboard hook via pynput in QThread
- `core/overlay.py` - Main rendering window, object pooling, paint logic
- `core/gui.py` - Configuration UI window
- `core/ui/components.py` - UI widget groups
- `core/ui/theme.py` - Dark theme constants

### Key Patterns
1. **Dependency Injection**: Pass `AppConfig` or `SettingsManager` to components
2. **Signal-Slot**: Use Qt signals for loose coupling between components
3. **Object Pooling**: Reuse Bar objects to avoid GC pressure
4. **Configuration Separation**: Data holds values, SettingsManager handles I/O

## Testing

This project currently does not have formal tests configured. When adding tests:
- Consider pytest as the test framework
- Mock Qt components for unit tests
- Test configuration persistence logic
- Verify object pool behavior under load
- Test input filtering (autorepeat prevention)

## File Structure

```
core/
├── __init__.py
├── configuration.py      # Dataclasses for all settings
├── settings_manager.py   # Config persistence, signal emission
├── input_mon.py          # Keyboard hook in QThread
├── overlay.py            # Main rendering window, paint logic
├── gui.py                # Settings UI window
└── ui/
    ├── __init__.py
    ├── theme.py          # Dark theme constants
    └── components.py     # UI widget groups
```

## Platform Notes

- **Windows Only**: Uses pywin32 for click-through transparency
- Python 3.10+ required
- Requires external overlay compatibility with game window
