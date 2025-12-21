# RainingKeys (Python)

**A high-performance, external rhythm game input visualizer.**

RainingKeys is a purely external overlay application that visualizes keyboard inputs as falling bars, similar to the "Rain" mode found in various rhythm game mods. It provides visual feedback on rhythm stability, micro-jitter, and input timing without injecting code into the game process.

> [!NOTE]
> This project is a **standalone external tool**. It is **NOT** a game mod and does **NOT** perform DLL injection or memory hooking. It is safe to use with anti-cheat software that permits external overlays.

---

## Features

- **External Overlay**: Runs as a transparent, always-on-top, click-through window over any game.
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

```
RainingKeysPython/
├── core/
│   ├── config.py       # User configuration (Keys, speeds, colors)
│   ├── input_mon.py    # Global input listener
│   └── overlay.py      # Main rendering loop and window logic
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
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

1.  Run the application:
    ```bash
    python main.py
    ```
2.  The overlay will appear (default: full screen transparent window).
3.  Press the configured keys (Default: `a`, `s`, `l`, `;`) to see the visualization.
4.  The Debug Overlay in the top-left corner shows FPS and object pool stats.
5.  **To Exit**: Press `Ctrl+C` in the terminal window.

## Configuration

Edit `core/config.py` to customize the overlay:

| Parameter | Description |
| :--- | :--- |
| `SCROLL_SPEED` | Falling speed in pixels per second. |
| `LANE_MAP` | Dictionary mapping specific keys (e.g., `'a'`, `'Key.space'`) to lane indices. |
| `BAR_WIDTH` | Visual width of the falling notes. |
| `INPUT_LATENCY_OFFSET` | Seconds to offset rendering (useful for audio sync). |
| `MAX_BARS` | Soft limit for the object pool (prevents memory leaks). |
| `COLORS` | RGBA values for bars and text. |

## Roadmap

- [ ] Interactive Configuration UI (GUI for settings)
- [ ] Save/Load config from JSON/YAML
- [ ] Multi-monitor support
- [ ] Custom skins/textures for bars

## Disclaimer

This software is an unofficial community tool. It is not affiliated with, endorsed by, or connected to 7th Beat Games (developers of A Dance of Fire and Ice) or any other game developer. Use responsibly.

## License

MIT License. See `LICENSE` for details.
