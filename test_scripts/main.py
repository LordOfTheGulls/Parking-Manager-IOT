import asyncio
from asyncio import Task, exceptions
import functools
import logging
from msilib.schema import Error
import multiprocessing
from secrets import randbits
import signal

import threading
from threading import Event, Condition

from time import sleep
from multiprocessing import Process, Pipe
from typing import List
import random
from urllib import request

# from websockets import server

from multiprocessing import Pipe
from smbus2 import SMBus
# from websockets import server
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
from websockets.server import WebSocketServerProtocol
import websocket
import websockets

#from websocket_server import start_ws_server
#from pygpio import gpio as GPIO, connector
#LED Segment Display Library
#from tm1637 import TM1637

from utils import ParkingSpot, ParkingSpotType, MCP23018, SpotType


logging.basicConfig(level=logging.INFO)

#    parkingStatus: True|False  placeStatus: { 13: False, 14: True}
#   if(!parkingStatus) { print('1213')}

def start_parking_spots(pipe2):
    
    #Initialize I2C Communication Bus.
    smbus = SMBus(1)

    #Initialize Parking Spots.
    MCP23018.InititializeParkingSpots(smbus)

    #Start Realtime Parking Spot detection.
    try:
        while True:
            sleep(0.5)

            parkingSpots = MCP23018.getAllParkingSpots()

            total_spots      = 0
            total_free_spots = 0

            for idx, spotId in enumerate(parkingSpots.keys()):                  
                led_color = (0, 0, 0)

                parkingSpot: ParkingSpot = MCP23018.parkingSpots[spotId]

                if MCP23018.IsSpotActive(spotId):
                    total_spots = total_spots + 1

                    if MCP23018.isSpotTaken(spotId): 
                        led_color = parkingSpot.spotType.RGB_TAKEN
                    else:
                        led_color = parkingSpot.spotType.RGB_FREE

                        total_free_spots = total_free_spots + 1

                #led_sensor[idx] = led_color

            #sensor_leds.show()
             
            #tm.numbers(total_free_spots, len(parkingSpots))
            
            #if pipe2.poll():
            #parkingSpots = pipe2.recv()
            #print('RECEIVE FROM SUBPROCESS: ', parkingSpots[4].taken)
            #pipe2.send(parkingSpots[4].taken)
    except KeyboardInterrupt:
        print('Parking Sensors Process has been TERMINATED!')
    except IOError as error:
        print(error)
        #spotsQueue.put(parkingSpots)
        #emit on change detection
        #

    #GPIO.cleanup()

    # parking_spots = dict.fromkeys(gpio_pins, False)
    # conn.send(parking_spots)
    # while(True):
    #     parking_lots = {}
    #     copy_parking_spots = parking_spots.copy()
    #     sleep(3)
    #     for gpio_pin in gpio_pins: 
    #         parking_spots[gpio_pin] = bool(random.getrandbits(1))#GPIO.input(gpio_pin)
    #         if(parking_spots[gpio_pin] != copy_parking_spots[gpio_pin]):
    #             parking_spots.update({ gpio_pin: parking_spots[gpio_pin] })
    #             parking_lots.update({ gpio_pin: parking_spots[gpio_pin] })
    #     if parking_lots != {} :
    #         conn.send(parking_lots)
    #         parking_lots.clear()
    # conn.close()
def start_barriers():
    return

connected_clients: dict[any, WebSocketServerProtocol] = dict()

# async def websocket_client(URL):
#     print(URL)
#     async with websockets.connect(URL) as websocket:
#         try:
#             print('Client OK')
#             await websocket.send('test')
#             print(await websocket.recv())
#         except websockets.ConnectionClosed:
#             print('Closed')
#         except websockets.ConnectionRefused:
#             print('Refused')

# async def websocket_handler(websocket: WebSocketServerProtocol):
#     try:
#         connected_clients[websocket.id] = websocket
#         async for message in websocket:
#             print(message)
#         # while(True):
#         #     action = await websocket.recv()
#         #     await websocket.send('Wih')
#         #     print(action)
#     except(ConnectionClosed, ConnectionClosedError, ConnectionClosedOK, ConnectionError) as e: 
#         print(f'A Client has disconnected.')
#     finally:
#         connected_clients.pop(websocket.id)

# async def websocket_server(stop_event):
#     #partial = functools.partial(websocket_handler, c = c)
#     async with server.serve(websocket_handler, "localhost", 8765):
#         await asyncio.Future()
#         # while not stop_event.wait(1):
#         #     s = ''
#     print('Websocket Server Terminated!')


async def on_ws_receive(websocket):
    while(True):
        msg_rcv = await websocket.recv()
        print('Received: ', msg_rcv)

async def main():
    WS_URL   = 'ws://localhost:7156/ws'

    WS_TOKEN = ''

    MCP23018.Inititialize()

    pipe1, pipe2 = Pipe()

    parkSensorsProcess = Process(target = start_parking_spots, args=(pipe2), daemon=True)

    async for websocket in websockets.connect(WS_URL, extra_headers={"Authorization": f"Bearer {WS_TOKEN}"}):
        ws_recv_task: Task = None
        #parkingSpotsProcess.start()

        try:
            #Create a separate coroutine for the Receiving End in non-blocking manner.
            ws_recv_task = asyncio.create_task(on_ws_receive(websocket))

            while(True):
                #if pipe2.poll():
                #print(pipe2.recv())
                #await websocket.send('HELO')
                #await asyncio.sleep(2)
                #print(await websocket.recv())
                await websocket.send('Hello')

                await asyncio.sleep(2)

        except(ConnectionRefusedError, ConnectionClosed, ConnectionClosedError, ConnectionClosedOK, ConnectionError):
            print('Websocket Client Connection has Closed.')
        except WindowsError:
            print('Critical Error while trying to establish Web Socket connection!')
        finally:
            ws_recv_task.cancel()

            parkSensorsProcess.terminate()

            await asyncio.sleep(12)

            print('Attempting reconnection with Address: ', WS_URL)

            continue


    #parkSensorsProcess = Process(target = init_park_sensors, args=(pipe2, parkingSpots), daemon=True)
    
    #parkSensorsProcess.start()
    
    # websocket_thread = threading.Thread(target=asyncio.run, args=(websocket_client('ws://localhost:7156'),), daemon=True)
    # websocket_thread.start()
   
    
    #TO-DO: Fix Blocking by the await keyword
        # if(len(connected_clients) > 0):
        #     for clientId, client in connected_clients.items():
        #         if(client.open):
        #             await client.send("hELLO")
            #if(await socket.ensure_open()):

        #     print('ANOTHER LOOP')
        #print(wss.stop_server())
        # if pipe2.poll():
        #     action = pipe2.recv()
        
        #     pipe1.send(parkingSpots)
    #except KeyboardInterrupt:
        #return
        #stop_event.set()
        #websocket_thread.join()
    #finally:
        #print('Main Parking Process has been TERMINATED!')
        #exit(0)


if __name__ == '__main__':
    asyncio.run(main())