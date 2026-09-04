#Project: Earthrover
#Created by: Jitesh Saini

import time,os
import sys

sys.path.insert(0, '/var/www/html/earthrover')
import util as ut

local_path=os.path.dirname(os.path.realpath(__file__))

status = sys.argv[1]
#ut.speak_tts(status,"f")

# Match the pattern the ML launchers already use:
#   -u        unbuffered, so a dying worker does not lose its last words
#   > log     PHP exec() waits on the inherited pipe; without a redirect the
#             children hold it open forever and ajax_rangeSensor.php hangs
#             until Apache times out. It also means tracebacks went to PHP,
#             which discarded them - that is why avoid_collision.py could die
#             on every toggle for months without leaving a trace.
# All three append to ONE log so the startup sequence reads in order. It must
# be ">>", not ">": three workers each truncating the same file would wipe the
# lines the previous one just wrote. Truncated once per toggle, below.
LOGFILE = "/var/www/html/earthrover/logs/range_sensor.log"
LOG = " >> " + LOGFILE + " 2>&1 &"

if (status=="1"):
	# stop any previous set first - repeated ON presses used to stack duplicate
	# monitorSensor.py watchdogs, all racing to pkill and restart the sensor
	os.system("sudo pkill -f range_sensor.py")
	os.system("sudo pkill -f monitorSensor.py")
	os.system("sudo pkill -f avoid_collision.py")
	time.sleep(0.2)

	open(LOGFILE, "w").close()          # one fresh log per toggle
	os.chmod(LOGFILE, 0o664)

	os.system("sudo python3 -u " + local_path + "/range_sensor.py" + LOG)
	time.sleep(1) #should be equal to settling time of range sensor
	os.system("sudo python3 -u " + local_path + "/monitorSensor.py" + LOG)
	time.sleep(0.1)
	os.system("sudo python3 -u " + local_path + "/avoid_collision.py" + LOG)
	
	
if (status=="0"):
	
	ut.speak_tts("sensor off ","f")
	os.system("sudo pkill -f monitorSensor.py")
	time.sleep(0.1)
	os.system("sudo pkill -f range_sensor.py")
	time.sleep(0.1)
	os.system("sudo pkill -f avoid_collision.py")
	
	f1 = open(local_path+"/web/range.txt", "w")   # text mode for Python 3
	f1.write("--")
	f1.close()
		


