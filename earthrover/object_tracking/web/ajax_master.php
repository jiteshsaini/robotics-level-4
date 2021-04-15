<?php

$state=$_POST["state"];

$xx=exec("sudo python /var/www/html/earthrover/object_tracking/master.py $state");

?>
