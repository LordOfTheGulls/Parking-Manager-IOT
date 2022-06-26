import asyncio
from asyncio import Task
import csv
from datetime import datetime, timedelta
from functools import partial
import json
import math
import multiprocessing
import cv2
import torch
import os
from sched import scheduler
from time import sleep
from multiprocessing import Process, Pipe
import warnings
from zoneinfo import ZoneInfo
from requests import request
from smbus import SMBus
from tzlocal import get_localzone

from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
import websockets

from barriers import start_barriers

from helpers import ParkingEvent, ParkingEventDto, ParkingSpot, MCP23018, Sparkfun7Segment

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.combining import OrTrigger, AndTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
import logging

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute",)
#logging.basicConfig(level=logging.INFO)

async def on_ws_receive(websocket):
    while(True):
        msg_rcv = await websocket.recv()
        print('Received: ', msg_rcv)

def open_parking(process: Process):
    print('Opening Parking')
    print(process)
    process.start()

def close_parking(process: Process):
    print('Closing Parking')
    print(process)
    process.terminate()

def switch_lights(on: bool):
    print('Switch Lights On')

def schedule_workhours(getLatest: bool = False):
    if getLatest is True:
        print('Fetching Latest Workhours from Server')

    openTriggers, closeTriggers = list(), list()

    try:
        with open(file='workhours.csv', mode='r') as file:
            fileReader = csv.DictReader(file)
            for row in fileReader:
                if row['date'] is not None:
                    if row['open_time'] is not None and row['close_time'] is not None:
                        openDate  = datetime.strptime(f"{row['date']} {row['open_time']}", '%Y-%m-%d %H:%M:%S')
                        closeDate = datetime.strptime(f"{row['date']} {row['close_time']}", '%Y-%m-%d %H:%M:%S')
                        openTriggers.append(CronTrigger(day_of_week=openDate.weekday(),hour=openDate.hour,minute=openDate.minute,second=openDate.second))
                        closeTriggers.append(CronTrigger(day_of_week=closeDate.weekday(),hour=closeDate.hour,minute=closeDate.minute,second=closeDate.second))
    except ValueError:
        print('File has incorrect format!')
    except FileNotFoundError:
        print("Cannot find Parking's Workhours File!")
    finally:
        file.close()
    
    return (OrTrigger(openTriggers), OrTrigger(closeTriggers))

async def main():
    API_URL = 'http://192.168.0.150:7156'
    WS_URL  = 'ws://192.168.0.150:7156/ws'
    TOKEN   = ''

    neuralNet = torch.hub.load(os.getcwd(), 'custom', source='local', path = 'static/yolov5m.onnx')

    parkingSpotsPipe1, parkingSpotsPipe2 = Pipe()

    #parkingSpotsProcess = Process(target = start_parking_spots, args=(parkingSpotsPipe2,), daemon=True)
    barriersProcess = Process(target = start_barriers, args=(neuralNet, False, ), daemon=True)
    
    barriersProcess.start()
    
    #parkingSpotsProcess.start()

    try:
        scheduler = BackgroundScheduler(tz=get_localzone())

        (openTriggers, closeTriggers) = schedule_workhours(getLatest=True)

        #openJob  = scheduler.add_job(func=partial(open_parking, parkingSpotsProcess),  trigger=openTriggers, replace_existing=True)
        #closeJob = scheduler.add_job(func=partial(close_parking, parkingSpotsProcess), trigger=closeTriggers, replace_existing=True)
  
        #updateHoursCron = scheduler.add_job(func=partial(schedule_workhours, True), trigger=CronTrigger(year='*',month='*',day_of_week=0,hour=6,minute=0,second=0))

        #scheduler.start(False)
    except RuntimeError:
        print('Scheduler Error!')

    async for websocket in websockets.connect(WS_URL):
        ws_recv_task: Task = None

        #if(not parkingSpotsProcess.is_alive()):
            #parkingSpotsProcess.start()
        await asyncio.sleep(10)
        
        barriersProcess.terminate()
        
        try:
            #Create a separate coroutine for the Receiving End in non-blocking manner.
            ws_recv_task = asyncio.create_task(on_ws_receive(websocket))

            while(True):
                #print('Emitting From Main Socket')
                #print(parkingSpotsPipe1.recv())
                # if parkingSpotsPipe1.poll():
                #     print(parkingSpotsPipe1.recv())
                #await websocket.send(2)
                
                    #await websocket.send(json.dumps((parkingSpotsPipe2.recv())))
                # if not parkingSpotsPipe1.closed and parkingSpotsPipe1.poll:
                #     print(parkingSpotsPipe1.recv())
                #print(MCP23018.getAllParkingSpots())
                # if not pipe2.closed and pipe2.poll:          
                #     await websocket.send(pipe2.recv())
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
    
if __name__ == '__main__':
    asyncio.run(main())
