"""
Transmits rover controls either directly or through drone

@author [name] [github]

Date last modified: 06/26/2024
"""

import hid

gamepad = hid.device()
gamepad.open(0x1209, 0x4f54)
gamepad.set_nonblocking(True)

while True:
    report = gamepad.read(64)
    if report:
        print(report)

