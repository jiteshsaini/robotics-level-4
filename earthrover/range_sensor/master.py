#Project: Earthrover
#Created by: Jitesh Saini

import time,os
import sys

sys.path.insert(0, '/var/www/html/earthrover')
import util as ut

local_path=os.path.dirname(os.path.realpath(__file__))

status = sys.argv[1]
#ut.speak_tts(status,"f")

if (status=="1"):
	#print "starting 2 python scripts"
	os.system("sudo python /var/www/html/earthrover/range_sensor/range_sensor.py &")
	time.sleep(1) #should be equal to settling time of range sensor
	os.system("sudo python /var/www/html/earthrover/range_sensor/monitorSensor.py &")
	time.sleep(0.1)
	os.system("sudo python /var/www/html/earthrover/range_sensor/avoid_collision.py &")
	
	
if (status=="0"):
	
	ut.speak_tts("sensor off ","f")
	os.system("sudo pkill -f monitorSensor.py")
	time.sleep(0.1)
	os.system("sudo pkill -f range_sensor.py")
	time.sleep(0.1)
	os.system("sudo pkill -f avoid_collision.py")
	
	f1 = open(local_path+"/web/range.txt", "wb")
	f1.write("--")
	f1.close()
		


