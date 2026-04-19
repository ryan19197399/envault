"""Clipboard utilities for envault — copy secret values to clipboard with optional auto-clear."""

import threading
import time

try:
    import pyperclip
    _PYPERCLIP_AVAILABLE = True
except ImportError:
    _PYPERCLIP_AVAILABLE = False


def _check_available():
    if not _PYPERCLIP_AVAILABLE:
        raise RuntimeError(
            "pyperclip is not installed. Run: pip install pyperclip"
        )


def copy_to_clipboard(value: str) -> None:
    """Copy a string value to the system clipboard."""
    _check_available()
    pyperclip.copy(value)


def clear_clipboard() -> None:
    """Clear the system clipboard by copying an empty string."""
    _check_available()
    pyperclip.copy("")


def copy_with_autoclear(value: str, timeout: int = 30) -> None:
    """Copy value to clipboard, then clear it after `timeout` seconds."""
    _check_available()
    pyperclip.copy(value)

    def _clear_after():
        time.sleep(timeout)
        try:
            current = pyperclip.paste()
            if current == value:
                pyperclip.copy("")
        except Exception:
            pass

    t = threading.Thread(target=_clear_after, daemon=True)
    t.start()


def is_available() -> bool:
    """Return True if clipboard support is available."""
    return _PYPERCLIP_AVAILABLE
