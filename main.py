import asyncio
from asyncio import Task
import csv
from datetime import datetime, timedelta
from functools import partial
import json
import math
import multiprocessing
from queue import Queue
import cv2
from matplotlib.font_manager import json_dump
import torch
import os
from time import sleep
from multiprocessing import Process, Pipe, Manager
from multiprocessing.managers import BaseManager
import psutil, os, time

import warnings
from zoneinfo import ZoneInfo
from requests import request
#from smbus import SMBus
from tzlocal import get_localzone

from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
import websockets

from spots import start_parking_spots
from barriers import start_barriers

from helpers import SPOT_TYPE, ParkingEvent, ParkingEventDto, ParkingSpot, MCP23018, Sparkfun7Segment, SpotType

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import Job
from apscheduler.triggers.combining import OrTrigger, AndTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
import copy
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
import logging

isOpen: bool = False

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings("ignore", message="The localize method is no longer necessary, as this time zone supports the fold attribute",)
logging.basicConfig(level=logging.INFO)

async def on_ws_receive(websocket):
    while(True):
        msg_rcv = await websocket.recv()
        print('Received: ', msg_rcv)

def open_parking(processes: list):
    for proc in processes:
        proc.start()

def close_parking(processes: list):
    for proc in processes:
        proc.terminate()
        proc.join()

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

    WS_URL  = f'ws://192.168.0.150:7156/ws'

    TOKEN   = ''

    with multiprocessing.Manager() as manager:
        eventQueue   = manager.Queue()
        barriers     = manager.dict({ 'entranceIsOpen': False, 'exitIsOpen': False, })
        parkingSpots = manager.dict({
             1: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             2: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             3: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             4: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             5: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             6: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             7: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             8: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
             9: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            10: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            11: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            12: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            13: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            14: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            15: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
            16: manager.dict({'spotTaken': False, 'spotType': 1, 'spotActive': True}),
        })

        mainProcess     = psutil.Process(os.getpid())
        slotsProcess    = Process(target = start_parking_spots, args=(parkingSpots, eventQueue,), daemon=True)
        barriersProcess = Process(target = start_barriers,      args=(eventQueue, ),              daemon=True)
    
        scheduledProcesses = [slotsProcess, barriersProcess]
        
        try:
            scheduler = BackgroundScheduler(tz = get_localzone())

            (openTriggers, closeTriggers) = schedule_workhours(getLatest=True)

            openJob  = scheduler.add_job(func = partial(open_parking,  scheduledProcesses), trigger=openTriggers,  replace_existing=True)
            closeJob = scheduler.add_job(func = partial(close_parking, scheduledProcesses), trigger=closeTriggers, replace_existing=True)

            #updateHoursCron = scheduler.add_job(func=partial(schedule_workhours, True), trigger=CronTrigger(year='*',month='*',day_of_week=0,hour=6,minute=0,second=0))
            #scheduler.start(False)
            slotsProcess.start()
        except RuntimeError:
            print('Scheduler Error!')

        async for ws in websockets.connect(WS_URL):
            ws_recv_task: Task = None

            parking_metadata = {
                'name': 'Parking Lot 1',
                'system_start_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mainProcess.create_time())),
                'is_open': isOpen,
                'gps': dict({ 'lat': 1, 'lon': 2 }),
                'total_slots': len(parkingSpots),
            }

            await ws.send(json.dumps(parking_metadata))

            try:
                #Create a separate coroutine for the Receiving End in non-blocking manner.
                ws_recv_task = asyncio.create_task(on_ws_receive(ws))

                while(True):
                    parking_echo = {
                        'is_open':       isOpen,
                        'slots_echo':    copy.deepcopy(dict(parkingSpots)),
                        'barriers_echo': dict(barriers)
                    }
                    await ws.send(json.dumps(parking_echo))
                    await asyncio.sleep(2)

            except(ConnectionRefusedError, ConnectionClosed, ConnectionClosedOK, ConnectionClosedError, ConnectionError):
                print('Websocket Client Connection has Closed.')
            except WindowsError as e:
                print('Critical Error while trying to establish Web Socket connection!', e)
            except Exception as e:
                print('Error while trying to establish Web Socket connection! ', e)
            finally:
                if(ws_recv_task is not None):
                    ws_recv_task.cancel()

                await asyncio.sleep(12)

                print('Attempting Re-connection with Address: ', WS_URL)

                continue
            
if __name__ == '__main__':
    asyncio.run(main())
