<?php
include_once '../vars.php';
	
$msg=$_POST["message"];

if ($msg=="forward"){
	forward();
	set_gpio($cameralight,'0');
}
elseif ($msg=="backward"){
	back();
	set_gpio($cameralight,'0');
}
elseif ($msg=="light_on"){
	stop();
	set_gpio($cameralight,'1');
}
else{
	stop();
	set_gpio($cameralight,'0');
}

?>
