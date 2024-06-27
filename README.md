[![python](https://img.shields.io/badge/python-3.10-blue.svg?style=flat&logo=python&logoColor=blue)](https://pypi.org/project/cookiecutter/)
[![license](https://img.shields.io/badge/license-mit-green.svg?logo=cachet&style=flat&logoColor=green)](https://choosealicense.com/licenses/)

---

# WARDEN -- COMET 2024
Wireless Assessment Rover with Drone Extended Network

</br>

https://github.com/https://github.com/njii-comet-2024/WARDEN

---

## Description

This repository holds the control code for the COMET 2024 internship project. 


This system is a deployable field recon ground vehicle. The objective is to extend the range of the ground vehicle by using an air vehicle, thus being able to cover more ground. 


This project is still a work in progress. 

---

## Definitions

**Rover:** The ground vehicle used for reconnaissance.


**Drone:** The air vehicle used to extend the rover's range.


**Central:** The laptop used to receive video footage from both vehicles.


**Rover Control:** The controller used to transmit movement controls to the rover.


**Drone Control:** The controller used to transmit movement controls to the drone.


**Ground Station:** Refers to all command controllers and receivers-- central, rover control, and drone control.

---

## Goals

- Communicate with both the ground and air vehicles to control them.
- Receive video feed from both the ground and air vehicles.
- Send commands to the ground vehicle through the air vehicle when connection is lost.

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