#Project: Earthrover
#Created by: Jitesh Saini

import time,sys,os

sys.path.insert(0, '/var/www/html/earthrover')
import util as ut

#dynamically obtain path of current file
local_path=os.path.dirname(os.path.realpath(__file__))

ut.init_gpio()

while 1:
	
	f1 = open(local_path+"/web/range.txt", "r+")
	distance = f1.read(20);
	f1.close()
	
	print ("distance:", distance)
	
	#if due to some reason file is empty, ignore such occurance
	if (distance=="" or distance=="--"):
		print("blank file")
		continue
    	
	if(float(distance)<30): #to be removed from here, move to seperate python file
		ut.back()
		ut.speak_tts("obstacle detected","f")
		time.sleep(1)
		ut.stop()
	
	time.sleep(0.2)
