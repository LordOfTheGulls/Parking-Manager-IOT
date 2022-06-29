from multiprocessing import Queue
import signal
from time import sleep
#from smbus import SMBus UNCOMMENT ON PERRY

from helpers import ParkingEvent, ParkingEventDto, ParkingSpot, MCP23018, Sparkfun7Segment

isParkingOpen = True

def handler_stop_signals(signum, frame):
    global isParkingOpen
    isParkingOpen = False
    
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def start_parking_spots(parkingSpots: dict, eventQueue: Queue):
    #Initialize I2C Communication Bus.
    #smbus = SMBus(1)
    #Initialize Parking Spots Display.
    #Sparkfun7Segment.Initialize(smbus)
    #Initialize Parking Spots.
    #MCP23018.Initialize(parkingSpots, smbus)
    #Start Realtime Parking Spot detection.
    try:
        while isParkingOpen:
            sleep(3)

            totalSpots, totalAvailable = 0, 0

            # for spotId in parkingSpots.keys():
            #     led_color = (0, 0, 0)

            #     if MCP23018.isSpotActive(spotId):
            #         parkingSpots[spotId]['spotActive'] = True

            #         totalSpots = totalSpots + 1

            #         if MCP23018.isSpotTaken(spotId): 
            #             parkingSpots[spotId]['spotTaken'] = True
            #             print(f'Spot [{spotId}] is Taken!')
            #             #led_color = parkingSpot.spotType.value.RGB_TAKEN
            #         else:
            #             parkingSpots[spotId]['spotTaken'] = False
            #             print(f'Spot [{spotId}] is Free!')
            #             #led_color = parkingSpot.spotType.value.RGB_FREE
            #             totalAvailable = totalAvailable + 1
            #     else:
            #        parkingSpots['spotActive'] = False

            #Sparkfun7Segment.updateDisplay(totalSpots, totalAvailable)

            #pipe.send(ParkingEventDto(ParkingEvent.Echo_Slot_Status, parkingSpots).__dict__)

    except KeyboardInterrupt:
        print('Parking Sensors Process has been TERMINATED!')
    except IOError as error:
        print(error)
