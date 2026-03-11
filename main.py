import signal
import sys
from PySide6.QtWidgets import QApplication
from core.overlay import RainingKeysOverlay
from core.input_mon import InputMonitor
from core.settings_manager import SettingsManager
from core.gui import SettingsWindow
from core.logging_config import setup_logging

def main():
    # Allow Ctrl+C to terminate the application immediately
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

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
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
