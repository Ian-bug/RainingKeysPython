# RainingKeys (Python)

![License](https://img.shields.io/github/license/Ian-bug/RainingKeysPython?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Safe](https://img.shields.io/badge/status-External_Overlay-success?style=for-the-badge)



**A high-performance, external rhythm game input visualizer.**

RainingKeys is a purely external overlay application that visualizes keyboard inputs as falling bars, similar to the "Rain" mode found in various rhythm game mods. It provides visual feedback on rhythm stability, micro-jitter, and input timing without injecting code into the game process.

> [!NOTE]
> This project is a **standalone external tool**. It is **NOT** a game mod and does **NOT** perform DLL injection or memory hooking. It is safe to use with anti-cheat software that permits external overlays.

---

## Features

- **External Overlay**: Runs as a transparent, always-on-top, click-through window over any game.
- **Graphic Interface**: Live configuration window to adjust settings on the fly.
- **Positioning**: Configurable X/Y overlay position.
- **Fall Direction**: Supports both Down (Classic) and Up (Reverse) fall directions.
- **Accurate Timing**: Uses high-resolution monotonic clocks (`time.perf_counter`) for smooth, jitter-free falling animation.
- **Lane System**: Configurable key-to-lane mapping (e.g., WASD, Space, Enter).
- **Long Press Support**: Visualizes held keys with variable-length bars.
- **Performance Optimized**: Implements object pooling and efficient rendering logic to minimize CPU/GPU usage.
- **Fade Out**: Distance-based fade-out for visual clarity.
- **Input Latency Compensation**: Configurable offset to visually align inputs with audio latency.

## Tech Stack

- **Python 3.10+**
- **PySide6 (Qt)**: High-performance rendering and window management.
- **pynput**: Global low-level keyboard hook.
- **pywin32**: Windows API integration for transparency and click-through flags.

## Project Structure

```text
RainingKeysPython/
├── core/
│   ├── config.py           # Default configuration constants
│   ├── gui.py              # Configuration Window GUI
│   ├── input_mon.py        # Global input listener
│   ├── overlay.py          # Main rendering loop and window logic
│   └── settings_manager.py # Handles config loading/saving
├── build.py                # Build script for creating standalone executable
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Installation

1.  **Prerequisites**: Ensure you have Python 3.10 or newer installed.
2.  **Clone the repository** (or download source):
    ```bash
    git clone https://github.com/your-username/RainingKeysPython.git
    cd RainingKeysPython
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the build script:
    ```bash
    python build.py
    ```
2.  The script will generate:
    -   Folder: `dist/RainingKeysPython/`
    -   Zip: `RainingKeysPython.zip` (or `RainingKeysPython-debug.zip` if in debug mode)

### Debug vs Release Build
You can toggle the console window visibility via `config.ini`:** window (controls settings).
3.  Use the Config window to move the overlay or change speed/direction live.
4.  **Configure Lanes**:
    -   Click "Record Lane Keys" in the config window.
    -   Press the keys you want to bind (e.g., `Z`, `X`, `.`, `/`).
    -   Click "Stop Recording" to save. The overlay uses these keys immediately.
5.  **To Exit**: Close the Config window or press `Ctrl+C` in the terminal.

## Configuration

Settings are stored in `config.ini` (automatically created on first run).
You can edit this file manually or use the **GUI Settings Window**.

### Config Options

| Section | Parameter | Description |
| :--- | :--- | :--- |
| `Visual` | `scroll_speed` | Falling speed in pixels per second. |
| `Visual` | `fall_direction` | `down` or `up`. |
| `Position` | `x` | Overlay X position (pixels). |
| `Position` | `y` | Overlay Y position (pixels). |
| `lanes` | `keys` | Comma-separated list of keys (e.g., `'z','x','.'`). |

*Note: Key mappings and colors are currently defined in `core/config.py`.*

## Todo

- [x] Interactive Configuration UI (GUI for settings)
- [x] Save/Load config from ini
- [ ] Multi-monitor support
- [ ] Custom color
- [x] Custom key mapping 

## Disclaimer

This software is an unofficial community tool. It is not affiliated with, endorsed by, or connected to 7th Beat Games (developers of A Dance of Fire and Ice) or any other game developer. Use responsibly.

## License

MIT License. See `LICENSE` for details.
