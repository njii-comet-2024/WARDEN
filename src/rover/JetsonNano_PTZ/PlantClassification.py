# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

"""
Initializes camera, adds plant classification, sends packets to central

@author [Zoe Rizzo] [@zizz-0]

Date last modified: 11/20/2024
"""

import cv2
import cvzone
import time
import os
import math

try:
    from Queue import Queue
except ModuleNotFoundError:
    from queue import Queue

import threading
import signal
import sys
import socket
import base64
from jetson_inference import detectNet
from jetson_utils import cudaFromNumpy, cudaDeviceSynchronize
from PlantNet300k.utils import load_model
from torchvision.models import resnet18
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms
import torch
import json
import geocoder
import folium
from folium.plugins import MarkerCluster

#These are for WARDEN and should be same for EXT since they are static IPS
#RoverCam = 192.168.110.169
#Drone =  192.168.110.228
#Rover  = 192.168.110.19
#Central = 192.168.110.5

IP = '10.255.0.102'
PORT = 9999

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

# net = detectNet("ssd-mobilenet-v2", threshold=0.5)

def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=840,
    display_height=560,
    framerate=21,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "pixelformat=RG10, framerate=(fraction)%d/1 ! "
        "queue max-size-buffers=2 leaky=upstream ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

class FrameReader(threading.Thread):
    queues = []
    _running = True
    camera = None
    def __init__(self, camera, name):
        threading.Thread.__init__(self)
        self.name = name
        self.camera = camera
 
    def run(self):
        while self._running:
            _, frame = self.camera.read()
            while self.queues:
                queue = self.queues.pop()
                queue.put(frame)
    
    def addQueue(self, queue):
        self.queues.append(queue)

    def getFrame(self, timeout = None):
        queue = Queue(1)
        self.addQueue(queue)
        return queue.get(timeout = timeout)

    def stop(self):
        self._running = False

class Previewer(threading.Thread):
    window_name = "Arducam"
    _running = True
    camera = None
    def __init__(self, camera, name):
        threading.Thread.__init__(self)
        self.name = name
        self.camera = camera

        # Load the PlantNet model and class mappings
        self.filename = 'PlantNet300k/resnet18_weights_best_acc.tar'  # path to model weights
        self.use_gpu = False  # set to True if you have a GPU and want to use it
        self.device = torch.device("cuda" if self.use_gpu and torch.cuda.is_available() else "cpu")
        
        # Initialize model
        self.model = resnet18(num_classes=1081)  # 1081 classes in Pl@ntNet-300K
        load_model(self.model, filename=self.filename, use_gpu=self.use_gpu)
        self.model.to(self.device)
        self.model.eval()

        # Load JSON mappings
        with open("PlantNet300k/class_idx_to_species_id.json", "r") as f:
            self.class_idx_to_species_id = json.load(f)
        with open("PlantNet300k/plantnet300K_species_id_2_name.json", "r") as f:
            self.species_id_to_name = json.load(f)

        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # biodiversity map init
        self.species_clusters = {}
        self.mapPath = "plant_species_map.html"
        self.mapDataPath = "plant_species_data.json"

        self.mapData = self.loadMapData()
        self.map = self.loadOrCreateMap()

    """
    Loads biodiversity html map or creates it if it does not already exist
    """
    def loadOrCreateMap(self):
        if os.path.exists(self.mapPath) and self.mapData:
            lastMarker = self.mapData[-1]
            folium_map = folium.Map(location=[lastMarker['lat'], lastMarker['long']], zoom_start=15)
        else:
            folium_map = folium.Map(location=[0, 0], zoom_start=2)

        self.marker_cluster = MarkerCluster().add_to(folium_map)
        self.temp_cluster = MarkerCluster().add_to(folium_map)

        species_set = set()
        
        # adds existing species to map as markers
        for marker in self.mapData:
            if isinstance(marker.get('species'), list):
                for species in marker['species']:
                    species_set.add(species)
                    folium.Marker([marker['lat'], marker['long']], popup=species, title=species).add_to(self.marker_cluster)
            elif isinstance(marker.get('species'), str):
                species_set.add(marker['species'])
                folium.Marker([marker['lat'], marker['long']], popup=species, title=species).add_to(self.marker_cluster)

        return folium_map
    
    """
    Loads JSON data for map markers
    """
    def loadMapData(self):
        if os.path.exists(self.mapDataPath):
            with open(self.mapDataPath, 'r') as f:
                data = json.load(f)
                for marker in data:
                    if isinstance(marker.get('species'), str):
                        marker['species'] = [marker['species']]
                    print(marker['species'])
                return data
        return []

    """
    Saves map JSON data
    """
    def saveMapData(self):
        with open(self.mapDataPath, 'w') as f:
            json.dump(self.mapData, f, indent=4)
    
    """
    Adds a new marker to the map
    """
    def addMarker(self, lat, long, species, tolerance=0.00025):
        for marker in self.mapData:
            distance = math.sqrt((marker['lat'] - lat) ** 2 + (marker['long'] - long) ** 2)
            if distance < tolerance and species in marker['species']:
                return

        new_marker = {
            'lat': lat,
            'long': long,
            'species': [species],
            'popup': species
        }
        self.mapData.append(new_marker)
        folium.Marker([lat, long], popup=species, title=species).add_to(self.marker_cluster)

        self.saveMapData()
        self.saveMap()

    """
    Saves html map
    """
    def saveMap(self):
        self.map.save(self.mapPath)

    """
    Gets current coordinates based on IP address
    TEMPORARY FUNCTION -- will be replaced with GPS module so internet connection is not required
    """
    def getGPSCoordinates(self):
        g = geocoder.ip('me')
        if g.latlng:
            return g.latlng
        else:
            return None

    def run(self):
        global camTilt
        global camRotation
        global camZoom
        
        #Read Images
        hudTop = cv2.imread('hudCompassHorizontal.png', cv2.IMREAD_UNCHANGED)
        hudSide = cv2.imread('hudCompassHorizontal.png', cv2.IMREAD_UNCHANGED)
        hudTopIndicator = cv2.imread('arrow.png', cv2.IMREAD_UNCHANGED)
        hudSideIndicator = cv2.imread('arrow.png', cv2.IMREAD_UNCHANGED)
        infoBackground = cv2.imread('rectangle.png', cv2.IMREAD_UNCHANGED)
    
        #rotate and resize images to be properly aligned
        hudTop = cv2.rotate(hudTop, cv2.ROTATE_180)
        hudTop = cv2.resize(hudTop, (0, 0), None, 1.5, 1)
        hudSide = cv2.rotate(hudSide, cv2.ROTATE_90_CLOCKWISE)
        hudSide = cv2.resize(hudSide, (0, 0), None, 1.5, 1)
        hudSideIndicator = cv2.rotate(hudSideIndicator, cv2.ROTATE_180)
        hudSideIndicator = cv2.resize(hudSideIndicator, (0,0), None, .5, .5)
        hudTopIndicator = cv2.rotate(hudTopIndicator, cv2.ROTATE_90_COUNTERCLOCKWISE)
        hudTopIndicator = cv2.resize(hudTopIndicator, (0, 0), None, .5, .5)
        infoBackground = cv2.resize(infoBackground, (0, 0), None, .9, .9)
        
        #Connect to server Socket
        bufferSize = 65536
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)

        self._running = True
        while self._running:
            frame = self.camera.getFrame(2000)
            if frame is None:
                continue

            # Convert the frame to PIL format for preprocessing
            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            input_tensor = self.preprocess(pil_frame).unsqueeze(0).to(self.device)
                
            imgResult = cvzone.overlayPNG(frame, hudTop, [210, -85])  # Adds top HUD
            imgResult = cvzone.overlayPNG(imgResult, hudSide, [-130, 120])  # Adds side HUD
            imgResult = cvzone.overlayPNG(imgResult, infoBackground, [30, 455])  # Info background
            
            imgResult = cv2.putText(imgResult, 'Zoom: ' + str(camZoom), (40, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            tilt = self.numToRange(camTilt, 0, 180, 180, 0)
            imgResult = cv2.putText(imgResult, 'Tilt: ' + str(tilt) + ' | Rotation: ' + str(camRotation), (40, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            #overlay indicator
            imgResult = cvzone.overlayPNG(imgResult, hudTopIndicator, [(camRotation * 5) - 60, -20])#adds moving vertical
            imgResult = cvzone.overlayPNG(imgResult, hudSideIndicator, [-15, (camTilt * 5) - 500])

            # Run the model and get predictions
            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = F.softmax(output, dim=1)  # Get class probabilities
                confidence, predicted_class = torch.max(probabilities, 1)  # Get max probability and class
                confidence = confidence.item()  # Get the confidence score as a float
                predicted_class = predicted_class.item()  # Get the class index as an integer

            confidence_threshold = 0.8

            if confidence >= confidence_threshold:
                # Get species name from class index
                species_id = self.class_idx_to_species_id.get(str(predicted_class))
                species_name = self.species_id_to_name.get(str(species_id), "Unknown Species")
                
                # Draw the prediction on the frame
                cv2.putText(imgResult, f"Species: {species_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                gpsCoordinates = self.getGPSCoordinates()
                if gpsCoordinates:
                    lat, long = gpsCoordinates
                    self.addMarker(lat, long, species_name)
                    self.saveMap()

            cv2.imshow(self.window_name, imgResult)
            
            frame = imgResult
            frame = cv2.resize(frame, (1024, 600))
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 20])
            message = base64.b64encode(buffer)
            clientSocket.sendto(message, (IP, PORT))
            
            keyCode = cv2.waitKey(16) & 0xFF
        cv2.destroyWindow(self.window_name)

    def start_preview(self):
        self.start()
    def stop_preview(self):
        self._running = False
        
    def numToRange(self, num, inMin, inMax, outMin, outMax):
        flSpeed = outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                        - outMin))
        return int(flSpeed)

class Camera(object):
    frame_reader = None
    cap = None
    previewer = None

    def __init__(self):
        self.open_camera()
        self.cameraRotation = 90
        self.cameraHeight = 90
        self.cameraTilt = 90
        self.cameraZoom = 8

    def open_camera(self):
        self.cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera!")
        if self.frame_reader == None:
            self.frame_reader = FrameReader(self.cap, "")
            self.frame_reader.daemon = True
            self.frame_reader.start()
        self.previewer = Previewer(self.frame_reader, "")

    def getFrame(self):
        return self.frame_reader.getFrame()

    def start_preview(self):
        self.previewer.daemon = True
        self.previewer.start_preview()

    def stop_preview(self):
        self.previewer.stop_preview()
        self.previewer.join()
    
    def close(self):
        self.frame_reader.stop()
        self.cap.release()
        
    def setCamTilt(self, setVal):
        global camTilt
        #mappedTilt = self.numToRange(setVal, 0, 180, 180, 0)
        #self.cameraTilt = mappedTilt
        #camTilt = self.cameraTilt
        self.cameraTilt = setVal
        camTilt = self.cameraTilt
    
    def setCamRotation(self, setVal):
        global camRotation
        mappedRotation = self.numToRange(setVal, 0, 180, 180, 0)
        self.cameraRotation = mappedRotation
        camRotation = self.cameraRotation
    
    def setCamZoom(self, setVal):
        global camZoom
        self.cameraZoom = setVal
        camZoom = self.cameraZoom
        
    """
    Maps a number from one range to another

    @param `num` : number to re-map
    @param `inMin` : original range min
    @param `inMax` : original range max
    @param `outMin` : target range min
    @param `outMax` : target range max

    @return (int) number mapped to new range
    """
    def numToRange(self, num, inMin, inMax, outMin, outMax):
        flSpeed = outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                        - outMin))
        return int(flSpeed)

if __name__ == "__main__":
    camera = Camera()
    camera.start_preview()
    time.sleep(10)
    camera.stop_preview()
    camera.close()