<?php
// Starting a detector takes roughly 25-30 seconds: the model has to load and
// the camera has to come up before Flask binds port 2204. Wait for that
// port to accept a connection before replying, so the UI reveals the video
// link only when the stream is really there. Racing a fixed timer is why the
// iframe used to show "refused to connect".
set_time_limit(90);

$state = $_POST["state"];

exec("sudo python /var/www/html/earthrover/human_following/master.py $state");

if ($state == "1") {
	$deadline = time() + 60;
	while (time() < $deadline) {
		$sock = @fsockopen("127.0.0.1", 2204, $errno, $errstr, 1);
		if ($sock) { fclose($sock); break; }
		usleep(300000);   // 300 ms between probes
	}
}

echo "state: $state";
?>
