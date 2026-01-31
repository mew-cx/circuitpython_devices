import board
import microcontroller as soc

def PinMap():
    pinlist = []
    for mpin in dir(soc.pin):

        mpin_attr = getattr(soc.pin, mpin)
        print("\tsoc.pin.", mpin, "=", mpin_attr)

        isinst_Pin = isinstance(mpin_attr, soc.Pin)
        print("\tisinstance(", mpin_attr, ",", soc.Pin, ") =", isinst_Pin)

        if isinst_Pin:
            pins = ["microcontroller.{}".format(mpin)]
            for bpin in dir(board):

                bpin_attr = getattr(board, bpin)
                print("\t\tboard.", bpin, "=", bpin_attr)

                isinst_mpin_attr = bpin_attr is mpin_attr
                print("\t\t", bpin_attr, "is", mpin_attr, "=", isinst_mpin_attr)

                if isinst_mpin_attr:
                    pins.append("board.{}".format(bpin))
            pinlist.append("\t".join(pins))
    return sorted(pinlist)

print("dir(soc.pin)", dir(soc.pin))
print("dir(board) ", dir(board))
for i in PinMap():
    print(i)
