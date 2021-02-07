"""
record.py - Record the keystrokes and mouse clicks for Windows system.

Example:
    $python record.py
    # Press `CTRL` key to terminate the recording.
"""
import log
import json
import logging
import os
from ctypes import (
    windll, GetLastError, c_long, c_ulonglong,
    byref, create_unicode_buffer, pointer
)
from ctypes.wintypes import RECT

import win_utils
from win_const import *


# Termination condition
END_KEY = VIRTUAL_KEYS_REVERSE["CTRL"]

# Shorthand for the required dll librairies
user32 = windll.user32
kernel32 = windll.kernel32
shcore = windll.shcore

# Log writter
writer = log.Writer("log.txt", END_KEY)

# Handlers of callback procedure
kb_handle = None
mouse_handle = None


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


def hook_procedure(nCode, wParam, lParam):
    """Hook procedure to monitor and log for mouse and keyboard events.

    Args:
        nCode: HC_ACTION code
        wParam: Identifier of the message
        lParam: Address to an input structure depends on wParam
    """
    # Terminated condition
    if win_utils.is_pressed(END_KEY):
        uninstall_hook(kb_handle)
        uninstall_hook(mouse_handle)
        user32.PostQuitMessage(1)
        writer.wait_event()
        return user32.CallNextHookEx(
            kb_handle, nCode, wParam, c_ulonglong(lParam)
        )

    handle = kb_handle
    if nCode == HC_ACTION:
        if writer.keyboardll_msg(wParam, lParam):
            handle = kb_handle
        elif writer.mousell_msg(wParam, lParam):
            handle = mouse_handle

    return user32.CallNextHookEx(handle, nCode, wParam, c_ulonglong(lParam))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(filename)s:%(lineno)d][%(levelname)s] %(message)s")

    # Install keyboard/mouse hook procedures
    ptr = HOOKPROC(hook_procedure)
    kb_handle = install_hook(WH_KEYBOARD_LL, ptr)
    mouse_handle = install_hook(WH_MOUSE_LL, ptr)

    # Retrieves a message from the calling thread's message queue.
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessagea
    msg = MSG()
    user32.GetMessageA(byref(msg), 0, 0, 0)
