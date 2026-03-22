# RainingKeys (Python)

![License](https://img.shields.io/github/license/Ian-bug/RainingKeysPython?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/Ian-bug/RainingKeysPython/Code%20Quality?style=for-the-badge)
![Release](https://img.shields.io/github/v/release/Ian-bug/RainingKeysPython?style=for-the-badge)
![Safe](https://img.shields.io/badge/status-External_Overlay-success?style=for-the-badge)

**A high-performance, external rhythm game input visualizer.**

RainingKeys is a purely external overlay application that visualizes keyboard inputs as falling bars, similar to "Rain" mode found in various rhythm game mods. It provides visual feedback on rhythm stability, micro-jitter, and input timing without injecting code into the game process.

> [!NOTE]
> This project is a **standalone external tool**. It is **NOT** a game mod and does **NOT** perform DLL injection or memory hooking. It is safe to use with anti-cheat software that permits external overlays.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Developer Guide](#developer-guide)
- [GitHub Actions CI/CD](#github-actions-cicd)
- [Local CI Runner](#local-ci-runner)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## Features

- **External Overlay**: Runs as a transparent, always-on-top, click-through window over any game.
- **Graphic Interface**: Live configuration window to adjust settings on the fly.
- **Positioning**: Configurable X/Y overlay position.
- **Fall Direction**: Supports both Down (Classic) and Up (Reverse) fall directions (controlled by KeyViewer position).
- **Accurate Timing**: Uses high-resolution monotonic clocks (`time.perf_counter`) for smooth, jitter-free falling animation.
- **Lane System**: Configurable key-to-lane mapping (e.g., WASD, Space, Enter).
- **KeyViewer Panel**: Visual keyboard representation that shows key presses and counts.
- **KeyViewer Transparency**: Adjustable opacity for inactive keys.
- **Custom Visuals**: Configurable colors (RGBA) and adjustable overlay speed.
- **Long Press Support**: Visualizes held keys with variable-length bars.
- **Performance Optimized**: Implements object pooling and efficient rendering logic to minimize CPU/GPU usage.
- **Thread-Safe**: Proper locking for concurrent input access.
- **Config Migration**: Automatic schema migration for configuration files.
- **Atomic Writes**: Crash-safe configuration saving.

---

## Tech Stack

- **Python 3.10+**
- **PySide6 (Qt)**: High-performance rendering and window management.
- **pynput**: Global low-level keyboard hook.
- **pywin32**: Windows API integration for transparency and click-through flags.
- **GitHub Actions**: Automated CI/CD pipeline with git-cliff changelog generation.

---

## Project Structure

```text
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
├── cliff.toml              # Git-cliff configuration for changelog generation
├── run_local_ci.py        # Local CI runner script
├── build.py               # Build script for creating standalone executable
├── main.py                # Application entry point
├── requirements.txt        # Dependencies
├── config.ini             # Auto-generated configuration file
└── README.md             # This file
```

---

## Installation

### Prerequisites

1. **Python 3.10 or newer** installed
2. **Administrator privileges** (for global keyboard hook)

### Steps

1. **Clone repository** (or download source):
    ```bash
    git clone https://github.com/Ian-bug/RainingKeysPython.git
    cd RainingKeysPython
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Optional: Build Standalone Executable

For a portable executable without Python installation:

```bash
python build.py
```

This creates `RainingKeysPython.exe` in the `dist/` folder.

---

## Usage

### Basic Usage

1. **Run application**:
    ```bash
    python main.py
    ```

2. **Two windows will launch**:
    - **Transparent Overlay**: The visualizer itself (click-through)
    - **Config Window**: The controls (Alt+Tab to find if hidden)

### Configure Lanes

1. Click "Record Lane Keys" in the config window
2. Press keys you want to bind (e.g., `Z`, `X`, `.`, `/`)
3. Click "Stop Recording" to save

### Customize

- **Adjust Scroll Speed** and **Bar Color** in Visual settings
- **Enable KeyViewer** to see static key panel
- **Drag Inactive Opacity** to change how faint unpressed keys look
- **Change KeyViewer Position** (Above/Below) to automatically flip fall direction

---

## Configuration

Settings are stored in `config.ini` (automatically created on first run).

You can edit this file manually or use the **GUI Settings Window**.

### Config Options

| Section | Parameter | Description |
| :--- | :--- | :--- |
| `Visual` | `scroll_speed` | Falling speed in pixels per second. |
| `Visual` | `bar_color` | RGBA color string (e.g., `0,255,255,200`). |
| `Visual` | `fall_direction` | `up` or `down` - falling animation direction. |
| `Position` | `x` | Overlay X position (pixels). |
| `Position` | `y` | Overlay Y position (pixels). |
| `Lanes` | `keys` | Comma-separated list of keys (e.g., `Z,X,./,`). |
| `KeyViewer` | `enabled` | Show/Hide KeyViewer panel. |
| `KeyViewer` | `panel_position` | `above` or `below`. Affects fall direction. |
| `KeyViewer` | `opacity` | Opacity of inactive keys (0.0 - 1.0). |

### Configuration Schema Version

The configuration file includes a `CONFIG_VERSION` field for automatic migration. When updating to a new version with breaking config changes, the application will automatically migrate your settings.

---

## Developer Guide

This project is open to contributions. For detailed development guides, see the following documentation:

- **[AGENTS.md](AGENTS.md)** - Core components and architecture
- **[GITHUB_WORKFLOWS.md](GITHUB_WORKFLOWS.md)** - CI/CD workflow documentation
- **[GIT_CLIFF_MIGRATION.md](GIT_CLIFF_MIGRATION.md)** - Git-cliff migration guide
- **[.github/README.md](.github/README.md)** - Workflow directory reference

### Quick Start

1. **Run local CI** (fast quality check):
    

2. **Install dependencies**:
    

3. **Make changes** and run tests:
    

4. **Commit with conventional format**:
    

5. **Push to GitHub**:
    

See [LOCAL_CI.md](LOCAL_CI.md) for complete local CI runner documentation.
## GitHub Actions CI/CD

This project uses GitHub Actions for automated quality validation and release management.

### Workflows Overview

#### 1. 🚀 Create Release (`.github/workflows/release.yml`)

**Trigger:** Tag push starting with `v*` or manual workflow dispatch

**Purpose:** Automatically creates GitHub releases using git-cliff for changelog generation

**Features:**
- ✅ Extracts version from git tag
- ✅ Uses git-cliff to generate changelog automatically
- ✅ Supports existing `CHANGELOG_{VERSION}.md` files (can override)
- ✅ Creates GitHub release with formatted notes
- ✅ Uploads build artifacts:
  - `RainingKeysPython.zip` (Release build)
  - `RainingKeysPython-debug.zip` (Debug build)
  - `CHANGELOG_{VERSION}.md` (Changelog file)
- ✅ Commits generated changelog to repository

**Changelog Generation:**
- Uses [git-cliff](https://github.com/orhun/git-cliff) for automated changelog
- Configured via `cliff.toml` in repository root
- Generates changelog for commits since last tag
- Follows [Conventional Commits](https://www.conventionalcommits.org/) format
- Supports commit types: `feat`, `fix`, `perf`, `refactor`, `chore`, `test`, `docs`, `style`

**Manual Trigger:**
```bash
gh workflow run release.yml -f version=1.5.0

# With existing changelog
gh workflow run release.yml -f version=1.5.0 -f use_existing_changelog=true
```

**Automatic Trigger:**
```bash
# Tag version
git tag v1.5.0
git push origin v1.5.0

# Release workflow runs automatically
```

#### 2. ✅ Code Quality (`.github/workflows/ci.yml`)

**Trigger:** Push to main/master/develop branches or Pull Requests

**Purpose:** Comprehensive code quality validation on Windows

**Jobs:**

**Syntax Check**
- Compiles all Python files to validate syntax
- Checks `main.py`, `core/*.py`, `core/ui/*.py`
- Fails build if syntax errors found

**Linting Check**
- Runs `pyflakes` on all Python files
- Detects unused imports and undefined variables
- Checks basic code quality issues

**Import Validation**
- Tests all module imports
- Validates import order and dependencies
- Checks for circular imports

**Type Checking**
- Validates AST (Abstract Syntax Tree) for all files
- Ensures type hints are valid
- Checks for syntax-level type errors

**Configuration Validation**
- Tests default configuration creation
- Validates schema checking
- Tests config save/load operations
- Tests temporary config file handling

**Failure Behavior:**
Any job failure will fail the entire workflow, preventing merge of problematic code.

### Configuration Files

#### 3. cliff.toml - Git-Cliff Configuration

**Purpose:** Configuration for git-cliff changelog generator

**Key Settings:**

```toml
[changelog]
header = "# Changelog - {{ version }} [{{ date }}]"
body = "{{ range .patches }}..."
footer = "Full Changelog:..."

[git]
conventional_commits = true
sort = "date"
git_tag_pattern = "v*"

[git.conventional_commits]
types = ["feat", "fix", "perf", "refactor", "chore", "test", "docs", "style"]
```

### Conventional Commits Guide

**Format:**
```
<type>[optional scope]: <subject>

[optional body]

[optional footer(s)]
```

**Commit Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `perf`: A code change that improves performance
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `chore`: Changes to the build process or auxiliary tools/libraries
- `test`: Adding missing tests or correcting existing tests
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, semi-colons, etc)

**Examples:**
```bash
# Feature addition
git commit -m "feat(input): Add keyboard shortcuts"

# Bug fix
git commit -m "fix(overlay): Resolve font caching issue"

# Performance improvement
git commit -m "perf(rendering): Optimize paint event"

# Breaking change
git commit -m "feat!: Change configuration file format"
```

### Migration to Git-Cliff

**What Changed:**
- ❌ Deleted `.github/workflows/changelog.yml` - Old manual changelog automation workflow
- ✅ Added `cliff.toml` - Git-cliff configuration file
- ✅ Updated `.github/workflows/release.yml` - Integrated git-cliff
- ✅ Added `GITHUB_WORKFLOWS.md` - Complete workflow documentation
- ✅ Added `GIT_CLIFF_MIGRATION.md` - Migration guide

**Why Git-Cliff?**
- Automated changelog generation from commits
- Consistent format across all releases
- Follows conventional commits structure
- Can be overridden with manual changelogs

**Benefits:**
- ✅ Automated (no manual maintenance)
- ✅ Accurate (based on actual commits)
- ✅ Consistent (professional presentation)
- ✅ Flexible (customizable templates)

See [GIT_CLIFF_MIGRATION.md](GIT_CLIFF_MIGRATION.md) for complete migration guide.

### Troubleshooting

#### CI Workflow Fails

**Check:**
1. Token is configured as `GITHUB_TOKEN` secret
2. Workflow YAML syntax is valid
3. Push was to correct branch (`main`, not `main`)
4. Tag format is correct (`vX.Y.Z`)

#### Changelog Generation Issues

**Issue:** Changelog doesn't generate properly

**Causes:**
- Not using conventional commit format
- Missing `cliff.toml` configuration file
- No commits since last tag

**Solutions:**
1. Use conventional commit format (see above guide)
2. Ensure `cliff.toml` is in repository root
3. Check commit messages for valid types
4. Verify git history is available: `git log --oneline`

#### Override Not Working

**Issue:** Existing changelog not being used

**Causes:**
- Wrong filename format (must be `CHANGELOG_{VERSION}.md`)
- Not passing `use_existing_changelog=true`

**Solutions:**
1. Verify changelog filename matches version exactly
2. Use `use_existing_changelog=true` input when triggering workflow
3. Check workflow logs for changelog detection messages

---

## Contributing

Contributions are welcome! We'd love to make this tool better together.

### Have a big idea or found a bug?

**[Open an Issue](https://github.com/Ian-bug/RainingKeysPython/issues)** and tell us about it!

### Want to help implement a feature?

**Fork repository and submit a Pull Request.**

**Before Submitting:**
1. **Run local CI:** `python run_local_ci.py`
2. **Use conventional commits:** Follow the commit format above
3. **Write tests:** Add tests for new features
4. **Update documentation:** Update relevant documentation

**Any contributions you make are greatly appreciated.**

### Development Workflow

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/RainingKeysPython.git
cd RainingKeysPython

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit code ...

# 4. Run local CI (fast!)
python run_local_ci.py

# 5. Only push if all checks pass
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature

# 6. Create Pull Request on GitHub
```

---

## Credits

This project is inspired by **RainingKeys** mod for *A Dance of Fire and Ice*, originally created by **[paring-chan](https://github.com/paring-chan/RainingKeys)**.

Also credits to **[AdofaiTweaks](https://github.com/PizzaLovers007/AdofaiTweaks)** by **PizzaLovers007**.

---

## Disclaimer

This software is an unofficial community tool. It is not affiliated with, endorsed by, or connected to 7th Beat Games (developers of A Dance of Fire and Ice) or any other game developer. Use responsibly.

---

## License

MIT License. See `LICENSE` for details.

---

## Links

- **[GitHub Repository](https://github.com/Ian-bug/RainingKeysPython)**
- **[Releases](https://github.com/Ian-bug/RainingKeysPython/releases)**
- **[Issues](https://github.com/Ian-bug/RainingKeysPython/issues)**
- **[AGENTS.md - Developer Guide](AGENTS.md)**
- **[GITHUB_WORKFLOWS.md - CI/CD Documentation](GITHUB_WORKFLOWS.md)**
- **[GIT_CLIFF_MIGRATION.md - Migration Guide](GIT_CLIFF_MIGRATION.md)**
- **[LOCAL_CI.md - Local CI Runner](LOCAL_CI.md)**

---

**Made with ❤️ by the RainingKeysPython community**
