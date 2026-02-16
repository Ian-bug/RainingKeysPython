# Release Notes - Version 1.3.5

## Bug Fixes
- Fixed `NameError: name 'layout' is not defined` in LaneSettingsGroup
  - Moved `self.setLayout(layout)` from `update_from_config()` to `init_ui()` in core/ui/components.py:136

## UI Improvements
- Increased settings window default size to 400×670 (was 340×500)

## Configuration Updates
- Updated default configuration to match current config.ini values:
  - Added `fall_direction` setting with default value "up"
  - KeyViewer now enabled by default (was disabled)
  - Default lane keys set to d, f, j, k
  - SettingsManager now persists fall_direction setting
  - Debug mode disabled by default (production-ready)

## Technical Details
- Added `__post_init__` method to AppConfig for default lane initialization
- Improved settings persistence logic in SettingsManager

## Files Changed
- core/configuration.py - Updated defaults and added __post_init__
- core/settings_manager.py - Added fall_direction load/save support
- core/gui.py - Increased window size
- core/ui/components.py - Fixed layout initialization bug

## Build Artifacts
- RainingKeysPython.zip - Release build (no console)
- RainingKeysPython-debug.zip - Debug build (with console)
