[![python](https://img.shields.io/badge/python-3.10-blue.svg?style=flat&logo=python&logoColor=blue)](https://pypi.org/project/cookiecutter/)
[![license](https://img.shields.io/badge/license-mit-green.svg?logo=cachet&style=flat&logoColor=green)](https://choosealicense.com/licenses/)

---

# WARDEN -- COMET 2024
Wireless Assessment Rover with Drone Extended Network

---

<details><summary><b>Contents</b></summary>

- [Description](Description)
- [Goals](Goals)
- [Changelog](Changelog)
- [Standards](Standards)

</details>

*Repository url:* https://github.com/https://github.com/njii-comet-2024/WARDEN

---

## Description

This repository holds the control code for the COMET 2024 internship project. 

</br>

This system is a deployable field recon ground vehicle. The objective is to extend the range of the ground vehicle by using an air vehicle, thus being able to cover more ground. 

</br>

This project is still a work in progress. 

---

## Goals

- Communicate with both the ground and air vehicles to control them.
- Receive video feed from both the ground and air vehicles.
- Send commands to the ground vehicle through the air vehicle when connection is lost.

---

## Changelog

Major changes will be documented in ![Changelog](docs/about/changelog.md). These changes will be tagged as a new version.

---

## Standards

### Comments

Multi-line comments at the beginning of every function explaining what it does, the return value, and any parameters.

</br>

Multi-line comments at the beginning of every class detailing the class's purpose, the author(s), and date last updated.

</br>

Single line comment before any complex code blocks.

</br>

**Tags**

- @author [author name] [author github username]
- @param `param name` [param description]

### Naming Conventions

Both variables and functions should be named using camel case (e.g. camelCase).