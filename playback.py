from win_const import *
from ctypes import windll, c_int, sizeof, GetLastError
import log
import time
# Shorthand for the required dll librairies
user32 = windll.user32
kernel32 = windll.kernel32

reader = log.Reader("log.txt")
for in_arr, wainting_ms in reader.get_next_input_array():
    time.sleep(wainting_ms/1000)
    nums = user32.SendInput(len(in_arr), in_arr, c_int(sizeof(INPUT)))
    if nums < len(in_arr):
        raise OSError(GetLastError())
