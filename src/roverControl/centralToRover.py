"""
Transmits rover controls either directly or through drone

@author Zoe Rizzo [@zizz-0]

Date last modified: 07/01/2024
"""

import hid

for device in hid.enumerate():
    print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

gamepad = hid.device()
gamepad.open(0x045e, 0x02ff) # controller vendor id, product id
gamepad.set_nonblocking(True)

while True:
    report = gamepad.read(64)
    if report:
        print(report)