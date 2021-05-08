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
<body onload="init()">
<?php

$host=$_SERVER['SERVER_ADDR'];//192.168.1.20
$path=rtrim(dirname($_SERVER["PHP_SELF"]), "/\\"); //earthrover

echo"<div align='center' id='box_outer'>";//------------------------
	echo"<b align='center' style='font-size:40px;color:#0000b3'>Earth Rover</b>";
	echo"<a href='readme/' target='_blank'><img style='float:right' src='/earthrover/control_panel/css/images/earthrover.png' height='60px'></a>";
	echo"<div align='center' class='box_inner'>";//------------------------
		//Range Sensor block
		echo"<div class='box_controls' style='width:15%'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Range Sensor</label><br>";
				echo"<b id='range' style='float:right;color:blue;font-size:30px'></b>";
				echo"<input style='height:40px' id='range_button' type='submit' onclick=toggle_rangeSensor('range_button'); value='OFF'/>";
				echo"<script src='/earthrover/range_sensor/web/rangesensor.js'></script>";
			echo"</zz>";
		echo"</div>";
		
		//Javascript Robotics block
		echo"<div class='box_controls' style='width:20%'>";
			echo"<zz>";
				echo"<label class='floatLabel' style='width: 120px;'>Javascript Robotics</label><br>";
				
				echo"<div style='float:left;width:98%;border:0px solid red'>";
					$w1="30%"; //width of tooltip
					$w2="80%"; //width of button inside tooltip
					
					$href_acc= 'https://'.$host."/earthrover/accelerometer";
					$href_voice= 'https://'.$host."/earthrover/voice_control";
					$href_obj= 'https://'.$host."/earthrover/compass";
					
					//Accelerometer control
					echo"<div class='tooltip' style='width:$w1'>
						 <a href='$href_acc' target='_blank'><button style='width:$w2'><img src='css/images/acc.png' height='40px'></button></a>
					 	 <span class='tooltiptext'>Control the robot with your Mobile phone's Accelerometer data</a></span>
					 	 </div>";
					
					//Voice control (Web Speech API)
					echo"<div class='tooltip' style='width:$w1'>
						<a href='$href_voice' target='_blank'><button style='width:$w2'><img src='css/images/speak.png' height='40px'></button></a>
						<span class='tooltiptext'>Control the robot through Voice commands </span>
						</div>";
					
					//Javascript Compass
					echo"<div class='tooltip' style='width:$w1'>
						<a href='$href_obj' target='_blank'><button style='width:$w2'><img src='css/images/compass.png' height='35px'></button></a>
						<span class='tooltiptext'>Use mobile phone as Compass for the robot</span>
						</div>";	
					
				echo"</div>";
			echo"</zz>";
		echo"</div>";

		//AI Robotics block
		echo"<div class='box_controls' style='width:60%'>";
			echo"<zz>";
				echo"<label class='floatLabel' style='width: 100px;'>AI Robotics</label><br>";
				
				echo"<div style='float:left;width:88%;border:0px solid red'>";
					
					$w1="19%"; //width of tooltip
					$w2="85%"; //width of button inside tooltip
					
					$href= 'https://'.$host."/earthrover/tm/";
					
					//Gesture control
					echo"<div class='tooltip' style='width:$w1'>
						<a href='$href' target='_blank'><button style='width:$w2;background-color:#fcfcc5'>Gesture Controls</button></a>
						<span class='tooltiptext'>Model generated using Teachable Machine. Control the robot using hand gestures.</span>
						</div>";	
					
					//Image Classification
					echo"<div class='tooltip' style='width:$w1'>
						<button id='image_classification' onclick=button_AI_action(id); style='width:$w2'>Image Classification</button>
						<span class='tooltiptext'>Real-time Image Classification</span>
						</div>";	
					
					//Object Detection
					echo"<div class='tooltip' style='width:$w1'>
						<button id='object_detection' onclick=button_AI_action(id); style='width:$w2'>Object Detection</button>
						<span class='tooltiptext'>Robot Detects a selected object and raises alarm</span>
						</div>";
						
					//Object Tracking
					echo"<div class='tooltip' style='width:$w1'>
						<button id='object_tracking' onclick=button_AI_action(id); style='width:$w2'>Object Tracking</button>
						<span class='tooltiptext'>Robot tracks and follows a small object such as ball</span>
						</div>";
					
					//Human Following
					echo"<div class='tooltip' style='width:$w1'>
						<button id='human_following' onclick=button_AI_action(id); style='width:$w2'>Human Following</button>
						<span class='tooltiptext'>Robot tracks and follows a human </span>
						</div>";
					
				echo"</div>";
				
				//Display the Green button 
				echo"<div style='float:left;width:10%;border:0px solid green'>";
					$style_img="display:none;position:absolute;top:1px";
				
					$href= 'http://'.$host.':2204';
					echo"<a id='img_object_tracking' style=$style_img href='$href' target='_blank'><img src='css/images/obj_tracking.png' height='60px'></a>";
					
					$href= 'http://'.$host."/earthrover/object_detection/web";
					echo"<a id='img_object_detection' style=$style_img href='$href' target='_blank'><img src='css/images/obj_detection.png' height='60px'></a>";
					
					$href= 'http://'.$host.':2204';
					echo"<a id='img_human_following' style=$style_img href='$href' target='_blank'><img src='css/images/human_follower.png' height='60px'></a>";
					
					$href= 'http://'.$host.':2204';
					echo"<a id='img_image_classification' style=$style_img href='$href' target='_blank'><img src='css/images/img_classification.png' height='60px'></a>";
					
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
	
	echo"<div align='center' class='box_inner'>";//------------------------
		
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
				echo"<input id='camlight' type='submit' onclick=toggle_light('camlight'); value='OFF'/>";
				echo"<input id='headlight' type='submit' onclick=toggle_light('headlight'); value='OFF'/>";
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
	
	echo"<div align='center' style='margin-top:50px;margin-bottom:10px' class='box_inner'>";//------------------------
		echo"<span id='hw_1'></span>";
		echo"<span style='margin-left:15%' id='hw_2'></span>";
		echo"<span style='margin-left:15%' id='hw_3'></span>";
	echo"</div>";
	
echo"</div>";//--box_outer---------------------------------------------------

?>


</body>
</html>
