<!--
Project: Earthrover
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in

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

echo"<div align='center' id='box_outer'>";//------------------------
	echo"<h1 align='center' style='color:#0000b3'>Earth Rover</h1>";
	
	echo"<div align='center' id='box_top'>";
		//Range Sensor block
		echo"<div class='box_controls' style='width:10%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Range Sensor</label><br>";
				echo"<b id='range' style='float:right;color:blue;font-size:30px'></b>";
				echo"<input id='range_button' type='submit' onclick=toggle_rangeSensor('range_button'); value='OFF'/>";
				echo"<script src='/earthrover/range_sensor/web/rangesensor.js'></script>";
			echo"</zz>";
		echo"</div>";
		
		//Javascript Robotics block
		echo"<div class='box_controls' style='width:25%'>";
			echo"<zz>";
				echo"<label class='floatLabel' style='width: 120px;'>Javascript Robotics</label><br>";
				echo"<div style='float:left;width:20%;border:0px solid blue'>";
					$href_acc= 'https://'.$host."/earthrover/accelerometer";
					echo"<a href='$href_acc' target='_blank'><button><img src='css/images/acc.png' height='40px'></button></a>";
				echo"</div>";
				echo"<div style='float:left;width:20%;margin-left:5%;border:0px solid red'>";
					$href_voice= 'https://'.$host."/earthrover/voice_control";
					echo"<a href='$href_voice' target='_blank'><button><img src='css/images/speak.png' height='40px'></button></a>";
				echo"</div>";
				echo"<div style='float:left;width:20%;margin-left:5%;border:0px solid red'>";
					$href_obj= 'https://'.$host."/earthrover/compass";
					echo"<a href='$href_obj' target='_blank'><button><img src='css/images/compass.png' height='35px'></button></a>";
				echo"</div>";
			echo"</zz>";
		echo"</div>";

		//AI Robotics block
		echo"<div class='box_controls' style='width:60%'>";
			echo"<zz>";
				echo"<label class='floatLabel' style='width: 100px;'>AI Robotics</label><br>";
				
				echo"<div style='float:left;width:80%;border:0px solid red'>";
					$style="width:18%;";
					echo"<button id='image_classification' onclick=button_AI_action(id); style=$style>Image Classification</button>";
					echo"<button id='object_detection' onclick=button_AI_action(id); style=$style>Object Detection</button>";
					echo"<button id='object_tracking' onclick=button_AI_action(id); style=$style>Object Tracking</button>";
					echo"<button id='human_following' onclick=button_AI_action(id); style=$style>Human Following</button>";
					
				echo"</div>";
				
				echo"<div style='float:left;width:18%;border:0px solid red'>";
					$style_img="display:none;";
				
					$href= 'http://'.$host.':2204';
					echo"<button id='img_object_tracking' style=$style_img><a href='$href' target='_blank'><img src='css/images/track.png' height='35px'></a></button>";
					
					$href= 'http://'.$host."/earthrover/object_detection/web";
					echo"<button id='img_object_detection' style=$style_img><a href='$href' target='_blank'><img src='css/images/obj.png' height='40px'></a></button>";
					
					$href= 'http://'.$host.':2204';
					echo"<button id='img_human_following' style=$style_img><a href='$href' target='_blank'><img src='css/images/human_follower.png' height='40px'></a></button>";
					
					$href= 'http://'.$host.':2204';
					echo"<button id='img_image_classification' style=$style_img><a href='$href' target='_blank'><img src='css/images/compass.png' height='40px'></a></button>";
					
					
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
	
	echo"<div align='center' id='box_bottom'>";
		
		//Camera Controls block
		echo"<div class='box_controls' style='width:14%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Camera</label><br>";
				echo"<input id='cam_on' type='submit' onclick=camera('on'); value='ON'/>";
				echo"<input id='cam_off' type='submit' onclick=camera('off'); value='OFF'/>";
				echo"<br>";
				echo"<txt> .</txt>";
			echo"</zz>";
		echo"</div>";
		
		//Lights Controls block
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
		
		//Sound Controls block
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
		
		
	echo"</div>";
	
	
echo"</div>";//------------------------------------------------------

?>

</body>
</html>
