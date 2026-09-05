"""
camera_compat.py - a drop-in replacement for cv2.VideoCapture.

Why this exists
---------------
The rover's vision scripts were written for Raspberry Pi OS Buster, where the
`bcm2835-v4l2` kernel module presented the CSI ribbon camera as an ordinary
V4L2 device. `cv2.VideoCapture(0)` therefore just worked.

That module was removed in Bullseye. On Bookworm/Trixie `/dev/video0` is
`unicam` - the raw Bayer CSI receiver - so `cv2.VideoCapture(0)` opens the
device but `read()` never returns a frame. (Verified with 190 MB free, so it
is not a memory problem: OpenCV yields nothing while picamera2 captures fine.)

Rather than rewrite the capture loop in seven scripts, this class exposes the
same slice of the cv2.VideoCapture API those scripts actually use, and picks a
backend that works on the hardware present:

  1. V4L2 through OpenCV - so USB webcams keep working exactly as before
  2. picamera2           - for the CSI ribbon camera

Usage:
    import camera_compat
    cap = camera_compat.VideoCapture(0)
    ret, frame = cap.read()     # frame is BGR, as OpenCV expects
    cap.release()
"""

import os
import sys
import time
import cv2

# The web UI writes config.txt at the app root; this file sits there too.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
try:
    from util import setting, FLIP_CV2, FLIP_TRANSFORM
except Exception:                      # util needs GPIO; keep working without it
    FLIP_CV2 = {"none": None, "rotate_180": -1,
                "horizontal_flip": 1, "vertical_flip": 0}
    FLIP_TRANSFORM = {"none": (0, 0), "rotate_180": (1, 1),
                      "horizontal_flip": (1, 0), "vertical_flip": (0, 1)}
    def setting(key, default):
        try:
            path = os.path.dirname(os.path.realpath(__file__)) + "/config.txt"
            for line in open(path):
                k, _, v = line.partition("=")
                if k.strip() == key:
                    return type(default)(v.strip())
        except (OSError, ValueError):
            pass
        return default

CAM_INDEXES = 5        # /dev/video0..4, searched for a USB webcam
DEFAULT_SIZE = (640, 480)
WARMUP_SECONDS = 0.5      # AE/AWB settle time. Was 2.0; it is paid on every
                         # start, so it is 1.5s of the wait before the launch
                         # button appears.


class VideoCapture:
    """Mimics the part of cv2.VideoCapture the rover scripts use."""

    def __init__(self, src=0, size=DEFAULT_SIZE):
        self.backend = None
        self.error = None
        self._cap = None
        self._picam = None
        self._flip = None               # cv2.flip code for the v4l2 path
        self.size = size

        # Which camera, and which way up, come from config.txt so that the
        # video stream and the vision scripts agree rather than each guessing.
        want = setting("camera", "auto")            # auto | USB_cam | RPI_cam

        if want in ("auto", "USB_cam") and self._try_v4l2(src):
            self._flip = FLIP_CV2.get(setting("flip_USB_cam", "none"))
            return
        if want in ("auto", "RPI_cam"):
            self._try_picamera2(size)
        elif want == "USB_cam":
            print("camera_compat: camera=USB_cam but no webcam delivered a frame")

    # ---- backends ----------------------------------------------------

    def _try_v4l2(self, src):
        """A real V4L2 capture device, i.e. a USB webcam. Must actually
        yield a frame - on this OS /dev/video0 opens but never delivers.

        The webcam is not on a fixed index. A Pi numbers its own CSI receiver
        and codec blocks as /dev/video* too, so a webcam typically lands on
        video1 or later. Trying only the index we were handed found unicam,
        got no frame, and fell through to the ribbon camera - so a USB camera
        was never used even when one was plugged in.
        """
        for index in range(src, src + CAM_INDEXES):
            if self._open_v4l2(index):
                return True
        return False

    def _open_v4l2(self, src):
        try:
            # CAP_V4L2 explicitly. With a GStreamer-enabled OpenCV the default
            # backend builds a gst pipeline against unicam, which can never
            # deliver a frame - it failed slowly (7.4s measured under memory
            # pressure) before falling through to picamera2. V4L2 is also the
            # correct backend for the USB webcams this probe exists to serve:
            # it fails in 0.35s here and opens a real webcam normally.
            cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
            if cap.isOpened():
                for _ in range(3):
                    ok, frame = cap.read()
                    if ok and frame is not None:
                        self._cap = cap
                        self.backend = "v4l2"
                        print("camera_compat: usb webcam on /dev/video%d" % src)
                        return True
                    time.sleep(0.1)
            cap.release()
        except Exception as e:
            self.error = e
        return False

    def _try_picamera2(self, size):
        try:
            from picamera2 import Picamera2
            from libcamera import Transform
            p = Picamera2()
            # The sensor does the flip, so it costs nothing per frame.
            h, v = FLIP_TRANSFORM.get(setting("flip_RPI_cam", "none"), (0, 0))
            # picamera2's "RGB888" is B,G,R in memory order - already what
            # OpenCV expects, so no cvtColor is needed on the hot path.
            p.configure(p.create_video_configuration(
                main={"size": size, "format": "RGB888"},
                transform=Transform(hflip=h, vflip=v)))
            p.start()
            time.sleep(WARMUP_SECONDS)
            self._picam = p
            self.backend = "picamera2"
            return True
        except Exception as e:
            self.error = e
            return False

    # ---- cv2.VideoCapture-compatible surface -------------------------

    def isOpened(self):
        return self.backend is not None

    def read(self):
        """Returns (ok, frame) with frame in BGR, like cv2.VideoCapture."""
        if self.backend == "v4l2":
            ok, frame = self._cap.read()
            if ok and self._flip is not None:
                frame = cv2.flip(frame, self._flip)
            return ok, frame
        if self.backend == "picamera2":
            try:
                return True, self._picam.capture_array()
            except Exception as e:
                self.error = e
                return False, None
        return False, None

    def release(self):
        if self._cap is not None:
            try: self._cap.release()
            except Exception: pass
            self._cap = None
        if self._picam is not None:
            try:
                self._picam.stop()
                self._picam.close()
            except Exception: pass
            self._picam = None
        self.backend = None

    def set(self, prop, value):
        if self.backend == "v4l2":
            return self._cap.set(prop, value)
        return False        # picamera2 is configured at construction

    def get(self, prop):
        if self.backend == "v4l2":
            return self._cap.get(prop)
        if prop == cv2.CAP_PROP_FRAME_WIDTH:
            return float(self.size[0])
        if prop == cv2.CAP_PROP_FRAME_HEIGHT:
            return float(self.size[1])
        return 0.0

    def __del__(self):
        try: self.release()
        except Exception: pass
