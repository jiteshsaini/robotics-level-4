<?php

global $m1_1,$m1_2,$m2_1,$m2_2;

 $m1_1 = 8; //motor 1
 $m1_2 = 11; //motor 1
 $m2_1 = 14; //motor 2
 $m2_2 = 15; //motor 2  
 
 $headlight_right = 18; //head light Right 
 $headlight_left = 27; //head light Left
 $cameralight = 17; //camera light

// pinctrl refuses to drive a pin that is not already an output - it answers
// "Can't set pin value, not an output" and does nothing. Only the control
// panel used to set the mode, so any page that moved the robot without the
// panel having been loaded first failed silently.
//
// One call, and mode only: `op` without dh/dl leaves the pin's level alone,
// so this is safe to repeat and will not switch the lights off mid-drive.
exec("pinctrl set " . implode(",", array($m1_1, $m1_2, $m2_1, $m2_2,
                                         $headlight_right, $headlight_left,
                                         $cameralight)) . " op");

//pwm pins are 20 & 21 (seperately handled in python). 
//Rpi's Hardware PWM interferes with audio port.

function gpio_initialise(){
	//echo"init<br>";
	global $m1_1,$m1_2,$m2_1,$m2_2;

	//====motors=================
	
	set_gpio($m1_1,'output');
	set_gpio($m1_2,'output');
	set_gpio($m2_1,'output');
	set_gpio($m2_2,'output');
	
	set_gpio($m1_1,'0');
	set_gpio($m1_2,'0');
	set_gpio($m2_1,'0');
	set_gpio($m2_2,'0');
	
	global $cameralight,$headlight_left,$headlight_right;

	//====Lights============
	set_gpio($headlight_right,'output');
	set_gpio($headlight_left,'output');
	set_gpio($cameralight,'output');
	
	set_gpio($headlight_right,'0');
	set_gpio($headlight_left,'0');
	set_gpio($cameralight,'0');
}

function set_speed($pwm_val){
    $myFile = __DIR__ . "/control_panel/pwm/pwm1.txt";
    $fh = fopen($myFile, 'w') or die("can't open file");
    fwrite($fh, $pwm_val);
    fclose($fh);

    exec("python3 " . __DIR__ . "/control_panel/pwm/pwm_control.py");# launch Python script

}

function move($dir){
	switch ($dir) {	
		case 'f': forward(); break;
		case 'b': back(); break;
		case 'r': right(); break;
		case 'l': left(); break;
		case 's': stop(); break;	
	}
}

function right(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	set_gpio($m1_1,'1');
	set_gpio($m1_2,'0');
	set_gpio($m2_1,'1');
	set_gpio($m2_2,'0');
	
}
function left(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	set_gpio($m1_1,'0');
	set_gpio($m1_2,'1');
	set_gpio($m2_1,'0');
	set_gpio($m2_2,'1');
}
function forward(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	set_gpio($m1_1,'1');
	set_gpio($m1_2,'0');
	set_gpio($m2_1,'0');
	set_gpio($m2_2,'1');
	//echo"fwd<br>";
}
function back(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	set_gpio($m1_1,'0');
	set_gpio($m1_2,'1');
	set_gpio($m2_1,'1');
	set_gpio($m2_2,'0');
}
function stop(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	set_gpio($m1_1,'0');
	set_gpio($m1_2,'0');
	set_gpio($m2_1,'0');
	set_gpio($m2_2,'0');
}

function set_gpio($pin,$x){
	switch($x){
		case '1': $z='dh';break;
		case '0': $z='dl';break;
		case 'output': $z='op';break;
	}
	$cmd="pinctrl set $pin $z";
	system($cmd);
	//echo"$x: $cmd <br>";
}

?>

