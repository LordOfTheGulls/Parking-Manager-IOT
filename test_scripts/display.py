from operator import xor
import subprocess
import re

from smbus2 import SMBus 
from time import sleep

registries = {
    "DisplayRegistry": 0x71,
    "ClearDisplay": 0x76,
    "Brightness": 0x7A,
    "FirstSegment": 0x7B,
    "SecondSegment": 0x7C,
    "ThirdSegment": 0x7D,
    "FourthSegment": 0x7E,
    "FactoryReset": 0x81,
}

bus = SMBus(1)

matchRegex = "(?<=\s)+[0-9]{2}(?=\s)"

cmd = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)

registry = re.findall(matchRegex, cmd.stdout)

if registry:
    address = "0x" + registry[0]
    if address == "0x71":
        address = 0x71

        bus.write_block_data(address, registries["FirstSegment"], [0x4,0x2])
        bus.write_block_data(address, registries["ThirdSegment"], [0x5,0x1])

        sleep(3)
        bus.write_byte(address, registries["ClearDisplay"])

  
    else:
        print('Address %s is not the correct registry for the display!' % address)
else:
    print('No devices found connected to I2C pin.')