#! /bin/bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" || exit 10

SRC_ROOT="../HIDE"
TGT_DIR="$(pwd -P)"

SRC_DIR="${SRC_ROOT}/adafruit-circuitpython-bundle-20220630/lib/"
for i in adafruit_dotstar.mpy adafruit_ds1307.mpy adafruit_htu21d.mpy \
    adafruit_mpl3115a2.mpy adafruit_register neopixel.mpy adafruit_ntp.mpy
do
    echo "refreshing $i"
    [ -e "${SRC_DIR:?}/$i" ] || { echo "Source '$i' not found" >&2; exit 1; }
    rm -rf "${TGT_DIR:?}/$i"
    cp -a "${SRC_DIR}/$i" "${TGT_DIR}/$i"
done

SRC_DIR="${SRC_ROOT}/gits/Adafruit_CircuitPython_SPS30/"
for i in adafruit_sps30
do
    echo "refreshing $i"
    [ -e "${SRC_DIR:?}/$i" ] || { echo "Source '$i' not found" >&2; exit 1; }
    rm -rf "${TGT_DIR:?}/$i"
    cp -a "${SRC_DIR}/$i" "${TGT_DIR}/$i"
done

# vim: set sw=4 ts=8 et ic ai:
