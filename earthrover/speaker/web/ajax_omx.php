<?php

$path = $_POST["rec_path"];
$cmd_speak="sudo omxplayer -o local /var/www/html/".$path;
os.system($cmd_speak);

?>
