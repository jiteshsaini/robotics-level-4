# Robotics Level 4 : On-board Machine Learning

**Updated to work with the latest Raspberry Pi OS (Trixie, Debian 13).**

<p align="left">
Visit the website: <a href='https://helloworld.co.in/term/robotics4' target='_blank'>
   <img src='https://raw.githubusercontent.com/jiteshsaini/files/main/img/logo3.gif' height='40px'>
</a> Youtube Channel:
<a href='https://www.youtube.com/channel/UC_2OyRNVCWCH8ipgmAoJ1mA' target='_blank'>
   <img src='https://raw.githubusercontent.com/jiteshsaini/files/main/img/btn_youtube_2.png' height='40px'>
</a>
</p>

Building on <a href='https://github.com/jiteshsaini/robotics-level-3'>Robotics Level 3</a>,
this level runs **machine learning on the robot itself**. The camera feed is
passed through a TensorFlow Lite model on the Pi — no cloud, no account, no
network round trip — and what the model sees drives the motors.

Everything from the earlier levels is still here: camera, lights, distance
sensor, speaker, the direction pad, and the phone-sensor pages.

## The five ML projects

| Project | What the robot does |
|---|---|
| **Object Detection** | Watches for one chosen object and raises an alarm on the control panel when it appears |
| **Object Tracking** | Follows a ball, with the camera view visible in a browser while it tracks |
| **Human Following** | Follows a person |
| **Image Classification** | Streams the camera view with the model's guess overlaid, and speaks the name of what it recognises |
| **Gesture Control** | Recognises hand gestures using a model trained with Google's Teachable Machine. Swap the model files in `earthrover/tm/` to teach it something else |

Each folder has its own `README.md` with the detail.

## Hardware

Everything from level 3, plus:

- **Google Coral USB Accelerator** — optional. The models run on the CPU
  without one; the Coral makes them roughly ten times faster. It is detected
  at runtime, so the same code works either way.

Some things worth knowing before you build this level:

- **512 MB boards need the desktop off.** On a Pi 3A+ with the desktop
  running, the detector ends up in swap and manages about 0.1 FPS instead of
  10. The installer's `--headless` flag turns the desktop off for you.
- Everything from level 3's pin map applies unchanged.

## Install

Two commands on a Raspberry Pi already running Raspberry Pi OS 12 or 13.

```bash
curl -fsSL https://raw.githubusercontent.com/jiteshsaini/robotics-level-4/main/earthrover/setup_level4.sh -o setup_level4.sh
```

```bash
bash setup_level4.sh
```

**Not with `sudo`** — the script calls `sudo` itself, and says so if you try.

On a 512 MB board add `--headless`, which boots to the console instead of
the desktop: with the desktop running the vision features end up in swap.
It also closes VNC, so it is not the default.

Downloading first, rather than piping into a shell, lets you read the script
before it runs.

It fetches the code and the ML models, installs them to
`/var/www/html/earthrover` and `/var/www/html/all_models`, and sets up
everything they need. An existing install is moved aside rather than
overwritten. Then open:

```
http://<your-pi-ip>/earthrover/
```

**Allow an hour or more on a first run.** The script brings the whole OS up to
date before installing the camera and vision packages, so they are not built
against an older kernel. Nothing reboots by itself — it tells you at the end if
a restart is needed.

### Other ways to run it

| | |
|---|---|
| `bash setup_level4.sh --no-code` | set up the environment only, leave the web root alone |
| `bash setup_level4.sh --fix-perms` | re-apply ownership on code you placed yourself |
| `bash setup_level4.sh --verify` | check everything end to end, change nothing |
| `bash setup_level4.sh --help` | the full list |

`--verify` is the one to reach for when something misbehaves: it needs no
password and touches nothing.

Tested on **Raspberry Pi OS Trixie (Debian 13)** on a Raspberry Pi 3A+.

## What the script did

1. Brought the OS fully up to date.
2. Installed Apache, PHP, the GPIO library, the camera stack, and the speech
   and audio tools.
3. Installed the TensorFlow Lite runtime (`ai-edge-litert`) and OpenCV.
4. Installed Coral USB Accelerator support — harmless if you do not have one.
5. Fetched the code and models into `/var/www/html`.
6. Gave the web server the group memberships and file ownership it needs.
7. Generated a self-signed certificate and switched on https, which the
   phone-sensor pages require.
8. Optionally switched the desktop off (`--headless`).

The GPIO library is `rpi-lgpio` rather than the older `RPi.GPIO`, because the
older one does not work on a Raspberry Pi 5. `raspi-gpio` was removed from
Raspberry Pi OS and `pinctrl` replaces it.

## Where things live

| Folder | Role |
|---|---|
| `control_panel/` | The main UI, direction pad, speed control |
| `vars.php`, `util.py` | Pin map and movement functions, for PHP and Python |
| `camera_lights/` | MJPEG video stream and the LED switching |
| `range_sensor/`, `speaker/` | Distance sensor and text to speech |
| `accelerometer/`, `compass/`, `voice_control/` | The phone-sensor control pages |
| `object_detection/`, `object_tracking/`, `human_following/`, `image_classification/`, `tm/` | The five ML projects |
| `logs/` | Worker output — the first place to look when an ML feature misbehaves |
| `all_models/` | The `.tflite` models and label files, alongside `earthrover/` |
| `setup_level4.sh` | The installer above |

Worker logs are written to `logs/` rather than `/tmp` on purpose: Apache gives
itself a private `/tmp`, so anything written there is invisible from a normal
shell.
