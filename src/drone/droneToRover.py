"""
Transmits control code to rover

@author [Zoe Rizzo] [@zizz-0]

Date last modified: 07/08/2024
"""

# Libraries
import socket
import pickle

DRONE_IP = '172.168.10.136'
CENTRAL_IP = '172.168.10.136'
PORT = 56789

"""
State interface used to determine and switch control state (from direct to drone)
Starts as direct control
0 --> direct
1 --> drone
"""
class ControlState:
    def __init__(self):
        self._state = 0

    """
    Switches control state from direct to drone (and vice versa)
    """
    def switch(self):
        if self._state == 0:
            self._state = 1
            print("Switching to drone")
        elif self._state == 1:
            self._state = 0
            print("Switching to central")
        else:
            pass # incorrect input
    
    """
    Returns the current state
    """
    def getState(self):
        return self._state

"""
Class that defines a drone as retransmitter and its functionality in retransmitting controls to rover
"""
class Retransmitter:
    """
    Initializes an instance of Retransmitter 
    """
    def __init__(self):
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvsock.bind((CENTRAL_IP, PORT))
        
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.on = True
        self.controlState = ControlState()

    def start(self):
        while self.on:
            self.receive()

    def receive(self):
        self.serializedControls, addr = self.recvsock.recvfrom(1024)
        controls = pickle.loads(self.serializedControls)
        if(controls["controlToggle"] > 0):
                self.controlState.switch()

        # Only retransmit if control state is drone
        if(self.controlState.getState() == 1):
            self.retransmit()

    def retransmit(self):
        self.sendsock.sendto(self.serializedControls, (DRONE_IP, PORT))

        print("Retransmitting")

retransmit = Retransmitter()
retransmit.start()