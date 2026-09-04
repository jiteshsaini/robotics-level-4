#Project: Earthrover
#Created by: Jitesh Saini

import time,os
import sys

local_path=os.path.dirname(os.path.realpath(__file__))

print ("local_path: ", local_path)

status = sys.argv[1]

file_name="object_tracking.py"

if (status=="1"):
	print("starting Object Detection script")
	# Stop any previous instance first. Only one process can hold the
	# camera, so a second one produces a blank feed - and each extra
	# instance also competes for scarce RAM.
	# The camera has a single holder: release the MJPEG camera server
	os.system("sudo pkill -f cam_server.py")
	os.system("sudo pkill -f " + file_name)
	time.sleep(1)

	# Hand over the speed pins.
	#
	# generate_pwm.py runs continuously to serve the speed slider, and holds
	# GPIO 20 and 21 for software PWM. This worker drives the motors itself and
	# claims the same two pins, so the generator has to let go first: the kernel
	# allows only one owner of a GPIO line, and the second claim fails with
	# "GPIO not allocated", killing the worker before it can serve anything.
	os.system("sudo pkill -f generate_pwm.py")
	time.sleep(0.5)          # let the kernel release the lines


	cmd= "sudo python3 -u " + local_path + "/" + file_name + " > /var/www/html/earthrover/logs/object_tracking.log 2>&1 &"   # redirect: PHP waits on the inherited pipe (and /tmp is namespaced)
	print ("cmd: ", cmd)
	os.system(cmd)
	time.sleep(1) 
	

if (status=="0"):
	cmd= "sudo pkill -f " +  file_name
	os.system(cmd)

	# Give the speed pins back, so the slider works again.
	os.system("sudo python /var/www/html/earthrover/control_panel/pwm/pwm_control.py")

