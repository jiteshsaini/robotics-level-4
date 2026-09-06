# Web streaming server for the Earthrover camera.
#
# Originally based on the PiCamera web-streaming recipe:
#   http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
# Ported to picamera2, because the legacy 'picamera' library depends on the
# Broadcom MMAL stack that was removed in Raspberry Pi OS Bullseye and is
# not installable on Bookworm/Trixie.
#
# An MJPEG stream on port 8000.
#   http://<pi-ip>:8000/           -> viewer page
#   http://<pi-ip>:8000/stream.mjpg -> raw MJPEG stream
#
# Works with either camera: the CSI ribbon camera through picamera2, or a USB
# webcam through OpenCV. Which one, and which way up, come from config.txt -
# the same settings camera_compat.py reads, so the stream and the vision
# scripts never disagree about the camera.
#
# The two sources differ in kind. picamera2 PUSHES encoded JPEGs from its
# hardware encoder; OpenCV hands back raw frames that have to be pulled and
# encoded. Both end up writing whole JPEGs into the same buffer, so the HTTP
# server below never knows which camera it has.

import io
import logging
import os
import socketserver
import sys
import threading
import time
from threading import Condition
from http import server
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from util import setting, FLIP_CV2, FLIP_TRANSFORM

RESOLUTION = (640, 480)
FRAMERATE = 24
PORT = 8000
CAM_INDEXES = 5        # /dev/video0..4, searched for a USB webcam

SOURCE = setting("camera", "auto")          # auto | USB_cam | RPI_cam

PAGE="""\
<html>
<head>
<title>Rpi Cam-Server</title>
</head>
<style>
html,body{height:100%;margin:0;background:#8d9ab0}
body{display:flex;align-items:center;justify-content:center}
img{max-width:100%;max-height:100%;display:block}
</style>
<body>
<!--<center><h1>Raspberry Pi - Surveillance Camera</h1></center>-->
<img src="stream.mjpg">
<!--<input  type='submit' onclick=button_reload(); value='refresh'/>-->

</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    """Holds the most recent JPEG frame and wakes up waiting clients.

    Simpler than the picamera version: picamera streamed raw bytes and the
    old code had to detect JPEG start markers (\\xff\\xd8) to split frames.
    picamera2's JpegEncoder hands over exactly one complete frame per
    write(), so no buffering or marker detection is needed.
    """
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Path only: the control panel appends a cache-busting query when it
        # re-points the video iframe, and an exact match on '/' would 404 it.
        path = urlparse(self.path).path
        if path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def start_rpi_cam(output):
    """CSI ribbon camera. picamera2 encodes to JPEG in hardware and pushes
    each frame, so nothing is copied or re-encoded on the way out."""
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    from libcamera import Transform

    h, v = FLIP_TRANSFORM.get(setting("flip_RPI_cam", "none"), (0, 0))
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(
        main={"size": RESOLUTION},
        transform=Transform(hflip=h, vflip=v),
        controls={"FrameRate": FRAMERATE},
    ))
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    return picam2


def start_usb_cam(output):
    """USB webcam. OpenCV hands back raw frames, so a thread pulls them,
    encodes each one, and writes it into the same buffer the ribbon camera
    pushes to. Returns None if no usable webcam is present.

    The webcam is not on a fixed index: a Pi numbers its own CSI receiver and
    codec blocks as /dev/video* too, so a webcam typically lands on video1 or
    later - and video0, the CSI receiver, opens happily and then delivers
    nothing. Opening is therefore no proof: take the first index that hands
    back an actual frame.
    """
    try:
        import cv2
    except ImportError:
        print("USB_cam: OpenCV is not installed - see the README")
        return None

    flip = FLIP_CV2.get(setting("flip_USB_cam", "none"))

    for index in range(CAM_INDEXES):
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if not cap.isOpened():
            continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION[1])

        for _ in range(5):
            ok, frame = cap.read()
            if ok and frame is not None:
                print("USB_cam: webcam on /dev/video%d" % index)
                break
            time.sleep(0.1)
        else:
            cap.release()
            continue
        break
    else:
        print("USB_cam: no webcam delivered a frame")
        return None

    def pump():
        delay = 1.0 / FRAMERATE
        while True:
            ok, frame = cap.read()
            if ok and frame is not None:
                if flip is not None:
                    frame = cv2.flip(frame, flip)
                ok, jpg = cv2.imencode(".jpg", frame)
                if ok:
                    output.write(jpg.tobytes())
            time.sleep(delay)

    threading.Thread(target=pump, daemon=True).start()
    return cap


output = StreamingOutput()
camera = None

if SOURCE in ("auto", "USB_cam"):
    camera = start_usb_cam(output)
    if camera:
        print("camera: USB_cam")

if camera is None and SOURCE in ("auto", "RPI_cam"):
    camera = start_rpi_cam(output)
    print("camera: RPI_cam")

if camera is None:
    raise SystemExit("camera: none available for source '%s'" % SOURCE)

try:
    address = ('', PORT)
    current_server = StreamingServer(address, StreamingHandler)
    current_server.serve_forever()
finally:
    if hasattr(camera, "stop_recording"):
        camera.stop_recording()
        camera.close()
    else:
        camera.release()
    picam2.close()
