import asyncio
from datetime import datetime
from enum import Enum, IntEnum
import json
#from watchdog.events import FileSystemEventHandler
from collections import namedtuple
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
import websockets
import websockets

SPOT_TYPE = namedtuple('SPOT_TYPE', ['typeId', 'RGB_FREE', 'RGB_TAKEN']) 

PARKING_ID = 1

class SpotType(Enum):
    Default    = SPOT_TYPE(typeId = 1, RGB_FREE = (255, 0, 0),     RGB_TAKEN = (0, 255, 0))
    Handicaped = SPOT_TYPE(typeId = 2, RGB_FREE = (0, 0, 255),     RGB_TAKEN = (0, 255, 0))
    Charging   = SPOT_TYPE(typeId = 3, RGB_FREE = (255, 255, 255), RGB_TAKEN = (0, 255, 0))
    Reserved   = SPOT_TYPE(typeId = 4, RGB_FREE = (255, 255, 0),   RGB_TAKEN = (0, 255, 0))

class ParkingSpot():
    def __init__(self, deviceAddress, registerBit, spotType = SpotType.Default, active = True):
        self.deviceAddress    = deviceAddress
        self.registerBit      = registerBit
        self.spotType         = spotType
        self.active           = active
        self.taken            = False
        self.reserved         = False

    def __str__(self):
        return f'Parking Spot attached to Device with Address: {self.deviceAddress} and bit value of {self.registerBit}!'

class Sparkfun7Segment():
    __DEVICE_ADDR     = 0x71
    __BRIGHTNESS_ADDR = 0x7A
    __RESET_ADDR      = 0x76

    __DIGIT1_ADDR     = 0x7B
    __Digit2_ADDR     = 0x7C
    __Digit3_ADDR     = 0x7D
    __Digit4_ADDR     = 0x7E

    __BAUD_ADDR       = 0x7F
    __SMBus = None

    @staticmethod
    def Initialize(SMBus):
        #Initialize Communication Bus.
        Sparkfun7Segment.__SMBus = SMBus
        # #Assign Custom Address.
        # SMBus.write_byte_date(0x80, Sparkfun7Segment.__DEVICE_ADDR)
        #Assign BAUD Rate of 19200 (bps).
        #Sparkfun7Segment.setBaudRate(0x5)
        #Assign Max Brightness.
        Sparkfun7Segment.setBrightness(100)
        #Clear the display from previous updates.
        Sparkfun7Segment.resetDisplay()
        #Reset back to 0 each segment.
        SMBus.write_block_data(Sparkfun7Segment.__DEVICE_ADDR, Sparkfun7Segment.__DIGIT1_ADDR, [0, 0, 0, 0])

    @staticmethod
    def updateDisplay(totalTaken: int, totalAvailable: int):
        #Clear and Reset cursor to first segment.
        Sparkfun7Segment.resetDisplay()
        #Separate ones and tens places of the values in order to be displayed.
        Digit3 = (int)(totalTaken % 100 * .1)
        Digit4 = totalTaken % 10
        Digit1 = (int)(totalAvailable % 100 * .1)
        Digit2 = totalAvailable % 10
        Sparkfun7Segment.__SMBus.write_block_data(Sparkfun7Segment.__DEVICE_ADDR, Sparkfun7Segment.__DIGIT1_ADDR, [Digit1, Digit2, Digit3, Digit4])

    @staticmethod
    def resetDisplay():
        Sparkfun7Segment.__SMBus.write_byte(Sparkfun7Segment.__DEVICE_ADDR, Sparkfun7Segment.__RESET_ADDR)

    @staticmethod
    def setBrightness(value: int):
        Sparkfun7Segment.__SMBus.write_byte_data(Sparkfun7Segment.__DEVICE_ADDR, Sparkfun7Segment.__BRIGHTNESS_ADDR, value)

    @staticmethod
    def setBaudRate(value: int):
        Sparkfun7Segment.__SMBus.write_byte_data(Sparkfun7Segment.__DEVICE_ADDR, Sparkfun7Segment.__BAUD_ADDR, value)


class MCP23018():
    IO_01_ADDR = 0x20
    IO_02_ADDR = 0x27

    #Offset Addresses
    #--IO Direction (Input or Output).
    IODIRA  = 0x0
    IODIRB  = 0x1
    #--IO Polarity (1 or 0).
    IPOLA = 0x2
    IPOLB = 0x3
    #--IO State.
    GPIOA = 0x12
    GPIOB = 0x13   
    #--IO Pull-Up Resistors.
    GPIOAPU = 0x0C
    GPIOBPU = 0x0D
    #--IO State.
    OLATA = 0x14
    OLATB = 0x15  

    SMBus = None

    parkingSpots = dict()

    @staticmethod
    def Initialize(parkingSpots: dict, SMBus):
        #Initialize Communication Bus.
        MCP23018.SMBus = SMBus
        #Set GPIO-A Pins Configuration to INPUT for both IO Extenders.
        MCP23018.write_byte_data(MCP23018.IO_01_ADDR, MCP23018.IODIRA, 0xFF)
        MCP23018.write_byte_data(MCP23018.IO_02_ADDR, MCP23018.IODIRA, 0xFF)
        #Set GPIO-B Pins Configuration to OUTPUT for both IO Extenders.
        MCP23018.write_byte_data(MCP23018.IO_01_ADDR, MCP23018.IODIRB, 0x0)
        MCP23018.write_byte_data(MCP23018.IO_02_ADDR, MCP23018.IODIRB, 0x0)
        #Set GPIO-A Pull Up Resistors for both IO Extenders.
        #MCP23018.write_byte_data(MCP23018.IO_01_ADDR, MCP23018.GPIOAPU, 0xFF)
        #MCP23018.write_byte_data(MCP23018.IO_02_ADDR, MCP23018.GPIOAPU, 0xFF)
        #Set GPIO-B Pull Up Resistors for both IO Extenders.
        #MCP23018.write_byte_data(MCP23018.IO_01_ADDR, MCP23018.GPIOBPU, 0x0)
        #MCP23018.write_byte_data(MCP23018.IO_02_ADDR, MCP23018.GPIOBPU, 0x0)
        #Set GPIO-B Pins to On.
        MCP23018.write_byte_data(MCP23018.IO_01_ADDR, MCP23018.GPIOB, 0x0)
        MCP23018.write_byte_data(MCP23018.IO_02_ADDR, MCP23018.GPIOB, 0x0)
        #Invert Polarity of the A Port for both IO Extenders, for more convenience.
        #MCP23018.write_byte_data(MCP23018.IO_01_ADDR, MCP23018.IPOLA, 0xFF)
        #MCP23018.write_byte_data(MCP23018.IO_02_ADDR, MCP23018.IPOLA, 0xFF)
        #Initialize ParkingSpots by mapping them to the correct Bit and IO-Expander.
        
        for idx, spotId in enumerate(parkingSpots.keys()):
            if idx >= 7:
                MCP23018.parkingSpots.update({spotId: ParkingSpot(MCP23018.IO_01_ADDR, (idx + 1) % 8, SpotType.Default, parkingSpots[spotId]['spotActive'])})
            else:
                MCP23018.parkingSpots.update({spotId: ParkingSpot(MCP23018.IO_02_ADDR, (idx + 1) % 8, SpotType.Default, parkingSpots[spotId]['spotActive'])})
       
        print(MCP23018.parkingSpots[1])

    @staticmethod
    def getAllParkingSpots():
        return MCP23018.parkingSpots

    @staticmethod
    def getParkingSpotsState():
        return False

    @staticmethod
    def isSpotActive(spotId: int):
        if spotId in MCP23018.parkingSpots:
            parkingSpot = MCP23018.parkingSpots[spotId]

            byte_value = MCP23018.SMBus.read_byte_data(parkingSpot.deviceAddress, MCP23018.OLATB)

            return (byte_value & (1 << (parkingSpot.registerBit - 1))) == 0
        
        raise Exception(f"Spot with ID: {spotId} is non existent!")

    @staticmethod
    def isSpotTaken(spotId: int):
        if spotId in MCP23018.parkingSpots:
            parkingSpot = MCP23018.parkingSpots[spotId]

            byte_value = MCP23018.read_byte_data(parkingSpot.deviceAddress, MCP23018.GPIOA)
            
            return (byte_value & (1 << (parkingSpot.registerBit - 1))) == 0
            
        raise Exception(f"Spot with ID: {spotId} is non existent!")

    @staticmethod
    def isSpotReserved(spotId: int):
        MCP23018.SMBus.read_byte_data()
    
    @staticmethod
    def write_byte_data(i2c_address, register, data):
        MCP23018.SMBus.write_byte_data(i2c_address, register, data)

    @staticmethod
    def read_byte_data(i2c_address, register):
        return MCP23018.SMBus.read_byte_data(i2c_address, register)
   
# class FileModifiedHandler(FileSystemEventHandler):
#     def __init__(self, file_name, on_modified):
#         self.file_name = file_name
#         self.on_modified_callback = on_modified

#     def on_modified(self, event):
#         if event.event_type != 'modified':
#             return None

#         if event.is_directory:
#             return None

#         if event.src_path.endswith(self.file_name):
#             self.on_modified_callback()

#     def on_created(self, event):
#         pass

#     def on_moved(self, event):
#         pass

#     def on_deleted(self, event):
#         pass

# def checkIfProcessRunning(processName):
#     #Iterate over the all the running process
#     for proc in psutil.process_iter():
#         try:
#             # Check if process name contains the given name string.
#             if processName.lower() in proc.name().lower():
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#     return False

class ParkingEvent(IntEnum):
    System_Live              = 1,
    Echo_Slot_Status         = 2
    Open_Parking             = 3,
    Close_Parking            = 4,
    Open_Barrier             = 5,
    Close_Barrier            = 6,
    Activate_Parking_Slot    = 7,
    Deactive_Parking_Slot    = 8,
    Take_Parking_Slot        = 9,
    Free_Parking_Slot        = 10,
    Block_Entrance_Attempt   = 11,
    Lights_On                = 12,
    Lights_Off               = 13,
    Update_Workhours         = 14,
    Parking_Full             = 15,

class ParkingEventDto:
    def __init__(self, eventType: ParkingEvent, eventPayload: any):
        self.parkingLotId = PARKING_ID
        self.eventType    = eventType
        self.eventDate    = datetime.now()
        self.eventPayload = eventPayload

    def toJSON(self):
        return json.dumps(self.__dict__, default=str, sort_keys=True, indent=4)

class Parking:
    isOpened   = False,
    totalSpots = 0,
    totalFree  = 0,


class WebSocketClient(object):
    subscribers = None

    def __init__(self):
        self.conn = None

    async def connect(self, ws_url):
        async for websocket in websockets.connect(ws_url):
            self.websocket = websocket
            ws_recv_task: asyncio.Task = None
            try:
                #Create a separate coroutine for the Receiving End in non-blocking manner.
                ws_recv_task = asyncio.create_task(self.receive(websocket))
            except(ConnectionRefusedError, ConnectionClosed, ConnectionClosedError, ConnectionError):
                print('Websocket Client Connection has Closed Unexpectedly.')
            except WindowsError as e:
                print('Critical Error while trying to establish Web Socket connection!')
            finally:
                #ws_recv_task.cancel()
                await asyncio.sleep(12)
                print('Attempting Re-connection with Address: ', ws_url)
                continue
        return self.websocket

    async def send(self, msg):
        await self.websocket.send(msg)

    async def receive_handler(self):
        while(True):
            msg = await self.websocket.recv()
            for subscriber in len(self.subscribers):
                subscriber(msg)

    def subscribe(self, callback):
        self.subscribers.append(callback)

    async def close_connection(self):
        await self.websocket.close()
