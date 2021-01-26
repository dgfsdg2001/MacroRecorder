"""
playback.py - Replay the keystokes/mouse clicks behaviors for Windows system.

Example:
    $ python playback.py --repeat 10 --file log.txt
"""
import log
import time
import argparse
import logging
from ctypes import windll, c_int, sizeof, GetLastError

from win_const import *

# Shorthand for the required dll librairies
user32 = windll.user32
kernel32 = windll.kernel32


def playback(filepath, repeat_times=1):
    """Repeat the keystrokes and mouse clicks behaviors from a log file.

    Args:
        filepath: The path to the log file.
        repeat_times: Repeat times for actions in the log file.
    """
    for i in reversed(range(repeat_times)):
        logging.info("{} repeat times remained.".format(i))
        reader = log.Reader(filepath)
        for in_arr, waiting_time in reader.get_next_input_array():
            # Wait until the next action is taken.
            time.sleep(waiting_time)

            # Synthesizes keystrokes, mouse motions, and button clicks.
            # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
            if in_arr:
                nums = user32.SendInput(
                    len(in_arr),
                    in_arr,
                    c_int(sizeof(INPUT))
                )
                if nums < len(in_arr):
                    raise OSError(GetLastError())


def parse_arg():
    """Replay the mouse/keybaord actions which is logged by record.py."""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-r", "--repeat", type=int, default=3)
    parser.add_argument("-f", "--file", type=str, default="log.txt")
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(filename)s:%(lineno)d][%(levelname)s] %(message)s")

    args = parse_arg()
    playback(args.file, args.repeat)
