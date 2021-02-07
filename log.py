"""
log.py - Read/Write mouse/keyboard event from/to a file.
"""
import json
import logging
from datetime import datetime, timedelta

import win_utils
from win_const import *

DOWN_UP_DELAY = 0.001   # second

KEYBOARD_MSGS = {
    WM_KEYDOWN, WM_KEYUP,
    WM_SYSKEYDOWN, WM_SYSKEYUP
}

MOUSE_MSGS = {
    WM_MOUSEMOVE,
    WM_LBUTTONDOWN, WM_LBUTTONUP,
    WM_RBUTTONDOWN, WM_RBUTTONUP
}

MSG_TO_LOG = {
    WM_KEYDOWN: "KeyDown",
    WM_KEYUP: "KeyUp",
    WM_SYSKEYDOWN: "SysKeyDown",
    WM_SYSKEYUP: "SysKeyUp",
    WM_MOUSEMOVE: "MouseMove",
    WM_LBUTTONDOWN: "MouseLeftDown",
    WM_LBUTTONUP: "MouseLeftUp",
    WM_RBUTTONDOWN: "MouseRightDown",
    WM_RBUTTONUP: "MouseRightUp"
}

LOG_TO_MSG = {
    value: key for key, value in MSG_TO_LOG.items()
}

MSG_TO_MOUSE_EVENT = {
    WM_MOUSEMOVE: MOUSEEVENTF_MOVE,
    WM_LBUTTONDOWN: MOUSEEVENTF_LEFTDOWN,
    WM_LBUTTONUP: MOUSEEVENTF_LEFTUP,
    WM_RBUTTONDOWN: MOUSEEVENTF_RIGHTDOWN,
    WM_RBUTTONUP: MOUSEEVENTF_RIGHTUP
}

CTRL_KEYS = {
    VIRTUAL_KEYS_REVERSE["CTRL"],
    VIRTUAL_KEYS_REVERSE["LCTRL"],
    VIRTUAL_KEYS_REVERSE["RCTRL"]
}

SHIFT_KEYS = {
    VIRTUAL_KEYS_REVERSE["SHIFT"],
    VIRTUAL_KEYS_REVERSE["LSHFT"],
    VIRTUAL_KEYS_REVERSE["RSHFT"]
}

ALT_KEYS = {
    VIRTUAL_KEYS_REVERSE["ALT"],
    VIRTUAL_KEYS_REVERSE["LALT"],
    VIRTUAL_KEYS_REVERSE["RALT"]
}

if not set(MSG_TO_LOG).issuperset(KEYBOARD_MSGS):
    raise Exception(
        "All items in KEYBOARD_MSGS should be defined in MSG_TO_LOG")

if not set(MSG_TO_LOG).issuperset(MOUSE_MSGS):
    raise Exception(
        "All items in MOUSE_MSGS should be defined in MSG_TO_LOG")


class Writer:
    def __init__(self, filepath, end_key):
        """Constructor for opening the log file."""
        self.file = open(filepath, "w")
        self.last_time = None
        self.first_key = True

        # There may be two ALT, CTRL, and SHIFT keys on the keyboard.
        if end_key in CTRL_KEYS:
            self.end_keys = CTRL_KEYS
        elif end_key in SHIFT_KEYS:
            self.end_keys = SHIFT_KEYS
        elif end_key in ALT_KEYS:
            self.end_keys = ALT_KEYS
        else:
            self.end_keys = {end_key}

    def _waiting_time(self) -> float:
        """Reterive the waiting time in seconds since last logged event."""
        waiting_time = 0
        now = datetime.now()
        if self.last_time:
            waiting_time = (now - self.last_time)/timedelta(seconds=1)
        self.last_time = now
        return waiting_time

    def _write(self, log: dir):
        """Write key-value pair to the file in JSON format.

        Write key-value pair in `log` plus elasped time since the last
        call of the method.

        Args:
            log: A dictionary that is going to be logged.
        """
        log["WAITING_TIME"] = self._waiting_time()
        self.file.write(json.dumps(log) + "\n")
        self.file.flush()

    def wait_event(self):
        """Write wait event to the file."""
        self._write(dict())

    def keyboardll_msg(self, wParam, lParam) -> bool:
        """Write low level keyboard message to the file.

        The virtual-key codes used by Windows are defined on the website.
        https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

        Args:
            wParam: information about a keystroke message
            lParam: information about a keystroke message

        Return:
            True if args is an intersted keyboard message. False otherwise.
        """
        # Not an interested keyboard message
        if wParam not in KEYBOARD_MSGS:
            return False

        # Exclude not intersted keys
        kb = KBDLLHOOKSTRUCT.from_address(lParam)
        if kb.vkCode not in VIRTUAL_KEYS:
            return False

        # Exclude the end keys
        if kb.vkCode in self.end_keys:
            return False

        # Exclude the first event if it's key up.
        if self.first_key and wParam == WM_KEYUP:
            self.first_key = False
            return False

        log = {
            MSG_TO_LOG[wParam]: VIRTUAL_KEYS[kb.vkCode]
        }
        self._write(log)
        return True

    def mousell_msg(self, wParam, lParam) -> bool:
        """Write low level mouse message to the file.

        Args:
            wParam: information about a keystroke message
            lParam: information about a keystroke message

        Return:
            True if args is an intersted mouse message. False otherwise.
        """
        # Not an interested mouse message
        if wParam not in MOUSE_MSGS:
            return False

        mouse = MSLLHOOKSTRUCT.from_address(lParam)
        x, y = win_utils.normalized_screen_coordinates(
            mouse.pt.x, mouse.pt.y)

        # TODO: Bunch of mousemove messages are logged.
        log = {
            "x": x,
            "y": y,
            MSG_TO_LOG[wParam]: True
        }
        self._write(log)
        return True

    def __del__(self):
        """Destructor for closing the log file."""
        self.file.close()


class Reader:
    def __init__(self, filepath):
        """Constructor for opening the file."""
        self.file = open(filepath, "r")

    def _get_keyboard_msg(self, logs: dict):
        """Get keyboard message from logs."""
        for key in logs:
            msg = LOG_TO_MSG.get(key, None)
            if msg and msg in KEYBOARD_MSGS:
                return msg
        return None

    def _get_mouse_msg(self, logs: dict):
        """Get mouse message from logs."""
        for key in logs:
            msg = LOG_TO_MSG.get(key, None)
            if msg and msg in MOUSE_MSGS:
                return msg
        return None

    def _keyboard_msg(self, logs: dict):
        """Generate keyboard INPUT array from logs."""
        msg = self._get_keyboard_msg(logs)
        if not msg:
            return None

        # Simulate for key down-up with reasonable delay.
        in_arr = (INPUT * 1)()
        in_arr[0].type = INPUT_KEYBOARD
        in_arr[0].u.ki.wVk = VIRTUAL_KEYS_REVERSE[logs[MSG_TO_LOG[msg]]]
        if msg == WM_KEYUP or msg == WM_SYSKEYUP:
            in_arr[0].u.ki.dwFlags = KEYEVENTF_KEYUP

        return in_arr

    def _mouse_msg(self, logs: dict):
        """Generate mouse INPUT array from logs."""
        msg = self._get_mouse_msg(logs)
        if not msg:
            return None

        # Simulate for click down-up with reasonable delay.
        in_arr = (INPUT * 1)()
        in_arr[0].type = INPUT_MOUSE
        in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = logs["x"], logs["y"]
        flag = MOUSEEVENTF_ABSOLUTE
        for m, log in MSG_TO_LOG.items():
            if log in logs:
                flag = flag | MSG_TO_MOUSE_EVENT[m]
        in_arr[0].u.mi.dwFlags = flag
        return in_arr

    def get_next_input_array(self):
        """Generator for getting an array of IPNUT structures.

        Read lines from the file and generates INPUT structures
        to simulate the keystorkes and button click. The INPUT
        structure is defined in
        https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input

        Return:
            An array of INPUT structures which will be consumed by
            user32.SendInput() API.
        """
        for line in self.file:
            logs = json.loads(line)

            empty_event = True

            # Generate keyboard event from logs
            in_arr = self._keyboard_msg(logs)
            if in_arr:
                empty_event = False
                # Generate running status
                act = "down"
                if in_arr[0].u.ki.dwFlags & KEYEVENTF_KEYUP:
                    act = "up"
                sts = "Key `{key}` {act} in {sec:.2f} sec.".format(
                    key=VIRTUAL_KEYS[in_arr[0].u.ki.wVk],
                    act=act,
                    sec=logs["WAITING_TIME"]
                )
                logging.info(sts)
                yield in_arr, logs["WAITING_TIME"]

            # Generate mouse event from logs
            in_arr = self._mouse_msg(logs)
            if in_arr:
                empty_event = False
                # Generate running status
                act = "mouse "
                if in_arr[0].u.mi.dwFlags & MOUSEEVENTF_MOVE:
                    act += "move "
                if in_arr[0].u.mi.dwFlags & MOUSEEVENTF_LEFTDOWN:
                    act += "left down"
                if in_arr[0].u.mi.dwFlags & MOUSEEVENTF_LEFTUP:
                    act += "left up"
                if in_arr[0].u.mi.dwFlags & MOUSEEVENTF_RIGHTDOWN:
                    act += "right down "
                if in_arr[0].u.mi.dwFlags & MOUSEEVENTF_RIGHTUP:
                    act += "right up "
                sts = "{act} in {sec:.2f} sec.".format(
                    act=act,
                    sec=logs["WAITING_TIME"]
                )
                logging.info(sts)
                yield in_arr, logs["WAITING_TIME"]

            # Neither mouse nor keyboard event
            if empty_event:
                yield None, logs["WAITING_TIME"]

    def __del__(self):
        """Destructor to close the file."""
        self.file.close()
