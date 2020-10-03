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
			document.getElementById(id).style.backgroundColor="lightgray";
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
		$.post("/earthrover/camera_lights/ajax_camera.php",
		{
		camera:status
		}
		);
		sleep(1000);
		location.reload();
}


function sleep(milliseconds) {
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds){
			break;
		}
	}
}

