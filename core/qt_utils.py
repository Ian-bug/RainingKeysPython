"""
Qt utility functions and helpers.

Provides context managers and helper functions for Qt operations.
"""
from contextlib import contextmanager
from typing import Generator
from PySide6.QtWidgets import QWidget
from .logging_config import get_logger

logger = get_logger(__name__)


@contextmanager
def signals_blocked(*widgets: QWidget) -> Generator[None, None, None]:
    """
    Context manager to temporarily block signals on one or more Qt widgets.

    Ensures signals are re-enabled even if an exception occurs.

    Args:
        *widgets: One or more Qt widgets to block signals on.

    Yields:
        None

    Example:
        with signals_blocked(spin_x, spin_y):
            spin_x.setValue(new_x)
            spin_y.setValue(new_y)
        # Signals are automatically unblocked here
    """
    # Store original blocked states
    original_states = [w.signalsBlocked() for w in widgets]

    try:
        # Block all signals
        for widget in widgets:
            widget.blockSignals(True)
        yield
    finally:
        # Restore signals to their original state
        for widget, original_state in zip(widgets, original_states):
            widget.blockSignals(original_state)


@contextmanager
def signals_blocked_single(widget: QWidget) -> Generator[None, None, None]:
    """
    Context manager to temporarily block signals on a single Qt widget.

    Convenience wrapper for signals_blocked() with a single widget.

    Args:
        widget: Qt widget to block signals on.

    Yields:
        None

    Example:
        with signals_blocked_single(my_spinbox):
            my_spinbox.setValue(42)
    """
    with signals_blocked(widget):
        yield
