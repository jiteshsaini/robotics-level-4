<?php

$label=$_POST["lbl"];
$myfile = fopen(__DIR__ . "/object_cmd.txt", "w") or die("Unable to open file!");
fwrite($myfile, $label);
fclose($myfile);
?>
