<?php
// Reads and writes one value in config.txt, for the gear icons on the panel.
// Keys and values are whitelisted: this file is written by the web server and
// read by scripts that drive the hardware, so nothing arbitrary goes into it.

$FILE = __DIR__ . "/config.txt";
$ALLOWED = array(
	"camera"        => "/^(auto|USB_cam|RPI_cam)$/",
	"flip_RPI_cam"  => "/^(none|rotate_180|horizontal_flip|vertical_flip)$/",
	"flip_USB_cam"  => "/^(none|rotate_180|horizontal_flip|vertical_flip)$/",
	"distance"      => "/^[0-9]{1,3}$/",
);

// Is a ribbon camera bound? Read from sysfs, which opens no device.
//
// NOT rpicam-hello --list-cameras. That answers correctly even while the
// camera is streaming, but answering is not free: it has libcamera touch a
// sensor another process is holding, and the live preview visibly jumps and
// shifts colour. Opening the settings box should not disturb the picture the
// settings box is about.
//
// Only v4l-subdev entries are considered. A CSI sensor registers one; a USB
// webcam does not, so this cannot mistake a webcam for the ribbon camera.
// The Pi's own blocks are named unicam/bcm2835/rp1-cfe and are skipped.
if (isset($_POST["probe"]) && $_POST["probe"] === "rpi") {
	$found = "0";
	foreach (glob("/sys/class/video4linux/v4l-subdev*/name") as $f) {
		$name = trim((string) @file_get_contents($f));
		if ($name === "" || preg_match('/^(unicam|bcm2835|rp1-cfe)/i', $name)) { continue; }
		$found = "1";
		break;
	}
	echo $found;
	exit;
}

$key = isset($_POST["key"]) ? $_POST["key"] : "";
if (!isset($ALLOWED[$key]) && !isset($_POST["set"])) {
	http_response_code(400); echo "unknown setting"; exit;
}

$lines = is_file($FILE) ? file($FILE, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) : array();

// Several keys at once: set[camera]=RPI_cam&set[flip_USB_cam]=horizontal_flip
//
// One request, one read-modify-write. Sending a request per key raced - each
// one read the file before the others had written, so the last reply won and
// the rest were silently lost.
if (isset($_POST["set"]) && is_array($_POST["set"])) {
	$updates = array();
	foreach ($_POST["set"] as $k => $v) {
		if (!isset($ALLOWED[$k]))            { http_response_code(400); echo "unknown setting $k"; exit; }
		$v = trim($v);
		if (!preg_match($ALLOWED[$k], $v))   { http_response_code(400); echo "bad value for $k"; exit; }
		$updates[$k] = $v;
	}
	$out = array();
	foreach ($lines as $l) {
		$hit = null;
		foreach ($updates as $k => $v) {
			if (strpos($l, "$k=") === 0) { $hit = "$k=$v"; unset($updates[$k]); break; }
		}
		$out[] = $hit === null ? $l : $hit;
	}
	foreach ($updates as $k => $v) { $out[] = "$k=$v"; }   // keys not already present

	if (@file_put_contents($FILE, implode("\n", $out) . "\n") === false) {
		http_response_code(500); echo "could not write " . $FILE; exit;
	}
	echo "saved";
	exit;
}

if (!isset($_POST["value"])) {                     // read
	foreach ($lines as $l) {
		if (strpos($l, "$key=") === 0) { echo substr($l, strlen($key) + 1); exit; }
	}
	exit;
}

$value = trim($_POST["value"]);                    // write
if (!preg_match($ALLOWED[$key], $value)) { http_response_code(400); echo "bad value"; exit; }

$out = array(); $written = false;
foreach ($lines as $l) {
	if (strpos($l, "$key=") === 0) { $out[] = "$key=$value"; $written = true; }
	else                            { $out[] = $l; }
}
if (!$written) $out[] = "$key=$value";

// report a failed write rather than saying "saved" - the file is owned by the
// web server on a real install, and a copy made by hand often is not
if (@file_put_contents($FILE, implode("\n", $out) . "\n") === false) {
	http_response_code(500);
	echo "could not write " . $FILE;
	exit;
}
echo "saved";
?>
