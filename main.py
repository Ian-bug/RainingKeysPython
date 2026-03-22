import importlib.util
import signal
import sys
from typing import Optional
from PySide6.QtWidgets import QApplication, QMessageBox
from core.overlay import RainingKeysOverlay
from core.input_mon import InputMonitor
from core.settings_manager import SettingsManager
from core.gui import SettingsWindow
from core.logging_config import setup_logging, get_logger

def check_dependencies() -> bool:
    """Check if all required dependencies are available.

    Returns:
        True if all dependencies are available, False otherwise.
    """
    missing: list[str] = []

    # Check pynput
    if importlib.util.find_spec('pynput') is None:
        missing.append("pynput")

    # Check pywin32 (Windows-only, but we're on Windows)
    if importlib.util.find_spec('win32gui') is None or importlib.util.find_spec('win32con') is None:
        missing.append("pywin32")

    if missing:
        error_msg = (
            "Missing required dependencies:\n\n"
            f"- {', '.join(missing)}\n\n"
            "Please install them using:\n"
            f"pip install {' '.join(missing)}"
        )
        try:
            QMessageBox.critical(None, "Dependency Error", error_msg)
        except Exception:
            print(error_msg)
        return False

    return True

def main() -> int:
    """Main application entry point.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Check dependencies first
    if not check_dependencies():
        return 1

    # Allow Ctrl+C to terminate the application immediately
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    logger: Optional[object] = None

    try:
        # Initialize Settings first to get debug mode
        settings_mgr = SettingsManager()

        # Setup logging with appropriate level
        logger = setup_logging(debug_mode=settings_mgr.app_config.DEBUG_MODE)

        logger.info(f"RainingKeys v{settings_mgr.app_config.VERSION} started.")
        logger.info("Overlay active.")
        logger.info("Settings window open.")
        logger.info("Press Ctrl+C in terminal to stop.")

        # Initialize Settings Window (Control Panel)
        settings_win = SettingsWindow(settings_mgr)
        settings_win.show()  # Show GUI

        # Create the overlay window
        overlay = RainingKeysOverlay(settings_mgr)
        overlay.show()

        # Create and start the input monitor thread
        # Dependency Injection: Pass the configuration object
        input_mon = InputMonitor(settings_mgr.app_config)
        input_mon.key_pressed.connect(overlay.handle_input)
        input_mon.key_released.connect(overlay.handle_release)
        # Connect raw key signal to Settings Window for recording
        input_mon.raw_key_pressed.connect(settings_win.handle_raw_key)
        input_mon.start()

        # Execute app
        return app.exec()

    except Exception as e:
        # Use logger if available, otherwise fallback to basic logger
        if logger is None:
            logger = get_logger(__name__)

        try:
            logger.critical(f"Fatal error: {e}", exc_info=True)
        except Exception:
            pass

        try:
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"RainingKeys encountered a fatal error:\n\n{str(e)}\n\n"
                "The application will now exit."
            )
        except Exception:
            print(f"Fatal error: {e}")

        return 1

if __name__ == "__main__":
    sys.exit(main())
