'''
Project: Earthrover Robot
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in

'''

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

import os, time
import ctypes, glob, re

# this file sits at the app root, so the tree can live anywhere
APP = os.path.dirname(os.path.realpath(__file__))


def setting(key, default):
    #one value from config.txt, the file the web UI writes. Missing file or
    #key gives the default, so the rover still runs without it.
    try:
        for line in open(APP + "/config.txt"):
            k, _, v = line.partition("=")
            if k.strip() == key:
                return type(default)(v.strip())
    except (OSError, ValueError):
        pass
    return default


# How a frame is turned the right way up, per backend. Named the same way in
# config.txt, so the web UI and both camera paths agree.
FLIP_TRANSFORM = {                      # picamera2: (hflip, vflip)
    "none": (0, 0), "rotate_180": (1, 1),
    "horizontal_flip": (1, 0), "vertical_flip": (0, 1),
}
FLIP_CV2 = {                            # cv2.flip code; None means no call
    "none": None, "rotate_180": -1,
    "horizontal_flip": 1, "vertical_flip": 0,
}

# ---------------------------------------------------------------------------
# Coral USB Accelerator: detected, not configured by hand.
#
# This used to be `edgetpu = 1`, edited per machine. Neither default is right:
# ship 1 and a rover with no accelerator raises OSError behind an empty HTTP 500
# on the video feed; ship 0 and everyone who has one silently runs ~4.8x slower
# on CPU (230 ms vs 48 ms per inference). So detect it instead.
#
# Every module that needs this does `from util import edgetpu`, so this is the
# single place that decides.
# ---------------------------------------------------------------------------

# One device, two states: it enumerates as Global Unichip until the host pushes
# firmware to it, then re-enumerates as Google. Matching only the second would
# miss an accelerator that was plugged in but not yet used.
_CORAL_FALLBACK_IDS = {("1a6e", "089a"), ("18d1", "9302")}


def _coral_usb_ids():
    """The USB IDs to look for, taken from libedgetpu's own udev rules.

    Those rules are what grant userspace access to the device, so they cannot be
    narrower than what the installed runtime can actually drive - which makes
    them a better source than a list hardcoded here, and one that keeps working
    if a future revision ships new IDs. The known pair stays as a floor in case
    the rules file is moved or renamed.
    """
    ids = set(_CORAL_FALLBACK_IDS)
    pattern = re.compile(r'idVendor}=="([0-9a-fA-F]{4})".*?idProduct}=="([0-9a-fA-F]{4})"')
    for rules_dir in ("/usr/lib/udev/rules.d", "/lib/udev/rules.d", "/etc/udev/rules.d"):
        for rules_file in glob.glob(rules_dir + "/*edgetpu*.rules"):
            try:
                with open(rules_file) as fh:
                    ids.update((v.lower(), p.lower()) for v, p in pattern.findall(fh.read()))
            except OSError:
                pass
    return ids


def _coral_available():
    """True only if the accelerator is attached AND its runtime is installed.

    Both halves matter. Hardware without libedgetpu is exactly the combination
    that used to raise OSError behind an empty 500; libedgetpu without hardware
    fails later, inside load_delegate.

    Reads sysfs rather than shelling out to lsusb (usbutils is not guaranteed to
    be installed), and only dlopen()s the library - that does not claim the USB
    device, so it cannot interfere with the worker's own load_delegate a moment
    later.

    Deliberately NOT implemented by trying load_delegate: that claims the
    device, costs real time, and against a mismatched runtime it SEGFAULTS -
    which Python cannot catch, so a probe built that way would take
    the whole worker down instead of falling back to CPU.

    Covers the USB Accelerator only. The M.2 / mini-PCIe Corals are not on the
    USB bus at all (they appear as /dev/apex_N); that check is not here because
    there is no such device to test it against.
    """
    wanted = _coral_usb_ids()
    for vendor_path in glob.glob("/sys/bus/usb/devices/*/idVendor"):
        try:
            with open(vendor_path) as fh:
                vid = fh.read().strip()
            with open(vendor_path[:-len("idVendor")] + "idProduct") as fh:
                pid = fh.read().strip()
        except OSError:
            continue                      # device went away mid-scan
        if (vid.lower(), pid.lower()) in wanted:
            try:
                ctypes.CDLL("libedgetpu.so.1")
                return True
            except OSError:
                return False              # accelerator present, runtime missing
    return False


# EARTHROVER_EDGETPU=0 forces CPU (useful for benchmarking), =1 forces the
# accelerator. Unset - the normal case - means detect. Resolved once at import,
# i.e. once per worker start: ~16 ms attached, ~2 ms not.
_edgetpu_override = os.environ.get("EARTHROVER_EDGETPU")
edgetpu = int(_edgetpu_override) if _edgetpu_override in ("0", "1") else int(_coral_available())

m1_1 = 8
m1_2 = 11
m2_1 = 14 
m2_2 = 15 
cam_light = 17
headlight_right = 18
headlight_left = 27 
sp_light=9 


def init_gpio():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(m1_1,GPIO.OUT)
	GPIO.setup(m1_2,GPIO.OUT)
	GPIO.setup(m2_1,GPIO.OUT)
	GPIO.setup(m2_2,GPIO.OUT)
	GPIO.setup(cam_light,GPIO.OUT)
	GPIO.setup(headlight_right,GPIO.OUT)
	GPIO.setup(headlight_left,GPIO.OUT)
	# NOT sp_light (9). speaker_tts.py claims that line while it talks, and
	# under rpi-lgpio a second claim raises "GPIO not allocated" - which took
	# down every caller of this function that started mid-sentence.
	# red_light() claims it on demand instead.
	

def back():
    print("moving back!!!!!!")
    GPIO.output(m1_1, False)
    GPIO.output(m1_2, True)
    GPIO.output(m2_1, True)
    GPIO.output(m2_2, False)
    
def right():
	GPIO.output(m1_1, True)
	GPIO.output(m1_2, False)
	GPIO.output(m2_1, True)
	GPIO.output(m2_2, False)

def left():
	GPIO.output(m1_1, False)
	GPIO.output(m1_2, True)
	GPIO.output(m2_1, False)
	GPIO.output(m2_2, True)
	
def forward():
	GPIO.output(m1_1, True)
	GPIO.output(m1_2, False)
	GPIO.output(m2_1, False)
	GPIO.output(m2_2, True)
	
def stop():
	GPIO.output(m1_1, False)
	GPIO.output(m1_2, False)
	GPIO.output(m2_1, False)
	GPIO.output(m2_2, False)

def speak_tts(text,gender):
	cmd=("python3 " + os.path.dirname(os.path.realpath(__file__)) +
	     "/speaker/speaker_tts.py '" + text + "' " + gender + " &")
	os.system(cmd)
	
def camera_light(state):
	if(state=="ON"):
		GPIO.output(cam_light, True)
		#print("light on")
	else:
		GPIO.output(cam_light, False)
		#print("light off")
		
def head_lights(state):
	if(state=="ON"):
		GPIO.output(headlight_left, True)
		GPIO.output(headlight_right, True)
		#print("light on")
	else:
		GPIO.output(headlight_left, False)
		GPIO.output(headlight_right, False)
		#print("light off")
		
def red_light(state):
	# GPIO 9 is shared with speaker_tts.py and is decorative on both sides:
	# a blink here, a mouthpiece blink there. Claim it on first use; if the
	# speaker already has it, skip the blink and say so - an LED is never
	# worth taking down a detection loop for.
	try:
		# setmode is idempotent; red_light must not depend on init_gpio() first
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(sp_light, GPIO.OUT)   # claim on first use, no-op after
		GPIO.output(sp_light, state=="ON")
	except Exception as e:
		print("red_light: GPIO 9 unavailable -", e)
	
