import sys
import signal
from PySide6.QtWidgets import QApplication
from core.overlay import RainingKeysOverlay
from core.input_mon import InputMonitor

def main():
    # Allow Ctrl+C to terminate the application immediately
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    
    # Create the overlay window
    overlay = RainingKeysOverlay()
    overlay.show()
    
    # Create and start the input monitor thread
    input_mon = InputMonitor()
    input_mon.key_pressed.connect(overlay.handle_input)
    input_mon.key_released.connect(overlay.handle_release)
    input_mon.start()
    
    print("RainingKeys started. Press Ctrl+C in terminal to stop.")
    
    # Execute app
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
