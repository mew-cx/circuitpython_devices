# ntp_ds1307.py -- http://mew.cx/ 2022-06-04
# Set DS1307 RTC from NTP

from secrets import secrets
import wifi
import socketpool
#import ipaddress
import struct
import time
import board
import adafruit_ds1307

HOST = "pool.ntp.org"
PORT = 123
TIMEOUT = 5  #None

def DayOfWeek(wday):
    # https://docs.python.org/3/library/time.html#time.struct_time
    # describes tm_wday as "range [0, 6], Monday is 0"
    return ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[wday]

def NtpToUnixEpoch(seconds):
    # Convert 1900-01-01T00:00:00 to 1970-01-01T00:00:00
    return (seconds - 2208988800)

def GetNtp():
    print("connecting to AP", secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("my ipaddr", wifi.radio.ipv4_address)

    pool = socketpool.SocketPool(wifi.radio)

    #server_ipv4 = ipaddress.ip_address(pool.getaddrinfo(HOST, PORT)[0][4][0])
    #print("server ipaddr", server_ipv4)
    #print("ping time", wifi.radio.ping(server_ipv4), "ms")

    print("socket()")
    with pool.socket(pool.AF_INET, pool.SOCK_DGRAM) as sock:
        #sock.settimeout(TIMEOUT)

        # build packet
        packet = bytearray(48)
        packet[0] = 0b00100011  # Not leap second, NTP version 4, Client mode

        print("sendto()")
        sock.sendto(packet, (HOST, PORT))

        print("recvfrom()")
        size, address = sock.recvfrom_into(packet)
        print("size", size, "address", address)

        ntp_secs = struct.unpack_from("!I", packet, offset=len(packet) - 8)[0]
        return time.localtime(NtpToUnixEpoch(ntp_secs))


t = GetNtp()
print(t)

i2c = board.I2C()
ds = adafruit_ds1307.DS1307(i2c)
ds.datetime = t
print("{} {}-{:02}-{:02} {:02}:{:02}:{:02}".format(
    DayOfWeek(t.tm_wday),
    t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))

# eof
