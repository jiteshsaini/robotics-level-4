##########Project: Earthrover        #####################
##########Created by: Jitesh Saini   #####################

import os, time

os.system("sudo pkill -f generate_pwm.py")
print("stopped !!!")

#time.sleep(0.1)

print("starting pwm")
os.system("python /var/www/html/earthrover/control_panel/pwm/generate_pwm.py &")
print("started !!!")
