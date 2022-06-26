
import asyncio
from asyncio import Task
import csv
from datetime import datetime
from functools import partial
from msilib.schema import Error
from sched import scheduler
import sched
from time import sleep
from multiprocessing import Process, Pipe
from multiprocessing import Pipe
import psutil
from requests import request
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
import websockets
#from smbus import SMBus

from utils import FileModifiedHandler, ParkingSpot, MCP23018, checkIfProcessRunning

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

#logging.basicConfig(level=logging.INFO)

def start_parking_spots(pipe2):
    
    #Initialize I2C Communication Bus.
    #smbus = SMBus(1)

    #Initialize Parking Spots.
    MCP23018.Inititialize(None)

    #Start Realtime Parking Spot detection.
    try:
        while True:
            sleep(3)

            parkingSpots = MCP23018.getAllParkingSpots()

            spotsCapacity, spotsFree = 0, 0

            for idx, spotId in enumerate(parkingSpots.keys()):                  
                led_color = (0, 0, 0)

                parkingSpot: ParkingSpot = MCP23018.parkingSpots[spotId]

                print(spotId)

                if MCP23018.isSpotActive(spotId):
                    spotsCapacity = spotsCapacity + 1

                    if MCP23018.isSpotTaken(spotId): 
                        print(f'Spot [{spotId}] is Taken!')
                        led_color = parkingSpot.spotType.RGB_TAKEN
                    else:
                        print(f'Spot [{spotId}] is Free!')
                        led_color = parkingSpot.spotType.RGB_FREE

                        totalFreeSpots = totalFreeSpots + 1

            print(f'Parking Spaces: {spotsFree}/{spotsCapacity}')

	    #print(f'{total_free_spots}/{total_spots}')
                #led_sensor[idx] = led_color

            #sensor_leds.show()
             
            #tm.numbers(total_free_spots, len(parkingSpots))
           
    except KeyboardInterrupt:
        print('Parking Sensors Process has been TERMINATED!')
    except IOError as error:
        print(error)
        
def start_barriers():
    return

async def on_ws_receive(websocket):
    while(True):
        msg_rcv = await websocket.recv()
        print('Received: ', msg_rcv)

def open_parking():
    print('Opening Parking')

def close_parking():
    print('Closing Parking')

def schedule_workhours(getLatest: bool = False):
    week_workhours = list()

    if getLatest is True:
        print('Fetching Latest Workhours from Server')

    try:
        with open('workhours.csv') as f:
            fileReader = csv.DictReader(f)
            for row in fileReader:
                if row['date'] is not None:
                    week_workhours.append(row)
    except FileNotFoundError:
        print("Cannot find Parking's Workhours File!")
    finally:
        f.close()

    openTriggers, closeTriggers = list(), list()

    for wh in week_workhours:
        openDate  = datetime.strptime(f"{wh['date']} {wh['open_time']}",'%Y-%m-%d %H:%M:%S')
        closeDate = datetime.strptime(f"{wh['date']} {wh['close_time']}",'%Y-%m-%d %H:%M:%S')
        openTriggers.append(DateTrigger(run_date=openDate))
        closeTriggers.append(DateTrigger(run_date=closeDate))

    return (OrTrigger(openTriggers), OrTrigger(closeTriggers))

async def main():
    API_URL  = 'http://192.168.0.150:7156'
    WS_URL   = 'ws://192.168.0.150:7156/ws'
    TOKEN = ''

    parkingWorkHours = dict()

    try:

        scheduler = BackgroundScheduler(timezone="Europe/Sofia")
        openJob   = scheduler.add_job(func=open_parking,  trigger='date', replace_existing=True)
        closeJob  = scheduler.add_job(func=close_parking, trigger='date', replace_existing=True)
        weeklyJob = scheduler.add_job(func=partial(schedule_workhours, True), trigger='cron', second="10", replace_existing=True)
        (openTriggers, closeTriggers) = schedule_workhours(getLatest=True)
        openJob.reschedule(trigger=openTriggers)
        closeJob.reschedule(trigger=closeTriggers)
        scheduler.start()
        # observer = Observer()
        # observer.schedule(FileModifiedHandler('workhours.csv', workhours_partial), r'C:\Users\Aleksandar\Desktop\RaspberryPi', recursive=False)
        # observer.start()

    except RuntimeError:
        print('Scheduler Error!')
        # observer.stop()
        # observer.join()
    finally:
        print('Done')

    #workHoursScheduler.add_job()

    pipe1, pipe2 = Pipe() 

    #workhoursProcess    = Process(target = start_workhours_scheduler, args=(None,), daemon=True)
    #parkingSpotsProcess = Process(target = start_parking_spots, args=(pipe2,), daemon=True)

    async for websocket in websockets.connect(WS_URL):
        ws_recv_task: Task = None

        #if(not parkingSpotsProcess.is_alive()):
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
        except WindowsError as e:
            print('Critical Error while trying to establish Web Socket connection!')
        finally:
            ws_recv_task.cancel()

            await asyncio.sleep(12)

            print('Attempting Re-connection with Address: ', WS_URL)

            continue
    
    #observer.stop()

if __name__ == '__main__':
    asyncio.run(main())
