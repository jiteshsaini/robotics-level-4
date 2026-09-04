#Project: Earthrover
#Created by: Jitesh Saini
#
# Ported from Python 2 to Python 3 (2026-08-30). Also: the original called
# `espeak`, which no longer ships on Raspberry Pi OS - `espeak-ng` replaced it
# and accepts the same arguments (verified: -ven-us+m5 -s120 ... --stdout).

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

import os, sys, shutil

text = sys.argv[1]
gender = sys.argv[2]

print("text to speech: ", text)
#print("gender: ", gender)

speaker_light = 9 #17

# The mouthpiece LED is decorative, and GPIO 9 has a second claimant:
# util.red_light(), used by human_following and object_tracking. Under
# rpi-lgpio only one process may hold a line, and losing it used to raise
# here - killing the speech along with the blink, before espeak ever ran.
# Speech is the point; the LED is not. Blink if we get the line, speak either
# way.
blink = None
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(speaker_light, GPIO.OUT)
    blink = GPIO.PWM(speaker_light, 3) #frequency
    blink.start(0)
    blink.ChangeDutyCycle(50) #start blinking the mouthpiece LED as the text is converted to speech
except Exception as e:
    print("speaker_tts: LED unavailable, speaking without it -", e)

# espeak-ng is the current package; fall back to espeak if an older image has it
TTS = "espeak-ng" if shutil.which("espeak-ng") else "espeak"

def alsa_device():
    """Pick an output ALSA actually has.

    With no /etc/asound.conf, ALSA defaults to card 0 - which on a Pi is HDMI.
    On a headless rover nothing is plugged into HDMI, so aplay fails with
    'audio open error: Unknown error 524' and the speaker is silent. Prefer the
    3.5mm jack when the board has one, addressed by CARD NAME because card
    indexes move between boots and boards. Boards without a jack (Pi 5) fall
    back to the default.
    """
    try:
        with open("/proc/asound/cards") as f:
            if "Headphones" in f.read():
                return " -D plughw:CARD=Headphones,DEV=0"
    except OSError:
        pass
    return ""

cmd_speak = (TTS + " -ven-us+" + gender + "5 -s120 " + "'" + text + "'" +
             " --stdout |aplay" + alsa_device())

print(cmd_speak)
os.system(cmd_speak)

if blink:
    blink.ChangeDutyCycle(0) #stop blinking the mouthpiece LED
    GPIO.output(speaker_light, False)
