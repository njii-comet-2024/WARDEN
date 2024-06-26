"""
Control code for air vehicle

@author [name] [github]

Date last modified: 06/26/2024
"""

# Libraries

# Classes
from helpers import Helpers

class Control:

    global sitl
    global connection_string
    global vehicle

    def __init__(self):
        print("initializing")