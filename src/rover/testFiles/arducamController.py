import cv2
import numpy as np
import os
import sys
import time
import argparse
from RpiCamera import Camera
from Focuser import Focuser
import pygame
from datetime import datetime

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Initialized joystick: {joystick.get_name()}")

# Controls mapping
buttonInputs = {"SA": 0, "SD": 1}

axisInputs = {3: 0, 5: 0, 7: 0}

controls = {
    "cameraTilt": 0, 
    "cameraLeft": 0, 
    "cameraRight": 0, 
    "cameraZoom": 0, 
    "cameraFocus": 0
}

auto_focus_map = []
auto_focus_idx = 0

class ZoomFocusData:
    def __init__(self, zoom=0, focus=0):
        self.zoom = zoom
        self.focus = focus

def parse_controller_input(focuser, camera):
    global auto_focus_idx
    motor_step = 5
    focus_step = 5

    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == buttonInputs["SA"]:
                controls["cameraLeft"] = 1
                focuser.set(Focuser.OPT_MOTOR_X, focuser.get(Focuser.OPT_MOTOR_X) - motor_step)
            if event.button == buttonInputs["SD"]:
                focuser.set(Focuser.OPT_MOTOR_X, focuser.get(Focuser.OPT_MOTOR_X) + motor_step)
                controls["cameraRight"] = 1

        if event.type == pygame.JOYBUTTONUP:
            if event.button == buttonInputs["SA"]:
                controls["cameraLeft"] = 0
            if event.button == buttonInputs["SD"]:
                controls["cameraRight"] = 0

        if event.type == pygame.JOYAXISMOTION:
            axisInputs[event.axis] = event.value

            if abs(axisInputs[3]) > 0.5:
                controls["cameraTilt"] = axisInputs[3]
            else:
                controls["cameraTilt"] = 0

            if abs(axisInputs[5]) > 0.5:
                controls["cameraFocus"] = axisInputs[5]
            else:
                controls["cameraFocus"] = 0

            if abs(axisInputs[7]) > 0.5:
                controls["cameraZoom"] = axisInputs[7]
            else:
                controls["cameraZoom"] = 0

    run_inputs(focuser, focus_step)

def run_inputs(focuser, focus_step):
    global auto_focus_idx
    if controls["cameraLeft"] == 1:
        focuser.set(Focuser.OPT_FOCUS, focuser.get(Focuser.OPT_FOCUS) - focus_step)
    elif controls["cameraRight"] == 1:
        focuser.set(Focuser.OPT_FOCUS, focuser.get(Focuser.OPT_FOCUS) + focus_step)

    if controls["cameraTilt"] > 0:
        auto_focus_idx = (auto_focus_idx + 1) % len(auto_focus_map)
        focuser.move(auto_focus_map[auto_focus_idx].focus, auto_focus_map[auto_focus_idx].zoom)
    elif controls["cameraTilt"] < 0:
        auto_focus_idx = (auto_focus_idx - 1) % len(auto_focus_map)
        focuser.move(auto_focus_map[auto_focus_idx].focus, auto_focus_map[auto_focus_idx].zoom)

def gen_focus_map(focuser, camera):
    focus_map = coarse_adjustment(focuser, camera)
    focuser.write_map(focus_map)

def coarse_adjustment(focuser, camera):
    zoom_step = 200
    focus_step = 100
    focus_map = [focuser.opts[Focuser.OPT_ZOOM]["MAX_VALUE"], focuser.opts[Focuser.OPT_FOCUS]["MAX_VALUE"]]
    
    for i in range(0, 10):
        focuser.set(Focuser.OPT_ZOOM, i * zoom_step)
        max_val = 0
        cur_focus = 0
        
        for j in range(0, 22, 2):
            focuser.set(Focuser.OPT_FOCUS, j * focus_step)
            focuser.waitingForFree()
            time.sleep(0.01)
            image = camera.getFrame()
            img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image_var = cv2.Laplacian(img2gray, cv2.CV_64F).var()
            if max_val < image_var:
                max_val = image_var
                cur_focus = j * focus_step
        
        cur_focus = cur_focus - focus_step if cur_focus - focus_step > 0 else 0
        curr_focus_step, _ = focus_map_fine(camera, focuser, cur_focus)
        focus_map.extend([i * zoom_step, curr_focus_step])
    
    return focus_map

def focus_map_fine(camera, focuser, beg):
    max_val = 0
    cur_focus = 0
    end = focuser.opts[Focuser.OPT_FOCUS]["MAX_VALUE"]
    dec_count = 0

    for i in range(beg, end, 10):
        focuser.set(Focuser.OPT_FOCUS, i)
        focuser.waitingForFree()
        time.sleep(0.5)
        image = camera.getFrame()
        img2gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image_var = cv2.Laplacian(img2gray, cv2.CV_64F).var()
        if max_val < image_var:
            max_val = image_var
            cur_focus = i
            dec_count = 0
        else:
            dec_count += 1
            if dec_count >= 21:
                break
    
    return cur_focus, max_val

def focus_reset(i2c_bus):
    return Focuser(i2c_bus)

def focus_map_load(focuser, camera):
    global auto_focus_map
    auto_focus_map.clear()
    data = focuser.read_map()
    if data[0] == 0xffff:
        focuser.set(Focuser.OPT_MODE, 0x01)
        time.sleep(3)
        gen_focus_map(focuser, camera)
        time.sleep(0.01)
        focus_map_load(focuser, camera)
    else:
        focuser.opts[Focuser.OPT_ZOOM]["MAX_VALUE"] = data[0]
        focuser.opts[Focuser.OPT_FOCUS]["MAX_VALUE"] = data[1]

        for i in range(2, len(data), 2):
            t = ZoomFocusData(data[i], data[i + 1])
            auto_focus_map.append(t)

def main():
    camera = Camera()
    camera.start_preview(1280, 720)
    time.sleep(1)
    focuser = focus_reset(1)
    
    if focuser.driver_version() >= 0x104:
        focus_map_load(focuser, camera)
    else:
        print("Firmware version too low!")
        sys.exit(0)

    try:
        while True:
            parse_controller_input(focuser, camera)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    camera.stop_preview()
    camera.close()

if __name__ == "__main__":
    main()