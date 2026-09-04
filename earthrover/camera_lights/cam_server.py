# Web streaming server for the Earthrover camera.
#
# Originally based on the PiCamera web-streaming recipe:
#   http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
# Ported to picamera2, because the legacy 'picamera' library depends on the
# Broadcom MMAL stack that was removed in Raspberry Pi OS Bullseye and is
# not installable on Bookworm/Trixie.
#
# Behaviour is unchanged: an MJPEG stream on port 8000.
#   http://<pi-ip>:8000/           -> viewer page
#   http://<pi-ip>:8000/stream.mjpg -> raw MJPEG stream

import io
import logging
import socketserver
from threading import Condition
from http import server

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform

RESOLUTION = (640, 480)
FRAMERATE = 24
ROTATE_180 = True      # set False if the image ends up upside down
PORT = 8000

PAGE="""\
<html>
<head>
<title>Rpi Cam-Server</title>
</head>
<body>
<!--<center><h1>Raspberry Pi - Surveillance Camera</h1></center>-->
<center><img src="stream.mjpg" width="640" height="480"></center>
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
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
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

picam2 = Picamera2()
# 180-degree rotation is expressed as horizontal + vertical flip.
transform = Transform(hflip=1, vflip=1) if ROTATE_180 else Transform()
picam2.configure(picam2.create_video_configuration(
    main={"size": RESOLUTION},
    transform=transform,
    controls={"FrameRate": FRAMERATE},
))

output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', PORT)
    current_server = StreamingServer(address, StreamingHandler)
    current_server.serve_forever()
finally:
    picam2.stop_recording()
    picam2.close()
