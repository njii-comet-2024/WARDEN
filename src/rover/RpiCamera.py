from picamera2 import Picamera2
import cv2
import threading
import time
import os
from flask import Flask, Response

app = Flask(__name__)

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

camera = Camera()
camera.start_preview()

@app.route('/video_feed')
def video_feed():
    def gen_frames():
        while camera.is_running:
            frame = camera.getFrame()
            if frame is None:
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    flask_thread.setDaemon(True)
    flask_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        camera.stop_preview()
        camera.close()
