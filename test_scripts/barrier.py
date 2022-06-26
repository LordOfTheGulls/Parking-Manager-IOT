#!/usr/bin/env python
import sys
import cv2
import imutils
import numpy as np
import pytesseract
import re
from PIL import Image
from picamera.array import PiRGBArray
from picamera import PiCamera
import smtplib
import RPi.GPIO as GPIO
import time
from multiprocessing import Process
from threading import Thread

GPIO.setmode(GPIO.BOARD)
  
def filter_lp_chars(text):
    regex = "^[\\.{})(!@\\[\\]_=+-#\\$~\\^&]*$"
    return text.replace(regex, "")

def startBarriers():
    entranceBarrierP = Thread(target = startEntranceBarrier).start()
    #exitBarrierP = Thread(target = startExitBarrier).start()
    
def openBarrier(servoRef):
    servoDuty = 3
    # Loop for barrierMotorDuty values from 3 to 7 (0 to 60 degrees)
    while servoDuty <= 7:
        servoRef.ChangeDutyCycle(servoDuty)
        servoDuty = servoDuty + 1

def closeBarrier(servoRef):
    #turn back to 0 degrees
    servoRef.ChangeDutyCycle(3)
    time.sleep(0.5)
    servoRef.ChangeDutyCycle(0)

def imageToLicensePlate(image):
     text = None
     cropped = None
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grey scale
     #gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
     edged = cv2.Canny(gray, 30, 200) #Perform Edge detection
     cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
     cnts = imutils.grab_contours(cnts)
     cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
     screenCnt = None
     for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.010 * peri, True)
        if len(approx) == 4:
          screenCnt = approx
          break

     if screenCnt is None:
       print ("No License Plate Detected at Entrance!")
     else:
       cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 3)
       mask = np.zeros(gray.shape,np.uint8)
       new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
       new_image = cv2.bitwise_and(image,image,mask=mask)
       (x, y) = np.where(mask == 255)
       (topx, topy) = (np.min(x), np.min(y))
       (bottomx, bottomy) = (np.max(x), np.max(y))
       cropped = gray[topx:bottomx+1, topy:bottomy+1]
       text = pytesseract.image_to_string(cropped, config="--psm 11")
       text = filter_lp_chars(text)
     return text, cropped
       
def startEntranceBarrier():
    GPIO.setup(11,GPIO.OUT)
    entranceServo = GPIO.PWM(11,50) # Note 11 is pin, 50 = 50Hz pulse
    entranceServo.start(0)
    with PiCamera() as entranceCam:
        entranceCam.resolution = (1264, 784)
        entranceCam.framerate = 5
        entranceCam.brightness = 50
        entranceCam.contrast = 90
        entranceCamCapture  = PiRGBArray(entranceCam, size=(1264, 784))
        for frame in entranceCam.capture_continuous(entranceCamCapture, format="bgr", use_video_port=True):
                image = frame.array
                cv2.imshow("Entrance Barrier", image)
                key = cv2.waitKey(1) & 0xFF
                entranceCamCapture.truncate(0)
                if key == ord("s"):
                   text, cropped = imageToLicensePlate(image)
                   if text is not None and cropped is not None:
                       print(f'Detected License Plate Number at Entrance is: [{text}]')
                       cv2.imshow("Entrance Barrier", image)
                       cv2.imshow('Entrance Barrier - Cropped', cropped)
                       openBarrier(entranceServo)
                       time.sleep(4)
                       closeBarrier(entranceServo)
                       cv2.waitKey(0)
                elif key == ord('q'):
                    cv2.destroyWindow("Entrance Barrier")
                    cv2.destroyWindow("Entrance Barrier - Cropped")
                    cv2.waitKey(1)
                    break
        entranceCam.stop_preview()
        entranceCam.close()
        entranceServo.stop()
     
    
def startExitBarrier():
    GPIO.setup(13,GPIO.OUT)
    exitServo = GPIO.PWM(13,50) # Note 11 is pin, 50 = 50Hz pulse
    exitServo.start(0)
    with PiCamera() as exitCam:
        exitCam.resolution = (1264, 784)
        exitCam.framerate = 5
        exitCam.brightness = 50
        exitCam.contrast = 90
        exitCamCapture  = PiRGBArray(exitCam, size=(1264, 784))
        for frame in exitCam.capture_continuous(exitCamCapture, format="bgr", use_video_port=True):
                image = frame.array
                cv2.imshow("Exit Barrier", image)
                key = cv2.waitKey(1) & 0xFF
                exitCamCapture.truncate(0)
                if key == ord("s"):
                       text, cropped = imageToLicensePlate(image)
                       if text is not None and cropped is not None:
                           print(f'Detected License Plate Number at Exit is: [{text}]')
                           cv2.imshow("Exit Barrier -", image)
                           cv2.imshow('Cropped License Plate at Exit', cropped)
                           openBarrier(exitServo)
                           time.sleep(4)
                           closeBarrier(exitServo)
                           cv2.waitKey(0)
                elif key == ord('q'):
                    cv2.destroyWindow("Exit Barrier")
                    cv2.destroyWindow("Exit Barrier - Cropped")
                    cv2.waitKey(1)
                    break;
        exitCam.stop_preview()
        exitCam.close()
        exitServo.stop()
    
startBarriers()