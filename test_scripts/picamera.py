from picamera import PiCamera
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2

with PiCamera() as entranceCam:
    entranceCam.resolution = (1264, 784)
    entranceCam.framerate = 5
    entranceCam.brightness = 50
    entranceCam.contrast = 90
    entranceCamCapture  = PiRGBArray(entranceCam, size=(1264, 784))
    for frame in entranceCam.capture_continuous(entranceCamCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Entrance Barrier", image)

