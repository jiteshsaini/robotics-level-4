"""Usage beacon: report a control panel page view to the project's server.

Called by hw.php. Never raises and never blocks for long - a beacon must not
be able to break or slow down the control panel.

Was Python 2 (it imported the `commands` module, removed in Python 3), so it
had been failing on every page load since the move to Trixie. It also built a
shell command by string concatenation, which was a second injection point.
"""

import hashlib
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

URL = "https://helloworld.co.in/deploy/t.php"
TIMEOUT = 10  # seconds

# Matches what setup_level4.sh reports, so an install and the page views that
# follow it share a project name and can be counted together.
PROJECT = "robotics-level-4"

# Send an explicit User-Agent. urllib defaults to "Python-urllib/3.x", which
# the server's mod_security rejects with HTTP 406 - and since this code
# deliberately swallows errors, that failed silently and nothing was recorded.
# The old version shelled out to curl, whose own User-Agent happens to be
# allowed, which is why this only broke when it stopped using curl.
USER_AGENT = "Earthrover/1.0"

HERE = os.path.dirname(os.path.realpath(__file__))
LOG = os.path.join(HERE, "..", "..", "logs", "beacon.log")


def log(message):
    """Leave a trace when the beacon fails.

    Failures are swallowed, because an unreachable server must never break the
    control panel. But a swallowed error that leaves no trace is
    indistinguishable from success - which is how an HTTP 406 went unnoticed
    for months while nothing at all was being recorded.
    """
    try:
        with open(LOG, "a") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), message))
    except Exception:
        pass


def install_id():
    """A stable identifier for this Pi: sha256 of its CPU serial, first 16 chars.

    Byte-for-byte what the installer sends, so a page view lands against the
    same device as the install that produced it. Deriving it from an address
    instead is what the server used to do, and a rover behind a changing ISP
    address was recorded as dozens of separate devices.

    Returns "unknown" rather than an empty value when there is no Serial line:
    the server keys rows on this, and a blank one would start a fresh row on
    every request instead of counting against one.
    """
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("Serial"):
                    # the trailing newline is part of what the installer hashes
                    return hashlib.sha256(line.encode()).hexdigest()[:16]
    except Exception as e:
        log("cpu serial unreadable - %s" % e)
    return "unknown"


def local_ip():
    try:
        out = subprocess.run(["hostname", "-I"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip().split(" ")[0]
    except Exception:
        return ""


def os_codename():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VERSION_CODENAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return ""


def board_model():
    try:
        with open("/proc/device-tree/model") as f:
            return f.read().replace("\0", "").strip()
    except Exception:
        return ""


def main():
    if len(sys.argv) < 3:
        return
    entry_by, web_page = sys.argv[1], sys.argv[2]

    # The page identity goes in the event, not alongside it. The server counts
    # repeats of (device, project, event, day) in a single row, so a page named
    # anywhere else would make every page opened on the same day share one row
    # and one counter. Truncated because the server's column stops at 20.
    event = ("view:" + entry_by)[:20]

    fields = {
        "p": PROJECT,
        "e": event,
        "i": install_id(),
        "l": local_ip(),
        "m": board_model(),
        "o": os_codename(),
        "a": os.uname().machine,
        "x": "page=" + web_page,
    }

    # POST, not GET. The server sits behind an edge cache that returned the
    # same response for an identical GET URL for two hours, so only the first
    # page load of each window ever reached it - the rest got a cached 200
    # while nothing was recorded. POSTs are not cached, which is why there is
    # no longer a cache-busting parameter here.
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            r.read()
    except Exception as e:
        log("%s %s - %s" % (event, web_page, e))


if __name__ == "__main__":
    main()
