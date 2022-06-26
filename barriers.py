import math
import signal
from time import sleep
import cv2
import pandas as pd

from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2 import Picamera2, Preview, MappedArray

from functools import partial

import pytesseract
import imutils
import re

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
        licensePlateRegex = re.compile(r'([0-9a-zA-Z- ]+)', re.DOTALL)

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
                entrance_boxes = pd.DataFrame(results.head(1))
                #Preprocessing Stage.
                cropped = entranceImg[math.floor(entrance_boxes['ymin']):math.floor(entrance_boxes['ymax']), math.floor(entrance_boxes['xmin']):math.floor(entrance_boxes['xmax'])]
                cropped_resized = imutils.resize(cropped, width=416)
                cropped_gray = cv2.cvtColor(cropped_resized, cv2.COLOR_BGR2GRAY)
                cropped_equalized = cv2.equalizeHist(cropped_gray)
                cropped_denoised = cv2.fastNlMeansDenoising(cropped_equalized, None, 18, 7, 21) 
                cropped_binary = cv2.threshold(cropped_denoised, 0, 255, cv2.THRESH_OTSU)[1]
                
                licensePlateTxt = pytesseract.image_to_string(cropped_binary, lang='eng', config='--psm 7 --oem 3')

                licensePlateMatch = re.search(licensePlateRegex, licensePlateTxt)

                if licensePlateMatch is not None:
                    print('License Plate is: ', licensePlateMatch.group())

        #entrance_cam.stop_encoder()
        entrance_cam.stop()

    except Exception as err:
        print('There was an error with entrance camera: ', err)
    
    
    