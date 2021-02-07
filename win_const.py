"""
win_const.py - Definition of data structure and consts for the Windows API.
"""

from ctypes import (
    WINFUNCTYPE, HRESULT, c_int, Structure, Union
)
from ctypes.wintypes import (
    WORD, DWORD, LPARAM, WPARAM, MSG,
    POINT, PULONG, LONG
)

# Windows hook ID
# https://docs.microsoft.com/en-us/windows/win32/winmsg/about-hooks
WH_KEYBOARD_LL = 13     # Hook ID for low-level keyboard input events
WH_MOUSE_LL = 14        # Hook ID for low-level mouse input events

# Keyboard input notifications
# https://docs.microsoft.com/en-us/windows/win32/inputdev/keyboard-input-notifications
WM_KEYDOWN = 0x0100       # Posted when a nonsystem key is pressed
WM_KEYUP = 0x0101         # Posted when a nonsystem key is released
WM_SYSKEYDOWN = 0x0104    # Posted when the user presses the F10 key (which activates
                          # the menu bar) or holds down the ALT key and then presses
                          # another key.
WM_SYSKEYUP = 0x0105      # Posted when the user releases a key that was pressed while
                          # the ALT key was held down.
WM_MOUSEMOVE = 0x0200     # Posted when the cursor moves
WM_LBUTTONDOWN = 0x0201   # Posted when the user presses the left mouse button
WM_LBUTTONUP = 0x0202     # Posted when the user releases the left mouse button
WM_RBUTTONDOWN = 0x0204   # Posted when the user presses the right mouse button
WM_RBUTTONUP = 0x0205     # Posted when the user releases the right mouse button

# A code the hook procedure uses to determine how to process the keyboard/mouse
# message.
HC_ACTION = 0

# The virtual-key codes used by Windows system. The key-value pair maps a
# virtual-key code to readable keystroke for US standard keyboard.
# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
VIRTUAL_KEYS = {
    0x08: "BACKSPACE",  # BACKSPACE key
    0x09: "TAB",        # TAB key
    0x0C: "CLEAR",      # CLEAR key
    0x0D: "ENTER",      # ENTER key
    0x10: "SHIFT",      # SHIFT key
    0x11: "CTRL",       # CTRL key
    0x12: "ALT",        # ALT key
    0x13: "PAUSE",      # PAUSE key
    0x14: "CAPSLOCK",   # CAPS LOCK key
    0x1B: "ESC",        # ESC key
    0x20: "SPACEBAR",   # SPACEBAR
    0x21: "PAGEUP",     # PAGE UP key
    0x22: "PAGEDOWN",   # PAGE DOWN key
    0x23: "END",        # END key
    0x24: "HOME",       # HOME key
    0x25: "LEFT",       # LEFT ARROW key
    0x26: "UP",         # UP ARROW key
    0x27: "RIGHT",      # RIGHT ARROW key
    0x28: "DOWN",       # DOWN ARROW key
    0x29: "SELECT",     # SELECT key
    0x2A: "PRINT",      # PRINT key
    0x2C: "SNAPSHOT",   # PRINT SCREEN key
    0x2D: "INSERT",     # INS key
    0x2E: "DELETE",     # DEL key
    0x30: "0",  # 0 key
    0x31: "1",  # 1 key
    0x32: "2",  # 2 key
    0x33: "3",  # 3 key
    0x34: "4",  # 4 key
    0x35: "5",  # 5 key
    0x36: "6",  # 6 key
    0x37: "7",  # 7 key
    0x38: "8",  # 8 key
    0x39: "9",  # 9 key
    0x41: "A",  # A key
    0x42: "B",  # B key
    0x43: "C",  # C key
    0x44: "D",  # D key
    0x45: "E",  # E key
    0x46: "F",  # F key
    0x47: "G",  # G key
    0x48: "H",  # H key
    0x49: "I",  # I key
    0x4A: "J",  # J key
    0x4B: "K",  # K key
    0x4C: "L",  # L key
    0x4D: "M",  # M key
    0x4E: "N",  # N key
    0x4F: "O",  # O key
    0x50: "P",  # P key
    0x51: "Q",  # Q key
    0x52: "R",  # R key
    0x53: "S",  # S key
    0x54: "T",  # T key
    0x55: "U",  # U key
    0x56: "V",  # V key
    0x57: "W",  # W key
    0x58: "X",  # X key
    0x59: "Y",  # Y key
    0x5A: "Z",  # Z key
    0x5B: "LWIN",   # Left Windows key (Natural keyboard)
    0x5C: "RWIN",   # Right Windows key (Natural keyboard)
    0x70: "F1",   # F1 key
    0x71: "F2",   # F2 key
    0x72: "F3",   # F3 key
    0x73: "F4",   # F4 key
    0x74: "F5",   # F5 key
    0x75: "F6",   # F6 key
    0x76: "F7",   # F7 key
    0x77: "F8",   # F8 key
    0x78: "F9",   # F9 key
    0x79: "F10",  # F10 key
    0x7A: "F11",  # F11 key
    0x7B: "F12",  # F12 key
    0x90: "NUMLOCK",    # NUM LOCK key
    0x91: "SCROLL",     # SCROLL LOCK key
    0xA0: "LSHFT",      # Left SHIFT key
    0xA1: "RSHFT",      # Right SHIFT key
    0xA2: "LCTRL",      # Left CONTROL key
    0xA3: "RCTRL",      # Right CONTROL key
    0xA4: "LALT",       # Left ALT key
    0xA5: "RALT",       # Right ALT key
    0xBA: ";",      # `;` for US standard keyboard. vary by keyboard
    0xBB: "+",
    0xBC: ",",
    0xBD: "-",
    0xBE: ".",
    0xBF: "/",
    0xC0: "~",      # `~` for US standard keyboard. vary by keyboard
    0xDB: "[",      # `[` for US standard keyboard. vary by keyboard
    0xDC: "\\",     # `\` for US standard keyboard. vary by keyboard
    0xDD: "]",      # `]` for US standard keyboard. vary by keyboard
    0xDE: "'",      # `'` for US standard keyboard. vary by keyboard
}

# The reverse maaping of VIRTUAL_KEYS.
VIRTUAL_KEYS_REVERSE = {
    value: key for key, value in VIRTUAL_KEYS.items()
}

# An application-defined or library-defined callback function signature used
# with the SetWindowsHookEx function.
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-hookproc
HOOKPROC = WINFUNCTYPE(HRESULT, c_int, WPARAM, LPARAM)


# Contains information about a low-level keyboard input event.
# KBDLLHOOKSTRUCT structure (winuser.h)
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", DWORD),
        ("scanCode", DWORD),
        ("flags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", DWORD)
    ]


# Contains information about a low-level mouse input event.
# MSLLHOOKSTRUCT structure (winuser.h)
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-msllhookstruct?redirectedfrom=MSDN
class MSLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", DWORD),
        ("flags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", PULONG)
    ]


# Contains information about a simulated mouse event.
# MOUSEINPUT structure (winuser.h)
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput
class MOUSEINPUT(Structure):
    _fields_ = [
        ("dx", LONG),
        ("dy", LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", PULONG)
    ]


MOUSEEVENTF_MOVE = 0x0001       # Movement occurred.
MOUSEEVENTF_LEFTDOWN = 0x0002   # The left button was pressed.
MOUSEEVENTF_LEFTUP = 0x0004     # The left button was released.
MOUSEEVENTF_RIGHTDOWN = 0x0008  # The right button was pressed.
MOUSEEVENTF_RIGHTUP = 0x0010    # The right button was released.
MOUSEEVENTF_ABSOLUTE = 0x8000   # Indicates the dx and dy is normalized.


# Contains information about a simulated keyboard event.
# KEYBDINPUT structure (winuser.h)
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput
class KEYBDINPUT(Structure):
    _fields_ = [
        ("wVk", WORD),
        ("wScan", WORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", PULONG)
    ]


# Contains information about a simulated message generated by an input device
# other than a keyboard or mouse.
# HARDWAREINPUT structure (winuser.h)
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-hardwareinput
class HARDWAREINPUT(Structure):
    _fields_ = [
        ("uMsg", DWORD),
        ("wParamL", WORD),
        ("wParamH", WORD)
    ]


class DUMMYUNIONNAME(Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]


# Used by SendInput to store information for synthesizing input events such as
# keystrokes, mouse movement, and mouse clicks.
# INPUT structure (winuser.h)
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input
class INPUT(Structure):
    _fields_ = [
        ("type", DWORD),
        ("u", DUMMYUNIONNAME)
    ]


# The type of the input event.
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input
INPUT_MOUSE = 0     # Mouse event. Use the mi structure of the union.
INPUT_KEYBOARD = 1  # Keyboard event. Use the ki structure of the union.
INPUT_HARDWARE = 2  # Hardware event. Use the hi structure of the union.

# Various aspects of a keystroke
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput
KEYEVENTF_KEYUP = 0x0002

# Determines the function's return value if the window does not intersect any
# display monitor.
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-monitorfromwindow
# https://lazarus-ccr.sourceforge.io/docs/lcl/lcltype/monitor_defaulttoprimary.html
MONITOR_DEFAULTTOPRIMARY = 1

# Common HRESULT Values
# https://docs.microsoft.com/en-us/windows/win32/seccrypto/common-hresult-values
S_OK = 0x00000000   # Operation successful
