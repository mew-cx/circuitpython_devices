"""CircuitPython Capacitive Touch NeoPixel Brightness Control Example"""
import time
import board
import touchio
import neopixel
from rainbowio import colorwheel

touch1 = touchio.TouchIn(board.TOUCH1)
touch2 = touchio.TouchIn(board.TOUCH2)

NUM_PIXELS = 4
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS, auto_write=False)

BRIGHTNESS_INCREMENT = 1.0/20.0
pixels.brightness = BRIGHTNESS_INCREMENT

def rainbow(color_index):
    for led in range(NUM_PIXELS):
        pixel_index = (led * 256 // NUM_PIXELS) + color_index
        pixels[led] = colorwheel(pixel_index & 0xff)
    pixels.show()

last_touched = time.monotonic()
color = 0
while True:
    color += 1
    color &= 0xff

    rainbow(color)

    if time.monotonic() - last_touched < 0.15:
        continue

    if touch1.value:
        pixels.brightness += BRIGHTNESS_INCREMENT
    elif touch2.value:
        pixels.brightness -= BRIGHTNESS_INCREMENT

    last_touched = time.monotonic()
