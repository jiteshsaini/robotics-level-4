"""Usage beacon: report a page view to the project's server.

Called by hw.php. Never raises and never blocks for long - a beacon must not
be able to break or slow down the control panel.

Was Python 2 (it imported the `commands` module, removed in Python 3), so it
had been failing on every page load since the move to Trixie. It also built a
shell command by string concatenation, which was a second injection point.
"""

import subprocess
import sys
import time
import urllib.parse
import urllib.request

URL = "https://helloworld.co.in/deploy/run.php"
TIMEOUT = 10  # seconds

# Send an explicit User-Agent. urllib defaults to "Python-urllib/3.x", which
# the server's mod_security rejects with HTTP 406 - and since this code
# deliberately swallows errors, that failed silently and nothing was recorded.
# The old version shelled out to curl, whose own User-Agent happens to be
# allowed, which is why this only broke when it stopped using curl.
USER_AGENT = "Earthrover/1.0"


def local_ip():
    try:
        out = subprocess.run(["hostname", "-I"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip().split(" ")[0]
    except Exception:
        return ""


def main():
    if len(sys.argv) < 3:
        return
    entry_by, web_page = sys.argv[1], sys.argv[2]

    # urlencode, so a value containing & or a space cannot corrupt the query.
    #
    # "t" is a cache-buster and is load-bearing. The server sits behind an edge
    # cache that returns the same response for an identical URL for two hours -
    # so without this, only the first page load of each two-hour window ever
    # reaches the server, and every later one gets a cached 200 while nothing is
    # recorded. The receiving script ignores this parameter.
    query = urllib.parse.urlencode(
        {"p": "%s*%s*%s" % (entry_by, web_page, local_ip()),
         "t": "%d" % (time.time() * 1000)})

    req = urllib.request.Request(URL + "?" + query,
                                 headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            r.read()
    except Exception:
        pass          # unreachable server is not the control panel's problem


if __name__ == "__main__":
    main()
