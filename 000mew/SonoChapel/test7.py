# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2023-2025 Mike Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT
#
# rfid_experiment/test7/test7.py
# Developed using CircuitPython on Raspberry Pi Pico W.
# Read NTAG21x RFID tags using four PN532 sensor modules.
# Indicate which sensors are detecting tags using an LED strip.
# Part of the Sono Chapel position-sensing experiments.
# 2025-03-15

"""Sono Chapel Pod firmware"""

# About this code:
__version__ = "0.6.2.2"
__repo__ = "https://github.com/itchy-o/rfid_experiment.git"
__impl_name__ = 'circuitpython'         # sys.implementation.name
__impl_version__ = (9, 2, 1, '')        # sys.implementation.version
__board_id__ = "raspberry_pi_pico_w"    # board.board_id

# The version of sono_protocol.txt we implement here:
PROTOCOL_VERSION = const("0.1.0.3")

#############################################################################

# put this big file first, to minimize memory fragmentation
import tag_coords

import board
import busio
import time
import atexit
import os
import wifi
import socketpool
import supervisor
#from touchio import TouchIn
from neopixel import NeoPixel
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI
from micropython import const

#############################################################################

def reboot(reason):
    print("\nreboot() : reason", reason)
    supervisor.reload()

#############################################################################

class PodMessenger:
    "Send messages from pod to server via UDP over WiFi"

    def __init__(self):
        "Initialize from settings.toml"
        self._pod_id = const(os.getenv('SONOCHAPEL_POD_ID'))
        self._msg_delay = const(os.getenv('SONOCHAPEL_MSG_DELAY')/1000)
        self._server = (const(os.getenv('SONOCHAPEL_SERVER_IPADDR')),
                        const(os.getenv('SONOCHAPEL_SERVER_PORT')))
        self._infoLevel = os.getenv('SONOCHAPEL_INFO_LEVEL')
        self._sock = None       # a single socket we reuse forever
        self._seq = None        # the message sequence counter

    def connect(self):
        print("We are pod_id", self._pod_id,
            "mac", ":".join("{:02x}".format(i) for i in wifi.radio.mac_address))

        ssid   = os.getenv('CIRCUITPY_WIFI_SSID')
        passwd = os.getenv('CIRCUITPY_WIFI_PASSWORD')
        print("Connecting to SSID", ssid)
        wifi.radio.connect(ssid, passwd)

        print("We are pod_id", self._pod_id, "ip", wifi.radio.ipv4_address)
        print("Sending to", *self._server)

        pool = socketpool.SocketPool(wifi.radio)
        self._sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)

    def _send(self, type, data):
        packet = "%s %d %d %s" % (type, self._pod_id, self._seq, data)
        print(packet)
        self._sock.sendto(packet, self._server)
        self._seq += 1
        time.sleep(self._msg_delay)

    # Messages as defined by sono_protocol.txt:

    def sendBOOT(self):
        self._seq = 0
        data = "%s %s" % (PROTOCOL_VERSION, __version__)
        self._send("BOOT", data)

    def sendDATA(self, posx, posy, t1, num_tags):
        data = "%.3f %.3f %d %d" % (posx, posy, t1, num_tags)
        self._send("DATA", data)

    def sendINFO(self, infoLevel, data):
        if infoLevel >= self._infoLevel:
            self._send("INFO", data)

#############################################################################

class Sensor:
    "A single PN532 RFID sensor module"

    def __init__(self, i, spi, chip_select):
        self._i = i
        self._rfid_timeout = const(os.getenv('SONOCHAPEL_RFID_TIMEOUT')/1000)
        self.pn532 = None
        self.coord = None

        leds[self._i] = CYAN            # construct the sensor
        cs_pin = DigitalInOut(chip_select)
        try:
            self.pn532 = PN532_SPI(spi=spi, cs_pin=cs_pin, debug=False)
        except:
            pm.sendINFO(95, "Sensor %d not initializing" % i)
            leds[self._i] = RED         # sensor is disabled
            self.pn532 = None
            return

        pm.sendINFO(60, "Sensor %d firmware_version %s"
                % (i, self.pn532.firmware_version))
        self.pn532.SAM_configuration()

        self.power_down()
        leds[self._i] = BLACK           # sensor is idle

    def read(self):
        "Read the sensor, try to detect a tag, and lookup in table"
        leds[self._i] = WHITE           # sensor is reading
        id = None
        self.coord = None

        self.reset_pre_read()
        try:
            id = self.pn532.read_passive_target(timeout=self._rfid_timeout)
        except:
            leds[self._i] = YELLOW      # sensor error
            pm.sendINFO(90, "Sensor %d error" % self._i)
            # what to do: retry, ignore, reboot, disable sensor, etc?
            self.reset_post_error()
            return      # fallback in case reboot() is stubbed out

        self.power_down()
        leds[self._i] = BLACK           # sensor is idle

        if id is None:
            return      # no tag detected

        # Attempt to retrieve data from tag_coord mapping table
        tag_id = "".join("{:02x}".format(i) for i in id)
        tag_data = tag_coords.data.get(tag_id)
        pm.sendINFO(50, "Sensor %d tag_id %s tag_data %s"
                % (self._i, tag_id, tag_data))

        if tag_data is None:
            # unrecognized tag_id: bad read? ignore it
            leds[self._i] = MAGENTA
            return

        # Does this tag indicate a special command?
        if isinstance(tag_data, str):
            if tag_data.startswith("!REBOOT!"):
                reboot(reason=1)
                return      # fallback in case reboot() is stubbed out
            else:
                # Other special commands could go here
                return

        # Assuming data is 2-tuple with valid x,y coordinate.
        # assert isinstance(tag_data, tuple) and len(tag_data)==2
        leds[self._i] = GREEN
        self.coord = tag_data

    def reset_pre_read(self):
        self.pn532.reset()

    def reset_post_error(self):
        pm.sendINFO(42, "reset_post_error")
        self.pn532.reset()

    def power_down(self):
        # True if powered down successfully
        result = self.pn532.power_down()

#############################################################################

class SensorDeck:
    "The pod's collection of Sensors"

    # Pins for each Sensor's SPI chip-select (CS) signal:
    CS_GPIOS = (board.GP10, board.GP11, board.GP12, board.GP13)

    def __init__(self, spi):
        "Attempt to construct all the Sensors on this SensorDeck"
        self._prevCoord = (0,0) # Our previous averaged coordinate
        self._sensors = []      # List of SensorDeck's enabled Sensors
        for i, cs_gpio in enumerate(self.CS_GPIOS):
            s = Sensor(i, spi, cs_gpio)
            if s.pn532 is not None:
                self._sensors.append(s)

        num_sensors = len(self._sensors)
        pm.sendINFO(99, "SensorDeck has %d enabled sensors" % num_sensors)
        if num_sensors == 0:
            # no enabled sensors?!  try rebooting
            reboot(reason=10)
            sys.exit(10)        # fallback in case reboot() is stubbed out

    def readAll(self):
        "A generator as infinite iterator that reads all sensors once."
        while True:
            for s in self._sensors:
                s.read()
            yield

    def readOne(self):
        "A generator as infinite iterator that reads a single sensor."
        while True:
            for s in self._sensors:
                s.read()
                yield

    def coord(self):
        "Return the average of Sensors that have valid coordinates."
        n,x,y = 0,0,0
        for s in self._sensors:
            c = s.coord
            if c is not None:
                n += 1
                x += c[0]
                y += c[1]

        # If no Sensors have valid coords, return the previous coordinate.
        if n == 0:
            x,y = self._prevCoord
        else:
            x /= n
            y /= n
            self._prevCoord = x,y

        return n,x,y

#############################################################################

# Set up 5-LED neopixel strip
brightness = os.getenv('SONOCHAPEL_LED_BRIGHTNESS') / 100.0
leds = NeoPixel(pin=board.GP0, n=5, brightness=brightness, auto_write=True)

BLACK   = const(0)
BLUE    = const(0x0000ff)
GREEN   = const(0x00ff00)
CYAN    = const(0x00ffff)
RED     = const(0xff0000)
MAGENTA = const(0xff00ff)
YELLOW  = const(0xffff00)
WHITE   = const(0xffffff)

#############################################################################

pm = PodMessenger()

def main():
    leds.fill(GREEN)
    print("\n\nSono Chapel version", __version__, "protocol", PROTOCOL_VERSION)
    print("len(tag_coords.data)", len(tag_coords.data))

    pm.connect()
    leds.fill(BLUE)
    pm.sendBOOT()

    # touch1 = TouchIn(board.GP1)

    leds.fill(BLACK)
    spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP20)
    sd = SensorDeck(spi)

    for s in sd.readOne():
        t1 = False   # touch1.value
        leds[4] = GREEN if t1 else BLACK

        num_tags, x, y = sd.coord()
        pm.sendDATA(x, y, t1, num_tags)

@atexit.register
def shutdown():
    "Turn off LEDs when this code terminates"
    leds.fill(BLACK)
    leds.show()

# vim: set sw=4 ts=8 et ic ai:
