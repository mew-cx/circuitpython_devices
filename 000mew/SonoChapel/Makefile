# Makefile (for use on RaspberryPi)
# build a release

TGT = RELEASE.txt
MPY = tag_coords.mpy test7.mpy assign_xy.mpy

MPY_CROSS = ./mpy-cross-raspios-9.2.1
#MPY_CROSS = ./mpy-cross-windows-9.2.1.static.exe

.PHONEY: all
all: $(TGT) $(MPY)

$(TGT): FORCE
	> $@
	git describe --long --tags --dirty >> $@
	git remote -v | awk '/ \(fetch\)$$/ {print $$2}' >> $@
	date -Isec >> $@

%.mpy : %.py
	$(MPY_CROSS) $<

.PHONEY : clean clobber nuke
clean clobber nuke:
	-rm -f $(TGT) $(MPY)

.PHONEY: FORCE
FORCE:

# vim: set sw=8 ts=8 noet ic ai:
