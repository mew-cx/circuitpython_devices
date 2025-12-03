This repo has several branches:
- main : the runtime environment, meant to be installed on the target device.
- docs : non-runtime, and often big, files.  Not meant for the device.


::::::::::::::
dust_clone.txt
::::::::::::::
# on temporary-attached dust RaspberryPi Zero:
cd /mnt/CIRCUITPY
git clone --separate-git-dir=/home/pi/gits/dust_runtime.git git@github.com:mew-cx/dust_runtime.git
mv dust_runtime/.git .
rmdir dust_runtime/
git checkout -f dust

::::::::::::::
dust.git
::::::::::::::
gitdir: /home/pi/gits/dust_runtime.git

