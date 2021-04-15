<?php

$myfile = fopen("../../robot_compass/heading.txt", "r") or die("Unable to open file!");
$str = fread($myfile,5);
fclose($myfile);

echo "$str";
?>
