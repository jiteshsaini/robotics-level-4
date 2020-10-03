<?php

global $m1_1,$m1_2,$m2_1,$m2_2;

 $m1_1 = 8; //motor 1
 $m1_2 = 11; //motor 1
 $m2_1 = 14; //motor 2
 $m2_2 = 15; //motor 2  
 
 $headlight_right = 18; //head light Right 
 $headlight_left = 27; //head light Left
 $cameralight = 17; //camera light 

//pwm pins are 20 & 21 (seperately handled in python). 
//Rpi's Hardware PWM interferes with audio port.

function gpio_initialise(){
	//echo"init<br>";
	global $m1_1,$m1_2,$m2_1,$m2_2;

	//====motors=================
	system("gpio -g mode $m1_1 out");
	system("gpio -g mode $m1_2 out");
	system("gpio -g mode $m2_1 out");
	system("gpio -g mode $m2_2 out");
	system("gpio -g write $m1_1 0");
	system("gpio -g write $m1_2 0");
	system("gpio -g write $m2_1 0");
	system("gpio -g write $m2_2 0");
	
	global $cameralight,$headlight_left,$headlight_right;

	//====Lights============
	system("gpio -g mode $headlight_right out");
	system("gpio -g mode $headlight_left out");
	system("gpio -g mode $cameralight out");
	system("gpio -g write $headlight_right 0");
	system("gpio -g write $headlight_left 0");
	system("gpio -g write $cameralight 0");
}

function set_speed($pwm_val){
    $myFile = "/var/www/html/earthrover/control_panel/pwm/pwm1.txt";
    $fh = fopen($myFile, 'w') or die("can't open file");
    fwrite($fh, $pwm_val);
    fclose($fh);

    /* append following lines in /etc/sudoers file for launching python script from PHP:-
	pi ALL=(ALL) NOPASSWD: ALL
	www-data ALL=(ALL) NOPASSWD: ALL
    */
    exec("sudo python /var/www/html/earthrover/control_panel/pwm/pwm_control.py");# launch Python script

}

function move($dir){
	switch ($dir) {	
		case 'f': forward();	break;
		case 'b': back();		break;
		case 'r': right();		break;
		case 'l': left();		break;
		case 's': stop();		break;	
	}
}

function right(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	system("gpio -g write $m1_1 1");
	system("gpio -g write $m1_2 0");
	system("gpio -g write $m2_1 1");
	system("gpio -g write $m2_2 0");
}
function left(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	system("gpio -g write $m1_1 0");
	system("gpio -g write $m1_2 1");
	system("gpio -g write $m2_1 0");
	system("gpio -g write $m2_2 1");
}
function forward(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	system("gpio -g write $m1_1 1");
	system("gpio -g write $m1_2 0");
	system("gpio -g write $m2_1 0");
	system("gpio -g write $m2_2 1");
}
function back(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	system("gpio -g write $m1_1 0");
	system("gpio -g write $m1_2 1");
	system("gpio -g write $m2_1 1");
	system("gpio -g write $m2_2 0");
}
function stop(){
	global $m1_1,$m1_2,$m2_1,$m2_2; 
	system("gpio -g write $m1_1 1");
	system("gpio -g write $m1_2 1");
	system("gpio -g write $m2_1 1");
	system("gpio -g write $m2_2 1");
}
?>

