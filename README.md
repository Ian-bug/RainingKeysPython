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
- **Fall Direction**: Supports both Down (Classic) and Up (Reverse) fall directions (controlled by KeyViewer position).
- **Accurate Timing**: Uses high-resolution monotonic clocks (`time.perf_counter`) for smooth, jitter-free falling animation.
- **Lane System**: Configurable key-to-lane mapping (e.g., WASD, Space, Enter).
- **KeyViewer Panel**: Visual keyboard representation that shows key presses and counts.
- **KeyViewer Transparency**: Adjustable opacity for inactive keys.
- **Custom Visuals**: Configurable colors (RGBA) and adjustable overlay speed.
- **Long Press Support**: Visualizes held keys with variable-length bars.
- **Performance Optimized**: Implements object pooling and efficient rendering logic to minimize CPU/GPU usage.

## Tech Stack

- **Python 3.10+**
- **PySide6 (Qt)**: High-performance rendering and window management.
- **pynput**: Global low-level keyboard hook.
- **pywin32**: Windows API integration for transparency and click-through flags.

## Project Structure

```text
RainingKeysPython/
├── core/
│   ├── configuration.py    # Dataclasses for application configuration
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
    git clone https://github.com/Ian-bug/RainingKeysPython.git
    cd RainingKeysPython
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```
2.  The application launches two windows:
    -   **Transparent Overlay**: The visualizer itself (click-through).
    -   **Config Window**: The controls (Alt+Tab to find if hidden).
3.  **Configure Lanes**:
    -   Click "Record Lane Keys" in the config window.
    -   Press the keys you want to bind (e.g., `Z`, `X`, `.`, `/`).
    -   Click "Stop Recording" to save.
4.  **Customize**:
    -   Adjust **Scroll Speed** and **Bar Color**.
    -   Enable **KeyViewer** to see the static key panel.
    -   Drag **Inactive Opacity** to change how faint unpressed keys look.
    -   Change **KeyViewer Position** (Above/Below) to automatically flip the fall direction.

## Configuration

Settings are stored in `config.ini` (automatically created on first run).
You can edit this file manually or use the **GUI Settings Window**.

### Config Options

| Section | Parameter | Description |
| :--- | :--- | :--- |
| `Visual` | `scroll_speed` | Falling speed in pixels per second. |
| `Visual` | `bar_color` | RGBA color string (e.g., `0,255,255,200`). |
| `Position` | `x` | Overlay X position (pixels). |
| `Position` | `y` | Overlay Y position (pixels). |
| `lanes` | `keys` | Comma-separated list of keys. |
| `keyviewer` | `enabled` | Show/Hide KeyViewer panel. |
| `keyviewer` | `panel_position` | `above` or `below`. Affects fall direction. |
| `keyviewer` | `opacity` | Opacity of inactive keys (0.0 - 1.0). |

## Todo

- [x] Interactive Configuration UI
- [x] Save/Load config
- [x] Custom color selection
- [x] Custom key mapping
- [x] KeyViewer Panel & Key Counters
- [ ] Multi-monitor support 

## Disclaimer

This software is an unofficial community tool. It is not affiliated with, endorsed by, or connected to 7th Beat Games (developers of A Dance of Fire and Ice) or any other game developer. Use responsibly.

## 🤝 Contributing

Contributions are welcome! We'd love to make this tool better together.

-   **Have a big idea or found a bug?**  
    [Open an Issue](https://github.com/Ian-bug/RainingKeysPython/issues) and tell us about it!
-   **Want to help implement a feature?**  
    Fork the repository and submit a Pull Request.

Any contributions you make are **greatly appreciated**.

## Credits

This project is inspired by the **RainingKeys** mod for *A Dance of Fire and Ice*, originally created by **[paring-chan](https://github.com/paring-chan/RainingKeys)**.

Also credits to **[AdofaiTweaks](https://github.com/PizzaLovers007/AdofaiTweaks)** by **PizzaLovers007**.

## License

MIT License. See `LICENSE` for details.
