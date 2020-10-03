$(document).keydown(function(e){
    if (e.keyCode == 37)  
    	 button_direction('l');
    if (e.keyCode == 38) 
        button_direction('f');
    if (e.keyCode == 39) 
    	  button_direction('r');
    if (e.keyCode == 40)
    	 button_direction('b');
    if (e.keyCode == 32)
    	 button_direction('s');
});

//---------DIRECTION---------------------------------
function button_direction(val)
{
	console.log("button val:" + val);
	$.post("ajax_direction.php",
    {
      direction: val
    }
    );
}

//---------SPEED--------------------------------------
function speed_slider(val)
{
	console.log("slider val:" + val);
	$.post("ajax_speed.php",
    {
      speed:val
    }
    );
}





