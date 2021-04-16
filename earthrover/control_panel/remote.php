<!--
Project: Earthrover
Author: Jitesh Saini
Github: https://github.com/jiteshsaini
website: https://helloworld.co.in
-->
<html>
<head>        
   <title>Remote</title>  
   <link href="css/remote.css" rel="stylesheet" type="text/css">  
   <script src="js/jquery.min.js"></script>  
   <script src="js/remote.js"></script>  
             
</head> 

<body>
<?php
include_once '../vars.php';

gpio_initialise(); // initialising the GPIO pins

?>
<div align="center" id='box_outer'>
	<!-- =================Direction Buttons=================================================== -->
	<div class='box_row'>
		<input  class="button"  type="submit" onclick="button_direction('f');" value="FWD"/>
	</div>
	<br />
	<div class='box_row'>
		<input class="button" style="float:left" type="submit" onclick="button_direction('l');" value="LEFT"/>
		<input class="button" type="submit" onclick="button_direction('s');" value="STOP"/>
		<input  class="button" style="float:right" type="submit" onclick="button_direction('r');" value="RIGHT"/>
	</div>
	<br />
	<div class='box_row'>
			<input  class="button" type="submit" onclick="button_direction('b');" value="BACK"/>
	</div>
	<!-- ================================================================================= -->
	
	<br><br>
	
	<!-- =============Range Slider for speed==============================================-->
	<div class='box_row'>
	
		<div class="slidecontainer">
			<input type="range" min="0" max="100" value="50" class="slider" id="myRange" step="5">
			<p>Speed: <span id="speed">50</span></p>
		</div>
		<script>
			var slider = document.getElementById("myRange");
			var output = document.getElementById("speed");
			output.innerHTML = slider.value;
			speed_slider(slider.value);
			slider.oninput = function() {
				output.innerHTML = this.value;
				speed_slider(this.value);
				}
		</script>
	</div>
	<!-- ================================================================================== -->
</div>

</body>
</html>
