"""
log.py - Read/Write mouse/keyboard event from/to a file.
"""
import json
import logging
from datetime import datetime, timedelta

from win_const import *


DOWN_UP_DELAY = 0.001   # second


class Writer:
    def __init__(self, filepath):
        """Constructor for opening the log file."""
        self.file = open(filepath, "w")
        self.last_time = None

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

    def keyboard_event(self, vkey, **kwargs):
        """Write keyboard event to the file.

        The virtual-key codes used by Windows are defined on the website.
        https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

        Args:
            vkey: virtual-key codes.
            kwargs: Supplementary data.
        """
        log = {k: v for k, v in kwargs.items()}
        log["KEY_PRESSED"] = VIRTUAL_KEYS[vkey]
        self._write(log)

    def mouse_event(self, x, y, right_click, **kwargs):
        """Write mouse event to the file.

        The (x, y) should be the absolute position of the mouse. The absolute
        position is normalized between 0 and 65535. Refer to the website for
        more details about the Windows mouse input event.
        https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput

        Args:
            x: x-axis of the absolute position of the mouse.
            y: y-axis of the absolute position of the mouse.
            right_click: True for click right, False for click left.
            kwargs: Supplementary data.
        """
        log = {k: v for k, v in kwargs.items()}
        click = "CLICK_RIGHT" if right_click else "CLICK_LEFT"
        log[click] = (x, y)
        self._write(log)

    def __del__(self):
        """Destructor for closing the log file."""
        self.file.close()


class Reader:
    def __init__(self, filepath):
        """Constructor for opening the file."""
        self.file = open(filepath, "r")

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
            log = json.loads(line)

            in_arr = None
            if "KEY_PRESSED" in log:
                msg = "Key `{key}` press in {sec:.2f} sec.".format(
                    key=log["KEY_PRESSED"], sec=log["WAITING_TIME"])
                logging.info(msg)

                # Simulate for key down-up with reasonable delay.
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_KEYBOARD
                in_arr[0].u.ki.wVk = VIRTUAL_KEYS_REVERSE[log["KEY_PRESSED"]]
                yield in_arr, log["WAITING_TIME"]

                in_arr[0].type = INPUT_KEYBOARD
                in_arr[0].u.ki.wVk = VIRTUAL_KEYS_REVERSE[log["KEY_PRESSED"]]
                in_arr[0].u.ki.dwFlags = KEYEVENTF_KEYUP
                yield in_arr, DOWN_UP_DELAY

            elif "CLICK_RIGHT" in log:
                msg = "Right click in {sec:.2f} sec.".format(
                    sec=log["WAITING_TIME"])
                logging.info(msg)

                # Simulate for click down-up with reasonable delay.
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = log["CLICK_RIGHT"]
                in_arr[0].u.mi.dwFlags = (
                    MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE)
                yield in_arr, log["WAITING_TIME"]

                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = 0, 0
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN
                yield in_arr, DOWN_UP_DELAY

                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = 0, 0
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_RIGHTUP
                yield in_arr, DOWN_UP_DELAY

            elif "CLICK_LEFT" in log:
                msg = "Left click in {sec:.2f} sec.".format(
                    sec=log["WAITING_TIME"])
                logging.info(msg)

                # Simulate for mouse move and button click down-up with
                # reasonable delay.
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = log["CLICK_LEFT"]
                in_arr[0].u.mi.dwFlags = (
                    MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE)
                yield in_arr, log["WAITING_TIME"]

                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = 0, 0
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
                yield in_arr, DOWN_UP_DELAY

                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = 0, 0
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_LEFTUP
                yield in_arr, DOWN_UP_DELAY

            elif "WAITING_TIME" in log:
                yield None, log["WAITING_TIME"]

    def __del__(self):
        """Destructor to close the file."""
        self.file.close()
