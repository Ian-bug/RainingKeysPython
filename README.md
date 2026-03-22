# RainingKeys (Python)

![License](https://img.shields.io/github/license/Ian-bug/RainingKeysPython?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/Ian-bug/RainingKeysPython/Code%20Quality?style=for-the-badge)
![Release](https://img.shields.io/github/v/release/Ian-bug/RainingKeysPython?style=for-the-badge)

A high-performance, external rhythm game input visualizer.

RainingKeys is a purely external overlay application that visualizes keyboard inputs as falling bars, similar to "Rain" mode found in various rhythm game mods. It provides visual feedback on rhythm stability, micro-jitter, and input timing without injecting code into game process.

> This project is a standalone external tool. It is NOT a game mod and does NOT perform DLL injection or memory hooking. It is safe to use with anti-cheat software that permits external overlays.

---

## Features

- External overlay with transparent, always-on-top, click-through window
- Graphic interface for live configuration
- Configurable X/Y overlay positioning
- Supports both Down (Classic) and Up (Reverse) fall directions
- High-resolution monotonic clocks for smooth animation
- Configurable key-to-lane mapping (e.g., WASD, Space, Enter)
- Visual keyboard representation showing key presses and counts
- Adjustable opacity for inactive keys
- Customizable RGBA colors and overlay speed
- Long press support with variable-length bars
- Performance optimized with object pooling and efficient rendering

## Tech Stack

- Python 3.10+
- PySide6 (Qt) for high-performance rendering and window management
- pynput for global low-level keyboard hook
- pywin32 for Windows API integration

## Project Structure

```
RainingKeysPython/
├── core/
│   ├── configuration.py    # Dataclasses for application configuration
│   ├── gui.py              # Configuration Window GUI
│   ├── input_mon.py        # Global input listener (thread-safe)
│   ├── logging_config.py   # Logging configuration
│   ├── overlay.py          # Main rendering loop and window logic
│   ├── settings_manager.py # Handles config loading/saving (atomic writes, migration)
│   └── ui/
│       ├── components.py     # Reusable UI components
│       └── theme.py         # Theme definitions
├── .github/
│   ├── workflows/
│   │   ├── ci.yml           # Code quality validation (Windows)
│   │   └── release.yml     # Automated releases with git-cliff
│   ├── scripts/
│   │   ├── syntax_check.py      # Python syntax validation
│   │   ├── type_check.py        # Type hints validation
│   │   ├── config_validation.py  # Configuration validation
│   │   └── monitor_ci.py       # CI monitoring script
│   └── README.md             # Workflow documentation
├── cliff.toml               # Git-cliff configuration for changelog generation
├── run_local_ci.py          # Local CI runner script
├── build.py                 # Build script for creating standalone executable
├── main.py                  # Application entry point
└── requirements.txt           # Dependencies
```

## Installation

1. Ensure you have Python 3.10 or newer installed
2. Clone repository or download source
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Optional: Build Standalone Executable

For a portable executable without Python installation:

```bash
python build.py
```

This creates `RainingKeysPython.exe` in the `dist/` folder.

## Usage

1. Run the application:

```bash
python main.py
```

2. The application launches two windows:
- Transparent Overlay: The visualizer (click-through)
- Config Window: The controls (Alt+Tab to find if hidden)

3. Configure lanes:
- Click "Record Lane Keys" in the config window
- Press keys to bind (e.g., `Z`, `X`, `.`, `/`)
- Click "Stop Recording" to save

4. Customize settings:
- Adjust Scroll Speed and Bar Color
- Enable KeyViewer to see the static key panel
- Drag Inactive Opacity to change faintness of unpressed keys
- Change KeyViewer Position (Above/Below) to flip fall direction

## Configuration

Settings are stored in `config.ini` (automatically created on first run). You can edit this file manually or use the GUI Settings Window.

### Config Options

| Section | Parameter | Description |
| --- | --- | --- |
| `Visual` | `scroll_speed` | Falling speed in pixels per second |
| `Visual` | `bar_color` | RGBA color string (e.g., `0,255,255,200`) |
| `Visual` | `fall_direction` | `up` or `down` - falling animation direction |
| `Position` | `x` | Overlay X position (pixels) |
| `Position` | `y` | Overlay Y position (pixels) |
| `Lanes` | `keys` | Comma-separated list of keys (e.g., `Z,X,./,`) |
| `KeyViewer` | `enabled` | Show/Hide KeyViewer panel |
| `KeyViewer` | `panel_position` | `above` or `below` - Affects fall direction |
| `KeyViewer` | `opacity` | Opacity of inactive keys (0.0 - 1.0) |

The configuration file includes a `CONFIG_VERSION` field for automatic migration. When updating to a new version with breaking config changes, the application will automatically migrate your settings.

## Developer Guide

This project is open to contributions. For detailed development guides, see the following documentation:

- [AGENTS.md](AGENTS.md) - Core components and architecture
- [GITHUB_WORKFLOWS.md](GITHUB_WORKFLOWS.md) - CI/CD workflow documentation
- [GIT_CLIFF_MIGRATION.md](GIT_CLIFF_MIGRATION.md) - Git-cliff migration guide
- [.github/README.md](.github/README.md) - Workflow directory reference

### Quick Start

1. Run local CI (fast quality check):

```bash
python run_local_ci.py
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make changes and test locally:

```bash
python run_local_ci.py
```

4. Commit with conventional format:

```bash
git commit -m "feat: Add new feature"
```

5. Push to GitHub:

```bash
git push
```

See [LOCAL_CI.md](LOCAL_CI.md) for complete local CI runner documentation.

## GitHub Actions CI/CD

This project uses GitHub Actions for automated quality validation and release management.

### Workflows

#### Code Quality
- Runs on every push and pull request
- Windows-based CI for consistency with production
- Syntax validation, linting, type checking, import testing

#### Release
- Triggered by tag push (format: `v*`)
- Generates changelog using git-cliff
- Creates GitHub releases with build artifacts:
  - `RainingKeysPython.zip` - Release build
  - `RainingKeysPython-debug.zip` - Debug build

### Conventional Commits

Use the following format for commit messages:

```
<type>[optional scope]: <subject>

[optional body]

[optional footer(s)]
```

**Types:** `feat`, `fix`, `perf`, `refactor`, `chore`, `test`, `docs`, `style`

## Local CI Runner

Run GitHub Actions CI checks locally for faster development iteration.

### Usage

```bash
# Run all checks
python run_local_ci.py

# Run individual checks
python run_local_ci.py --syntax    # Syntax check
python run_local_ci.py --lint      # Linting
python run_local_ci.py --import    # Import check
python run_local_ci.py --type      # Type check
python run_local_ci.py --config    # Config check
python run_local_ci.py --build     # Build test
```

### Benefits

- 10-100x faster than GitHub Actions
- Interactive debugging
- Unlimited runs
- Free (uses own computer)
- Same environment as development (Windows)

## Contributing

Contributions are welcome! We'd love to make this tool better together.

### Have a big idea or found a bug?

[Open an Issue](https://github.com/Ian-bug/RainingKeysPython/issues) and tell us about it!

### Want to help implement a feature?

Fork repository and submit a Pull Request.

### Before Submitting

1. Run local CI: `python run_local_ci.py`
2. Use conventional commits (format above)
3. Write tests for new features
4. Update documentation where needed

## Credits

This project is inspired by RainingKeys mod for *A Dance of Fire and Ice*, originally created by [paring-chan](https://github.com/paring-chan/RainingKeys).

Also credits to [AdofaiTweaks](https://github.com/PizzaLovers007/AdofaiTweaks) by PizzaLovers007.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Links

- [GitHub Repository](https://github.com/Ian-bug/RainingKeysPython)
- [Releases](https://github.com/Ian-bug/RainingKeysPython/releases)
- [Issues](https://github.com/Ian-bug/RainingKeysPython/issues)
- [AGENTS.md - Developer Guide](AGENTS.md)
- [GITHUB_WORKFLOWS.md - CI/CD Documentation](GITHUB_WORKFLOWS.md)
- [GIT_CLIFF_MIGRATION.md - Migration Guide](GIT_CLIFF_MIGRATION.md)
- [LOCAL_CI.md - Local CI Runner](LOCAL_CI.md)

---

**Made with love by the RainingKeysPython community**
