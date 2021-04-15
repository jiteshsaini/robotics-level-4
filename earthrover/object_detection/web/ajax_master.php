<?php

$state=$_POST["state"];

$xx=exec("sudo python /var/www/html/earthrover/object_detection/master.py $state");

?>
