##########Project: Earthrover        #####################
##########Created by: Jitesh Saini   #####################

import os, time

os.system("pkill -f generate_pwm.py")
print("stopped !!!")

#time.sleep(0.1)

print("starting pwm")
# From /tmp: the GPIO library drops a working file in the launch directory,
# and the callers' cwd is not ours to rely on.
os.system("cd /tmp && python3 " + os.path.dirname(os.path.realpath(__file__)) +
          "/generate_pwm.py > /dev/null 2>&1 &")
print("started !!!")
