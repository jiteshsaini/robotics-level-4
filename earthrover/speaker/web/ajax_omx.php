<?php

$path = $_POST["rec_path"];
$cmd_speak="sudo omxplayer /var/www/html/".$path;
os.system($cmd_speak);

?>
