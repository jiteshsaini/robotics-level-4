function button_tts()
{
	var str = document.getElementById("txt_tts").value;
	//var str2 = document.getElementById("radio1").value;
	var state = document.getElementById('radio1').checked;
	
	console.log(str);
	
	var gender;
	
	if (state)gender='m';
	else gender='f';
	
	
	console.log(gender);
	//alert(str);
	$.post("/earthrover/speaker/web/ajax_tts.php",
    {
      str:str.toLowerCase(),
      gen:gender
    }
    );
}

function button_recording(no)
{
	var path;
	switch(no) {
		case 1:path="earthrover/speaker/sounds/horn.mp3";break;
		case 2:path="earthrover/speaker/sounds/siren.mp3";break;
    }
	
	console.log(path);
	//alert(str);
	$.post("/earthrover/speaker/web/ajax_omx.php",
    {
      rec_path:path
    }
    );
}
