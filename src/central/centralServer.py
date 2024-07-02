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

    #accept new connection
    c, addr = s.accept()
    print ('Got connection from', addr)

    data = input(' -> ')

    while True:
        #recieve data from client and print it
        #data = c.recv(1024).decode()
        #print("from connected user: " + str(data))

        #send data to the client
        c.send(data.encode())

        #if statement to break the cycle
        if data == 'endServer':
            break

        #take another input
        data = input(' -> ')

    #Close the connection
    c.close()

serverProgram()
