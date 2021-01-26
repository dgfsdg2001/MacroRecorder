# About The Project
Record and placyback tehe keystorkes and mouse clicks for Windows system.

The scripts are tested on a Winodws 10 laptop without the secondary screen.

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

# Contact
Shaomin Chiu - dgfsdg2001@gmail.com

# Reference
- [Malware writing - Python malware, part 2: Keylogging with ctypes and SetWindowsHookExA](https://0x00sec.org/t/malware-writing-python-malware-part-2-keylogging-with-ctypes-and-setwindowshookexa/11858)
- 