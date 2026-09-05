<?php

// omxplayer was removed in Raspberry Pi OS Bullseye; mpv replaces it.
// system(), not os.system() - Python syntax in a PHP file, fatal on PHP 8.
//
// The requested path is whitelisted to the speaker's own sounds directory:
// this value comes from a POST and ends up in a command run as root, so it
// must never be trusted as-is.
$APP = dirname(dirname(__DIR__));
$SOUND_DIR = $APP . "/speaker/sounds";

$req  = basename($_POST["rec_path"] ?? "");
$file = $SOUND_DIR . "/" . $req;

if ($req === "" || !is_file($file) || pathinfo($file, PATHINFO_EXTENSION) !== "mp3") {
	http_response_code(400);
	echo "unknown sound";
	exit;
}

// Same reason as speaker_tts.py: ALSA defaults to card 0 (HDMI), which
// cannot be opened on a headless rover. Prefer the 3.5mm jack by card
// NAME when the board has one; boards without a jack use the default.
$dev = "";
if (@strpos(@file_get_contents("/proc/asound/cards"), "Headphones") !== false) {
	$dev = " --audio-device=alsa/plughw:CARD=Headphones,DEV=0";
}

$cmd = "mpv --no-video --really-quiet" . $dev . " " . escapeshellarg($file) . " > " . $APP . "/logs/speaker.log 2>&1 &";
system($cmd);

echo "playing " . $req;
?>
