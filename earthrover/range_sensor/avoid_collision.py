#Project: Earthrover
#Created by: Jitesh Saini

import time,sys,os

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import util as ut

#dynamically obtain path of current file
local_path=os.path.dirname(os.path.realpath(__file__))

ut.init_gpio()

while 1:
	
	f1 = open(local_path+"/web/range.txt", "r+")
	distance = f1.read(20);
	f1.close()
	
	# range_sensor.py truncates this file before rewriting it, so a reader can
	# catch it empty. Sleep here: `continue` skips the sleep at the bottom of
	# the loop, and without it this spins as fast as the CPU allows.
	if (distance=="" or distance=="--"):
		time.sleep(0.2)
		continue

	# Read every loop, so the gear icon in the panel applies without a restart.
	if(float(distance) < ut.setting("distance", 30)):
		ut.back()
		ut.speak_tts("obstacle detected","f")
		time.sleep(1)
		ut.stop()
	
	time.sleep(0.2)
