"""
Receives analog drone feed from drone VTX
Runs on Central Raspberry Pi

@author [Christopher Prol] [@prolvalone]

Date last modified: 08/05/2024
"""

import cv2 as cv

cap = cv.VideoCapture(0)  # Replace 0 with the index of your webcam if necessary

while True:
    ret, frame = cap.read()
    cv.imshow('Analog', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
