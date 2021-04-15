<?php
include_once '../vars.php';

$x=$_POST["acc_x"];
$y=$_POST["acc_y"];
$z=$_POST["acc_z"];

if ($y>4){
	right();
}
elseif($y<-4){
	left();
}
else{

	if ($z>5){
		forward();
	}
	elseif ($z<-5){
		back();
	}
	else{
		stop();
	}
}

?>
