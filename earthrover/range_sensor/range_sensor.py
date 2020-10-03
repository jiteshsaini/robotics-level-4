#Project: Earthrover
#Created by: Jitesh Saini

import RPi.GPIO as GPIO
import time,os

import sys
sys.path.insert(0, '/var/www/html/earthrover')
import util as ut

local_path=os.path.dirname(os.path.realpath(__file__))


TRIG = 23 
ECHO = 24

GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.output(TRIG, False)

ut.speak_tts("sensor ON","f")

print "Waiting For Sensor To Settle"
time.sleep(1) #settling time 

prev_distance=0

while 1:
	try:
		GPIO.output(TRIG, True)
		time.sleep(0.00001)
		GPIO.output(TRIG, False)

		while GPIO.input(ECHO)==0:
			pulse_start = time.time()

		while GPIO.input(ECHO)==1:
			pulse_end = time.time()

		pulse_duration = pulse_end - pulse_start

		distance = pulse_duration * 17150

		distance = round(distance, 5)
		
		diff = abs(distance - prev_distance)
		print "diff: ", diff
		
		if (diff < 10):
			
			print "Distance:",distance,"cm |||| Prev_Distance:",prev_distance,"cm"
			#print distance,"cm"
    
			f1 = open(local_path+"/web/range.txt", "wb")
			f1.write(str(distance))
			f1.close()
	
		else:
			print "Error in rangeSensor calculation:", distance - prev_distance
			
		
		
		prev_distance = distance
		time.sleep(0.25)
		
	except Exception as e: 
		ut.speak_tts(e,"f")
		pass

ut.speak_tts("closed range sensor","f")

