# About The Project
Record and placyback the keystorkes and mouse clicks for Windows system.
The scripts are tested on a Winodws 10 laptop without the secondary screen.

Functionality:
  1.  Log/Playback keys pressed/released for a US keyboard.
  2.  Log/Playback mouse movement and right/left button pressed/released.
  3.  Use "CTRL" key to terminate record/playback by default.

# Getting started
## Prerequisites
Install the lastest python3 version from https://www.python.org/.

# Usage
```shell
# Start recording keystorkes and mouse clicks and save to default log file `log.txt`.
# Press `CTRL` to stop recording.
python.exe .\\record.py

# Repeat the records from `log.txt` for 10 times.
python.exe .\\playback.py --repeat 10
```
# Known Issues
## Fail to change camera in FFXIV with mouse smoothly.

When moving mouse around with left/right button pressed,n FFXIV window, the mouse
point captured doesn't increase/decrease accordingly. It seems like FFXIV uses the
relative movement instead of the absolute coordinates. Here is an example of moving
point captured doesn't increase/decrease accordingly. It seems like FFXIV uses the
relative movement instead of the absolute coordinates. Here is an example of moving
camera from left to right by pressing right button:
```
{"x": 6860, "y": 23119, "raw": [201, 381], "MouseRightDown": true}
{"x": 6963, "y": 23058, "raw": [204, 380], "MouseMove": true}
{"x": 6963, "y": 23058, "raw": [204, 380], "MouseMove": true}
{"x": 6997, "y": 23058, "raw": [205, 380], "MouseMove": true}
{"x": 6929, "y": 23119, "raw": [203, 381], "MouseMove": true}
...
{"x": 6860, "y": 23119, "raw": [201, 381], "MouseRightUp": true}
````
Observation:
 - The mouse positions of MouseRightDown and MouseRightUp are identical.
 - The raw POINT.x POINT.y before normalization is not monotonic increasing.
 - Replay mouse message with the relative coordinates in SendInput by
    subtracting raw points of MouseMove from MouseRightDown message. The
    camera seems to move smoothly as what we did in recording. However, it
    tends to move more compares to what we did during recording.

# Contact
Shaomin Chiu - dgfsdg2001@gmail.com

# Reference
- [Malware writing - Python malware, part 2: Keylogging with ctypes and SetWindowsHookExA](https://0x00sec.org/t/malware-writing-python-malware-part-2-keylogging-with-ctypes-and-setwindowshookexa/11858)
- 