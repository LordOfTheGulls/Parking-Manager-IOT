import os
from apscheduler.schedulers.background import BackgroundScheduler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from time import sleep


def test():
    print('File Modified')
    scheduler.add_job(test_func, 'date', run_date=date(2021, 12, 24), args=['John'])
    scheduler.add_job(test_func, 'date', run_date=date(2021, 12, 24), args=['Mary'])
    scheduler.add_job(test_func, 'date', run_date=date(2021, 12, 24), args=['Jack'])

if __name__ == '__main__':
    event_handler = FileModifiedHandler('workhours.csv', test)

    observer = Observer()

    observer.schedule(event_handler, r'C:\Users\Aleksandar\Desktop\RaspberryPi\test_scripts\workhours', recursive=False)

    observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()