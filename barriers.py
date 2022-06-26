import math
import signal
from time import sleep
import cv2
import pandas as pd

from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2 import Picamera2, Preview, MappedArray

from functools import partial

isParkingOpen = True

entrance_boxes, exit_boxes = pd.DataFrame(), pd.DataFrame()

def handler_stop_signals(signum, frame):
    global isParkingOpen
    isParkingOpen = False
    
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def entrance_cam_callback(request):
    with MappedArray(request, "main") as im:
        for idx, rect in entrance_boxes.iterrows():
            cv2.rectangle(im.array, (math.floor(rect['xmin']), math.floor(rect['ymin'])), (math.floor(rect['xmax']), math.floor(rect['ymax'])), (0, 255, 0, 0))

def start_barriers(neuralNet, showPreview: bool):
    try:
        entrance_cam = Picamera2()
        entrance_cam_config = entrance_cam.video_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}, buffer_count=1)    
        entrance_cam.configure(entrance_cam_config)

        entrance_cam.post_callback = entrance_cam_callback
    
        encoder = H264Encoder(1000000)
        
        #entrance_cam.encoder.output = FileOutput(stream)
        #entrance_cam.start_encoder()
        entrance_cam.start()
        
        while isParkingOpen:
            entrance_boxes = pd.DataFrame()
            
            entranceImg = entrance_cam.capture_array()

            entranceImgRGB = cv2.cvtColor(entranceImg, cv2.COLOR_BGR2RGB)

            detection = neuralNet(entranceImgRGB)

            results = detection.pandas().xyxy[0]

            if len(results) > 0:
                cropps = pd.DataFrame(results.crop(Save=False))['im']
                entrance_boxes = pd.DataFrame(results)

        #entrance_cam.stop_encoder()
        entrance_cam.stop()

    except Exception as err:
        print('There was an error with entrance camera: ', err)
    
    
    