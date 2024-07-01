"""
sets up server for all vehicles to connect too
@author [Vito Tribuzio] [Snoopy-0]

Date last modified: 07/1/2024
"""

# Libraries
import socket
import sys

#create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#reserved a port on computer, can be anything
port = 56789

#bind to the port, no ip in ip field which makes server listen to request
s.bind(('', port))
print ("socket binded to %s" %(port))

#put socket into listening mode
s.listen(5)
print ("socket is listening")

while True:
    #establish connection with client
    c, addr = s.accept()
    print ('Got connection from', addr)

    #send message to the client. 
    c.send('connected successfully'.encode())

    #Close the connection
    c.close()

    break

#send commands to the drone to send to the ground vehicle
#def commands_to_drone(data):