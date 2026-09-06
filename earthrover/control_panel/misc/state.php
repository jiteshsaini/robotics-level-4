<?php
// What is actually running on the rover, so a page that arrives late can show
// it. Read-only: nothing here starts, stops or changes anything.
//
// The panel used to open every control at OFF regardless, because it had no
// way of knowing. That was wrong on a reload, and wrong on a second phone.
//
// vars.php is here for the pin numbers. Including it also re-asserts output
// mode on those pins, which every other endpoint in this app already does on
// every request; it does not change a level.
include_once dirname(__DIR__, 2) . "/vars.php";

header("Content-Type: application/json");

// One pgrep for every worker, and one pinctrl for both light pins. This runs
// on every page load of a 415 MB board that is also driving a robot, and each
// spawn cost about a tenth of a second when they were separate.
//
// The bracket stops the pattern matching the shell this runs in, which would
// otherwise report everything as running.
$names = array(
	"camera"               => "cam_server",
	"range"                => "range_sensor",
	"object_detection"     => "object_detection_web2",
	"object_tracking"      => "object_tracking",
	"human_following"      => "human_follower",
	"image_classification" => "image_recog_cv2",
);

$alts = array();
foreach ($names as $script) {
	$alts[] = "[" . $script[0] . "]" . substr($script, 1) . "\\.py";
}
exec("pgrep -af " . escapeshellarg(implode("|", $alts)) . " 2>/dev/null", $procs);
$ps = implode("\n", $procs);

function er_up($ps, $script) { return strpos($ps, $script . ".py") !== false ? 1 : 0; }

// "17: op -- -- | hi // GPIO17 = output", one line per pin
exec("pinctrl get " . (int) $cameralight . "," . (int) $headlight_right . " 2>/dev/null", $pins);
$camlight  = (isset($pins[0]) && strpos($pins[0], "| hi") !== false) ? 1 : 0;
$headlight = (isset($pins[1]) && strpos($pins[1], "| hi") !== false) ? 1 : 0;

// Only one can be running - they each hold the camera - so the first hit wins.
$ai = "";
foreach (array("object_detection", "object_tracking", "human_following", "image_classification") as $id) {
	if (er_up($ps, $names[$id])) { $ai = $id; break; }
}

echo json_encode(array(
	"camera"    => er_up($ps, "cam_server"),
	"range"     => er_up($ps, "range_sensor"),
	"ai"        => $ai,
	"camlight"  => $camlight,
	// the two headlights are switched together, so either answers for both
	"headlight" => $headlight,
));
?>
