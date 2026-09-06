<?php
// Starting a detector takes roughly 25-30 seconds: the model has to load and
// the camera has to come up before Flask binds port 2204. Wait for that
// port to accept a connection before replying, so the UI reveals the video
// link only when the stream is really there. Racing a fixed timer is why the
// iframe used to show "refused to connect".
set_time_limit(90);

$state = $_POST["state"];


// Only one process may own the motor and light pins, so refuse with an
// explanation rather than letting the worker die mid-start.
require_once dirname(dirname(__DIR__)) . "/vars.php";
if ($state == "1") { er_pin_guard("human following"); }

// From /tmp: the GPIO library drops a working file in the launch directory.
exec("cd /tmp && python3 " . dirname(dirname(__DIR__)) . "/human_following/master.py $state");

if ($state == "1") {
	$app   = dirname(dirname(__DIR__));
	$began = time();
	$up    = false;

	while (time() - $began < 60) {
		$sock = @fsockopen("127.0.0.1", 2204, $errno, $errstr, 1);
		if ($sock) { fclose($sock); $up = true; break; }

		// Give up early if the worker is already gone. It used to wait the
		// full minute and then report success anyway, so the panel revealed
		// a video link pointing at a port nothing was listening on - which
		// is what "refused to connect" was. The grace period is because the
		// worker takes a moment to appear after master.py returns.
		if (time() - $began > 3) {
			exec("pgrep -f " . escapeshellarg("$app/[h]uman_following/") . " > /dev/null 2>&1", $ignored, $rc);
			if ($rc !== 0) { break; }
		}
		usleep(300000);   // 300 ms between probes
	}

	if (!$up) {
		http_response_code(503);
		$log  = "$app/logs/human_following.log";
		$tail = is_file($log) ? trim((string) @shell_exec("tail -n 4 " . escapeshellarg($log))) : "";
		echo "could not start human following" . ($tail !== "" ? ":\n\n" . $tail : ".");
		exit;
	}
}

echo "state: $state";
?>
