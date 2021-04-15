<?php
include_once '../vars.php';

$deg=$_POST["heading_cmd"];

global $course;
$course=get_current_heading();

turn($deg);

echo"done";

function turn($h_final){
	//set_speed('30');
	global $course;
	$h=get_current_heading();
	$h_current=intval($h);
	
	$k=0;
	while($h_current != $h_final){

		$arr=get_dir_deg($h_current,$h_final);
		$dir=$arr[0];
		$degrees=$arr[1];
		$accuracy_factor=get_accuracy_factor($degrees);
		
		move($dir);
		$delay=$degrees*$accuracy_factor; //turning time  (milliseconds of motion. lesser the degrees, lesser the time)
		//echo "direction: $dir , Angle difference: $degrees ,delay= $delay<br>";
	
		usleep($delay * 1);
		move('s');
		usleep(300*1000); //pause between turning moves
		
		$h=get_current_heading();
		$h_current=intval($h);
		
		$k=$k+1;
		//if($k>30)
			//break;
	}
	$course=$h_current;
	//echo"<h2>settled in attempts: $k, new course: $course</h2>";
	//set_speed('50');
}

function get_accuracy_factor($deg){
	if ($deg>90)
		$k=7000;
		
	if ($deg>=45 and $deg<=90)
		$k=6500;
		
	if ($deg>=6 and $deg<45)
		$k=2100;
	
	if ($deg<6)
		$k=1;
		
	return $k;
}


function get_dir_deg($current,$final){
	$diff=abs($final-$current);
	
	if ($diff<=180){
		if($final>$current)
			$dir='r';
		else
			$dir='l';
		
		$deg=$diff;
	}
	else{
		if($final>$current){
			//final is bigger
			$dir='l';
			$deg=360-$final+$current;
			
		}
		else{
			//current is bigger
			$dir='r';
			$deg=360-$current+$final;
		}
			
	}
	
	$arr[0]=$dir;
	$arr[1]=$deg;
	
	return $arr;
}


function get_current_heading(){
	$myFile = "robot_compass/heading.txt";

	$fr=fopen($myFile, 'r') or die("can't open file");
	$h=fread($fr, '5');
	fclose($fr);
	
	return $h;
}


?>
