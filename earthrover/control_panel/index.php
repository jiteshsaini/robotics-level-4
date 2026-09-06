<!--
Project: Earthrover
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in
-->
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="utf-8">
   <!-- Without this the phone renders a ~980px desktop page and clips the
        left edge - and a phone is what this robot is driven from. -->
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <title>Control Panel</title>
   <link href="css/cp.css?v=<?php echo filemtime(__DIR__."/css/cp.css"); ?>" rel="stylesheet" type="text/css">  
   <script src="js/post.js?v=<?php echo filemtime(__DIR__."/js/post.js"); ?>"></script>        
   <script src="js/cp.js?v=<?php echo filemtime(__DIR__."/js/cp.js"); ?>"></script>
   <!-- also loaded by the remote pad in the iframe; here so the arrow keys
        work while the focus is anywhere on the panel -->
   <script src="js/remote.js?v=<?php echo filemtime(__DIR__."/js/remote.js"); ?>"></script>        
   <script>
	
	
   </script>
</head> 
<body onload="init()">
<?php

$host=$_SERVER['SERVER_ADDR'];//192.168.1.20
$path=rtrim(dirname($_SERVER["PHP_SELF"]), "/\\"); //earthrover

echo"<div align='center' id='box_outer'>";//------------------------
	echo"<b align='center' style='font-size:40px;color:#0000b3'>Earth Rover</b>";
	echo"<a href='readme/' target='_blank'><img style='float:right' src='css/images/earthrover.png' height='60px'></a>";
	echo"<div align='center' class='box_inner'>";//------------------------
		//Range Sensor block
		echo"<div class='box_controls blk-range'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Range Sensor</label><br>";
				echo"<b id='range' style='float:right;color:blue;font-size:30px'></b>";
				echo"<input style='height:40px' id='range_button' type='submit' onclick=toggle_rangeSensor('range_button'); value='OFF'/>";
				echo"<script src='../range_sensor/web/rangesensor.js?v=".filemtime(dirname(__DIR__)."/range_sensor/web/rangesensor.js")."'></script>";
			echo"</zz>";
			echo"<span class='gear' onclick=settings('range'); title='Settings'>&#9881;</span>";
		echo"</div>";
		
		//Javascript Robotics block
		echo"<div class='box_controls blk-js'>";
			echo"<zz>";
				echo"<label class='floatLabel' style='width: 120px;'>Javascript Robotics</label><br>";
				
				echo"<div class='row-js'>";
					
					$app_url = $host . rtrim(dirname(dirname($_SERVER['PHP_SELF'])), '/');
					$href_acc = 'https://' . $app_url . "/accelerometer";
					$href_voice = 'https://' . $app_url . "/voice_control";
					$href_obj = 'https://' . $app_url . "/compass";
					
					//Accelerometer control
					echo"<div class='tooltip tt-js'>
						 <a href='$href_acc' target='_blank'><button class='btn-fill'><img src='css/images/acc.png' height='40px'></button></a>
					 	 <span class='tooltiptext'>Control the robot with your Mobile phone's Accelerometer data</a></span>
					 	 </div>";
					
					//Voice control (Web Speech API)
					echo"<div class='tooltip tt-js'>
						<a href='$href_voice' target='_blank'><button class='btn-fill'><img src='css/images/speak.png' height='40px'></button></a>
						<span class='tooltiptext'>Control the robot through Voice commands </span>
						</div>";
					
					//Javascript Compass
					echo"<div class='tooltip tt-js'>
						<a href='$href_obj' target='_blank'><button class='btn-fill'><img src='css/images/compass.png' height='35px'></button></a>
						<span class='tooltiptext'>Use mobile phone as Compass for the robot</span>
						</div>";	
					
				echo"</div>";
			echo"</zz>";
		echo"</div>";

		//AI Robotics block
		echo"<div class='box_controls blk-ai'>";
			echo"<zz>";
				// Which inference backend the AI features below will use.
				// util.py decides this by detecting the accelerator; asking it
				// here rather than reimplementing the check in PHP keeps one
				// source of truth. ~110 ms, once per page load.
				$er_edgetpu = trim((string) @shell_exec(
					// from /tmp: importing util pulls in RPi.GPIO, which drops a
				// working file in the current directory
				"cd /tmp && python3 -c \"import sys; sys.path.insert(0,'" . dirname(__DIR__) . "');"
					. " from util import edgetpu; print(edgetpu)\" 2>/dev/null"));

				if ($er_edgetpu === '1') {
					$accel = "<span title='Coral USB Accelerator detected - about 57 ms per inference' style='color:#1a9e1a;font-size:12px;font-weight:600'>&#9679; Coral</span>";
				} elseif ($er_edgetpu === '0') {
					// Normal, not an error: no accelerator, or its runtime is absent.
					$accel = "<span title='No Coral detected - running on CPU, about 230 ms per inference' style='color:#888;font-size:12px'>&#9679; CPU</span>";
				} else {
					// Distinct from CPU on purpose: this is a broken install
					// (util.py missing or raising), not a hardware fact.
					$accel = "<span title='Could not read the backend from util.py - check the install' style='color:#c00;font-size:12px;font-weight:600'>&#9679; unknown</span>";
				}

				// The indicator goes INSIDE the label: .floatLabel is positioned
				// absolute (a floating caption over the box), so a sibling span
				// drops into normal flow and lands on top of the button row.
				// width:auto so a longer state ("unknown") is not clipped.
				echo"<label class='floatLabel' style='width:auto;padding:0 6px;white-space:nowrap;'>AI Robotics &nbsp;$accel</label><br>";
				
				echo"<div class='row-ai'>";
					
					
					$href = 'https://' . $app_url . "/tm/";
					
					//Gesture control
					echo"<div class='tooltip tt-ai'>
						<a href='$href' target='_blank'><button class='btn-fill btn-gesture'>Gesture Controls</button></a>
						<span class='tooltiptext'>Model generated using Teachable Machine. Control the robot using hand gestures.</span>
						</div>";	
					
					//Image Classification
					echo"<div class='tooltip tt-ai'>
						<button id='image_classification' onclick=button_AI_action(id); class='btn-fill'>Image Classification</button>
						<span class='tooltiptext'>Real-time Image Classification</span>
						</div>";	
					
					//Object Detection
					echo"<div class='tooltip tt-ai'>
						<button id='object_detection' onclick=button_AI_action(id); class='btn-fill'>Object Detection</button>
						<span class='tooltiptext'>Robot Detects a selected object and raises alarm</span>
						</div>";
						
					//Object Tracking
					echo"<div class='tooltip tt-ai'>
						<button id='object_tracking' onclick=button_AI_action(id); class='btn-fill'>Object Tracking</button>
						<span class='tooltiptext'>Robot tracks and follows a small object such as ball</span>
						</div>";
					
					//Human Following
					echo"<div class='tooltip tt-ai'>
						<button id='human_following' onclick=button_AI_action(id); class='btn-fill'>Human Following</button>
						<span class='tooltiptext'>Robot tracks and follows a human </span>
						</div>";
					
				echo"</div>";
				
				//Display the Green button 
				echo"<div class='row-ai-status'>";
					// One spinner serves all four AI buttons - only one feature
					// can run at a time (the camera has a single holder).
					echo"<span id='ai_spin' class='er-spin' style='display:none;position:absolute;top:20px'></span>";
					$style_img="display:none;position:absolute;top:1px";
				
					$href= 'http://'.$host.':2204';
					echo"<a id='img_object_tracking' style=$style_img href='$href' target='_blank'><img src='css/images/obj_tracking.png' height='60px'></a>";
					
					$href = 'http://' . $app_url . "/object_detection/web";
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
	// An IPv6 literal needs brackets, or the URL is malformed and no browser
	// can parse it.
	$vid_host = (strpos($host, ':') !== false) ? '['.$host.']' : $host;
	$link_vid= 'http://'.$vid_host.':8000';//http://192.168.1.20:8000
	
	// Wrapped so the pair can wrap onto separate lines on a narrow screen.
	// The ids stay on the iframes themselves - cp.js swaps #box_video's src.
	echo"<div class='box_media'>
		<iframe src='$link_vid' id='box_video' data-src='$link_vid'></iframe>
		<iframe src= '$link_remote' id='box_remote'></iframe>
	</div>";
	//****************************************************************************
	
	echo"<div align='center' class='box_inner'>";//------------------------
		
		//Camera Controls block
		echo"<div class='box_controls blk-cam'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Camera</label><br>";
				echo"<input id='cam_on' type='submit' onclick=camera('on'); value='ON'/>";
				echo"<input id='cam_off' type='submit' onclick=camera('off'); value='OFF'/>";
				echo"<br>";
				echo"<span id='cam_spin' class='er-spin' style='display:none'></span>";
				echo"<txt> .</txt>";
			echo"</zz>";
			echo"<span class='gear' onclick=settings('camera'); title='Settings'>&#9881;</span>";
		echo"</div>";
		
		//Lights Controls block
		echo"<div class='box_controls blk-lights'>";
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
		echo"<div class='box_controls blk-speaker'>";
			echo"<zz>";
				echo"<label class='floatLabel'>Speaker</label><br>";
				echo"<script src='../speaker/web/speaker.js?v=".filemtime(dirname(__DIR__)."/speaker/web/speaker.js")."'></script>";
				echo"<div class='spk-text'>";
					echo"<input id='txt_tts' type='text' style='width:90%'><br>";
					echo"<input id='radio1' type='radio' name='gender' value='male' checked> M ";
					echo"<input type='radio' name='gender' value='female'> F ";
					echo"<input id='tts' type='submit' onclick=button_tts(); value='speak' style='width:30%;height:20px;margin-left:5%'/>";
				echo"</div>";
				echo"<div class='spk-clips'>";
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
		echo"<span style='margin-left:15%' id='hw_4'></span>";
	echo"</div>";
	
echo"</div>";//--box_outer---------------------------------------------------

?>

<!-- One box, shared by every gear. cp.js fills in the fields. -->
<div id="cfg_bg" onclick="close_settings();"></div>
<div id="cfg">
	<label id="cfg_title"></label>
	<div id="cfg_fields"></div>
	<input type="submit" value="Save" onclick="save_settings();"/>
	<input type="submit" value="Cancel" onclick="close_settings();"/>
</div>


</body>
</html>
