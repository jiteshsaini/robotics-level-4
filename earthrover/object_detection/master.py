'''
Project: AI Robot - Object Detection
Author: Jitesh Saini
'''

import time,os
import sys

local_path=os.path.dirname(os.path.realpath(__file__))

print ("local_path: ", local_path)

status = sys.argv[1]

file_name="object_detection_web2.py"

if (status=="1"):
	print("starting Object Detection script")
	# Stop any previous instance first. Only one process can hold the
	# camera, so a second one produces a blank feed - and each extra
	# instance also competes for scarce RAM.
	# The camera has a single holder: release the MJPEG camera server
	os.system("pkill -f cam_server.py")
	os.system("pkill -f " + file_name)
	time.sleep(1)

	cmd= "python3 -u " + local_path + "/" + file_name + " > " + os.path.dirname(local_path) + "/logs/object_detection.log 2>&1 &"   # redirect: PHP waits on the inherited pipe (and /tmp is namespaced)
	print ("cmd: ", cmd)
	os.system(cmd)
	time.sleep(1) 
	

if (status=="0"):
	cmd= "pkill -f " +  file_name
	os.system(cmd)
