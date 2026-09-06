<?php
//include_once 'vars.php';

$cam = $_POST["camera"];

// The camera is a single-holder resource: only one process can open it. The
// four ML features each hold it while running, and previously nothing yielded
// it, so pressing "camera on" during object detection waited out the timeout
// and then reported success having started nothing.
$ML_WORKERS = array(
	"object_detection_web2.py",
	"object_tracking.py",
	"human_follower.py",
	"image_recog_cv2.py",
);

if ($cam == "on") {
	// Take the camera from whichever feature holds it - last button pressed wins,
	// which is what the UI implies since you pick one mode at a time.
	foreach ($ML_WORKERS as $w) {
		system("pkill -f " . escapeshellarg($w) . " > /dev/null 2>&1");
	}
	sleep(2);   // let libcamera release the device

	// Output is redirected so the backgrounded process does not keep the HTTP
	// connection open (PHP's system() otherwise waits on the child's inherited
	// stdout, and this request would appear to hang).
	// to the log rather than /dev/null: a camera that fails to start
	// should be able to say why
	$app = dirname(__DIR__);
	// Run from /tmp: the GPIO library writes a small notification file in
	// whatever folder a process starts in, and PHP starts its children in the
	// directory of the script that launched them. Children inherit the cwd, so
	// one cd covers the lot - without it those files land in the web tree.
	system("cd /tmp && python3 -u " . __DIR__ . "/cam_server.py > " . $app . "/logs/camera.log 2>&1 &");

	// picamera2 needs a couple of seconds to open the sensor and bind port 8000.
	// Wait for the stream to actually accept before replying, so the UI reloads
	// into a working frame instead of racing a fixed timer. A healthy start
	// binds in ~2.5s; 8s is generous without stalling the UI on a real failure.
	$ready = false;
	$deadline = time() + 8;
	while (time() < $deadline) {
		$sock = @fsockopen("127.0.0.1", 8000, $errno, $errstr, 1);
		if ($sock) { fclose($sock); $ready = true; break; }
		usleep(200000);
	}

	// Report what actually happened. Claiming success when the port never came
	// up is how this failure stayed invisible.
	echo $ready ? "camera: on" : "camera: FAILED to start";
	exit;
}

if ($cam == "off") {
	system("pkill -f cam_server.py");
	echo "camera: off";
	exit;
}

echo "camera: unknown request";
?>
