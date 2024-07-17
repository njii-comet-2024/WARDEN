"""
Sets up server for connection with pi on the drone. received video feed from external camera

@author [Vito Tribuzio][@Snoopy-0]

Date last modified: 07/15/2024
"""
import cv2
import socket
import struct
import pickle

# Socket parameters
host_ip = '0.0.0.0'
host_port = 5000

# Initialize socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host_ip, host_port))
server_socket.listen(5)
print("Listening for connections...")

# Accept connection
client_socket, addr = server_socket.accept()
print(f"Connection from: {addr}")
connection = client_socket.makefile('rb')

while True:
    # Read message length
    packed_msg_size = connection.read(struct.calcsize("Q"))
    if not packed_msg_size:
        break

    msg_size = struct.unpack("Q", packed_msg_size)[0]

    # Read message data
    data = b""
    while len(data) < msg_size:
        data += connection.read(msg_size - len(data))

    # Deserialize frame
    frame_data = data[:msg_size]
    frame = pickle.loads(frame_data)

    # Display frame
    cv2.imshow("Receiving Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
connection.close()
client_socket.close()
server_socket.close()
cv2.destroyAllWindows()
