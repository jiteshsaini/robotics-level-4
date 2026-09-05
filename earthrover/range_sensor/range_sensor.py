#Project: Earthrover
#Created by: Jitesh Saini
#
# Ported from Python 2 to Python 3 (2026-08-30). On Buster `python` was
# Python 2; on Trixie `python-is-python3` makes it 3.13, so the old
# `print "..."` statements were a SyntaxError and this never started.

import RPi.GPIO as GPIO
import time,os

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import util as ut

local_path=os.path.dirname(os.path.realpath(__file__))


TRIG = 23 
ECHO = 24

# If the sensor is unplugged or miswired ECHO never changes, and an unbounded
# `while GPIO.input(ECHO)==0` spins at 100% CPU as root forever. Bound both
# waits: a missed reading is skipped instead of wedging the board.
#
# Timings measured on this hardware (2026-08-30): ECHO rises ~0.5 ms after the
# trigger, and when nothing is detected the module holds it high for a very
# consistent 138 ms before dropping. So the fall timeout must sit well above
# 138 ms, or it fires mid-timeout and looks like a stuck line.
ECHO_RISE_TIMEOUT = 0.10   # rise normally happens in well under 1 ms
ECHO_FALL_TIMEOUT = 0.25   # must exceed the ~138 ms no-echo hold
MAX_RANGE_CM      = 400    # HC-SR04 spec limit; ~23 ms round trip
OUT_OF_RANGE      = 999    # sentinel written when nothing is detected;
                           # the UI shows "-" for anything over 400

GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.output(TRIG, False)

ut.speak_tts("sensor ON","f")

print("Waiting For Sensor To Settle")
time.sleep(1) #settling time 

prev_distance=0

while 1:
	try:
		GPIO.output(TRIG, True)
		time.sleep(0.00001)
		GPIO.output(TRIG, False)

		# wait for the echo pulse to start
		timeout_at = time.time() + ECHO_RISE_TIMEOUT
		while GPIO.input(ECHO)==0 and time.time() < timeout_at:
			pass
		if GPIO.input(ECHO)==0:
			print("No echo pulse - sensor not responding (check wiring/power)")
			time.sleep(0.25)
			continue
		pulse_start = time.time()

		# wait for it to end
		timeout_at = time.time() + ECHO_FALL_TIMEOUT
		while GPIO.input(ECHO)==1 and time.time() < timeout_at:
			pass
		pulse_end = time.time()
		if GPIO.input(ECHO)==1:
			print("Echo never fell - sensor may be faulty")
			time.sleep(0.25)
			continue

		pulse_duration = pulse_end - pulse_start

		distance = pulse_duration * 17150

		distance = round(distance, 5)

		# A very long pulse is the module's no-echo timeout, not a real
		# reading: nothing is within range. Don't write the bogus 20-metre
		# figure, but do write a sentinel above MAX_RANGE_CM - the front-end
		# already renders anything over 400 as "-". Writing nothing at all
		# leaves the last real reading on screen, which looks like a live
		# value and is how the display came to appear frozen.
		if distance > MAX_RANGE_CM:
			print("Out of range - nothing detected within %d cm" % MAX_RANGE_CM)
			f1 = open(local_path+"/web/range.txt", "w")
			f1.write(str(OUT_OF_RANGE))
			f1.close()
			prev_distance = distance   # keep in sync so recovery isn't rejected
			time.sleep(0.25)
			continue
		
		diff = abs(distance - prev_distance)
		print("diff: ", diff)
		
		if (diff < 10):
			
			print("Distance:",distance,"cm |||| Prev_Distance:",prev_distance,"cm")
			#print distance,"cm"
    
			# text mode, not "wb": Python 3 refuses str on a binary handle
			f1 = open(local_path+"/web/range.txt", "w")
			f1.write(str(distance))
			f1.close()
	
		else:
			print("Error in rangeSensor calculation:", distance - prev_distance)
			
		
		
		prev_distance = distance
		time.sleep(0.25)
		
	except Exception as e: 
		ut.speak_tts(str(e),"f")   # speak_tts concatenates: must be a str
		pass

ut.speak_tts("closed range sensor","f")
