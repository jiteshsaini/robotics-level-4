<?php
include_once '../vars.php';
	
$msg=$_POST["message"];

if ($msg=="left"){
	left();
}
elseif ($msg=="right"){
	right();
}
elseif ($msg=="forward"){
	forward();
}
elseif ($msg=="backward"){
	back();
}
elseif ($msg=="light_on"){
	system("sudo raspi-gpio set $cameralight dh");
}
else{
	stop();
	system("sudo raspi-gpio set $cameralight dl");
}
?>
