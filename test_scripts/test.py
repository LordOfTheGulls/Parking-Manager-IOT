import board
import neopixel
from time import sleep

pixels = neopixel.NeoPixel(board.D14, 10, brightness = 0.5)
pixels.fill((0, 0, 0))
sleep(2)
pixels.fill((255, 0, 0))
pixels.show()
print('test')