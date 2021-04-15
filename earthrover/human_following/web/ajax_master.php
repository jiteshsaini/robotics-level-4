<?php

$state=$_POST["state"];

$xx=exec("sudo python /var/www/html/earthrover/human_following/master.py $state");

?>
