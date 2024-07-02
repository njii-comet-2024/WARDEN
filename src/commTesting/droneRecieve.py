import serial
import cv2
import numpy as np

def receive_data(serial_port, packet_size, total_packets):
    ser = serial.Serial(serial_port, 115200)
    data = bytearray()

    while len(data) < packet_size * total_packets:
        if ser.in_waiting:
            data.extend(ser.read(packet_size))
    
    ser.close()
    return data

def display_image(image_data, width, height):
    image = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width, 3))
    cv2.imshow('Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    serial_port = 'COM3'  # Adjust the COM port based on your setup
    packet_size = 32
    total_packets = 240 * 320 * 3 // packet_size  # Adjust based on the image resolution and color depth

    data = receive_data(serial_port, packet_size, total_packets)
    display_image(data, 320, 240)  # Adjust the width and height based on your image resolution
