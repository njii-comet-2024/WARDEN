from picamera2 import Picamera2
import cv2
import threading
import time
import os
import socket
import struct
import pickle

# Socket parameters
#centralIP = '192.168.110.78'  # Replace with central server's IP address
#centralPort = 9999

# Initialize socket
#clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#clientSocket.connect((centralIP, centralPort))
#connection = clientSocket.makefile('wb')


class FrameReader:
    def __init__(self, size):
        self.size = size
        self.queue = [None for _ in range(self.size)]
        self.offset = 0

    def pushQueue(self, data):
        self.offset = (self.offset + 1) % self.size
        self.queue[self.offset] = data

    def popQueue(self):
        self.offset = self.size - 1 if self.offset - 1 < 0 else self.offset - 1
        return self.queue[self.offset]


class Camera:
    debug = True
    is_running = False
    window_name = "Arducam PTZ Camera Controller Preview"
    frame = FrameReader(5)

    def start_preview(self, width=640, length=360):
        self.is_running = True
        self.capture_ = threading.Thread(target=self.capture_and_preview_thread, args=(width, length,))
        self.capture_.setDaemon(True)
        self.capture_.start()

    def stop_preview(self):
        self.is_running = False
        self.capture_.join()

    def close(self):
        if hasattr(self, "cam"):
            self.cam.stop()
            self.cam.close()

    def capture_and_preview_thread(self, width, length):
        if self.debug:
            os.environ['DISPLAY'] = ':0'
        self.cam = Picamera2()
        self.cam.configure(self.cam.create_still_configuration(main={"size": (width, length), "format": "RGB888"}))
        self.cam.start()
        while self.is_running:
            buf = self.cam.capture_array()
            self.frame.pushQueue(buf)
            cv2.imshow(self.window_name, buf)
            keyCode = cv2.waitKey(1)
            if keyCode == ord('q'):
                break
        cv2.destroyWindow(self.window_name)

    def getFrame(self):
        return self.frame.popQueue()

    #def sendVideo(self):
       # try:
           # while self.is_running:
              #  frame = self.getFrame()
              #  _, frame_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
               # data = pickle.dumps(frame_encoded, protocol=pickle.HIGHEST_PROTOCOL)
               # message = struct.pack("Q", len(data)) + data
               # connection.write(message)
               # connection.flush()
              #  time.sleep(0.1)  # Adjust delay based on desired frame rate
       # except socket.error as e:
          #  print(f"Socket error: {e}")
        #finally:
           # if connection:
              #  connection.close()


if __name__ == "__main__":
    tmp = Camera()
    tmp.start_preview()
    #tmp.sendVideo()
    time.sleep(5)  # Keep sending video for 5 seconds (adjust as needed)
    tmp.stop_preview()
