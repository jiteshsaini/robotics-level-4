<?php
//include_once 'vars.php';

$cam=$_POST["camera"];

if($cam=="on"){
	os.system("sudo python3 /var/www/html/earthrover/camera_lights/cam_server.py &");
}

if($cam=="off"){
	os.system("sudo pkill -f cam_server.py");
}


//echo"Dir: \" $dir \"  <br>";

?>
