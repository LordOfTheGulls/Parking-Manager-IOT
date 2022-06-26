import RPi.GPIO as GPIO

pins = [4, 17, 27, 22, 23, 24, 18, 25, 5, 6, 12, 13, 19, 26, 16, 20, 21]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def controlParkingPins(pin, value):

      try:
          if pin in pins:

            GPIO.setup(pin, GPIO.IN)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, value)
                  
          else:
              print('Pin %s cannot be used!' %pin)
              
              
      except:
          print('Something wrong happened')
          
          
controlParkingPins(24, 0)