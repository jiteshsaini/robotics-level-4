#Project: Earthrover
#Created by: Jitesh Saini

import time,os

import sys
sys.path.insert(0, '/var/www/html/earthrover')
import util as ut

local_path=os.path.dirname(os.path.realpath(__file__))

prev_distance=0
counter=0
ut.speak_tts("monitoring","m")
while 1:	
	f0 = open(local_path+"/web/range.txt", "r+")
	distance = f0.read(15);
	f0.close()

	if(distance==prev_distance):
		counter=counter+1
	else:
		counter=0
	
	print (counter), distance
		
	
	
	if(counter==3):
		ut.speak_tts("restarting","m")
		os.system("sudo pkill -f range_sensor.py")
		print("stopped range_sensor.py !!!")
		time.sleep(0.1)
		os.system("python /var/www/html/earthrover/range_sensor/range_sensor.py &")
		print("started range_sensor.py !!!")

		
	prev_distance = distance
	time.sleep(0.7) #this should be more than file writing rate in range_sensor.py
		

