<?php

$state=$_POST["state"];

$xx=exec("sudo python3 /var/www/html/earthrover/image_classification/master.py $state");

?>
