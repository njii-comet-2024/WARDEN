[![python](https://img.shields.io/badge/python-3.10-blue.svg?style=flat&logo=python&logoColor=blue)](https://pypi.org/project/cookiecutter/)
[![license](https://img.shields.io/badge/license-mit-green.svg?logo=cachet&style=flat&logoColor=green)](https://choosealicense.com/licenses/)

---

![WARDEN_Project](WARDEN_logo.png)

# NJII COMET Summer 2024 Internship Project

![W.A.R.D.E.N. Presentation](docs/WARDEN_presentation.pdf)

---

## Description

This repository holds the control code for the COMET 2024 internship project. 


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

**Central Raspberry Pi:** Runs programs `roverFeed.py` to receive rover video from Camera Raspberry Pi, `centralToRover.py` to send controls to Controls Raspberry Pi, `droneFeed.py` to receive drone video from Drone Raspberry Pi, and `analogDroneFeed.py` to receive analog drone video from Drone VTX. Also used to SSH into Camera Raspberry Pi to run `roverToCentral.py`.

**Controls Raspberry Pi:** Runs program `roverControls.py` to receive controls from Central Raspberry Pi and run them on rover.

**Camera Raspberry Pi:** Runs program `roverToCentral.py` to receive camera positions from Central Raspberry Pi and send rover back video to Central Raspberry Pi.

**Drone Raspberry Pi:** Runs `droneToCentral.py` to transmit digital drone video to Central Raspberry Pi.

**Drone VTX:** Transmits analog drone video to Central Raspberry Pi.

---

## Necessary Libraries

- [OpenCV](https://opencv.org/get-started/)
- [cvzone](https://pypi.org/project/cvzone/)
- [pygame](https://www.pygame.org/news)
- [picamera and picamera[array]](https://picamera.readthedocs.io/en/release-1.13/install.html)
- [RPI.GPIO](https://pypi.org/project/RPi.GPIO/)

---

## Changelog

Major changes will be documented in the ![Changelog](docs/about/changelog.md). These changes will be tagged as a new version.

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
