"""
Helper functions for air vehicle

@author [name] [github]

Date last modified: 06/26/2024
"""

# Libraries
import logging


class Helpers:
    def __init__(self, logger: logging.Logger, config: dict):
        """
        Constructor method to create an instance from the class with initial arguments and
        global variables
        :param logger: logger defined in the main file
        :param config: configuration parameters
        """
        # Global variables
        self.logger = logger
        self.config = config
        self.example_global_variable = "Hello World"

    # >>> Declare your own methods here <<<

    # ⌄⌄⌄ Example. Not actual methods, remove before code. ⌄⌄⌄
    def _private_method(self):
        """
        Explain here the usage of this method
        :return: None
        """
        self.logger.info(f'This "{self._private_method.__name__}" is a method from {Helpers.__name__}.')

    def public_method(self):
        """
        Explain here the usage of this method
        :return: None
        """
        self.logger.info(f'This "{self.public_method.__name__}" is a method from {Helpers.__name__}.')
        self._private_method()
        self.logger.info(f'This "{self.example_global_variable}" is a global variable.')  
    # ⌃⌃⌃ Example. Not actual methods, remove before code. ⌃⌃⌃
