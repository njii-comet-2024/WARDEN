"""
Receives analog drone feed from drone VTX
Runs on Central Raspberry Pi 2

@author [Christopher Prol] [@prolvalone]

Date last modified: 08/05/2024
"""

import cv2

cap = cv2.VideoCapture(0)  # Replace 0 with the index of your webcam if necessary

while True:
    ret, frame = cap.read()
    cv2.imshow('Analog', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
