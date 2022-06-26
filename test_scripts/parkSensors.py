import RPi.GPIO as GPIO
#import tm1637
from time import sleep
import datetime

GPIO.setmode(GPIO.BOARD)
# IR sensor
GPIO.setup(11, GPIO.IN)
# red
GPIO.setup(15, GPIO.IN)
# green
GPIO.setup(13, GPIO.IN)

def blink(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def offLed(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def startParkSensors():
    while True:
        sensor4=GPIO.input(11)
        print(sensor4)
        if sensor4 == 1:
            print("Parking space is free")
            blink(13)
            offLed(15)
            sleep(1)
        elif sensor4 == 0:
            print("Parking space is taken")
            blink(15)
            offLed(13)
            sleep(1)
    GPIO.cleanup()
    
    
#def startDigitalDisplay():
  #  Display = tm1637.TM1637(23,24,tm1637.BRIGHT_TYPICAL)
  #  
  #  Display.Clear()
 #   Display.SetBrightnes(1)

#while(True):
   #now = datetime.datetime.now()
   #hour = now.hour
   #minute = now.minute
   #second = now.second
   #currenttime = [ int(hour / 10), hour % 10, int(minute / 10), minute % 10 ]
   #Display.Show(currenttime)
   #Display.ShowDoublepoint(second % 2)

   #time.sleep(1)
    


#startDigitalDisplay()
startParkSensors()