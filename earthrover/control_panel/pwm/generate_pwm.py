##########Project: Earthrover        #####################
##########Created by: Jitesh Saini   #####################

import RPi.GPIO as GPIO 
from time import sleep  # import sleep function from time module  
  
GPIO.setmode(GPIO.BCM)  # choose BCM numbering scheme  
  
GPIO.setup(20, GPIO.OUT)# set GPIO 20 as output pin
GPIO.setup(21, GPIO.OUT)# set GPIO 21 as output pin
  
pin20 = GPIO.PWM(20, 100)    # create object pin20 for PWM on port 20 at 100 Hertz  
pin21 = GPIO.PWM(21, 100)    # create object pin21 for PWM on port 21 at 100 Hertz  

pin20.start(0)              # start pin20 on 0 percent duty cycle (off)  
pin21.start(0)              # start pin21 on 0 percent duty cycle (off)  

###### read the disk file pwm1.txt for speed value#########################
f0 = open("/var/www/html/earthrover/control_panel/pwm/pwm1.txt", "r+")
str0 = f0.read(5)
f0.close()
str0=str0.strip()

duty = float(str0)
pin20.ChangeDutyCycle(duty) 
pin21.ChangeDutyCycle(duty) #same for pin21
print("duty= ",duty)

while True:
    sleep(1)
