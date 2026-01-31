# https://gist.github.com/anecdata/1c345cb2d137776d76b97a5d5678dc97
# Check GPIO capabilities:

import microcontroller
import board
import digitalio
#import analogio

for pin in dir(microcontroller.pin):
    if isinstance(getattr(microcontroller.pin, pin), microcontroller.Pin):

        print("".join(("microcontroller.pin.", pin, " -->")), end=" ")
        for alias in dir(board):
            if getattr(board, alias) is getattr(microcontroller.pin, pin):
                print("".join(("", "board.", alias)), end=" ")
        print()

        try:
            print("DigitalIn:", end=" ")
            with digitalio.DigitalInOut(getattr(microcontroller.pin, pin)) as digital_in:
                digital_in.direction = digitalio.Direction.INPUT
                # digital_in.pull = digitalio.Pull.UP
                # digital_in.pull = digitalio.Pull.DOWN
                print(digital_in.value)
        except Exception as e:
            print(pin, e)

        try:
            print("DigitalOut:", end=" ")
            with digitalio.DigitalInOut(getattr(microcontroller.pin, pin)) as digital_out:
                digital_out.direction = digitalio.Direction.OUTPUT
                print(digital_out.value)
        except Exception as e:
            print(pin, e)

        try:
            print("AnalogIn:", end=" ")
            with analogio.AnalogIn(getattr(microcontroller.pin, pin)) as analog_in:
                print(analog_in.value)
        except Exception as e:
            print(pin, e)

        try:
            print("AnalogOut:", end=" ")
            with analogio.AnalogOut(getattr(microcontroller.pin, pin)) as analog_out:
                analog_out.value = 16384
                print("success")
        except Exception as e:
            print(pin, e)

        print()
