import math
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2 import Picamera2, Preview, MappedArray
import time
from time import sleep
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QApplication, QWidget
import torch
import os
import pandas as pd
import numpy

model = torch.hub.load(os.getcwd(), 'custom', source='local', path = 'static/best2.onnx')

boxes = pd.DataFrame()

def camera01_callback(request):
    with MappedArray(request, "main") as im:
        for idx, rect in boxes.iterrows():
            cv2.rectangle(im.array, (math.floor(rect['xmin']), math.floor(rect['ymin'])), (math.floor(rect['xmax']), math.floor(rect['ymax'])), (0, 255, 0, 0))
            #cv2.putText(im, 'Lice, (int(rect[0]*2) + 10, int(rect[1]*2) + 10), font, 1, (255,255,255),2,cv2.LINE_AA)
    
picam2 = Picamera2()

picam2.start_preview(Preview.QT)

picam2_config = picam2.preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}, buffer_count=3)

picam2.configure(picam2_config)

picam2.post_callback = camera01_callback

encoder = H264Encoder(1000000)

picam2.encoder.output = FileOutput(stream)
picam2.start_encoder()
picam2.start()

while True:
    boxes = pd.DataFrame()
    
    img = picam2.capture_array()

    imgRgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

    detection = model(imgRgb)

    results = detection.pandas().xyxy[0]

    if len(results) > 0:
        cropps = pd.DataFrame(results.crop(Save=False))['im']
        boxes  = pd.DataFrame(detect)
        
    sleep(1)
    
picam2.stop_encoder()
picam2.stop()
