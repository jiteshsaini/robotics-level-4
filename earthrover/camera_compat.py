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

import time
import cv2

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
        self.size = size

        if self._try_v4l2(src):
            return
        self._try_picamera2(size)

    # ---- backends ----------------------------------------------------

    def _try_v4l2(self, src):
        """A real V4L2 capture device, i.e. a USB webcam. Must actually
        yield a frame - on this OS /dev/video0 opens but never delivers."""
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
                        return True
                    time.sleep(0.1)
            cap.release()
        except Exception as e:
            self.error = e
        return False

    def _try_picamera2(self, size):
        try:
            from picamera2 import Picamera2
            p = Picamera2()
            # picamera2's "RGB888" is B,G,R in memory order - already what
            # OpenCV expects, so no cvtColor is needed on the hot path.
            p.configure(p.create_video_configuration(
                main={"size": size, "format": "RGB888"}))
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
            return self._cap.read()
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
