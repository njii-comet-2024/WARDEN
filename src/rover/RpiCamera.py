from picamera2 import Picamera2
import cv2
import threading
import time
import os
import Focuser
import cvzone

TOP_HORIZ = -70
TOP_VERT = 0

SIDE_VERT = -100
SIDE_HORIZ = -5
SIDE_ACTU = 340

MOTOR_STEP = 5
FOCUS_STEP = 5

camTilt = 90
camRotation = 90
camZoom = 8

class FrameReader():

    def __init__(self,size):
        self.size=size
        self.queue = [None for _ in range(self.size)]
        self.offset = 0

    def pushQueue(self,data):
        self.offset = (self.offset + 1) % self.size
        self.queue[self.offset] = data
    
    def popQueue(self):
        self.offset = self.size -1 if self.offset -1 <0 else self.offset -1
        return self.queue[self.offset]

class Camera():
    global camTilt
    global camRotation
    global camZoom
    
    def __init__(self):
        self.cameraRotation = 90
        self.cameraHeight = 90
        self.cameraTilt = 90
        self.cameraZoom = 8
       
    def setCamTilt(self, setVal):
        global camTilt
        self.cameraTilt = setVal
        camTilt = self.cameraTilt
    
    def setCamRotation(self, setVal):
        global camRotation
        self.cameraRotation = setVal
        camRotation = self.cameraRotation
    
    def setCamZoom(self, setVal):
        global camZoom
        self.cameraZoom = setVal
        camZoom = self.cameraZoom
        
    debug = True
    is_running = False
    window_name = "Arducam PTZ Camera Controller Preview"
    frame = FrameReader(5)
    #def set_cam_height(int n1):
       # pass
        
    def start_preview(self,width=1024,length=600):
        self.is_running = True
        self.capture_ = threading.Thread(target=self.capture_and_preview_thread, args=(width,length,))
        self.capture_.setDaemon(True)
        self.capture_.start()

    def stop_preview(self): 
        self.is_running = False
        self.capture_.join()

    def close(self):
        if(hasattr(self,"cam")):
            self.cam.stop()
            self.cam.close()

    def capture_and_preview_thread(self,width,length):
        global camTilt
        global camRotation
        global camZoom

        #Read Images
        hudTop = cv2.imread('/home/rover-camera/Downloads/hudCompassHorizontal.png', cv2.IMREAD_UNCHANGED)
        hudSide = cv2.imread('/home/rover-camera/Downloads/hudCompassHorizontal.png', cv2.IMREAD_UNCHANGED)
        hudTopIndicator = cv2.imread('/home/rover-camera/Downloads/arrow.png', cv2.IMREAD_UNCHANGED)
        hudSideIndicator = cv2.imread('/home/rover-camera/Downloads/arrow.png', cv2.IMREAD_UNCHANGED)
        infoBackground = cv2.imread('/home/rover-camera/Downloads/blackRectangle.png', cv2.IMREAD_UNCHANGED)
    
        #rotate and resize images to be properly aligned
        hudTop = cv2.rotate(hudTop, cv2.ROTATE_180)
        hudTop = cv2.resize(hudTop, (0, 0), None, 1.5, 1)
        hudSide = cv2.rotate(hudSide, cv2.ROTATE_90_CLOCKWISE)
        hudSide = cv2.resize(hudSide, (0, 0), None, 1.5, 1)
        hudSideIndicator = cv2.rotate(hudSideIndicator, cv2.ROTATE_90_COUNTERCLOCKWISE)
        hudSideIndicator = cv2.resize(hudSideIndicator, (0,0), None, .1, .1)
        hudTopIndicator = cv2.resize(hudTopIndicator, (0, 0), None, .1, .1)
        infoBackground = cv2.resize(infoBackground, (0, 0), None, 1, .6)
        infoBackground = cv2.rotate(infoBackground, cv2.ROTATE_90_CLOCKWISE)
        
        if self.debug == True:
            os.environ['DISPLAY'] = ':0'
        self.cam = Picamera2()
        self.cam.configure(self.cam.create_still_configuration(main={"size": (width, length),"format": "RGB888"}))
        self.cam.start()
        while self.is_running == True:
            
            buf = self.cam.capture_array()
            #adds indicator bars to HUD
            imgResult = cvzone.overlayPNG(buf, hudTop, [TOP_HORIZ, TOP_VERT]) # adds top Hud
            imgResult = cvzone.overlayPNG(imgResult, hudSide, [SIDE_HORIZ, SIDE_VERT]) #adds side hud
            imgResult = cvzone.overlayPNG(imgResult, infoBackground, [5, 540])# adds info background for ease of seeing words
            #create positional data variables
            #display location coords
            imgResult = cv2.putText(imgResult,' Zoom: ' + str(camZoom) + 'x', (40, 570), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0),2)
            imgResult = cv2.putText(imgResult, 'ValueY: ' + str(camTilt) + '  ValueX: ' + str(camRotation), (40, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0),2)
            #display max limit messages
            if(camTilt == 0 or camTilt == 180):
                imgResult = cv2.putText(imgResult, 'Y AXIS LIMIT REACHED' , (390, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            if(camRotation == 0 or camRotation == 205):
                imgResult = cv2.putText(imgResult, 'X AXIS LIMIT REACHED' , (390, 570), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            if(camZoom == 0 or camZoom == 10):
                imgResult = cv2.putText(imgResult, 'ZOOM LIMIT REACHED' , (650, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            #overlay indicator
            imgResult = cvzone.overlayPNG(imgResult, hudTopIndicator, [(camRotation * 5) + 60, TOP_VERT])#adds moving vertical
            imgResult = cvzone.overlayPNG(imgResult, hudSideIndicator, [SIDE_HORIZ, (camTilt * 2)+100])
            self.frame.pushQueue(imgResult)
            cv2.imshow(self.window_name,imgResult)
            keyCode = cv2.waitKey(1)
            if(keyCode == ord('q')):
                break
        cv2.destroyWindow(self.window_name)
    def getFrame(self):
        return self.frame.popQueue()

if __name__ == "__main__":
    tmp = Camera()
    
    tmp.start_preview()
    time.sleep(5)
    tmp.stop_preview()
