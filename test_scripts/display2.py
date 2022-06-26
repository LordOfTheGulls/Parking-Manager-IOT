from smbus2 import SMBus 
from time import sleep
from utils import Sparkfun7Segment

bus = SMBus(1)

bus.write_byte(Sparkfun7Segment.DEVICE_ADDR, 0x1)

sleep(3)

bus.write_byte(Sparkfun7Segment.DEVICE_ADDR, 0x3)