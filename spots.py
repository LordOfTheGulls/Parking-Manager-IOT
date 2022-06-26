from smbus import SMBus
from helpers import ParkingEvent, ParkingEventDto, ParkingSpot, MCP23018, Sparkfun7Segment

def start_parking_spots(pipe2: Pipe):
    #Initialize I2C Communication Bus.
    #smbus = SMBus(1)
    #Initialize Parking Spots Display.
    #Sparkfun7Segment.Initialize(smbus)
    #Initialize Parking Spots.
    #MCP23018.Initialize(smbus)
    #Start Realtime Parking Spot detection.
    try:
        while True:
            sleep(3)

            parkingSpots = MCP23018.getAllParkingSpots()

            totalSpots, totalAvailable = 0, 0

            for idx, spotId in enumerate(parkingSpots.keys()):                  
                led_color = (0, 0, 0)

                parkingSpot: ParkingSpot = MCP23018.parkingSpots[spotId]

                if MCP23018.isSpotActive(spotId):
                    totalSpots = totalSpots + 1

                    if MCP23018.isSpotTaken(spotId): 
                        print(f'Spot [{spotId}] is Taken!')
                        led_color = parkingSpot.spotType.value.RGB_TAKEN
                    else:
                        print(f'Spot [{spotId}] is Free!')
                        led_color = parkingSpot.spotType.value.RGB_FREE

                        totalAvailable = totalAvailable + 1
            
            #pipe2.send(ParkingEventDto(ParkingEvent.Echo_Slot_Status, parkingSpots).__dict__)
            Sparkfun7Segment.updateDisplay(totalSpots, totalAvailable)
           
    except KeyboardInterrupt:
        print('Parking Sensors Process has been TERMINATED!')
    except IOError as error:
        print(error)
