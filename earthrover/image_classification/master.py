'''
Project: AI Robot - Real-time Image Classification
Author: Jitesh Saini
'''

import time,os
import sys

local_path=os.path.dirname(os.path.realpath(__file__))

#print ("local_path: ", local_path)

status = sys.argv[1]

file_name="image_recog_cv2.py"

if (status=="1"):
	# Stop any previous instance first. Only one process can hold the camera,
	# so a second one produces a blank feed - and each extra instance also
	# competes for scarce RAM.
	os.system("sudo pkill -f " + file_name)
	# The camera has a single holder: release the MJPEG camera server too.
	os.system("sudo pkill -f cam_server.py")
	time.sleep(1)

	# -u so the log is unbuffered, and redirect it: the child otherwise holds
	# the web server's inherited stdout and PHP waits on that pipe forever.
	# Not /tmp - Apache runs with systemd PrivateTmp=yes, so anything written
	# there lands in a namespace invisible from a normal shell.
	cmd= ("sudo python3 -u " + local_path + "/" + file_name +
	      " > /var/www/html/earthrover/logs/image_classification.log 2>&1 &")
	print ("cmd: ", cmd)
	os.system(cmd)
	time.sleep(1) 
	

if (status=="0"):
	cmd= "sudo pkill -f " +  file_name
	os.system(cmd)
