from datetime import datetime, timedelta
import json
from win_const import *

class Writer:
    def __init__(self, filepath):
        """Constructor to open the file."""
        self.file = open(filepath, "w")
        self.last_time = datetime.now()
    
    def _waiting_time_ms(self) -> float:
        """Reterive the waiting time in millisecond since last event."""
        now = datetime.now()
        waiting_time = (now - self.last_time)/timedelta(milliseconds=1)
        self.last_time = now
        return waiting_time

    def _write(self, log: dir):
        """Write to the file."""
        log["WAITING_TIME_MS"] = self._waiting_time_ms()
        self.file.write(json.dumps(log) + "\n")
        self.file.flush()

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
                in_arr = (INPUT * 1)()
                in_arr[0].type = INPUT_KEYBOARD
                in_arr[0].u.ki.wVk = VIRTUAL_KEYS_REVERSE[log["KEY_PRESSED"]]

            if "CLICK_RIGHT" in log:
                in_arr = (INPUT * 3)()
                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = log["CLICK_RIGHT"]
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
                
                in_arr[1].type = INPUT_MOUSE
                in_arr[1].u.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN

                in_arr[2].type = INPUT_MOUSE
                in_arr[2].u.mi.dwFlags = MOUSEEVENTF_RIGHTUP
            
            if "CLICK_LEFT" in log:
                in_arr = (INPUT * 3)()
                in_arr[0].type = INPUT_MOUSE
                in_arr[0].u.mi.dx, in_arr[0].u.mi.dy = log["CLICK_LEFT"]
                in_arr[0].u.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
                
                in_arr[1].type = INPUT_MOUSE
                in_arr[1].u.mi.dwFlags = MOUSEEVENTF_LEFTDOWN

                in_arr[2].type = INPUT_MOUSE
                in_arr[2].u.mi.dwFlags = MOUSEEVENTF_LEFTUP

            if in_arr:
                yield in_arr, log["WAITING_TIME_MS"]


    def __del__(self):
        """Destructor to close the file."""
        self.file.close()

if __name__ == "__main__":
    write = Writer("test.log")
    write.keyboard_event(0x50)
    import time
    time.sleep(1.0)
    write.mouse_event(1,2,False)
    write.mouse_event(1,2,True, Hello="World")
    write.keyboard_event(0x51)
    del write

    read = Reader("test.log")
    for in_arr, waiting_time in read.get_next_input_array():
        print(in_arr[0].type, waiting_time)
