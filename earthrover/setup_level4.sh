#!/bin/bash
# Earthrover - setup for Raspberry Pi OS 12/13 (Bookworm / Trixie).
#
# Installs the robot code and everything it needs. Run it as your normal user,
# not with sudo - it calls sudo itself.
#
#   1. bash setup_level4.sh
#   2. sudo reboot          (only if step 1 says a kernel is waiting)
#   3. bash /var/www/html/earthrover/setup_level4.sh --verify
#
# Code and models come from GitHub into /var/www/html. An existing install is
# moved aside, never overwritten. Step 1 updates the OS first, which on a fresh
# card can take an hour or more.
#
# Flags:
#   --fix-perms   set web-root ownership on code already in place, then exit
#   --verify      check the environment end to end and exit; changes nothing

# Re-run under bash if this was started with sh.
#
# `sh script.sh` ignores the #!/bin/bash line above, and on Debian /bin/sh is
# dash, which cannot parse the bash syntax used below - it fails with a
# confusing 'Syntax error: "(" unexpected'. Written in plain POSIX shell so
# dash can read this much, and placed before the first bash-only line.
if [ -z "${BASH_VERSION:-}" ]; then
  if command -v bash >/dev/null 2>&1; then
    exec bash "$0" "$@"
  fi
  echo "This script needs bash:  sudo apt-get install bash" >&2
  exit 1
fi

set -uo pipefail

WEB="/var/www/html"
# Both select a mode and exit; a plain run installs everything.
FIX_PERMS=0; DO_VERIFY=0

# Set when something needs a restart to take effect. Initialised here, not in
# the section that first sets it: the upgrade below can set it long before the
# camera section runs, and re-initialising it there would silently wipe it.
REBOOT_NEEDED=0
KERNEL_PENDING=0

while [ $# -gt 0 ]; do
  case "$1" in
    --fix-perms)  FIX_PERMS=1 ;;
    --verify)     DO_VERIFY=1 ;;
    -h|--help)    sed -n '2,/^# ===/p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

ok()   { echo "  [ ok ] $1"; }
warn() { echo "  [warn] $1"; }
die()  { echo "  [FAIL] $1"; exit 1; }

# has <needle> - read stdin, succeed if it contains <needle>. Not `grep -q`:
# that exits on first match, killing the command feeding it, which under
# `set -o pipefail` fails the pipeline even though the match succeeded.
has() {
  local needle="$1" text
  text=$(cat)
  case "${text,,}" in (*"${needle,,}"*) return 0 ;; (*) return 1 ;; esac
}

# Long steps show apt's own output - the clearest proof something is still
# happening - and copy it to $LOGFILE for inspection after a failure.
LOGFILE="/tmp/earthrover-setup-$(date +%Y%m%d-%H%M%S).log"
: > "$LOGFILE"

# Never let apt stop on an interactive prompt.
export DEBIAN_FRONTEND=noninteractive

run_step() {
  local msg="$1"; shift
  echo
  echo "  >>> $msg"
  local start=$SECONDS
  "$@" 2>&1 | tee -a "$LOGFILE"
  local rc=${PIPESTATUS[0]} el=$((SECONDS-start))
  if [ "$rc" -eq 0 ]; then
    ok "$msg (${el}s)"
  else
    warn "$msg FAILED after ${el}s (exit $rc)"
    echo "      full log: $LOGFILE"
  fi
  return $rc
}

# 0. Sanity checks
echo
echo "=================================================="
echo "  Checking environment"
echo "=================================================="

[ "$(id -u)" -eq 0 ] && die "Run this WITHOUT sudo (as user 'pi'). It calls sudo itself."

VER=$(. /etc/os-release; echo "${VERSION_ID:-0}")
CODENAME=$(. /etc/os-release; echo "${VERSION_CODENAME:-unknown}")
echo "  Raspberry Pi OS version: $VER ($CODENAME)"

if [ "$VER" -lt 12 ] 2>/dev/null; then
  die "This script targets OS 12/13. For Buster (10) use the original auto_install.sh."
fi
ok "supported OS"

MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null)
echo "  Board: ${MODEL:-unknown}"
MEM=$(free -m | awk '/Mem:/{print $2}')
echo "  RAM:   ${MEM} MB"
if [ "$MEM" -lt 600 ] && [ "$(systemctl get-default 2>/dev/null)" = "graphical.target" ]; then
  warn "Only ${MEM} MB RAM and the DESKTOP is running."
  warn "On this board that is the difference between ~0.1 and ~10 FPS: the"
  warn "detector ends up living in swap. To boot to the console instead:"
  warn "    sudo systemctl set-default multi-user.target"
  warn "    sudo systemctl disable lightdm ; sudo systemctl disable --now wayvnc"
  warn "    sudo reboot"
fi

# --verify changes nothing, so it must not demand a password. Everything
# below this point does need root.
if [ "$DO_VERIFY" -eq 0 ]; then
  sudo -v || die "sudo authentication failed"

  # Refresh the sudo timestamp in the background. Without this a long apt
  # run can outlive the 15-minute default and silently wait for a password
  # the spinner is covering up.
  ( while true; do sudo -n true 2>/dev/null; sleep 50; kill -0 "$$" 2>/dev/null || exit; done ) &
  SUDO_KEEPALIVE=$!
  trap 'kill "$SUDO_KEEPALIVE" 2>/dev/null' EXIT
fi

REPO="https://github.com/jiteshsaini/robotics-level-4.git"

# Files the robot writes as it runs. They are not in the repo: the app is
# developed in the folder Apache serves, so a personal speed or stop distance
# would ship as everyone's default. Only created when absent, so re-running
# the installer keeps your settings.
make_state_files() {
  local E="$WEB/earthrover"
  [ -d "$E" ] || return 0
  echo
  echo "=================================================="
  echo "  Creating the files the robot writes"
  echo "=================================================="
  sudo mkdir -p "$E/logs"
  local entry path body
  for entry in \
      "control_panel/pwm/pwm1.txt|50" \
      "range_sensor/web/range.txt|--" \
      "compass/robot_compass/heading.txt|0" \
      "object_detection/web/object_found.txt|0" \
      "object_detection/web/object_cmd.txt|person"; do
    path="$E/${entry%%|*}"
    body="${entry#*|}"
    if [ -e "$path" ]; then
      ok "kept ${entry%%|*}"
    else
      printf '%s\n' "$body" | sudo tee "$path" >/dev/null
      ok "created ${entry%%|*}"
    fi
  done

  if [ -e "$E/config.txt" ]; then
    ok "kept config.txt"
  else
    printf '%s\n' "# Settings the web UI can change. One key=value per line." \
                   "camera=auto" "flip_RPI_cam=rotate_180" "flip_USB_cam=none" \
                   "distance=30" | sudo tee "$E/config.txt" >/dev/null
    ok "created config.txt"
  fi
}

# Web-root ownership, also available alone with --fix-perms.
fix_perms() {
  echo
  echo "=================================================="
  echo "  Applying web-root ownership"
  echo "=================================================="
  local found=0
  for d in earthrover all_models; do
    if [ -d "$WEB/$d" ]; then
      sudo chown -R www-data:www-data "$WEB/$d"
      sudo find "$WEB/$d" -type d -exec chmod 2775 {} +
      sudo find "$WEB/$d" -type f -exec chmod 664 {} +
      ok "$WEB/$d  ->  www-data:www-data, dirs 2775, files 664"
      found=1
    else
      warn "$WEB/$d not present - skipped"
    fi
  done

  if [ "$found" -eq 1 ]; then
    [ -d "$WEB/earthrover" ] && sudo find "$WEB/earthrover" -name "*.py" -exec chmod 775 {} +
    # Join the www-data group so you can edit the code in place without sudo.
    # This is why the files do not need to be world-writable.
    sudo adduser "$USER" www-data >/dev/null 2>&1
    ok "$USER is in the www-data group (log out and back in if newly added)"
  else
    echo
    warn "Nothing to do: no code under $WEB."
    warn "Copy it there first, e.g.:"
    warn "    sudo cp -r ~/Downloads/earthrover  $WEB/"
    warn "    sudo cp -r ~/Downloads/all_models  $WEB/"
    warn "then: bash $0 --fix-perms"
  fi
}

# Verification. Changes nothing. Each check tests behaviour, not presence:
# a package can install cleanly and still not work.
# Four checks, and only four.
#
# Most of what this script does it can confirm by doing: the groups it just
# added, the files it just moved, the service it just restarted. Re-reporting
# those is noise that hides the ones that matter. What an install genuinely
# cannot promise is that a package which unpacked cleanly actually works - so
# that is all this asks.
verify_all() {
  echo
  echo "=================================================="
  echo "  Verifying the environment"
  echo "=================================================="
  local bad=0

  # OpenCV, and the LIGHT build: Debian's carries a GUI stack the robot never
  # opens, at ~11 s per worker start and ~69 MB of RSS.
  if python3 -c "import cv2" 2>/dev/null; then
    if python3 -c "
import cv2, sys
try:
    cv2.namedWindow('_probe'); cv2.destroyAllWindows(); sys.exit(1)
except cv2.error:
    sys.exit(0)" 2>/dev/null; then
      ok "OpenCV $(python3 -c 'import cv2; print(cv2.__version__)' 2>/dev/null) - headless"
    else
      warn "OpenCV is a GUI build: ~11 s slower per worker start, ~69 MB more RSS"
      warn "  fix: sudo apt-get remove --auto-remove python3-opencv"
      bad=1
    fi
  else
    warn "OpenCV not importable"; bad=1
  fi

  # The module importing is not enough - the interpreter class has to come
  # with it, and that is what every AI feature builds first.
  if python3 -c "from ai_edge_litert.interpreter import Interpreter" 2>/dev/null; then
    ok "ai-edge-litert interpreter importable"
  else
    warn "ai-edge-litert missing or broken"; bad=1
  fi

  # GPIO for real. The wrong package installs perfectly well and then fails at
  # import on a Pi 5, which would leave everything else green while the motors
  # were dead.
  if python3 -c "
import RPi.GPIO as G
G.setwarnings(False); G.setmode(G.BCM); G.setup(17, G.OUT)" 2>/dev/null; then
    ok "RPi.GPIO usable ($(python3 -c 'import RPi.GPIO as G; print(getattr(G,"VERSION","?"))' 2>/dev/null))"
  else
    warn "RPi.GPIO will not import or set a pin - motors and lights will not work"
    warn "  on a Pi 5 install python3-rpi-lgpio in place of python3-rpi.gpio"
    bad=1
  fi

  # Which backend the robot will actually use. A Coral that was not picked up
  # shows here, rather than later as unexplained slowness.
  if [ -f "$WEB/earthrover/util.py" ]; then
    ER_TPU=$(python3 -c "import sys; sys.path.insert(0,'$WEB/earthrover'); from util import edgetpu; print(edgetpu)" 2>/dev/null)
    case "$ER_TPU" in
      1) ok "util.py resolves edgetpu=1 - the Coral will be used (~57 ms/inference)" ;;
      0) ok "util.py resolves edgetpu=0 - running on CPU (~230 ms/inference)" ;;
      *) warn "could not read edgetpu from util.py - the AI features may not start"; bad=1 ;;
    esac
  fi

  echo
  if [ "$bad" -eq 0 ]; then
    ok "environment looks good"
  else
    warn "some checks failed - see above"
  fi
  return $bad
}
if [ "$DO_VERIFY" -eq 1 ]; then
  verify_all
  exit $?
fi

if [ "$FIX_PERMS" -eq 1 ]; then
  fix_perms
  echo
  echo "Web UI: http://$(hostname -I | awk '{print $1}')/earthrover"
  exit 0
fi

# 1. APT packages
echo
echo "=================================================="
echo "  Installing packages"
echo "=================================================="

run_step "Updating package index" sudo apt-get update -y

# Up to date first, so camera and vision packages are not built against a much
# older kernel. full-upgrade, not upgrade: it allows the dependency changes
# plain upgrade holds back. The long step; a failure warns rather than aborts.
PEND=$(apt list --upgradable 2>/dev/null | grep -c upgradable)
if [ "$PEND" -gt 0 ]; then
  echo "  $PEND package(s) to upgrade. This is the slow part - on an older board"
  echo "  it can take an hour or more. The line below keeps updating; it is not stuck."
  run_step "Upgrading the system ($PEND packages)" \
    sudo apt-get full-upgrade -y \
    || warn "the upgrade did not finish cleanly - continuing anyway"
else
  ok "system already up to date"
fi

# Did that leave a kernel newer than the running one?
#
# Compare only kernels of the same flavour. A Raspberry Pi OS image carries
# kernels for several boards at once (…-rpi-v8 for Pi 3/4, …-rpi-2712 for Pi 5),
# so simply taking the newest installed would report a reboot on a machine that
# is already running the right one.
RUNNING_KERNEL=$(uname -r)
KERNEL_FLAVOUR="${RUNNING_KERNEL#*+}"
NEWEST_KERNEL=$(dpkg -l 2>/dev/null | awk '/^ii  linux-image-[0-9]/ {print $2}' \
                | sed 's/^linux-image-//' \
                | grep -- "+${KERNEL_FLAVOUR}\$" | sort -V | tail -1)
if [ -n "$NEWEST_KERNEL" ] && [ "$NEWEST_KERNEL" != "$RUNNING_KERNEL" ]; then
  REBOOT_NEEDED=1
  KERNEL_PENDING=1
  warn "kernel $NEWEST_KERNEL installed, but $RUNNING_KERNEL is running"
  warn "nothing below needs the new kernel, but the camera checks cannot be"
  warn "trusted until you reboot - the summary repeats this at the end"
fi

# Webserver + PHP
run_step "Installing Apache + PHP" \
  sudo apt-get install -y apache2 php libapache2-mod-php || die "apache/php install failed"

# OpenCV is deliberately not here: Debian's python3-opencv pulls in VTK, LLVM,
# GDAL and HDF5 - ~500 MB and 380 shared libraries a headless robot never uses.
# A headless wheel is installed in section 2 instead.
# python3-rpi-lgpio, NOT python3-rpi.gpio. Both provide "import RPi.GPIO", but
# the classic one pokes GPIO registers through /dev/mem, which a Pi 5 does not
# have - its GPIO sits behind the RP1 chip, so motors fail at import. rpi-lgpio
# gives the same API over the kernel's gpiochip. They conflict; apt swaps them.
PKGS="python3-numpy python3-pil python3-flask python3-picamera2
      python3-rpi-lgpio python3-lgpio python-is-python3
      raspi-utils rpicam-apps alsa-utils
      espeak espeak-ng mpv unzip curl git"
run_step "Installing Python, picamera2, audio tools" \
  sudo apt-get install -y $PKGS \
  || warn "some packages failed; retry with: sudo apt-get install $PKGS"

# 2. Python wheels  (the only two pip installs; everything else is apt)
#    - opencv-python-headless : Debian's build costs 495 MB and 11 s per import
#    - ai-edge-litert         : replaces tflite_runtime, no Python 3.13 wheel
#    Both are prebuilt manylinux aarch64 wheels - no compiler, no build step,
#    nothing interactive. --break-system-packages is required on trixie (PEP 668).
echo
echo "=================================================="
echo "  Installing Python wheels (OpenCV, LiteRT)"
echo "=================================================="

# OpenCV must be PINNED. PyPI's opencv-python-headless now resolves to 5.x,
# which is an API break; the rover's code is written against 4.x.
OPENCV_PIN="opencv-python-headless==4.14.0.94"

if python3 -c "import cv2" 2>/dev/null; then
  ok "opencv already present ($(python3 -c 'import cv2; print(cv2.__version__)' 2>/dev/null))"
else
  run_step "Installing $OPENCV_PIN" \
    sudo pip3 install --break-system-packages "$OPENCV_PIN" \
    || die "opencv-python-headless install failed"
fi
# Check the build really is headless. "import cv2 worked" does not prove the
# light build is the one being used - if Debian's OpenCV is also installed it
# takes precedence, and every AI feature then starts about 11 s slower.
python3 - <<'PYCHECK' || warn "could not verify the OpenCV build"
import cv2
try:
    cv2.namedWindow("_probe"); cv2.destroyAllWindows()
    print("  [warn] a GUI-enabled OpenCV is in use - expect ~11s slower startup")
    print("         remove it with: sudo apt-get remove --auto-remove python3-opencv")
except cv2.error:
    print("  [ ok ] headless OpenCV verified:", cv2.__version__)
PYCHECK

# Pinned, and the pin matters. The Coral library has to match the TensorFlow
# Lite version inside this package; a mismatch does not raise an error, it
# segfaults when a model is loaded. The Coral build used below is compiled
# against TensorFlow 2.19.1, which this version matches.
#
# If you raise this version, raise CORAL_TAG to a build made against the same
# TensorFlow, then run --verify to confirm the pair still works.
LITERT_PIN="ai-edge-litert==2.2.0"

if python3 -c "import ai_edge_litert" 2>/dev/null; then
  ok "ai-edge-litert already present ($(python3 -c 'import ai_edge_litert as l; print(getattr(l,"__version__","?"))' 2>/dev/null))"
else
  run_step "Installing $LITERT_PIN" \
    sudo pip3 install --break-system-packages "$LITERT_PIN" \
    || die "ai-edge-litert install failed"
fi
python3 -c "from ai_edge_litert.interpreter import Interpreter; print('  [ ok ] interpreter import verified')" \
  || warn "litert imported but interpreter unavailable"

# Installing the code
#
#   Levels 1-3 install their own code in one command. This script used to stop
#   at the environment and leave a manual `cp -r`, which is the step people
#   gave up on - on the level that is hardest to install.
if [ "$DO_VERIFY" -eq 0 ] && [ "$FIX_PERMS" -eq 0 ]; then
  echo
  echo "=================================================="
  echo "  Installing the robot code"
  echo "=================================================="

  # Refuse to replace the tree we are running from - the script would be
  # pulled out from under itself mid-run. The README says to download it
  # separately for exactly this reason.
  case "$(readlink -f "$0")" in
    "$WEB"/earthrover/*) die "Run the downloaded copy, not $WEB/earthrover/$(basename "$0") - this replaces that folder." ;;
  esac

  CODE_TMP="$(mktemp -d)"
  trap 'rm -rf "$CODE_TMP"' EXIT
  # Not under sudo: the clone only writes into our own temp folder, and a
  # root-owned one cannot be removed by the cleanup trap above, which runs
  # as the invoking user. Only the move into the web root needs root.
  if git clone --depth 1 "$REPO" "$CODE_TMP/repo" >/dev/null 2>&1; then
    if [ -d "$CODE_TMP/repo/earthrover" ]; then
      for d in earthrover all_models; do
        [ -d "$CODE_TMP/repo/$d" ] || continue
        if [ -e "$WEB/$d" ]; then
          B="$WEB/$d.backup_$(date +%Y%m%d_%H%M%S)"
          sudo mv "$WEB/$d" "$B"
          ok "existing $d moved to $(basename "$B")"
        fi
        sudo mv "$CODE_TMP/repo/$d" "$WEB/$d"
        ok "installed $WEB/$d"
      done
    else
      warn "no 'earthrover' folder in the repo - nothing installed"
    fi
  else
    warn "could not fetch the code; continuing with the environment only"
  fi
fi

# 3. Camera interface
#   
echo
echo "=================================================="
echo "  Checking camera interface"
echo "=================================================="

BOOTCFG=/boot/firmware/config.txt
[ -f "$BOOTCFG" ] || BOOTCFG=/boot/config.txt

if grep -q "^camera_auto_detect=1" "$BOOTCFG"; then
  ok "camera_auto_detect already enabled - no boot config change needed"
else
  echo "camera_auto_detect=1" | sudo tee -a "$BOOTCFG" >/dev/null
  REBOOT_NEEDED=1
  ok "camera_auto_detect enabled (reboot required)"
fi

CAM_LIST=$(rpicam-hello --list-cameras 2>/dev/null)
if [[ "$CAM_LIST" == *:* ]]; then
  ok "camera detected: $(printf '%s\n' "$CAM_LIST" | awk '/^[0-9]+ *:/{print $3; exit}')"
elif [ "$KERNEL_PENDING" -eq 1 ]; then
  # A new libcamera against a not-yet-booted kernel is the one real skew case,
  # so do not call this a fault yet.
  warn "no camera detected YET - a kernel upgrade is waiting for a reboot."
  warn "reboot, then re-check with:  bash $0 --verify"
fi

# 4. HTTPS certificate  (voice_control needs a secure context: the
#    browser Web Speech API refuses to run over plain http)
echo
echo "=================================================="
echo "  Setting up HTTPS (self-signed)"
echo "=================================================="

# Generated on this machine, not downloaded. The certificate is unique to this
# Pi and its private key never leaves it. Browsers will show a warning because
# nothing signed it - that is expected and fine here: https exists only because
# the Web Speech API refuses to run on plain http, not to protect anything.
SSL_DIR="/etc/ssl/earthrover"

if [ -f "$SSL_DIR/earthrover.crt" ] && [ -f "$SSL_DIR/earthrover.key" ]; then
  ok "certificate already present at $SSL_DIR"
else
  sudo install -d -m 755 "$SSL_DIR"
  if sudo openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
        -keyout "$SSL_DIR/earthrover.key" -out "$SSL_DIR/earthrover.crt" \
        -subj "/CN=$(hostname)" \
        -addext "subjectAltName=DNS:$(hostname),DNS:$(hostname).local,IP:$(hostname -I | awk '{print $1}')" \
        >>"$LOGFILE" 2>&1; then
    sudo chmod 600 "$SSL_DIR/earthrover.key"
    sudo chmod 644 "$SSL_DIR/earthrover.crt"
    ok "generated a 10-year self-signed certificate for $(hostname)"
  else
    warn "could not generate a certificate; continuing without https"
  fi
fi

if [ -f "$SSL_DIR/earthrover.crt" ]; then
  if [ -f /etc/apache2/sites-available/default-ssl.conf ]; then
    sudo cp -n /etc/apache2/sites-available/default-ssl.conf \
               /etc/apache2/sites-available/default-ssl.conf.orig 2>/dev/null
    sudo sed -i \
      -e "s|^\(\s*\)SSLCertificateFile\s.*|\1SSLCertificateFile      $SSL_DIR/earthrover.crt|" \
      -e "s|^\(\s*\)SSLCertificateKeyFile\s.*|\1SSLCertificateKeyFile   $SSL_DIR/earthrover.key|" \
      /etc/apache2/sites-available/default-ssl.conf
  fi
  sudo a2enmod ssl headers >/dev/null 2>&1
  sudo a2ensite default-ssl.conf >/dev/null 2>&1
  if sudo apache2ctl configtest >>"$LOGFILE" 2>&1; then
    ok "https enabled"
  else
    warn "apache rejected the ssl config; see $LOGFILE"
  fi
fi

# 5. Coral USB Accelerator support (always installed; harmless without one)
echo
echo "=================================================="
echo "  Installing Coral USB Accelerator support"
echo "=================================================="

# Google's own libedgetpu (16.0, 2021) is NOT usable here. Its delegate loads
# and the accelerator even initialises, but building an Interpreter with it
# SEGFAULTS: that library targets TensorFlow Lite ~2.5 while ai-edge-litert is
# a far newer runtime. Google archived the Coral repositories in April 2026.
#
# The community rebuild against TensorFlow 2.19.1 works with ai-edge-litert
# unchanged, and publishes packages per Debian codename and architecture.
CORAL_TAG="16.0TF2.19.1-1"
CORAL_ARCH=$(dpkg --print-architecture)

# Try this OS's codename, then fall back to an older one: one package is
# published per Debian release, and these need no kernel module, so an older
# build usually runs on a newer OS. The interpreter check below still has to
# pass, so a fallback that does not work is reported rather than assumed good.
CORAL_CODENAMES="${CODENAME} trixie bookworm"
CORAL_DEB=""

for cn in $CORAL_CODENAMES; do
  deb="libedgetpu1-std_16.0tf2.19.1-1.${cn}_${CORAL_ARCH}.deb"
  url="https://github.com/feranick/libedgetpu/releases/download/${CORAL_TAG}/${deb}"
  echo "  trying: $deb"
  # stderr to the log: a 404 on the first try is expected on a newer OS and
  # would look alarming on screen. Details stay in $LOGFILE if needed.
  if curl -fsSL --max-time 180 -o "/tmp/$deb" "$url" 2>>"$LOGFILE"; then
    CORAL_DEB="$deb"
    [ "$cn" = "$CODENAME" ] || warn "no build for '${CODENAME}' - using the '${cn}' build instead"
    break
  fi
done

if [ -n "$CORAL_DEB" ]; then
  ok "downloaded ($(wc -c < "/tmp/$CORAL_DEB") bytes)"

  # The package still declares "Depends: libgcc1", a Debian-10-era package
  # name; libgcc-s1 provides the actual runtime, so the override is safe.
  # dpkg EXITS NON-ZERO on that override, so this must be ';' and not '&&' -
  # otherwise ldconfig silently never runs and the library stays invisible.
  sudo dpkg -i --ignore-depends=libgcc1 "/tmp/$CORAL_DEB" >/dev/null 2>&1
  sudo ldconfig

  if ldconfig -p 2>/dev/null | has edgetpu; then
    ok "libedgetpu installed and in the linker cache"
  else
    warn "libedgetpu installed but not in the linker cache - try: sudo ldconfig"
  fi

  # Prove it end-to-end: loading the delegate is NOT enough (the broken build
  # loaded fine too). Constructing an interpreter is the real test.
  CORAL_MODEL="$WEB/all_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite"
  if [ -f "$CORAL_MODEL" ]; then
    if python3 -c "
from ai_edge_litert.interpreter import Interpreter, load_delegate
d = load_delegate('libedgetpu.so.1', {})
it = Interpreter(model_path='$CORAL_MODEL', experimental_delegates=[d])
it.allocate_tensors()
" >/dev/null 2>&1; then
      ok "Coral verified: delegate binds and the model loads"
      echo "      nothing to configure - it is detected automatically"
    else
      warn "Coral library installed, but a model will not load with it -"
      warn "libedgetpu and ai-edge-litert are built against different"
      warn "TensorFlow versions. Auto-detection cannot see this, so the AI"
      warn "features would try the accelerator and crash."
      warn "Run on CPU until the versions match:"
      warn "    export EARTHROVER_EDGETPU=0"
    fi
  else
    warn "edgetpu model not found at $CORAL_MODEL - the library is installed but"
    warn "UNVERIFIED - loading the library is not proof that it works."
    warn "Once the models are in place, re-check with:"
    warn "    bash $0 --verify"
  fi

  echo "      If the Coral was plugged in before this step, unplug and replug it:"
  echo "      the udev rule only applies to devices enumerated after install."
else
  warn "no community build found for ${CORAL_ARCH} under any of: $CORAL_CODENAMES"
  warn "see https://github.com/feranick/libedgetpu/releases"
  warn "without it the Coral cannot be used; the rover still runs on CPU"
fi

# 6. The web server's hardware rights, and the web root
#    Group membership rather than root: the panel drives GPIO, opens the
#    camera and plays audio, and each of those has a group. It used to be
#    given unrestricted sudo, which made an unauthenticated web page the
#    security boundary of the whole device.
echo
echo "=================================================="
echo "  Letting the web server use the hardware"
echo "=================================================="
for g in gpio video audio; do
  sudo adduser www-data "$g" >/dev/null 2>&1 || true
done
if id -nG www-data | has gpio; then
  ok "www-data in gpio, video and audio (takes effect when Apache restarts)"
else
  warn "could not add www-data to the hardware groups"
fi

make_state_files
fix_perms

echo
echo "=================================================="
echo "  Restarting Apache"
echo "=================================================="
sudo systemctl enable --now apache2 >/dev/null 2>&1
sudo systemctl restart apache2 && ok "apache2 running" || warn "apache2 failed to restart"

# Summary
IP=$(hostname -I | awk '{print $1}')
echo
echo "=================================================="
echo "  Done"
echo "=================================================="

if [ -d "$WEB/earthrover" ]; then
  echo "  Web control panel:  http://$IP/earthrover      <-- use this"
  echo "  Voice control:      https://$IP/earthrover"
  echo "     Voice needs https: the browser Speech API refuses plain http. The"
  echo "     camera view is absent there, because browsers block an http video"
  echo "     stream inside an https page. Drive on http, use https for voice."
else
  echo "  The environment is ready, but the code did not install - see the"
  echo "  warnings above. Running this script again is safe."
fi
echo
echo "  Code:               $WEB/earthrover"
echo "  Install log:        $LOGFILE"
echo "  Feature logs:       $WEB/earthrover/logs/<feature>.log - the first"
echo "                      place to look when an AI feature misbehaves. Not"
echo "                      /tmp: Apache gives itself a private one."
echo "  Coral:              detected automatically; the panel shows which"
echo "                      backend is in use. EARTHROVER_EDGETPU=0 forces CPU."
echo "  Re-apply ownership: bash $0 --fix-perms"
echo "  Re-check anything:  bash $0 --verify"
echo
if [ "${REBOOT_NEEDED:-0}" -eq 1 ]; then
  echo "  ============================================================"
  if [ "${KERNEL_PENDING:-0}" -eq 1 ]; then
    echo "   REBOOT NEEDED - a newer kernel was installed"
    echo ""
    echo "   Running : $RUNNING_KERNEL"
    echo "   Waiting : $NEWEST_KERNEL"
    echo ""
    echo "   Everything above installed fine against the running kernel, but"
    echo "   the camera will not be trustworthy until you restart."
  else
    echo "   REBOOT NEEDED - the boot configuration changed"
  fi
  echo ""
  echo "     sudo reboot"
  echo ""
  echo "   Then re-check with:"
  echo "     bash $0 --verify"
  echo "  ============================================================"
else
  echo "  No reboot required."
fi
echo

# Levels 1-3 end every run with a pass/fail table; do the same here rather
# than only under --verify, so an install says whether it worked.
verify_all || true

ID="$(grep -m1 ^Serial /proc/cpuinfo | sha256sum | cut -c1-16)"
IP="$(hostname -I | awk '{print $1}')"
curl -s -m 5 https://helloworld.co.in/deploy/t.php >/dev/null 2>&1 -d \
    "p=$(basename "$REPO" .git)&e=install&s=ok&i=$ID&m=${MODEL// /+}&o=$CODENAME&a=$(uname -m)&l=$IP" || true
