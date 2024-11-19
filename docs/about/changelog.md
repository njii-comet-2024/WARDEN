# Changelog

## Release contributors

- [Zoe Rizzo (@zizz-0)](https://github.com/zizz-0)


## Version 0.1.0 (06/26/2024)

This is the first documentation release of [WARDEN](https://github.com/njii-comet-2024/WARDEN) project.


**Features**

- 


**Minor Changes**

- Documentation files added to the main repository


**Bugfixes**

- 

## Version 0.2.0 (07/03/2024)

This is the first release of project **WARDEN**. It is not yet production-ready.


**Features**

- UDP video and data transmission between two laptops
- Controller inputs
- Shell programs for rover control


**Minor Changes**

- README updated


**Bugfixes**

- 

## Version 0.3.0 (07/16/2024)

This release expands on previous releases and includes an arduino to run motor control code on the rover.


**Features**

- Controller inputs transmitted via UDP between laptops/raspberry pis
- Motors controlled using arduino -- controls sent from laptop to raspberry pi, then sent to arduino over serial connection
- Arduino rover control code


**Minor Changes**

- Updated diagrams
- Switched from PS4 controls to TX12 controls


**Bugfixes**

- Switched from picam to picam2 for compatibility with OpenCV, NumPy, and Python3

## Version 1.0.0 (08/08/2024)

This release completes all the basic goals of the project and is now considered fully functional.


**Features**

- Switched from Arduino motor control to Raspberry Pi 
- Rover control code finalized
- Ground station implemented to receive both vehicle feeds simultaneously and send camera/movement controls to ground vehicle
- Arducam PTZ camera implemented on ground vehicle with reactive GUI


**Minor Changes**

- Diagrams and documentation updated


**Bugfixes**

- No longer using Arduinos

## Version 1.1.0 (10/21/2024)

This release focuses on camera functionality by implementing basic object detection.


**Features**

- Swapped Camera Raspberry Pi with NVIDIA Jetson Orin Nano
- Added AI object detection overlayed on video stream using Jetson Inference detectNet


**Minor Changes**

- Updated documentation


**Bugfixes**

- 

## Version 1.2.0 (11/19/2024)

This release further implements object detection and classification.


**Features**

- Fully set up Jetson
- Improved detectNet object detection overlays
- Created a separate program for plant classification using PlantNet-300K


**Minor Changes**

- Heavily updated documentation with instructions, notes, and lessons learned


**Bugfixes**

- Fixed OpenCV GStreamer pipeline issues and installation issues (fixes reflected in [README](../../README.md#camera-initialization))