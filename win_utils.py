import logging
from ctypes import (
    windll, GetLastError, pointer, c_long)
from ctypes.wintypes import RECT

from win_const import *

# Shorthand for the required dll librairies
user32 = windll.user32
kernel32 = windll.kernel32
shcore = windll.shcore


def install_hook(hook_id, proc):
    """Install a keyboard hook callback function.

    Args:
        hook_id: Windows hook ID
        proc: HOOKPROC callback function.

    Return:
        Handle to the hook procedure if success, None otherwise.
    """
    handle = user32.SetWindowsHookExA(hook_id, proc, None, 0)
    if not handle:
        # https://docs.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
        msg = "Failed to install hook. errno=" + str(GetLastError())
        logging.error(msg)
    return handle


def uninstall_hook(handle):
    """Uninstall the keyboard hook.

    Args:
        handle: Handle to the hook procedure.
    """
    if handle:
        user32.UnhookWindowsHookEx(handle)


def is_pressed(vkey) -> bool:
    """Determine whether a key is pressed

    Args:
        vkey: virtual-key code

    Return:
        True if the virtual key is pressed, False otherwise
    """
    # GetKeyState returns a SHORT that specifies the status of the specified
    # virtual key. If the high-order bit is 1, the key is down; otherwise,
    # it is up.
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate
    return bool(user32.GetKeyState(vkey) & 0x8000)


def get_screen_resolution() -> (int, int):
    """Get screen resolution before rescaling.

    Return:
        x, y: the screen resolution before rescaling.
    """
    h_desktop = user32.GetDesktopWindow()

    # Get screen resoltion virtualized for DPI
    rect = RECT()
    success = user32.GetWindowRect(h_desktop, pointer(rect))
    if not success:
        raise OSError(GetLastError())

    # Get rescale factor for primary monitor
    hmonitor = user32.MonitorFromWindow(
        h_desktop, MONITOR_DEFAULTTOPRIMARY)
    rescale_factor = c_long(0)
    result = shcore.GetScaleFactorForMonitor(
        hmonitor, pointer(rescale_factor))
    if result != S_OK:
        logging.error("GetScaleFactorForMonitor failed.")
        raise OSError(GetLastError())

    # Calcuate the resolution before scaling.
    rescale_factor = rescale_factor.value
    res_x = int((rect.right - rect.left) * rescale_factor / 100)
    res_y = int((rect.bottom - rect.top) * rescale_factor / 100)
    return res_x, res_y


def normalized_screen_coordinates(x, y) -> (int, int):
    """Normalized x, y to absolute coordinates. (0-65535)

    The absolute position is normalized between 0 and 65535. Refer to the
    website for more details about the Windows mouse input event.
    https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput

    Args:
        x: x-axis on screen coordinates.
        y: y-axis on screen coordinates.

    Return
        x, y: Normalized x, y from 0 to 65535
    """
    res_x, res_y = get_screen_resolution()
    return int(x * 65536 / res_x), int(y * 65536 / res_y)
