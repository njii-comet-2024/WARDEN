"""
Transmits control code to rover

@author [Vito Tribuzio] [Snoopy-0]

Date last modified: 06/26/2024
"""

# Libraries
import socket

#create socket object
s = socket.socket()

#Define port for connection
port = 56789

#connect to the server on local computer
s.connect(('127.0.0.1', port))

#recieve data from the server and decoding to get string 
print(s.recv(1024).decode())

#close the connection
s.close()
