<!--
Project: Earthrover
Created by: Jitesh Saini
-->
<html>
<head>        
   <title>Object detection</title>
   <style>
   #box_outer{
		width:100%;
		height:100vh;
		float:left;
		border:1px solid gray;
	}
	#box_camera{
		width:68%;
		//height:100vh;
		float:left;
		border:1px solid lightgrey;
		padding:0.5%;
		margin: 0.5%;
	}
	#box_labels{
		width:28%;
		float:left;
		border:1px solid lightgrey;
		padding:0.4%;	
		height:400px
		//margin: 0.5%;
	}
	#box_remote{
		width:28%;
		float:left;
		border:1px solid lightgray;
		//padding:1%;	
		//margin: 0.5%;
	}
	#box_labels input{
		//border-width:2px; 
		//border-radius:5px;
		width:48%;
		height:50px;
		background-color:#011f61;
		color:white;
		float:left;
		font-size: 20px;
		margin:0.5%;
	}
	#box_labels input[type="submit"]:hover {
		//background-color: blue;
		color:green;
	}
	
   </style>
   <script src="/earthrover/control_panel/js/jquery.min.js"></script>            
   <script>
	function button_action(id)
	{
		label=document.getElementById(id).value
		label=label.toLowerCase(label);
		console.log("label:" + label);
		
		$.post("object_cmd.php",
		{
		lbl: label
		}
		);
		
		console.log("id:" + id);
		var i;
		for (i = 1; i <= 8; i++) {
			id1='b'+i;
			document.getElementById(id1).style.backgroundColor="#011f61";
			document.getElementById(id1).style.backgroundColor="#011f61";
		}
		
		document.getElementById(id).style.backgroundColor="#00ff00";
		
	}
	 
	function data_request_timer(delay){
		window.setInterval(get_data, delay); //timer for initiating ajax request 
		
	}

	function get_data(){
		console.log("fetching data from server");

		$.get("object_found.php", 
		function(data, status){
			//document.getElementById("info").innerHTML = data;
			if(data>0){
				document.body.style.background = "orange";
			}
			else{
				document.body.style.background = "white";
			}
		});

	}
	
	
   </script>
</head> 
<body onload="data_request_timer(600)">
<?php
//bgcolor='orange'
//onload=alert('start the python script manually to stream video')
$host=$_SERVER['SERVER_ADDR'];//192.168.1.20
$link_vid= 'http://'.$host.':2204';
$link_remote='http://'.$host.'/earthrover/control_panel/remote.php';
//echo"$link_remote";
echo"<div id='box_outer'>";//------------------------
	echo"<h2 align='center' style='color:darkblue'>Object Detection with TensorFlow Lite</h2>";
	//echo"<b id='info'></b>";
	echo"<div align='center' id='box_camera'>";//------------------------
		echo"<iframe src='$link_vid' height='650px' width='90%'></iframe>";
	echo"</div>";
	
	echo"<div id='box_labels'>";//------------------------
		echo"<h3 align='center' style='color:#011f61'>Select Object to Monitor</h3>";
		
		echo"<input id='b1' type='submit' onclick=button_action('b1'); value='Person'/>";
		
		echo"<input id='b2' type='submit' onclick=button_action('b2'); value='Dog'/>";
		
		echo"<input id='b3' type='submit' onclick=button_action('b3'); value='Cat'/>";
		
		echo"<input id='b4' type='submit' onclick=button_action('b4'); value='Car'/>";
		
		echo"<input id='b5' type='submit' onclick=button_action('b5'); value='Motorcycle'/>";
		
		echo"<input id='b6' type='submit' onclick=button_action('b6'); value='Bicycle'/>";
		
		echo"<input id='b7' type='submit' onclick=button_action('b7'); value='Bus'/>";
		
		echo"<input id='b8' type='submit' onclick=button_action('b8'); value='Airplane'/>";
		
		
		//echo"<input id='headlight' style='background-color:lightgray' type='submit' onclick=toggle_light('person'); value='OFF'/>";
	
	echo"</div>";
	
	echo"<div id='box_remote'>";//------------------------
		echo"<iframe src='$link_remote' height='380px' width='100%'></iframe>";
	echo"</div>";

echo"</div>";

?>

</body>
</html>
