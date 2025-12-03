# SPDX-FileCopyrightText: 2021 Kevin J. Walters
# SPDX-License-Identifier: MIT

import time
import board
import busio
from adafruit_sps30.i2c import SPS30_I2C

def some_reads(sps):
    PM_PREFIXES = ("pm10", "pm25", "pm40", "pm100")
    print("mass\tPM1\tPM2.5\tPM4\tPM10")
    for idx in range(5):
        data = sps.read()
        #print(data)
        print("\t{}\t{}\t{}\t{}".format(*[data[pm + " standard"] for pm in PM_PREFIXES]))
        time.sleep(0.1)

    print("ALL for last read")
    data = sps.read()
    for field in sps.FIELD_NAMES:
        print("{:s}: {}".format(field, data[field]))

def is_cleaning(sps):
    stat = sps.read_status_register()
    mask = sps.STATUS_FAN_CLEANING
    val  = stat & mask
    return bool(val)

def main():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
    sps30_fp = SPS30_I2C(i2c, fp_mode=True)
    print("Firmware version:", sps30_fp.firmware_version)

    sps30_fp.start()  # needed to return to "Measurement" mode
    print("reads after wakeup and start")
    some_reads(sps30_fp)

    # data sheet implies this takes 10 seconds but more like 14
    print("Fan clean (the speed up is audible)")
    t0 = time.monotonic()
    sps30_fp.clean(wait=4)
    for _ in range(60):
        #cleaning = bool(sps30_fp.read_status_register() & sps30_fp.STATUS_FAN_CLEANING)
        cleaning = is_cleaning(sps30_fp)
        print("c" if cleaning else ".", end="")
        if not cleaning:
            break
        time.sleep(0.5)
    t1 = time.monotonic()
    print(" took", t1-t0, "sec")
    print("reads after clean")
    some_reads(sps30_fp)

    print("END TEST")
    i2c.deinit()

main()
