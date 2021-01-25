from datetime import datetime, timedelta
import json
from win_const import *
import logging

DOWN_UP_DELAY = 0.001   # second

class Writer:
    def __init__(self, filepath):
        """Constructor to open the file."""
        self.file = open(filepath, "w")
        self.last_time = None
    
    def _waiting_time(self) -> float:
        """Reterive the waiting time in seconds since last event."""
        waiting_time = 0
        now = datetime.now()
        if self.last_time:
            waiting_time = (now - self.last_time)/timedelta(seconds=1)
        self.last_time = now
        return waiting_time

    def _write(self, log: dir):
        """Write to the file."""
        log["WAITING_TIME"] = self._waiting_time()
        self.file.write(json.dumps(log) + "\n")
        self.file.flush()

    def wait_event(self):
        self._write(dict())

    def keyboard_event(self, vkey, **kwargs):
        """Write keyboard event to the file."""
        log = {k: v for k, v in kwargs.items()}
        log["KEY_PRESSED"] = VIRTUAL_KEYS[vkey]
        self._write(log)

    def mouse_event(self, x, y, right_click, **kwargs):
        """Write mouse event to the file."""
        log = {k: v for k, v in kwargs.items()}
        click = "CLICK_RIGHT" if right_click else "CLICK_LEFT"
        log[click] = (x, y)
        self._write(log)

    def __del__(self):
        """Destructor to close the file."""
        self.file.close()


class Reader:
    def __init__(self, filepath):
        """Constructor to open the file."""
        self.file = open(filepath, "r")

    def get_next_input_array(self):
        """Generator for getting an array with single IPNUT structure.""" 
        for line in self.file:
            log = json.loads(line)

            in_arr = None
            if "KEY_PRESSED" in log:
                logging.info("Key `{}` press in {:.2f} sec.".format(log["KEY_PRESSED"], log["WAITING_TIME"]))
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_KEYBOARD
                in_arr[0].u.ki.wVk = VIRTUAL_KEYS_REVERSE[log["KEY_PRESSED"]]
                yield in_arr, log["WAITING_TIME"]

                in_arr[0].type = INPUT_KEYBOARD
                in_arr[0].u.ki.wVk = VIRTUAL_KEYS_REVERSE[log["KEY_PRESSED"]]
                in_arr[0].u.ki.dwFlags = KEYEVENTF_KEYUP
                yield in_arr, DOWN_UP_DELAY

            elif "CLICK_RIGHT" in log:
                logging.info("Right click in {:.2f} sec.".format(log["WAITING_TIME"]))
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = log["CLICK_RIGHT"]
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
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
                logging.info("Left click in {:.2f} sec.".format(log["WAITING_TIME"]))
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = log["CLICK_LEFT"]
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
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
