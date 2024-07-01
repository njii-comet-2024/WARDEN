"""
sets up server for all vehicles to connect too
@author [Vito Tribuzio] [Snoopy-0]

Date last modified: 07/1/2024
"""

# Libraries
import socket
import sys

def serverProgram():
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
        data = c.recv(1024).decode()
        #if data is not recieved then break
        if not data:
            break

        print("from connected user: " + str(data))
        data = input(' -> ')
        c.send(data.encode())

    #Close the connection
    c.close()

serverProgram()
