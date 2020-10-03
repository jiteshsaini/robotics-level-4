<!--
Project: Earthrover
Created by: Jitesh Saini
-->
<html>
<head>        
   <title>Control Panel</title>
   <link href="css/cp.css" rel="stylesheet" type="text/css">  
   <script src="js/jquery.min.js"></script>        
   <script src="js/cp.js"></script>        
   <script>
	
	
   </script>
</head> 
<body>
<?php

$host=$_SERVER['SERVER_ADDR'];//192.168.1.20
$path=rtrim(dirname($_SERVER["PHP_SELF"]), "/\\"); //earthrover

printf("<div align='center' id='box_outer'>");//------------------------
	echo"<div align='center' id='box_title'>";
		echo"<h1 style='color:#0000b3'>Earth Rover</h1>";
		
		echo"<div class='box_controls' style='width:14%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Camera</label><br>";
				echo"<input id='cam_on' type='submit' onclick=camera('on'); value='ON'/>";
				echo"<input id='cam_off' type='submit' onclick=camera('off'); value='OFF'/>";
				echo"<br>";
				echo"<txt> .</txt>";
			echo"</zz>";
		echo"</div>";
		
		echo"<div class='box_controls' style='width:14%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Lights</label><br>";
				echo"<input id='camlight' style='background-color:lightgray' type='submit' onclick=toggle_light('camlight'); value='OFF'/>";
				echo"<input id='headlight' style='background-color:lightgray' type='submit' onclick=toggle_light('headlight'); value='OFF'/>";
				echo"<br>";
				echo"<txt>Camera</txt>";
				echo"<txt>Front</txt>";
			echo"</zz>";
		echo"</div>";
		
		echo"<div class='box_controls' style='width:14%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Range Sensor</label><br>";
				echo"<b id='range' style='float:right;color:blue;font-size:30px'></b>";
				echo"<input id='range_button' type='submit' onclick=toggle_rangeSensor('range_button'); value='OFF'/>";
				echo"<script src='/earthrover/range_sensor/web/rangesensor.js'></script>";
			echo"</zz>";
		echo"</div>";
		
		echo"<div class='box_controls'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Speaker</label><br>";
				echo"<script src='/earthrover/speaker/web/speaker.js'></script>";
				echo"<div style='float:left;width:70%;border:0px solid blue'>";
					echo"<input id='txt_tts' type='text' style='width:90%'><br>";
					echo"<input id='radio1' type='radio' name='gender' value='male' checked> M ";
					echo"<input type='radio' name='gender' value='female'> F ";
					echo"<input id='tts' type='submit' onclick=button_tts(); value='speak' style='width:30%;height:20px;margin-left:5%'/>";
				echo"</div>";
				echo"<div style='float:left;width:25%;margin-left:2%;border:0px solid red'>";
					echo"<input id='rec1' type='submit' onclick=button_recording(1); value='horn' style='width:80%;height:20px;margin-bottom:3%'/>";
					echo"<input id='rec2' type='submit' onclick=button_recording(2); value='siren' style='width:80%;height:20px'/>";
				echo"</div>";
				
			echo"</zz>";
		echo"</div>";
		
		echo"<div class='box_controls' style='width:30%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Adv Controls</label><br>";
				echo"<div style='float:left;width:20%;border:0px solid blue'>";
					$href_acc= 'https://'.$host."/earthrover/accelerometer";
					echo"<a href='$href_acc' target='_blank'><button><img src='css/images/acc.png' height='40px'></button></a>";
				echo"</div>";
				echo"<div style='float:left;width:20%;margin-left:5%;border:0px solid red'>";
					$href_voice= 'https://'.$host."/earthrover/voice_control";
					echo"<a href='$href_voice' target='_blank'><button><img src='css/images/speak.png' height='40px'></button></a>";
				echo"</div>";
				
				echo"<div style='float:left;width:20%;margin-left:5%;border:0px solid red'>";
					$href_obj= 'http://'.$host."/earthrover/object_detection/web";
					echo"<a href='$href_obj' target='_blank'><button><img src='css/images/obj.png' height='40px'></button></a>";
				echo"</div>";
				
				echo"<div style='float:left;width:20%;margin-left:5%;border:0px solid red'>";
					$href_obj= 'http://'.$host.':2204';
					echo"<a href='$href_obj' target='_blank'><button><img src='css/images/track.png' height='35px'></button></a>";
				echo"</div>";
				
			echo"</zz>";
		echo"</div>";

	echo"</div>";
	
	//****************************************************************************
	
	$link_remote= 'http://'.$host.$path.'/'."remote.php";//http://192.168.1.20/earthrover/remote.php
	$link_vid= 'http://'.$host.':8000';//http://192.168.1.20:8000
	
	echo"
		<iframe src='$link_vid' id='box_video'></iframe>
		<iframe src= '$link_remote' id='box_remote'></iframe>
	";
	//****************************************************************************
	
echo"</div>";//------------------------------------------------------

?>

</body>
</html>
