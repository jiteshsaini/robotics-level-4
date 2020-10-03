<?php

$label=$_POST["lbl"];
$myfile = fopen("object_cmd.txt", "w") or die("Unable to open file!");
fwrite($myfile, $label);
fclose($myfile);
?>
