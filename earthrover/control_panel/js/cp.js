function toggle_light(id)
	{
		//alert(id);
		console.log(id);
		button_caption=document.getElementById(id).value;
		//alert(button_caption);
		if(button_caption=="OFF"){
			document.getElementById(id).value="ON";
			document.getElementById(id).style.backgroundColor="#66ff66";
			//alert("hi");
			set_lights(id,1);
		}
		if(button_caption=="ON"){
			document.getElementById(id).value="OFF";
			document.getElementById(id).style.backgroundColor="white";
			set_lights(id,0);
		}
			
	}
function set_lights(id,state)
{
		$.post("/earthrover/camera_lights/ajax_lights.php",
		{
		light_id: id,
		state: state
		}
		);

}

function camera(status)
{
		//alert(status);
		if (status=="on"){
			disable_buttons();
		}
		else{
			enable_buttons();
		}
		
		$.post("/earthrover/camera_lights/ajax_camera.php",
		{
		camera:status
		}
		);
		sleep(1000);
		location.reload();
}


var z=1;
function button_AI_action(id)
{
	console.log(id + "************");
	var path = "/earthrover/" + id + "/web/ajax_master.php"
	var id_img="img_" + id;
	
	if (z==1){
		console.log(id + " ON !!!!!!!!!!!!");
		z=z+1;
		document.getElementById(id).style.backgroundColor="#66ff66";//#66ff66
		disable_buttons();
		document.getElementById(id).disabled=false;
		
		$.post(path,{state: 1});
				
		sleep(2000);
		
		document.getElementById(id_img).style.display="block";
					
	}
	else{
		console.log(id + " OFF ###########");
		z=1;
		document.getElementById(id).style.backgroundColor="white";
		enable_buttons();
		$.post(path,{state: 0});
		
		document.getElementById(id_img).style.display="none";
	}
				
}

function disable_buttons(){
	console.log("disable_buttons");
	
	document.getElementById("object_detection").disabled=true;
	document.getElementById("object_tracking").disabled=true;
	document.getElementById("human_following").disabled=true;
	document.getElementById("image_classification").disabled=true;
	document.getElementById("cam_on").disabled=true;
	
	//document.getElementById(id).disabled=false;
	
}

function enable_buttons(){
	console.log("enable_buttons");
	
	document.getElementById("object_detection").disabled=false;
	document.getElementById("object_tracking").disabled=false;
	document.getElementById("human_following").disabled=false;
	document.getElementById("image_classification").disabled=false;
	document.getElementById("cam_on").disabled=false;
	
	
}

function init(){
	document.getElementById("hw_1").innerHTML="<a style='color:grey;text-decoration:none' href='https://helloworld.co.in' target='_blank'>helloworld.co.in</a>";
	document.getElementById("hw_2").innerHTML="<a style='color:grey;text-decoration:none' href='https://github.com/jiteshsaini' target='_blank'>github.com/jiteshsaini</a>";
	document.getElementById("hw_3").innerHTML="<a style='color:grey;text-decoration:none' href='https://www.youtube.com/channel/UC_2OyRNVCWCH8ipgmAoJ1mA' target='_blank'>YouTube</a>";
	
	console.log(">>>>");
	$.post("/earthrover/control_panel/misc/hw.php",
		{
		entry_by: 'control_panel',
		page: 'index.php'
		});
}

function sleep(milliseconds) {
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds){
			break;
		}
	}
}

