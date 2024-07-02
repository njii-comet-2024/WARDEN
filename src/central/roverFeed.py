"""
Receives video feed from rover

@author [Christopher Prol] [prolvalone]

Date last modified: 07/02/2024
"""

# Libraries
import cv2 as cv
import pickle
import struct


class Camera:

    def __init__(self):
        print("initializing")

    def getDroneFeed():
        capture = cv.VideoCapture(2) # need origin of camera, 2 potentially works, potentially doesnt
        
