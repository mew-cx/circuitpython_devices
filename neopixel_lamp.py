"""CircuitPython Capacitive Touch NeoPixel Brightness Control Example"""
import time
import board
import touchio
import neopixel

touch1 = touchio.TouchIn(board.TOUCH1)
touch2 = touchio.TouchIn(board.TOUCH2)

NUM_PIXELS = 4
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS, auto_write=False)

BRIGHTNESS_INCREMENT = 1.0/20.0
pixels.brightness = BRIGHTNESS_INCREMENT

pixels[0] = 0x880000
pixels[1] = 0x008800
pixels[2] = 0x000088
pixels[3] = 0x888888

last_touched = time.monotonic()
while True:
    if time.monotonic() - last_touched < 0.15:
        continue

    if touch1.value:
        pixels.brightness += BRIGHTNESS_INCREMENT
    elif touch2.value:
        pixels.brightness -= BRIGHTNESS_INCREMENT

    last_touched = time.monotonic()
    print(pixels.brightness)
    pixels.show()
