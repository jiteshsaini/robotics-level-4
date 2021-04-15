<?php
include_once '../vars.php';

$light_id=$_POST["light_id"];
$state=$_POST["state"];

if ($light_id=="camlight"){
	system("gpio -g write $cameralight $state");
}

if ($light_id=="headlight"){
	system("gpio -g write $headlight_right $state");
	system("gpio -g write $headlight_left $state");
}

echo"$light_id, $state";
/*
$myFile = "testFile.txt";
$fh = fopen($myFile, 'w') or die("can't open file");
fwrite($fh, $light_id.$state);
fclose($fh);
*/
?>
