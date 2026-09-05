##########Project: Earthrover        #####################
##########Created by: Jitesh Saini   #####################

import os, time

os.system("pkill -f generate_pwm.py")
print("stopped !!!")

#time.sleep(0.1)

print("starting pwm")
os.system("python3 " + os.path.dirname(os.path.realpath(__file__)) + "/generate_pwm.py > /dev/null 2>&1 &")
print("started !!!")
