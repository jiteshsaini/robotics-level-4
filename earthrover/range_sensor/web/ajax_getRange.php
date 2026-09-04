<?php

$myFile = "range.txt";

$fr=fopen($myFile, 'r') or die("can't open file");
$str=fread($fr, 20);
fclose($fr);

$str = trim($str);

// range.txt can legitimately hold non-numeric content: "--" is written by
// master.py when the sensor is switched off. PHP 7 let round() coerce that
// to 0 with a warning; PHP 8 throws a TypeError, which returned HTTP 500
// twice a second and froze the reading in the UI (the jQuery success handler
// never ran). Anything non-numeric now reports as out of range, which the
// front-end already renders as "-".
if ($str === "" || !is_numeric($str)) {
	echo "999";
} else {
	echo round((float)$str, 1);
}

?>
