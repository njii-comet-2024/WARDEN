[![python](https://img.shields.io/badge/python-3.10-blue.svg?style=flat&logo=python&logoColor=blue)](https://pypi.org/project/cookiecutter/)
[![license](https://img.shields.io/badge/license-mit-green.svg?logo=cachet&style=flat&logoColor=green)](https://choosealicense.com/licenses/)

![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi)
![nVIDIA](https://img.shields.io/badge/nVIDIA-%2376B900.svg?style=for-the-badge&logo=nVIDIA&logoColor=white)
![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)

---

![WARDEN_Project](WARDEN_logo.png)

# NJII COMET Summer/Fall 2024 Internship Project

Click ![here](docs/WARDEN_presentation.pdf) to view the full in-depth project report presentation from research to final designs.

---

## Contents

[Description](#description)

[Goals](#goals)

[Definitions](#definitions)

[Controller Components](#controller-components)

[Necessary Libraries](#necessary-libraries)

[Changelog](#changelog)

[Standards](#standards)

[Project Progress](#project-progress)

[NVIDIA Jetson Orin Nano Setup](#setting-up-nvidia-jetson-orin-nano)

---

## Description

This repository holds the control and communication code for the COMET 2024 internship project. This is an ongoing project.


The project, called W.A.R.D.E.N., is a deployable field recon system. It is comprised of a ground rover and aerial vehicle. The objective of the aerial vehicle is to extend the communication range of the ground rover for recon.

![W.A.R.D.E.N. Poster](docs/WARDEN_poster.png)
![W.A.R.D.E.N.](docs/WARDEN.png)
![Domain Model](docs/WARDENDomainModel.png)
![Controls](docs/controller_diagram.png)

---

## Goals

- Communicate with both the drone and rover to control them.
- Receive video feed from both the drone and rover.
- Extend the Wi-Fi range using the drone after the rover has lost connection.

---

## Definitions

**Rover:** The ground vehicle used for reconnaissance.


**Drone:** The aerial vehicle used to extend the rover's range.


**Central:** The Raspberry Pi used to receive video footage from both vehicles and display video footage and necessary feedback.


**Rover Control:** The controller used to transmit movement controls to the rover.


**Drone Control:** The controller used to transmit movement controls to the drone.


**Ground Station:** Refers to all command controllers and receivers and Wi-Fi network-- Central, rover control, drone control, and router.

---

## Controller Components

**Central Raspberry Pi** *(Raspberry Pi 4)*

Runs programs `roverFeed.py` to receive rover video from ~~Camera Raspberry Pi~~ Camera Jetson, `centralToRover.py` to send controls to Controls Raspberry Pi, `droneFeed.py` to receive drone video from Drone Raspberry Pi, and `analogDroneFeed.py` to receive analog drone video from Drone VTX. Also used to SSH into ~~Camera Raspberry Pi~~ Camera Jetson to run `roverToCentral.py`.

~~**Controls Arduino**  *(Arduino Uno)*~~ *Replaced with Raspberry Pi*

~~Runs program `roverControls.py` to receive controls from Central Raspberry Pi and run them on rover.~~ 


**Controls Raspberry Pi**  *(Raspberry Pi 4)*

Runs program `roverControls.py` to receive controls from Central Raspberry Pi and run them on rover.

~~**Camera Raspberry Pi:**  *(Raspberry Pi 4)*~~ *Replaced with NVIDIA Jetson.*

~~Runs program `roverToCentral.py` to receive camera positions from Central Raspberry Pi and send rover back video to Central Raspberry Pi.~~ 

**Camera Jetson**  *(NVIDIA Jetson Orin Nano)*

Runs program `roverToCentral.py` to receive camera positions from Central Raspberry Pi and send rover back video to Central Raspberry Pi.

**Drone Raspberry Pi**  *(Raspberry Pi Zero 2 W)*

Runs `droneToCentral.py` to transmit digital drone video to Central Raspberry Pi.

**Drone VTX** *([Rush Tank VTX 2.5w](https://www.amazon.com/Transmitter-Shell-Range-MultiRotor-Racing/dp/B0BRMMLVR2?crid=2CTFRSN8RZNY0&dib=eyJ2IjoiMSJ9.Ep95uNd_KIHQ_NfudOZkjacavk7IkO_HMLPncmSX4hPKJ7Htd1LIK6H60x-WQMAeLTqYsmTw-XttnXRyoeSBf7geDy-LK4m_Ot7ZY2xFTCmQStFHR1gcZK11FN3HuXEgWWCtCvLa-8XcAixjIzq05hXqyFlu579TaomtrKd2cAn0pWcRIo_2wtbg_gsOlwL5Lc7x0el0ZRvYCgYxnk1uQhFR9Y4B7VhYjrmgjpxs0zaKD-AAqNF5AVHNj0A6pspWuaGRUK2ncWSxe_jBvZKSVhbM2KBv1PThUY9bGBp_F8I.aXfZaHTuSs1NUDGYdNQBMw6FXfqc_P9ZIj2S3TazcPQ&dib_tag=se&keywords=rush+tank+solo&qid=1719510570&sprefix=rush+tank+solo%2Caps%2C142&sr=8-1))*

Transmits analog drone video to Central Raspberry Pi.


### The Switch to NVIDIA Jetson
The Camera Raspberry Pi was replaced with an NVIDIA Jetson Orin Nano to implement real-time object detection.

All Raspberry Pi programs are saved in this [folder](src/rover/raspi_cam_archive).

Orin Nano setup information can be found [here](#setting-up-nvidia-jetson-orin-nano).

---

## Necessary Libraries

- [OpenCV](https://opencv.org/get-started/)
- [cvzone](https://pypi.org/project/cvzone/)
- [pygame](https://www.pygame.org/news)
- ~~[picamera and picamera[array]](https://picamera.readthedocs.io/en/release-1.13/install.html)~~ Only used with Raspberry Pi
- [RPI.GPIO](https://pypi.org/project/RPi.GPIO/)

Used with NVIDIA Jetson Orin Nano:
- [jetson-utils](https://github.com/dusty-nv/jetson-utils)
- [jetson-inference](https://github.com/dusty-nv/jetson-inference)

---

## Changelog

Major changes will be documented in the ![Changelog](docs/about/changelog.md). These changes will be tagged as a new version.

Current Version: [v1.1.0](https://github.com/njii-comet-2024/WARDEN/releases/tag/v1.1.0)

---

## Standards

### Comments

Multi-line comments at the beginning of every function explaining what it does, the return value, and any parameters.


Multi-line comments at the beginning of every class detailing the class's purpose, the author(s), and date last updated.


Single line comment before any complex code blocks.


**Tags**

- @author `author name`: `author github username`
- @param \``param name`\`: `param description`
- @return \``variable name`\`: `variable description`

### Naming Conventions

Variables, functions, and classes should be named using camel case (e.g. camelCase).

---

## Project Progress

This project is ongoing since June 2024. Currently, all of the basic goals have been met and the system is fully functioning.

Ongoing and future changes surround the rover camera. The Camera Raspberry Pi has been swapped out with an NVIDIA Jetson Orin Nano to implement object detection and, in the future, possibly autonomy or semi-autonomy.

---

## Setting Up NVIDIA Jetson Orin Nano

NVIDIA Jetson Nanos can be a bit complicated to set up.

To flash a new Orin Nano, follow [this tutorial](https://developer.nvidia.com/embedded/learn/jetson-orin-nano-devkit-user-guide/software_setup.html). It requires a host machine that runs Ubuntu.

Any other set-up issues can be resolved by searching through [this guide](https://developer.nvidia.com/embedded/learn/get-started-jetson-orin-nano-devkit).

### Camera Initialization

Jetsons can be very picky with supported cameras. For Orin Nanos, many USB webcams are plug-and-play compatible. However, not many CSI cameras are plug-and-play since it can only support certain camera sensors. View [this list](https://developer.nvidia.com/embedded/jetson-partner-supported-cameras?t-1_supported-jetson-products=Orin) to see which cameras are compatible. Currently, this project uses an [Arducam B016712MP](https://www.uctronics.com/arducam-12mp-pan-tilt-zoom-ptz-camera-for-raspberry-pi-and-jetson-nano-b016712mp.html) (which uses an IMX477 sensor).

#### Arducam IMX477 Driver

ADD INFO HERE

### OpenCV

OpenCV needs to be built with GStreamer and GTK+ enabled.

Steps to install and build OpenCV for this project on Orin Nano:

\1. Download and install OpenCV:

`cd ~`\
`wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/heads/master.zip`\
`unzip opencv.zip`\
`cd opencv-master`

\2. Install dependencies for GTK+ and GStreamer:

`sudo apt-get update`\
`sudo apt-get install -y libgtk2.0-dev pkg-config`\
`sudo apt-get install -y libgtk-3-dev`\
`sudo apt-get install cmake g++ wget unzip`\
`sudo apt-get install libopencv-dev gstreamer1.0-tools gstreamer1.0-plugins-base`

\3. Ensure GStreamer path is accessible:

`echo $LD_LIBRARY_PATH`

You should see paths like `/usr/local/lib` or `/usr/lib/gstreamer-1.0/` in the output. If not, you will need to add LD_LIBRARY_PATH to the shell profile file:

`nano ~/.bashrc`

Add the following line to the end of the file:

`export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib/gstreamer-1.0:$LD_LIBRARY_PATH`

Apply the changes:

`source ~/.bashrc`

Confirm the changes were successful:

`echo $LD_LIBRARY_PATH`

\4. Clean (if already exists) and create your build directory:

`cd ~/opencv-master`\
`rm -rf build`\
`mkdir build`\
`cd build`

\5. Configure the build with GTK+ and GStreamer enabled:

`cmake -D WITH_GSTREAMER=ON -D WITH_QT=OFF -D WITH_GTK=ON -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ..`

\6. Build and install OpenCV:

`make -j4`\
`sudo make install`

\7. Verify installation:

`python3 -c "import cv2; print(cv2.getBuildInformation())"`

Look for GTK+ and GStreamer. Both should show they are enabled by specifying "ON"