<?php
/*
 * Project: Earthrover
 * Created by: Jitesh Saini
*/

include_once '../vars.php';
date_default_timezone_set("Asia/kolkata");
$time=date("H:i:s");

$text=$_POST["txt"];
//$text= "robot lights off";

$text=trim($text);
$text=strtolower($text);



$word=explode(" ", $text);
$sz=sizeof($word);
//move($dir);


if($word[0] == "robot" and $sz>1 and $sz<=3){

	if($word[1] == "forward"){
		forward();
		echo"[$time]: moving forward<br>";
	}
	elseif($word[1] == "backward"){
		back();
		echo"[$time]: moving backwards<br>";
	}
	elseif($word[1] == "left"){
		left();
		echo"[$time]: turning left<br>";
	}
	elseif($word[1] == "right"){
		right();
		echo"[$time]: turning right<br>";
	}
	elseif($word[1] == "stop"){
		stop();
		echo"[$time]: movement stopped<br>";
	}
	elseif($word[1] == "lights"){
		
		if($word[2] == "on"){
			system("gpio -g write $cameralight 1");
			system("gpio -g write $headlight_right 1");
			system("gpio -g write $headlight_left 1");
			
			echo"[$time]: Lights switched ON<br>";
		}
		elseif ($word[2] == "off") {
			system("gpio -g write $cameralight 0");
			system("gpio -g write $headlight_right 0");
			system("gpio -g write $headlight_left 0");
			
			echo"[$time]: Lights switched OFF<br>";
		}
		else{
			echo"Invalid command<br>";
		}

	}
	else{
		echo"Invalid command<br>";
	}

}
else{

	echo"Invalid command<br>";

}



?>
